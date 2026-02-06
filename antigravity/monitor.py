import time
import os
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer, Lock
from antigravity.auditor import Auditor
from antigravity.test_runner import run_tests_for_file
from antigravity.config import CONFIG
from antigravity.state_manager import StateManager

class AntigravityMonitor(FileSystemEventHandler):
    def __init__(self, project_root):
        self.project_root = project_root
        self.state_manager = StateManager(project_root)
        self.auditor = Auditor(project_root, state_manager=self.state_manager)
        self.timers = {}
        self.debounce_seconds = 3.0
        self.execution_lock = Lock() # Prevent recursive loops
        self.processing_files = set()
        
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
        """Trigger environment dependency check when PLAN.md changes."""
        from antigravity.env_checker import check_dependencies
        
        plan_path = os.path.join(self.project_root, "PLAN.md")
        if os.path.exists(plan_path):
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_content = f.read()
                
                print("🛑️ PLAN.md changed - Running environment check...")
                missing_deps = check_dependencies(plan_content)
                
                success = len(missing_deps) == 0
                self.state_manager.log_environment_check(missing_deps, success)
                
                if not success:
                    print(f"⚠️ Missing dependencies: {', '.join(missing_deps)}")
            except Exception as e:
                print(f"⚠️ Environment check failed: {e}")

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
