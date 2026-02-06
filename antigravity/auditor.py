import os
import requests
import json
import time
import re
from antigravity.utils import get_git_diff, get_tree_structure
from antigravity.notifier import alert_critical
from antigravity.config import CONFIG

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "YOUR_API_KEY_HERE")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions" # Example URL

class Auditor:
    def __init__(self, project_root):
        self.project_root = project_root
        self.failure_counts = {}
        
        # Enhanced "Executor" Prompt
        self.system_prompt = """
Role: You are Antigravity Executor (Sheriff-1). Your goal is to FULLY IMPLEMENT the PLAN.md.
Rules:
1. If the code is missing or incorrect, rewrite the ENTIRE file.
2. Wrap the code in ```python ... ``` blocks.
3. Logic must be robust (anti-bot, error handling).
4. Do NOT include explanations outside the code block if possible, or keep them minimal.
5. If the current code is empty or just a placeholder, implement the full logic based on PLAN.md.

Output Format:
- If task complete and code is correct: "STATUS: PASS"
- If fix/implementation needed:
  FIX_CODE:
  ```python
  [Full Code Here]
  ```
  RATIONALE: [Why]
"""

    def audit_and_fix(self, file_path, error_context=None):
        """
        Main entry point for Agent Takeover.
        Returns: "PASS", "FIXED", or "FAIL"
        """
        # Circuit Breaker Check
        if self.failure_counts.get(file_path, 0) >= CONFIG.get("RETRY_LIMIT", 3):
             print(f"Skipping {file_path}: Manual Mode engaged.")
             alert_critical(f"MANUAL MODE: Stopped auditing {os.path.basename(file_path)} after failures.")
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
                  self._log_audit(file_path, "STATUS: PASS")
                  self.failure_counts[file_path] = 0
                  return "PASS"
                  
             new_code = self._extract_code(response_content)
             if new_code:
                 # Self-Reflection / Safety Check could go here
                 self._apply_fix(file_path, new_code)
                 self._log_audit(file_path, f"[AGENT TAKEOVER]\nApplied Fix.\nRationale: Extracted from response.")
                 return "FIXED"
             else:
                 print("Failed to extract code from response.")
                 return "FAIL"
        elif "STATUS: PASS" in response_content:
             self._log_audit(file_path, "STATUS: PASS")
             self.failure_counts[file_path] = 0
             return "PASS"
        else:
             # Fallback: Assume fail if no explicit pass and no code
             self._log_audit(file_path, f"[UNCERTAIN RESPONSE]\n{response_content}")
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
                    "temperature": CONFIG.get("TEMPERATURE", 0.0),
                    "max_tokens": CONFIG.get("MAX_TOKENS", 4096)
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
         with open(os.path.join(self.project_root, "vibe_audit.log"), "a", encoding='utf-8') as log:
             log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {os.path.basename(file_path)}:\n{message}\n{'-'*20}\n")
