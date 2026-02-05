import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer
from antigravity.auditor import Auditor

class AntigravityMonitor(FileSystemEventHandler):
    def __init__(self, project_root):
        self.project_root = project_root
        self.auditor = Auditor(project_root)
        self.timers = {}
        self.debounce_seconds = 3

    def on_created(self, event):
        self.process_event(event)

    def on_modified(self, event):
        self.process_event(event)

    def process_event(self, event):
        if event.is_directory:
            return
        
        filename = event.src_path
        if not (filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.tsx') or filename.endswith('PLAN.md')):
            return
            
        # Loop Prevention: Check Signature
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if first_line.startswith("# FIXME: DeepSeek Auditor"):
                    print(f"Skipping audit for {filename} (Feedback loop prevention)")
                    return
        except Exception:
            pass # File might be locked or deleted

        # Debouncing
        if filename in self.timers:
            self.timers[filename].cancel()
        
        # Start new timer
        timer = Timer(self.debounce_seconds, self.trigger_audit, args=[filename])
        self.timers[filename] = timer
        timer.start()

    def trigger_audit(self, file_path):
        print(f"Debounce finished. Auditing {file_path}")
        self.auditor.audit_file(file_path)
        if file_path in self.timers:
            del self.timers[file_path]

if __name__ == "__main__":
    path = os.getcwd()
    monitor = AntigravityMonitor(path)
    observer = Observer()
    observer.schedule(monitor, path, recursive=True)
    observer.start()
    print(f"Antigravity Monitor started on {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
