"""
Antigravity P3 State Manager
Multi-project state management with global/local state split.
Follows Vibe Coding constraints: pathlib-first, zero hardcoding.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from threading import Lock


class P3StateManager:
    """
    P3: Multi-project state manager with global/local state split.
    
    Architecture:
    - Global state (.antigravity_global.json): Project registry only
    - Local state (projects/{name}/.antigravity_state.json): Detailed audit logs
    """
    
    def __init__(self, project_root="."):
        # Vibe Coding: Use pathlib exclusively
        self.root = Path(project_root).resolve()
        
        # Global state: project registry (lightweight)
        self.global_state_file = Path(".antigravity_global.json")
        
        # Local state: project-specific audit logs (detailed)
        self.state_file = self.root / ".antigravity_state.json"
        
        # Thread safety
        self._lock = Lock()
        
        # Initialize states
        self.global_state = self._load_global_state()
        self.state = self._load_state()
        
        # Auto-register if in projects/ directory
        self._auto_register_project()
    
    def _load_global_state(self) -> Dict:
        """Load global project registry"""
        if self.global_state_file.exists():
            try:
                return json.loads(self.global_state_file.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"Warning: Could not load global state: {e}")
                return self._create_default_global_state()
        return self._create_default_global_state()
    
    def _create_default_global_state(self) -> Dict:
        """Create default global state structure"""
        return {
            "projects": [],
            "last_active": None,
            "created_at": datetime.now().isoformat()
        }
    
    def _load_state(self) -> Dict:
        """Load project-specific state from file or create new state"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                return self._create_default_state()
        return self._create_default_state()
    
    def _create_default_state(self) -> Dict:
        """Create default project state structure"""
        return {
            "project_name": self.root.name,
            "project_path": str(self.root),
            "audits": [],
            "test_results": [],
            "environment_checks": [],
            "retry_counts": {},
            "system_status": {
                "takeover_status": "Idle",
                "last_error_log": None,
                "last_update": datetime.now().isoformat()
            },
            "last_sync": None,
            "created_at": datetime.now().isoformat()
        }
    
    def _auto_register_project(self):
        """Auto-register project if in projects/ directory"""
        # Check if we're in a projects/{name}/ structure
        if self.root.parent.name == "projects" or "projects" in self.root.parts:
            project_path = str(self.root.relative_to(Path.cwd()))
            self.register_project(project_path)
    
    def register_project(self, project_path: str):
        """Register new project in global index"""
        with self._lock:
            if project_path not in self.global_state["projects"]:
                self.global_state["projects"].append(project_path)
                self.global_state["last_active"] = project_path
                self._save_global_state()
                print(f"✅ P3: Registered project: {project_path}")
    
    def get_all_projects(self) -> List[str]:
        """Get list of all registered projects"""
        return self.global_state.get("projects", [])
    
    def _save_global_state(self):
        """Save global state to file"""
        try:
            self.global_state_file.write_text(
                json.dumps(self.global_state, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Error saving global state: {e}")
    
    def _save_state(self):
        """Save project state to file"""
        with self._lock:
            try:
                # Ensure parent directory exists
                self.state_file.parent.mkdir(parents=True, exist_ok=True)
                
                self.state_file.write_text(
                    json.dumps(self.state, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
            except Exception as e:
                print(f"Error saving state: {e}")
    
    # ===========================
    # Audit Logging
    # ===========================
    
    def log_audit(self, file_path: str, event_type: str, message: str, status: str = "INFO"):
        """
        Log an audit event.
        
        Args:
            file_path: Path to the file being audited
            event_type: Type of event (e.g., "audit", "fix", "pass", "fail")
            message: Event message
            status: Status level (INFO, PASS, FIXED, FAIL, CRITICAL)
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": Path(file_path).name,
            "full_path": file_path,
            "event_type": event_type,
            "message": message,
            "status": status
        }
        
        self.state["audits"].append(audit_entry)
        self.state["system_status"]["last_update"] = datetime.now().isoformat()
        
        # Keep only last 100 audits to prevent file bloat
        if len(self.state["audits"]) > 100:
            self.state["audits"] = self.state["audits"][-100:]
        
        self._save_state()
    
    def get_recent_audits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit entries"""
        audits = self.state.get("audits", [])
        return audits[-limit:] if len(audits) > limit else audits
    
    # ===========================
    # Retry Management
    # ===========================
    
    def get_retry_count(self, file_path: str) -> int:
        """Get current retry count for a file"""
        return self.state["retry_counts"].get(file_path, 0)
    
    def increment_retry(self, file_path: str) -> int:
        """Increment retry count for a file and return new count"""
        current = self.state["retry_counts"].get(file_path, 0)
        self.state["retry_counts"][file_path] = current + 1
        self._save_state()
        return current + 1
    
    def reset_retry(self, file_path: str):
        """Reset retry count for a file"""
        if file_path in self.state["retry_counts"]:
            self.state["retry_counts"][file_path] = 0
            self._save_state()
    
    # ===========================
    # System Status
    # ===========================
    
    def set_takeover_status(self, status: str, error_log: Optional[str] = None):
        """
        Set system takeover status.
        
        Args:
            status: One of "Idle", "Writing", "Testing", "Error"
            error_log: Optional error log if status is "Error"
        """
        self.state["system_status"]["takeover_status"] = status
        self.state["system_status"]["last_update"] = datetime.now().isoformat()
        
        if error_log:
            self.state["system_status"]["last_error_log"] = error_log
        
        self._save_state()
    
    def get_takeover_status(self) -> str:
        """Get current takeover status"""
        return self.state["system_status"].get("takeover_status", "Idle")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return self.state.get("system_status", {})
    
    # ===========================
    # Environment Checks
    # ===========================
    
    def log_environment_check(self, missing_deps: List[str], success: bool):
        """Log environment dependency check results"""
        check_entry = {
            "timestamp": datetime.now().isoformat(),
            "missing_dependencies": missing_deps,
            "success": success
        }
        
        self.state["environment_checks"].append(check_entry)
        
        # Keep only last 10 checks
        if len(self.state["environment_checks"]) > 10:
            self.state["environment_checks"] = self.state["environment_checks"][-10:]
        
        self._save_state()
    
    def get_last_environment_check(self) -> Optional[Dict[str, Any]]:
        """Get the most recent environment check result"""
        checks = self.state.get("environment_checks", [])
        return checks[-1] if checks else None
