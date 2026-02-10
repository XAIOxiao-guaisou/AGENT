import sys
import os
from pathlib import Path

# 审查官补丁：注入包根目录
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import time
import os
import fnmatch
import subprocess
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer, Lock
from antigravity.core.autonomous_auditor import AutonomousAuditor as Auditor
from antigravity.infrastructure.test_runner import run_tests_for_file
from antigravity.utils.config import CONFIG
from antigravity.infrastructure.state_manager import StateManager
from antigravity.infrastructure.change_detector import ChangeDetector
from antigravity.utils.p3_root_detector import find_project_root
from antigravity.infrastructure.p3_state_manager import P3StateManager

class AntigravityMonitor(FileSystemEventHandler):

    def __init__(self, project_root):
        self.project_root = project_root
        self.watch_root = Path(project_root).resolve()
        self.state_manager = StateManager(project_root)
        self.auditor = Auditor(project_root)
        self.timers = {}
        self.debounce_seconds = 3.0
        self.execution_lock = Lock()
        self.processing_files = set()
        self.change_detector = ChangeDetector(project_root)
        self.incremental_threshold = CONFIG.get('INCREMENTAL_THRESHOLD', 3)
        print(f'✅ P3: ChangeDetector initialized (threshold={self.incremental_threshold})')
        self.ignore_patterns = CONFIG.get('IGNORE_PATTERNS', [])
        self.watch_extensions = CONFIG.get('WATCH_EXTENSIONS', ['.py', '.js', '.tsx', '.ts', '.md'])

    def on_modified(self, event):
        self.process_event(event)

    def on_created(self, event):
        self.process_event(event)

    def _should_ignore(self, file_path):
        """Check if file should be ignored based on patterns."""
        normalized_path = file_path.replace('\\', '/')
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(normalized_path, pattern):
                return True
        return False

    def process_event(self, event):
        if event.is_directory:
            return
        filename = event.src_path
        if self._should_ignore(filename):
            return
        if not any((filename.endswith(ext) for ext in self.watch_extensions)):
            if not filename.endswith('PLAN.md'):
                return
        if filename.endswith('PLAN.md'):
            self._trigger_env_check()
            return
        if filename in self.processing_files:
            return
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
        from antigravity.utils.env_checker import check_dependencies
        plan_path = os.path.join(self.project_root, 'PLAN.md')
        if os.path.exists(plan_path):
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_content = f.read()
                print('🛡️ PLAN.md 变更 - 运行环境检查...')
                print('🛡️ PLAN.md changed - Running environment check...')
                missing_deps = check_dependencies(plan_content)
                success = len(missing_deps) == 0
                self.state_manager.log_environment_check(missing_deps, success)
                if not success:
                    print(f"⚠️ 缺失依赖: {', '.join(missing_deps)}")
                    print(f"⚠️ Missing dependencies: {', '.join(missing_deps)}")
                if self._is_major_plan_change(plan_content):
                    print('🌐 检测到架构级变更,触发项目级同步...')
                    print('🌐 Major architectural change detected, triggering project sync...')
                    self.trigger_project_sync()
            except Exception as e:
                print(f'⚠️ 环境检查失败: {e}')
                print(f'⚠️ Environment check failed: {e}')

    def _is_major_plan_change(self, plan_content):
        """
        检测 PLAN.md 是否涉及架构级变更
        Detect if PLAN.md involves architectural-level changes
        
        重大变更标准 / Major change criteria:
        - 包含 2+ 个目标文件 / Contains 2+ target files
        - 提到关键词: 项目/project/架构/architecture/重构/refactor/全部/all
        """
        file_patterns = re.findall('[`"\\\'\\s](src/[^\\s`"\\\']+\\.py)', plan_content)
        unique_files = set(file_patterns)
        keywords = ['项目', 'project', '架构', 'architecture', '重构', 'refactor', '全部', 'all', '所有']
        has_keywords = any((k in plan_content.lower() for k in keywords))
        is_major = len(unique_files) >= 2 or has_keywords
        if is_major:
            print(f'📊 检测到 {len(unique_files)} 个目标文件 / Detected {len(unique_files)} target files')
            if has_keywords:
                print('📊 检测到架构关键词 / Detected architectural keywords')
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
        with self.execution_lock:
            print('🌐 [P3 Project Sync] 启动智能同步流程...')
            print('🌐 [P3 Project Sync] Starting intelligent sync...')
            self.state_manager.set_takeover_status('Analyzing')
            try:
                project_files = []
                for root, dirs, files in os.walk(self.project_root):
                    dirs[:] = [d for d in dirs if not any((pattern in d for pattern in self.ignore_patterns))]
                    for file in files:
                        if any((file.endswith(ext) for ext in self.watch_extensions)):
                            rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                            project_files.append(rel_path.replace('\\', '/'))
                self.change_detector.scan_files(project_files)
                summary = self.change_detector.get_change_summary()
                changed_files = summary['changed']
                new_files = summary['new']
                total_changes = summary['total_changes']
                print(f'📊 Change Summary: {total_changes} changes ({len(changed_files)} modified, {len(new_files)} new)')
            except Exception as e:
                print(f'⚠️ Change detection failed: {e}, falling back to full sync')
                total_changes = 999
                changed_files = []
                new_files = []
            if total_changes == 0:
                print('✅ No physical changes detected, skipping API call')
                self.state_manager.set_takeover_status('Idle', 'No changes')
                return
            elif total_changes <= self.incremental_threshold:
                print(f'🎯 Incremental sync mode ({total_changes} ≤ {self.incremental_threshold} changes)')
                self.state_manager.set_takeover_status('Incremental Sync')
                self.auditor.set_mode('executor')
                target_files = changed_files + new_files
                result = self.auditor.audit_and_fix_project(target_files=target_files)
                if result['status'] == 'SUCCESS':
                    modified = len(result.get('files_modified', []))
                    print(f'✅ Incremental sync complete: {modified} files fixed')
                    print('🧪 Running tests on changed files...')
                    self.run_full_test_suite()
                    self.change_detector.save_snapshot({'mode': 'incremental', 'files': target_files})
                    print('✅ Snapshot saved')
                else:
                    print('❌ Incremental sync failed')
                    self.state_manager.set_takeover_status('Error', 'Incremental Sync Failed')
            else:
                print(f'🌐 Full sync mode ({total_changes} > {self.incremental_threshold} changes)')
                self.state_manager.set_takeover_status('Full Sync')
                self.auditor.set_mode('project_executor')
                result = self.auditor.audit_and_fix_project()
                if result['status'] == 'SUCCESS':
                    modified = len(result.get('files_modified', []))
                    deleted = len(result.get('files_deleted', []))
                    print(f'✅ Full sync complete: Modified {modified} files, Deleted {deleted} files')
                    print('🧪 Starting full integration test...')
                    self.run_full_test_suite()
                    self.change_detector.save_snapshot({'mode': 'full', 'total_files': len(project_files)})
                    print('✅ Snapshot saved')
                else:
                    print('❌ Full sync failed')
                    self.state_manager.set_takeover_status('Error', 'Full Sync Failed')

    def run_full_test_suite(self):
        """
        运行全量测试套件
        Run full test suite
        """
        print('🧪 正在执行集成测试套件...')
        print('🧪 Executing integration test suite...')
        try:
            result = subprocess.run(['pytest', 'tests/', '-v', '--tb=short', '--color=no'], capture_output=True, text=True, timeout=300, cwd=self.project_root)
            success = result.returncode == 0
            output = result.stdout + result.stderr
            if success:
                print('✅ 集成测试全量通过! / All integration tests passed!')
                self.state_manager.set_takeover_status('Idle')
            else:
                failed_files = self._parse_failed_tests(output)
                print(f'❌ 发现 {len(failed_files)} 个失败模块 / Found {len(failed_files)} failed modules')
                for file in failed_files:
                    print(f'   - {file}')
                print('\n📋 测试输出 / Test output:')
                print(output[-500:] if len(output) > 500 else output)
                self.state_manager.set_takeover_status('Error', f'{len(failed_files)} tests failed')
        except FileNotFoundError:
            print('⚠️ pytest 未安装,跳过测试 / pytest not found, skipping tests')
            self.state_manager.set_takeover_status('Idle')
        except subprocess.TimeoutExpired:
            print('⚠️ 测试超时 (300秒) / Test timeout (300s)')
            self.state_manager.set_takeover_status('Error', 'Test timeout')
        except Exception as e:
            print(f'⚠️ 测试执行失败: {e} / Test execution failed: {e}')
            self.state_manager.set_takeover_status('Error', str(e))

    def _parse_failed_tests(self, pytest_output):
        """
        从 Pytest 输出中提取失败的测试脚本路径
        Extract failed test script paths from Pytest output
        
        用于精准反馈给 Agent
        For precise feedback to Agent
        """
        pattern = 'FAILED (tests/test_[^\\s:]+\\.py)'
        matches = re.findall(pattern, pytest_output)
        return sorted(list(set(matches)))

    def trigger_takeover(self, file_path):
        """
        The Core Loop: Audit -> Fix -> Test -> Retry
        """
        with self.execution_lock:
            self.processing_files.add(file_path)
        self.state_manager.set_takeover_status('Writing')
        try:
            print(f'✨ Agent Takeover Triggered: {os.path.basename(file_path)}')
            status = self.auditor.audit_and_fix(file_path)
            if status == 'FIXED':
                self.state_manager.set_takeover_status('Testing')
                self.run_verification_loop(file_path)
            elif status == 'PASS':
                print('Code passed audit.')
                self.state_manager.set_takeover_status('Idle')
            else:
                print('Audit failed, waiting for user...')
                self.state_manager.set_takeover_status('Error', 'Audit failed')
        finally:
            with self.execution_lock:
                self.processing_files.discard(file_path)
            if self.state_manager.get_takeover_status() == 'Writing':
                self.state_manager.set_takeover_status('Idle')

    def run_verification_loop(self, file_path):
        """
        Active Retry Loop: Test -> Traceback -> Fix
        """
        retry_limit = CONFIG.get('RETRY_LIMIT', 3)
        for attempt in range(retry_limit):
            print(f'🔄 Verification Attempt {attempt + 1}/{retry_limit}')
            success, output = run_tests_for_file(file_path)
            if success:
                print(f'✅ Implementation Verified: {os.path.basename(file_path)}')
                self.state_manager.set_takeover_status('Idle')
                return
            print(f'❌ Test Failed. Feeding traceback to Agent...')
            self.state_manager.set_takeover_status('Error', output[:500])
            print(f'Feeding traceback to Agent for fix...')
            fix_status = self.auditor.audit_and_fix(file_path, error_context=output)
            if fix_status == 'FIXED':
                continue
            else:
                print('Agent failed to provide a fix based on error.')
                break
        else:
            print('❌ Retry limit reached. Manual Intervention Required.')
            self.state_manager.set_takeover_status('Error', 'Retry limit reached')
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Antigravity Monitor')
    parser.add_argument('--active-project', type=str, help='Path to active project to monitor directly')
    args = parser.parse_args()
    
    path = args.active_project if args.active_project else '.'
    if args.active_project:
        print(f"🎯 [Monitor] Targeted Mode: {path}")
    from antigravity.utils.env_checker import check_dependencies
    print('🛡️ Pre-flight Check: Scanning PLAN.md for dependencies...')
    try:
        if os.path.exists('PLAN.md'):
            with open('PLAN.md', 'r', encoding='utf-8') as f:
                check_dependencies(f.read())
    except Exception as e:
        print(f'Env Check Warning: {e}')
    print(f'Antigravity Monitor started at {os.path.abspath(path)}')
    observer = Observer()
    observer.schedule(AntigravityMonitor(path), path, recursive=True)
    observer.start()
    try:
        print("🧠 Monitor Heartbeat Active: Listening for Mission State...")
        from antigravity.utils.p3_root_detector import find_project_root
        from antigravity.core.mission_orchestrator import MissionOrchestrator, TaskState
        from antigravity.infrastructure.p3_state_manager import P3StateManager
        
        # Initialize Global State Manager to find active project
        # path is '.', assuming we are in AGENT root
        chk_state_mgr = P3StateManager(Path(path).resolve())
        
        while True:
            try:
                # 1. Identify Active Project
                # Reload global state to get latest active project
                chk_state_mgr.global_state = chk_state_mgr._load_global_state()
                active_rel = chk_state_mgr.global_state.get('last_active')
                
                if active_rel:
                    project_root = Path(path).resolve() / active_rel
                    state_file = project_root / ".antigravity" / "mission_state.json"
                    
                    if state_file.exists():
                        # 2. Load Orchestrator
                        orch = MissionOrchestrator(str(project_root))
                        orch.load_state(str(state_file))
                        
                        # 3. Process Pending/Active Tasks
                        # Logic: If current task is in a transient state, step it.
                        # States requiring auto-step: REVIEWING, GENERATING, HEALING, ROLLBACK
                        # PENDING is triggered by Dashboard. 
                        # ANALYZING is triggered by Dashboard (usually).
                        # DONE and AUDITING (waiting for user/check) are stable.
                        
                        modified = False
                        
                        # Check queue for PENDING if no current task
                        if not orch.current_task and orch.tasks:
                            for t in orch.tasks:
                                if t.state == TaskState.PENDING:
                                    orch.current_task = t
                                    modified = True
                                    break
                        
                        if orch.current_task:
                            current_state = orch.current_task.state
                            auto_states = [TaskState.REVIEWING, TaskState.GENERATING, TaskState.HEALING, TaskState.ROLLBACK]
                            
                            # Special case: If we just loaded and it's PENDING (missed trigger), kick it.
                            if current_state == TaskState.PENDING:
                                auto_states.append(TaskState.PENDING)
                                
                            # v2.1.14: Sovereign Drive (Aggressive Loop)
                            # If we are in a driving state, keep stepping until blocked or done
                            if current_state in auto_states or (current_state == TaskState.ANALYZING):
                                print(f"⚙️ [Mission Loop] Driving Task {orch.current_task.task_id} ({current_state.value})...")
                                
                                # Power-Through Loop
                                while True:
                                    prev_state = orch.current_task.state
                                    new_state = orch.step()
                                    
                                    if new_state != prev_state:
                                        print(f"✨ [Mission Loop] Transitioned to {new_state.value}")
                                        orch.save_state(str(state_file))
                                        modified = True
                                        
                                        # If we hit a stopping state, break
                                        if new_state in [TaskState.AUDITING, TaskState.DONE, TaskState.PENDING]:
                                            break
                                        # Otherwise, continue driving immediately (Zero-G)
                                    else:
                                        # State didn't change, break to avoid infinite loop if stuck
                                        break
                                    
                        # 4. Debounce
                        if modified:
                            time.sleep(0.2) # Ultra-fast debounce
                        else:
                            time.sleep(1.0) # Regular poll
                    else:
                        time.sleep(1.0) 
                else:
                    time.sleep(1.0)
                    
            except Exception as e:
                print(f"⚠️ [Mission Loop Error] {e}")
                time.sleep(5.0)
                
    except KeyboardInterrupt:
        observer.stop()
    observer.join()