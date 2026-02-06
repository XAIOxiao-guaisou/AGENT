import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer, Lock
from antigravity.auditor import Auditor
from antigravity.test_runner import run_tests_for_file
from antigravity.config import CONFIG

class AntigravityMonitor(FileSystemEventHandler):
    def __init__(self, project_root):
        self.project_root = project_root
        self.auditor = Auditor(project_root)
        self.timers = {}
        self.debounce_seconds = 3.0
        self.execution_lock = Lock() # Prevent recursive loops
        self.processing_files = set()

    def on_modified(self, event):
        self.process_event(event)
        
    def on_created(self, event):
        self.process_event(event)

    def process_event(self, event):
        if event.is_directory:
            return
        
        filename = event.src_path
        # Only monitor source files or PLAN
        if not (filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.tsx') or filename.endswith('PLAN.md')):
            return
            
        # IGNORE events if we are currently processing this file (Execution Lock)
        if filename in self.processing_files:
            return

        # Debouncing
        if filename in self.timers:
            self.timers[filename].cancel()
        
        timer = Timer(self.debounce_seconds, self.trigger_takeover, args=[filename])
        self.timers[filename] = timer
        timer.start()

    def trigger_takeover(self, file_path):
        """
        The Core Loop: Audit -> Fix -> Test -> Retry
        """
        with self.execution_lock:
            self.processing_files.add(file_path)
            
        try:
            print(f"✨ Agent Takeover Triggered: {os.path.basename(file_path)}")
            
            # Initial Audit & Fix
            status = self.auditor.audit_and_fix(file_path)
            
            if status == "FIXED":
                # Agent modified code, now verify
                self.run_verification_loop(file_path)
            elif status == "PASS":
                print("Code passed audit.")
            else:
                print("Audit failed, waiting for user...")
                
        finally:
             with self.execution_lock:
                 self.processing_files.discard(file_path)

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
                return
            
            print(f"❌ Test Failed. Feeding traceback to Agent...")
            
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
