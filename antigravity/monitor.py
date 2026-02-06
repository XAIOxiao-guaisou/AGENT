import time
import os
import fnmatch
import subprocess
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer, Lock
from antigravity.auditor import Auditor
from antigravity.test_runner import run_tests_for_file
from antigravity.config import CONFIG
from antigravity.state_manager import StateManager
from antigravity.change_detector import ChangeDetector

class AntigravityMonitor(FileSystemEventHandler):
    def __init__(self, project_root):
        self.project_root = project_root
        self.state_manager = StateManager(project_root)
        self.auditor = Auditor(project_root, state_manager=self.state_manager)
        self.timers = {}
        self.debounce_seconds = 3.0
        self.execution_lock = Lock() # Prevent recursive loops
        self.processing_files = set()
        
        # P3: 初始化变更检测器 / Initialize change detector
        self.change_detector = ChangeDetector(project_root)
        self.incremental_threshold = CONFIG.get("INCREMENTAL_THRESHOLD", 3)
        print(f"✅ P3: ChangeDetector initialized (threshold={self.incremental_threshold})")
        
        # Load ignore patterns from config
        self.ignore_patterns = CONFIG.get("IGNORE_PATTERNS", [])
        self.watch_extensions = CONFIG.get("WATCH_EXTENSIONS", [".py", ".js", ".tsx", ".ts", ".md"])

    def on_modified(self, event):
        self.process_event(event)
        
    def on_created(self, event):
        self.process_event(event)
    
    def _should_ignore(self, file_path):
        """Check if file should be ignored based on patterns."""
        # Normalize path for pattern matching
        normalized_path = file_path.replace("\\", "/")
        
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(normalized_path, pattern):
                return True
        
        return False

    def process_event(self, event):
        if event.is_directory:
            return
        
        filename = event.src_path
        
        # Check if file should be ignored
        if self._should_ignore(filename):
            return
        
        # Only monitor files with watched extensions or PLAN.md
        if not any(filename.endswith(ext) for ext in self.watch_extensions):
            if not filename.endswith('PLAN.md'):
                return
        
        # Special handling for PLAN.md changes - trigger environment check
        if filename.endswith('PLAN.md'):
            self._trigger_env_check()
            return  # PLAN.md 由 _trigger_env_check 处理,不再走单文件流程
            
        # IGNORE events if we are currently processing this file (Execution Lock)
        if filename in self.processing_files:
            return

        # Debouncing
        if filename in self.timers:
            self.timers[filename].cancel()
        
        timer = Timer(self.debounce_seconds, self.trigger_takeover, args=[filename])
        self.timers[filename] = timer
        timer.start()
    
    def _trigger_env_check(self):
        """
        触发环境检查和项目同步
        Trigger environment check and project sync
        """
        from antigravity.env_checker import check_dependencies
        
        plan_path = os.path.join(self.project_root, "PLAN.md")
        if os.path.exists(plan_path):
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_content = f.read()
                
                # 1. 环境依赖检查
                # 1. Environment dependency check
                print("🛡️ PLAN.md 变更 - 运行环境检查...")
                print("🛡️ PLAN.md changed - Running environment check...")
                missing_deps = check_dependencies(plan_content)
                
                success = len(missing_deps) == 0
                self.state_manager.log_environment_check(missing_deps, success)
                
                if not success:
                    print(f"⚠️ 缺失依赖: {', '.join(missing_deps)}")
                    print(f"⚠️ Missing dependencies: {', '.join(missing_deps)}")
                
                # 2. 检查是否需要项目级同步
                # 2. Check if project-level sync is needed
                if self._is_major_plan_change(plan_content):
                    print("🌐 检测到架构级变更,触发项目级同步...")
                    print("🌐 Major architectural change detected, triggering project sync...")
                    self.trigger_project_sync()
                    
            except Exception as e:
                print(f"⚠️ 环境检查失败: {e}")
                print(f"⚠️ Environment check failed: {e}")
    
    def _is_major_plan_change(self, plan_content):
        """
        检测 PLAN.md 是否涉及架构级变更
        Detect if PLAN.md involves architectural-level changes
        
        重大变更标准 / Major change criteria:
        - 包含 2+ 个目标文件 / Contains 2+ target files
        - 提到关键词: 项目/project/架构/architecture/重构/refactor/全部/all
        """
        # 标准1: 检测目标文件列表变动 (匹配 - `src/...)
        # Criterion 1: Detect target file list changes
        file_patterns = re.findall(r'[`"\'\s](src/[^\s`"\']+\.py)', plan_content)
        unique_files = set(file_patterns)
        
        # 标准2: 关键词检测
        # Criterion 2: Keyword detection
        keywords = ['项目', 'project', '架构', 'architecture', '重构', 'refactor', '全部', 'all', '所有']
        has_keywords = any(k in plan_content.lower() for k in keywords)
        
        is_major = len(unique_files) >= 2 or has_keywords
        
        if is_major:
            print(f"📊 检测到 {len(unique_files)} 个目标文件 / Detected {len(unique_files)} target files")
            if has_keywords:
                print("📊 检测到架构关键词 / Detected architectural keywords")
        
        return is_major
    
    def trigger_project_sync(self):
        """
        执行项目级智能同步循环 (P3 升级版)
        Execute project-level intelligent sync loop (P3 upgraded)
        
        P3 Features:
        - 变更检测: 0 变更 = 不触发 API / Change detection: 0 changes = no API
        - 增量同步: ≤3 变更 = 增量修复 / Incremental: ≤3 changes = incremental fix
        - 全量同步: >3 变更 = 全量重构 / Full sync: >3 changes = full refactor
        - 快照管理: 成功后自动保存快照 / Snapshot: auto-save after success
        """
        with self.execution_lock:  # 必须持有锁,静默所有文件变动事件 / Must hold lock to silence file events
            print("🌐 [P3 Project Sync] 启动智能同步流程...")
            print("🌐 [P3 Project Sync] Starting intelligent sync...")
            
            # 设置状态
            # Set status
            self.state_manager.set_takeover_status("Analyzing")
            
            # P3: 扫描项目文件并检测变更
            # P3: Scan project files and detect changes
            try:
                # 获取所有项目文件
                project_files = []
                for root, dirs, files in os.walk(self.project_root):
                    # 跳过忽略目录
                    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.ignore_patterns)]
                    
                    for file in files:
                        if any(file.endswith(ext) for ext in self.watch_extensions):
                            rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                            project_files.append(rel_path.replace('\\', '/'))
                
                # 扫描文件
                self.change_detector.scan_files(project_files)
                
                # 获取变更摘要
                summary = self.change_detector.get_change_summary()
                
                changed_files = summary['changed']
                new_files = summary['new']
                total_changes = summary['total_changes']
                
                print(f"📊 Change Summary: {total_changes} changes ({len(changed_files)} modified, {len(new_files)} new)")
                
            except Exception as e:
                print(f"⚠️ Change detection failed: {e}, falling back to full sync")
                total_changes = 999  # 强制全量同步
                changed_files = []
                new_files = []
            
            # P3: 智能决策 - 增量 vs 全量
            # P3: Intelligent decision - incremental vs full
            
            # 场景 1: 零变更 - 拦截事件,不触发 API
            # Scenario 1: Zero changes - block event, no API call
            if total_changes == 0:
                print("✅ No physical changes detected, skipping API call")
                self.state_manager.set_takeover_status("Idle", "No changes")
                return
            
            # 场景 2: 小变更 - 增量修复
            # Scenario 2: Small changes - incremental fix
            elif total_changes <= self.incremental_threshold:
                print(f"🎯 Incremental sync mode ({total_changes} ≤ {self.incremental_threshold} changes)")
                self.state_manager.set_takeover_status("Incremental Sync")
                
                # 切换至执行模式
                self.auditor.set_mode('executor')
                
                # 只处理变更的文件
                target_files = changed_files + new_files
                
                result = self.auditor.audit_and_fix_project(target_files=target_files)
                
                if result['status'] == 'SUCCESS':
                    modified = len(result.get('files_modified', []))
                    print(f"✅ Incremental sync complete: {modified} files fixed")
                    
                    # 运行测试
                    print("🧪 Running tests on changed files...")
                    self.run_full_test_suite()
                    
                    # 保存快照
                    self.change_detector.save_snapshot({"mode": "incremental", "files": target_files})
                    print("✅ Snapshot saved")
                else:
                    print("❌ Incremental sync failed")
                    self.state_manager.set_takeover_status("Error", "Incremental Sync Failed")
            
            # 场景 3: 大变更 - 全量同步
            # Scenario 3: Large changes - full sync
            else:
                print(f"🌐 Full sync mode ({total_changes} > {self.incremental_threshold} changes)")
                self.state_manager.set_takeover_status("Full Sync")
                
                # 切换至项目执行模式
                self.auditor.set_mode('project_executor')
                
                # 全量同步
                result = self.auditor.audit_and_fix_project()
                
                if result['status'] == 'SUCCESS':
                    modified = len(result.get('files_modified', []))
                    deleted = len(result.get('files_deleted', []))
                    print(f"✅ Full sync complete: Modified {modified} files, Deleted {deleted} files")
                    
                    # 触发全量集成测试
                    print("🧪 Starting full integration test...")
                    self.run_full_test_suite()
                    
                    # 保存快照
                    self.change_detector.save_snapshot({"mode": "full", "total_files": len(project_files)})
                    print("✅ Snapshot saved")
                else:
                    print("❌ Full sync failed")
                    self.state_manager.set_takeover_status("Error", "Full Sync Failed")
    
    def run_full_test_suite(self):
        """
        运行全量测试套件
        Run full test suite
        """
        print("🧪 正在执行集成测试套件...")
        print("🧪 Executing integration test suite...")
        
        try:
            # 使用 -v 获取详细输出,用于后续解析失败文件路径
            # Use -v for detailed output to parse failed file paths
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short", "--color=no"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.project_root
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                print("✅ 集成测试全量通过! / All integration tests passed!")
                self.state_manager.set_takeover_status("Idle")
            else:
                # 解析失败的测试文件
                # Parse failed test files
                failed_files = self._parse_failed_tests(output)
                print(f"❌ 发现 {len(failed_files)} 个失败模块 / Found {len(failed_files)} failed modules")
                for file in failed_files:
                    print(f"   - {file}")
                
                # 显示最后 500 字符的输出
                # Show last 500 characters of output
                print("\n📋 测试输出 / Test output:")
                print(output[-500:] if len(output) > 500 else output)
                
                self.state_manager.set_takeover_status("Error", f"{len(failed_files)} tests failed")
                
        except FileNotFoundError:
            print("⚠️ pytest 未安装,跳过测试 / pytest not found, skipping tests")
            self.state_manager.set_takeover_status("Idle")
        except subprocess.TimeoutExpired:
            print("⚠️ 测试超时 (300秒) / Test timeout (300s)")
            self.state_manager.set_takeover_status("Error", "Test timeout")
        except Exception as e:
            print(f"⚠️ 测试执行失败: {e} / Test execution failed: {e}")
            self.state_manager.set_takeover_status("Error", str(e))
    
    def _parse_failed_tests(self, pytest_output):
        """
        从 Pytest 输出中提取失败的测试脚本路径
        Extract failed test script paths from Pytest output
        
        用于精准反馈给 Agent
        For precise feedback to Agent
        """
        # 匹配 FAILED tests/test_xxx.py
        # Match FAILED tests/test_xxx.py
        pattern = r"FAILED (tests/test_[^\s:]+\.py)"
        matches = re.findall(pattern, pytest_output)
        
        return sorted(list(set(matches)))

    def trigger_takeover(self, file_path):
        """
        The Core Loop: Audit -> Fix -> Test -> Retry
        """
        with self.execution_lock:
            self.processing_files.add(file_path)
        
        # Set takeover status to Writing
        self.state_manager.set_takeover_status("Writing")
            
        try:
            print(f"✨ Agent Takeover Triggered: {os.path.basename(file_path)}")
            
            # Initial Audit & Fix
            status = self.auditor.audit_and_fix(file_path)
            
            if status == "FIXED":
                # Agent modified code, now verify
                self.state_manager.set_takeover_status("Testing")
                self.run_verification_loop(file_path)
            elif status == "PASS":
                print("Code passed audit.")
                self.state_manager.set_takeover_status("Idle")
            else:
                print("Audit failed, waiting for user...")
                self.state_manager.set_takeover_status("Error", "Audit failed")
                
        finally:
             with self.execution_lock:
                 self.processing_files.discard(file_path)
             # Reset to Idle if not already set
             if self.state_manager.get_takeover_status() == "Writing":
                 self.state_manager.set_takeover_status("Idle")

    def run_verification_loop(self, file_path):
        """
        Active Retry Loop: Test -> Traceback -> Fix
        """
        retry_limit = CONFIG.get("RETRY_LIMIT", 3)
        
        for attempt in range(retry_limit):
            print(f"🔄 Verification Attempt {attempt+1}/{retry_limit}")
            
            success, output = run_tests_for_file(file_path)
            
            if success:
                print(f"✅ Implementation Verified: {os.path.basename(file_path)}")
                self.state_manager.set_takeover_status("Idle")
                return
            
            print(f"❌ Test Failed. Feeding traceback to Agent...")
            self.state_manager.set_takeover_status("Error", output[:500])
            
            # Feed Traceback back to Auditor
            print(f"Feeding traceback to Agent for fix...")
            
            # Recursive fix call with error context
            fix_status = self.auditor.audit_and_fix(file_path, error_context=output)
            
            if fix_status == "FIXED":
                # If fixed, the loop continues to next iteration (attempt+1) to verify again
                continue
            else:
                print("Agent failed to provide a fix based on error.")
                break
        else:
             print("❌ Retry limit reached. Manual Intervention Required.")
             self.state_manager.set_takeover_status("Error", "Retry limit reached")
             
if __name__ == "__main__":
    path = "."
    
    # 0. Environment Safety Check
    from antigravity.env_checker import check_dependencies
    print("🛡️ Pre-flight Check: Scanning PLAN.md for dependencies...")
    try:
        if os.path.exists("PLAN.md"):
            with open("PLAN.md", "r", encoding='utf-8') as f:
                check_dependencies(f.read())
    except Exception as e:
        print(f"Env Check Warning: {e}")

    print(f"Antigravity Monitor started at {os.path.abspath(path)}")
    observer = Observer()
    observer.schedule(AntigravityMonitor(path), path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
