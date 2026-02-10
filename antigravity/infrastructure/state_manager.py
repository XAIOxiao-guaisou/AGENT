"""
Antigravity State Manager
Centralized state management with atomic writes and file locking.
"""
import json
import os
import time
from threading import Lock
from datetime import datetime
from typing import Dict, List, Optional, Any

class StateManager:
    """Thread-safe state manager for Antigravity system."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.state_file = os.path.join(project_root, "state.json")
        self._lock = Lock()
        self._ensure_state_file()
        
    def _ensure_state_file(self):
        """Create state file if it doesn't exist."""
        if not os.path.exists(self.state_file):
            initial_state = {
                "audits": [],
                "retry_counts": {},
                "system_status": {
                    "takeover_status": "Idle",
                    "last_error_log": None,
                    "last_update": datetime.now().isoformat()
                },
                "environment_checks": []
            }
            self._write_state(initial_state)
            
            # Migrate from old vibe_audit.log if exists
            self._migrate_old_logs()
    
    def _migrate_old_logs(self):
        """Migrate entries from vibe_audit.log to state.json."""
        old_log = os.path.join(self.project_root, "vibe_audit.log")
        if not os.path.exists(old_log):
            return
            
        try:
            with open(old_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple migration: add a single entry noting the migration
            if content.strip():
                state = self._read_state()
                state["audits"].append({
                    "timestamp": datetime.now().isoformat(),
                    "file_path": "MIGRATION",
                    "event_type": "migration",
                    "message": f"Migrated from vibe_audit.log ({len(content)} bytes)",
                    "status": "INFO"
                })
                self._write_state(state)
                print(f"✅ Migrated old logs from vibe_audit.log")
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")
    
    def _read_state(self) -> Dict[str, Any]:
        """Read state from file with locking."""
        with self._lock:
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Return default state if file is corrupted
                return {
                    "audits": [],
                    "retry_counts": {},
                    "system_status": {
                        "takeover_status": "Idle",
                        "last_error_log": None,
                        "last_update": datetime.now().isoformat()
                    },
                    "environment_checks": []
                }
    
    def _write_state(self, state: Dict[str, Any]):
        """Write state to file atomically with locking."""
        with self._lock:
            # Atomic write: write to temp file, then rename
            temp_file = self.state_file + ".tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                
                # Atomic rename (on Windows, need to remove target first)
                if os.path.exists(self.state_file):
                    os.remove(self.state_file)
                os.rename(temp_file, self.state_file)
            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise e
    
    def log_audit(self, file_path: str, event_type: str, message: str, status: str = "INFO"):
        """
        Log an audit event.
        
        Args:
            file_path: Path to the file being audited
            event_type: Type of event (e.g., "audit", "fix", "pass", "fail")
            message: Event message
            status: Status level (INFO, PASS, FIXED, FAIL, CRITICAL)
        """
        state = self._read_state()
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": os.path.basename(file_path),
            "full_path": file_path,
            "event_type": event_type,
            "message": message,
            "status": status
        }
        
        state["audits"].append(audit_entry)
        state["system_status"]["last_update"] = datetime.now().isoformat()
        
        # Keep only last 100 audits to prevent file bloat
        if len(state["audits"]) > 100:
            state["audits"] = state["audits"][-100:]
        
        self._write_state(state)
        
        # Also write to legacy log for backward compatibility
        self._write_legacy_log(file_path, message)
    
    def _write_legacy_log(self, file_path: str, message: str):
        """Write to vibe_audit.log for backward compatibility."""
        log_file = os.path.join(self.project_root, "vibe_audit.log")
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {os.path.basename(file_path)}:\n{message}\n{'-'*20}\n")
        except Exception:
            pass  # Silent fail for legacy log
    
    def get_retry_count(self, file_path: str) -> int:
        """Get current retry count for a file."""
        state = self._read_state()
        return state["retry_counts"].get(file_path, 0)
    
    def increment_retry(self, file_path: str) -> int:
        """Increment retry count for a file and return new count."""
        state = self._read_state()
        current = state["retry_counts"].get(file_path, 0)
        state["retry_counts"][file_path] = current + 1
        self._write_state(state)
        return current + 1
    
    def reset_retry(self, file_path: str):
        """Reset retry count for a file."""
        state = self._read_state()
        if file_path in state["retry_counts"]:
            state["retry_counts"][file_path] = 0
            self._write_state(state)
    
    def get_recent_audits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit entries."""
        state = self._read_state()
        audits = state["audits"]
        return audits[-limit:] if len(audits) > limit else audits
    
    def set_takeover_status(self, status: str, error_log: Optional[str] = None):
        """
        Set system takeover status.
        
        Args:
            status: One of "Idle", "Writing", "Testing", "Error"
            error_log: Optional error log if status is "Error"
        """
        state = self._read_state()
        state["system_status"]["takeover_status"] = status
        state["system_status"]["last_update"] = datetime.now().isoformat()
        
        if error_log:
            state["system_status"]["last_error_log"] = error_log
        
        self._write_state(state)
    
    def get_takeover_status(self) -> str:
        """Get current takeover status."""
        state = self._read_state()
        return state["system_status"].get("takeover_status", "Idle")
    
    def log_environment_check(self, missing_deps: List[str], success: bool):
        """Log environment dependency check results."""
        state = self._read_state()
        
        check_entry = {
            "timestamp": datetime.now().isoformat(),
            "missing_dependencies": missing_deps,
            "success": success
        }
        
        state["environment_checks"].append(check_entry)
        
        # Keep only last 10 checks
        if len(state["environment_checks"]) > 10:
            state["environment_checks"] = state["environment_checks"][-10:]
        
        self._write_state(state)
    
    def get_last_environment_check(self) -> Optional[Dict[str, Any]]:
        """Get the most recent environment check result."""
        state = self._read_state()
        checks = state.get("environment_checks", [])
        return checks[-1] if checks else None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        state = self._read_state()
        return state.get("system_status", {})

    # ===========================
    # P3 Compatibility Shim
    # ===========================
    def register_project(self, project_path: str):
        """
        Shim for P3 Auto-Registration.
        Delegates to P3StateManager to ensure global registry is updated.
        """
        try:
            from antigravity.infrastructure.p3_state_manager import P3StateManager
            # Verify path is valid
            abs_path = os.path.abspath(project_path)
            # Initialize P3 manager temporarily just to register
            p3_mgr = P3StateManager(abs_path)
            p3_mgr.register_project(project_path)
        except Exception as e:
            print(f"⚠️ StateManager Shim Error: {e}")
