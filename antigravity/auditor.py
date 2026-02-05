import os
import requests
import os
import requests
import json
import time
from antigravity.utils import get_git_diff, get_tree_structure
from antigravity.notifier import alert_critical

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "YOUR_API_KEY_HERE")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions" # Example URL

class Auditor:
    def __init__(self, project_root):
        self.project_root = project_root
        self.failure_counts = {}

    def audit_file(self, file_path):
        # Circuit Breaker Check
        if self.failure_counts.get(file_path, 0) >= 3:
            print(f"Skipping {file_path}: Manual Mode engaged due to repeated failures.")
            alert_critical(f"MANUAL MODE: Stopped auditing {os.path.basename(file_path)} after 3 failures.")
            return

        print(f"Auditing file: {file_path}")
        
        # 1. Context Assembly
        plan_path = os.path.join(self.project_root, "PLAN.md")
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_content = f.read()
        except FileNotFoundError:
            plan_content = "No PLAN.md found."

        tree = get_tree_structure(self.project_root)
        diff = get_git_diff(self.project_root, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()

        # 2. Construct Sheriff-1 Prompt
        system_prompt = """
Role: You are Sheriff-1, a Senior Auditor supervising Antigravity AI. Motto: "Vibe is good, but logic is king."

Work Rules:
- Spot Hallucinations: Focus on hollow shell code (e.g., // TODO or just function templates).
- Plan Contrast: Strictly check against PLAN.md for security/functionality.
- Correction Instructions: Imperative sentences (e.g., "Do not use hardcoded secret...").

Output Protocol:
- If Pass: "STATUS: PASS"
- If Fail: Start with "[SYSTEM CRITICAL]" followed by ERROR, FIX, RATIONALE.
"""
        
        user_prompt = f"""
[Project Context]
{tree}

[Plan]
{plan_content}

[File Content: {file_path}]
{current_code}

[Git Diff]
{diff}

Please audit the changes.
"""

        # 3. Call DeepSeek API (Mock implementation for now if no key)
        if DEEPSEEK_API_KEY == "YOUR_API_KEY_HERE":
            print("DeepSeek API Key not set. Using mock logic.")
            # Simple mock: if "TODO" in code and "Implement" in plan, fail.
            if "TODO" in current_code and "return True" in current_code: # Hallucination check
                response_content = """[SYSTEM CRITICAL]
ERROR: Hallucinated authentication logic.
FIX: Implement real JWT verification instead of returning True.
RATIONALE: Security risk."""
            else:
                response_content = "STATUS: PASS"
        else:
            try:
                response = requests.post(
                    DEEPSEEK_API_URL,
                    headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "deepseek-reasoner", # or deepseek-chat
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.0
                    },
                    timeout=30
                )
                response.raise_for_status()
                response_content = response.json()['choices'][0]['message']['content']
            except Exception as e:
                print(f"API Call Failed: {e}")
                return

        # 4. Process Result
        if "[SYSTEM CRITICAL]" in response_content:
            self.failure_counts[file_path] = self.failure_counts.get(file_path, 0) + 1
            self.handle_failure(file_path, response_content)
        else:
            print("Audit Passed.")
            self.failure_counts[file_path] = 0 # Reset on pass
            
            # Log success
            with open(os.path.join(self.project_root, "vibe_audit.log"), "a", encoding='utf-8') as log:
                 log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {os.path.basename(file_path)}: STATUS: PASS\n")

    def handle_failure(self, file_path, feedback):
        print("Audit Failed!")
        alert_critical("Audit Failed! See VIBE_FIX.md")
        
        # Log to vibe_audit.log for Dashboard
        with open(os.path.join(self.project_root, "vibe_audit.log"), "a", encoding='utf-8') as log:
             log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {os.path.basename(file_path)}: [SYSTEM CRITICAL]\n{feedback}\n{'-'*20}\n")

        # Write to VIBE_FIX.md
        fix_path = os.path.join(self.project_root, "VIBE_FIX.md")
        with open(fix_path, 'w', encoding='utf-8') as f:
            f.write(feedback)
            
        # Feedback Injection
        self.inject_feedback(file_path)

    def inject_feedback(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines[0].startswith("# FIXME: DeepSeek Auditor"):
            lines.insert(0, "# FIXME: DeepSeek Auditor identified a logic error. See VIBE_FIX.md\n")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Injected FIXME into {file_path}")
