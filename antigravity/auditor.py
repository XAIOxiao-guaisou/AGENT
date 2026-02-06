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
             self.state_manager.log_audit(file_path, "circuit_breaker", f"Manual mode after {retry_count} failures", "FAIL")
             return "FAIL"

        # Read PLAN.md
        plan_path = os.path.join(self.project_root, "PLAN.md")
        if not os.path.exists(plan_path):
            print("PLAN.md not found. Skipping audit.")
            return "PASS"
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = f.read()

        # Read current code
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist. Creating placeholder.")
            current_code = "# Placeholder\n"
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                current_code = f.read()

        # Get Git Diff
        diff = get_git_diff(self.project_root, file_path)

        # Build Prompt
        user_prompt = f"""
[PLAN.md]
{plan}

[Current Code: {os.path.basename(file_path)}]
```python
{current_code}
```

[Git Diff]
{diff if diff else "No diff available"}

[Error Context]
{error_context if error_context else "No errors reported"}
"""

        # Call DeepSeek
        response = self._call_deepseek(user_prompt)
        if not response:
            self.state_manager.increment_retry(file_path)
            return "FAIL"

        # Check if PASS
        if "STATUS: PASS" in response:
            print(f"✅ {os.path.basename(file_path)} passed audit.")
            self.state_manager.log_audit(file_path, "audit", "STATUS: PASS", "PASS")
            self.state_manager.reset_retry(file_path)
            return "PASS"

        # Extract and apply fix
        code = self._extract_code(response)
        if code:
            self._apply_fix(file_path, code)
            self.state_manager.log_audit(file_path, "fix", "[AGENT TAKEOVER] Applied Fix", "FIXED")
            self.state_manager.reset_retry(file_path)
            return "FIXED"
        else:
            print(f"❌ Could not extract code from response for {file_path}")
            self.state_manager.increment_retry(file_path)
            return "FAIL"

    def _call_deepseek(self, user_prompt):
        """
        Call DeepSeek API with current mode's configuration.
        """
        api_key = CONFIG.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("DEEPSEEK_API_KEY not configured.")
            return None

        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=CONFIG.get("API_TIMEOUT", 60)
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

    # ============================================================
    # Multi-File Project-Level Takeover Methods
    # 多文件项目级接管方法
    # ============================================================
    
    def _extract_multi_files(self, text):
        """
        解析 LLM 返回的多文件格式
        Parse multi-file format from LLM response
        
        Returns:
            {
                'create': {'src/a.py': 'code...', 'src/b.py': 'code...'},
                'delete': ['src/old.py']
            }
        """
        result = {'create': {}, 'delete': []}
        
        # 匹配 FILE: path + code block
        # Match FILE: path + code block
        file_pattern = r"FILE:\s*([^\n]+)\s*```python\n(.*?)\n```"
        for match in re.finditer(file_pattern, text, re.DOTALL):
            path = match.group(1).strip()
            code = match.group(2).strip()
            result['create'][path] = code
        
        # 匹配 DELETE: path
        # Match DELETE: path
        delete_pattern = r"DELETE:\s*([^\n]+)"
        for match in re.finditer(delete_pattern, text):
            path = match.group(1).strip()
            result['delete'].append(path)
        
        return result
    
    def _get_full_project_context(self, target_folder="src", target_files=None):
        """
        获取项目级上下文
        Get project-level context
        
        Args:
            target_folder: 目标文件夹 / Target folder
            target_files: 指定文件列表,如果为 None 则获取整个文件夹 / Specific files, or None for entire folder
        
        Returns:
            格式化的项目上下文字符串 / Formatted project context string
        """
        context = "=== PROJECT CONTEXT ===\n\n"
        
        # 添加项目树结构
        # Add project tree structure
        try:
            tree = get_tree_structure(self.project_root)
            context += f"[Project Tree]\n{tree}\n\n"
        except Exception as e:
            print(f"⚠️ Could not get tree structure: {e}")
        
        # 获取文件列表
        # Get file list
        if target_files is None:
            target_files = []
            target_path = os.path.join(self.project_root, target_folder)
            if os.path.exists(target_path):
                for root, dirs, files in os.walk(target_path):
                    for file in files:
                        if file.endswith(('.py', '.js', '.tsx', '.ts')):
                            target_files.append(os.path.join(root, file))
        
        # 添加文件内容
        # Add file contents
        context += "[Current Files]\n"
        for file_path in target_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    rel_path = os.path.relpath(file_path, self.project_root)
                    context += f"\nFILE: {rel_path}\n```python\n{content}\n```\n"
                except Exception as e:
                    print(f"⚠️ Could not read {file_path}: {e}")
        
        return context
    
    def audit_and_fix_project(self, target_folder="src", target_files=None):
        """
        项目级审计与修复
        Project-level audit and fix
        
        Args:
            target_folder: 目标文件夹 / Target folder
            target_files: 指定文件列表 / Specific file list
        
        Returns:
            {'status': 'SUCCESS/FAIL', 'files_modified': [...], 'files_deleted': [...]}
        """
        print("🌐 启动项目级接管...")
        print("🌐 Starting project-level takeover...")
        
        # 1. 读取 PLAN.md
        # 1. Read PLAN.md
        plan_path = os.path.join(self.project_root, "PLAN.md")
        if not os.path.exists(plan_path):
            print("❌ PLAN.md not found")
            return {'status': 'FAIL', 'files_modified': [], 'files_deleted': []}
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = f.read()
        
        # 2. 获取项目上下文
        # 2. Get project context
        context = self._get_full_project_context(target_folder, target_files)
        
        # 3. 构造 Prompt
        # 3. Build prompt
        user_prompt = f"""
{self.system_prompt}

[PROJECT PLAN]
{plan}

{context}

TASK: Implement or refactor the project according to the PLAN.
Output ALL necessary files using the FILE:/DELETE: format.
"""
        
        # 4. 调用 LLM
        # 4. Call LLM
        print("🤖 调用 DeepSeek API...")
        print("🤖 Calling DeepSeek API...")
        response = self._call_deepseek(user_prompt)
        
        if not response:
            print("❌ API call failed")
            return {'status': 'FAIL', 'files_modified': [], 'files_deleted': []}
        
        # 5. 解析多文件输出
        # 5. Parse multi-file output
        files_dict = self._extract_multi_files(response)
        
        if not files_dict['create'] and not files_dict['delete']:
            print("ℹ️ No file operations detected in response")
            return {'status': 'PASS', 'files_modified': [], 'files_deleted': []}
        
        # 6. 写入文件
        # 6. Write files
        modified_files = []
        for path, code in files_dict['create'].items():
            full_path = os.path.join(self.project_root, path)
            
            # 安全检查
            # Safety check
            skip = False
            for protected in CONFIG.get("PROTECTED_PATHS", []):
                if protected in path.replace("\\", "/"):
                    print(f"🛡️ Skipping protected path: {path}")
                    skip = True
                    break
            
            if skip:
                continue
            
            # 创建目录
            # Create directory
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 写入文件
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            modified_files.append(path)
            self.state_manager.log_audit(path, "project_create", "Created/modified by project executor", "FIXED")
            print(f"✅ Written: {path}")
        
        # 7. 删除文件
        # 7. Delete files
        deleted_files = []
        for path in files_dict['delete']:
            full_path = os.path.join(self.project_root, path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                deleted_files.append(path)
                self.state_manager.log_audit(path, "project_delete", "Deleted by project executor", "INFO")
                print(f"🗑️ Deleted: {path}")
        
        print(f"\n✅ 项目同步完成! / Project sync complete!")
        print(f"   修改文件 / Modified: {len(modified_files)}")
        print(f"   删除文件 / Deleted: {len(deleted_files)}")
        
        return {
            'status': 'SUCCESS',
            'files_modified': modified_files,
            'files_deleted': deleted_files
        }
