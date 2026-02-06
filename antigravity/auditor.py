import os
import requests
import json
import time
import re
from antigravity.utils import get_git_diff, get_tree_structure
from antigravity.notifier import alert_critical
from antigravity.config import CONFIG
from antigravity.state_manager import StateManager

class Auditor:
    def __init__(self, project_root, state_manager=None):
        self.project_root = project_root
        self.state_manager = state_manager or StateManager(project_root)
        self.current_mode = CONFIG.get("ACTIVE_MODE", "executor")
        
        # Load prompt from config
        self._load_prompt()
    
    def _load_prompt(self):
        """Load system prompt from config based on current mode."""
        prompts = CONFIG.get("prompts", {})
        modes = prompts.get("modes", {})
        
        if self.current_mode not in modes:
            print(f"⚠️ Warning: Mode '{self.current_mode}' not found. Using 'executor'.")
            self.current_mode = "executor"
        
        mode_config = modes.get(self.current_mode, {})
        self.system_prompt = mode_config.get("system_prompt", "You are a code assistant.")
        self.temperature = mode_config.get("temperature", 0.0)
        self.max_tokens = mode_config.get("max_tokens", 4096)
        
        print(f"🤖 Auditor Mode: {self.current_mode}")
    
    def set_mode(self, mode_name: str):
        """Switch to a different prompt mode."""
        self.current_mode = mode_name
        self._load_prompt()

    def audit_and_fix(self, file_path, error_context=None):
        """
        Main entry point for Agent Takeover.
        Returns: "PASS", "FIXED", or "FAIL"
        """
        # Circuit Breaker Check using StateManager
        retry_count = self.state_manager.get_retry_count(file_path)
        if retry_count >= CONFIG.get("RETRY_LIMIT", 3):
             print(f"Skipping {file_path}: Manual Mode engaged.")
             alert_critical(f"MANUAL MODE: Stopped auditing {os.path.basename(file_path)} after failures.")
             self.state_manager.log_audit(file_path, "circuit_breaker", 
                                         f"Manual mode after {retry_count} failures", "FAIL")
             return "FAIL"

        print(f"Auditing/Executing file: {file_path}")
        
        # 1. Context Assembly
        plan_path = os.path.join(self.project_root, "PLAN.md")
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_content = f.read()
        except FileNotFoundError:
            plan_content = "No PLAN.md found."

        tree = get_tree_structure(self.project_root)
        diff = get_git_diff(self.project_root, file_path)
        
        try:
             with open(file_path, 'r', encoding='utf-8') as f:
                current_code = f.read()
        except FileNotFoundError:
             current_code = "" # Empty file treatment

        # Inject Error Context if available (Smart Retry)
        error_section = ""
        if error_context:
            error_section = f"\n[Previous Test Failure Log]\n{error_context}\n\nFIX the code based on the above error log."

        user_prompt = f"""
[Project Context]
{tree}

[Plan]
{plan_content}

[File Content: {file_path}]
{current_code}

[Git Diff]
{diff}
{error_section}

Apply the plan and provide the full corrected code if necessary.
"""

        # 2. Call DeepSeek
        response_content = self._call_deepseek(user_prompt)
        if not response_content:
             return "FAIL"

        # 3. Process Result
        if "FIX_CODE:" in response_content or "```python" in response_content:
             # Check for "STATUS: PASS" to avoid false positives if LLM chats too much
             if "STATUS: PASS" in response_content and "FIX_CODE:" not in response_content:
                  self.state_manager.log_audit(file_path, "audit", "STATUS: PASS", "PASS")
                  self.state_manager.reset_retry(file_path)
                  return "PASS"
                  
             new_code = self._extract_code(response_content)
             if new_code:
                 # Self-Reflection / Safety Check could go here
                 self._apply_fix(file_path, new_code)
                 self.state_manager.log_audit(file_path, "fix", 
                                             "[AGENT TAKEOVER] Applied Fix", "FIXED")
                 return "FIXED"
             else:
                 print("Failed to extract code from response.")
                 return "FAIL"
        elif "STATUS: PASS" in response_content:
             self.state_manager.log_audit(file_path, "audit", "STATUS: PASS", "PASS")
             self.state_manager.reset_retry(file_path)
             return "PASS"
        else:
             # Fallback: Assume fail if no explicit pass and no code
             self.state_manager.log_audit(file_path, "uncertain", 
                                         f"Uncertain response: {response_content[:200]}", "FAIL")
             self.state_manager.increment_retry(file_path)
             return "FAIL"

    def _call_deepseek(self, user_prompt):
        api_key = CONFIG.get("DEEPSEEK_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            print("DeepSeek API Key not set.")
            return None # Or mock logic
            
        try:
            response = requests.post(
                CONFIG.get("DEEPSEEK_API_URL"),
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": CONFIG.get("MODEL_NAME", "deepseek-reasoner"),
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"API Call Failed: {e}")
            return None

    def _extract_code(self, text):
        """
        Robust code extractor supporting ```python ... ``` blocks.
        """
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback for generic blocks
        match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        return None

    def _apply_fix(self, file_path, code):
        """
        Directly overwrite the file (Agent Takeover).
        """
        # Safety Check: Protected Paths
        for protected in CONFIG.get("PROTECTED_PATHS", []):
            if protected in file_path.replace("\\", "/"):
                 print(f"Security Alert: Attempt to modify protected path {file_path}")
                 return

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Agent wrote code to {file_path}")

    def _log_audit(self, file_path, message):
        """Legacy log method - now handled by StateManager."""
        # Kept for backward compatibility, but StateManager is now primary
        pass
