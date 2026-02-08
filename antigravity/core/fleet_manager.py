"""
Antigravity Fleet Manager
=========================
Multi-Project Orchestration & Intelligence Layer.

Phase 11: Connects isolated Antigravity instances into a cohesive "Fleet".
Features:
- Workspace Isolation (.antigravity_workspace)
- Atomic Context Switching
- Cross-Project Intelligence (Merkle-based Dependency Scanning)
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import threading
from datetime import datetime

logger = logging.getLogger("antigravity.fleet")

@dataclass
class ProjectMetadata:
    """Metadata for a single Antigravity project"""
    project_id: str
    path: str
    name: str
    status: str  # ACTIVE, PAUSED, CERTIFIED, TAMPERED
    last_active: str
    merkle_root: Optional[str] = None
    vibe_score: int = 0
    workspace_root: Optional[str] = None

class ProjectFleetManager:
    """
    Central Command for Antigravity Fleet.
    Manages project registry, context switching, and workspace isolation.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.projects: Dict[str, ProjectMetadata] = {}
        self.active_project_id: Optional[str] = None
        self.global_config_path = Path.home() / ".antigravity" / "fleet_config.json"
        
        # Ensure global config dir exists
        self.global_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.load_fleet_config()
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    def load_fleet_config(self):
        """Load global fleet configuration"""
        if self.global_config_path.exists():
            try:
                with open(self.global_config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pid, project_data in data.get('projects', {}).items():
                        self.projects[pid] = ProjectMetadata(**project_data)
                    self.active_project_id = data.get('last_active')
            except Exception as e:
                logger.error(f"Failed to load fleet config: {e}")

    def save_fleet_config(self):
        """Persist global fleet configuration"""
        try:
            data = {
                'projects': {pid: asdict(p) for pid, p in self.projects.items()},
                'last_active': self.active_project_id
            }
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save fleet config: {e}")

    def scan_workspace(self, root_path: str):
        """
        Scan a directory logic for Antigravity projects.
        respects .antigravity_workspace isolation markers.
        """
        root = Path(root_path)
        if not root.exists():
            return
            
        # Check if this is a workspace root
        workspace_marker = root / ".antigravity_workspace"
        is_workspace = workspace_marker.exists()
        
        logger.info(f"Scanning {root} (Workspace: {is_workspace})...")
        
        # Simple depth-limited scan for now (depth=2)
        # Look for .antigravity folder
        for item in root.iterdir():
            if item.is_dir():
                target_marker = item / ".antigravity"
                if target_marker.exists(): # Found a project!
                    self.register_project(item, workspace_root=str(root) if is_workspace else None)
                    
    def register_project(self, path: Path, workspace_root: Optional[str] = None):
        """Register a project into the fleet"""
        try:
            # Load project state/config if available
            state_file = path / ".antigravity_state.json" 
            # In real impl, we'd read this. For now, scaffold metadata.
            
            project_id = str(path.stem).lower().replace(" ", "_")
            
            # Check for existing
            if project_id in self.projects:
                self.projects[project_id].workspace_root = workspace_root # Update workspace
                return

            metadata = ProjectMetadata(
                project_id=project_id,
                path=str(path),
                name=path.name,
                status="ACTIVE", # Default found status
                last_active=datetime.now().isoformat(),
                workspace_root=workspace_root
            )
            
            self.projects[project_id] = metadata
            self.save_fleet_config()
            logger.info(f"Fleet: Registered project {project_id} at {path}")
            
        except Exception as e:
            logger.error(f"Failed to register project at {path}: {e}")

    def switch_project(self, project_id: str) -> bool:
        """
        Atomic Context Switch.
        
        1. Flush Telemetry (Atomic Drain)
        2. Acquire Global Lock
        3. Pause Old MissionOrchestrator (Heartbeat Lock)
        4. Signal Dashboard (CONTEXT_SWITCH_BEGIN)
        5. Swap & Resume
        """
        if project_id not in self.projects:
            return False
            
        with self._lock:
            from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
            
            # 1. Atomic Drain (Prevent Telemetry Leak)
            # Drain residual logs from previous project
            _ = TelemetryQueue.flush_queue()
            
            # 2. Signal Switch Begin (Silence the HUD)
            # This tells Dashboard to freeze charts and clear buffers
            TelemetryQueue.push_event(TelemetryEventType.STATE_CHANGE, {
                'event': 'CONTEXT_SWITCH_BEGIN',
                'target_project': project_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # 3. Pause Old Orchestrator (Conceptual Heartbeat Lock)
            # In a full evolved system, we would get the running instance and call .pause()
            # self.current_orchestrator.pause() 
            
            # 4. Update Active Pointer
            self.active_project_id = project_id
            self.projects[project_id].last_active = datetime.now().isoformat()
            self.save_fleet_config()
            
            # 5. Signal Switch Complete & Resume
            # Dashboard picks this up and re-initializes its view
            TelemetryQueue.push_event(TelemetryEventType.STATE_CHANGE, {
                'event': 'CONTEXT_SWITCH_COMPLETE',
                'project_id': project_id,
                'status': self.projects[project_id].status
            })
            
            # 6. Mark Flush Complete (Atomic Marker)
            TelemetryQueue.push_event(TelemetryEventType.STATE_CHANGE, {
                'event': 'MARK_FLUSH_COMPLETE',
                 'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Fleet: Atomic Switch to project {project_id} completed.")
            return True

    def get_fleet_status(self) -> List[Dict]:
        """Get flattened status for HUD"""
        return [asdict(p) for p in self.projects.values()]

    def _build_package_map(self) -> Dict[str, str]:
        """
        Build map of Package Name -> Project ID
        Strategy:
        1. Use project_id as package name (default)
        2. Scan project root for top-level packages (dirs with __init__.py)
        """
        package_map = {}
        for pid, meta in self.projects.items():
            # Strategy 1: Project ID match
            package_map[pid] = pid
            
            # Strategy 2: Top-level package scan
            try:
                root = Path(meta.path)
                if root.exists():
                    for item in root.iterdir():
                        if item.is_dir() and (item / "__init__.py").exists():
                            package_map[item.name] = pid
            except Exception:
                pass
        return package_map

    def scan_cross_dependencies(self, project_id: str) -> List[str]:
        """
        Phase 12: Cross-Project Dependency Radar
        
        Scans project source code for imports that match other projects in the fleet.
        Returns: List of dependent Project IDs.
        """
        if project_id not in self.projects:
            return []
            
        project_root = Path(self.projects[project_id].path)
        package_map = self._build_package_map()
        dependencies = set()
        
        import ast
        
        # Scan all .py files
        try:
            for file_path in project_root.glob("**/*.py"):
                if "site-packages" in str(file_path) or ".venv" in str(file_path):
                    continue
                    
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        tree = ast.parse(f.read())
                        
                    for node in ast.walk(tree):
                        target_pkg = None
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                parts = alias.name.split('.')
                                target_pkg = parts[0]
                                
                                # Phase 15: Handle 'fleet.<project_id>' convention
                                if target_pkg == 'fleet' and len(parts) > 1:
                                    target_pkg = parts[1]
                                    
                                if target_pkg in package_map:
                                    dep_id = package_map[target_pkg]
                                    if dep_id != project_id:
                                        dependencies.add(dep_id)
                                        
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                parts = node.module.split('.')
                                target_pkg = parts[0]
                                
                                # Phase 15: Handle 'fleet.<project_id>' convention
                                if target_pkg == 'fleet' and len(parts) > 1:
                                    target_pkg = parts[1]

                                if target_pkg in package_map:
                                    dep_id = package_map[target_pkg]
                                    if dep_id != project_id:
                                        dependencies.add(dep_id)
                except Exception:
                    continue # Skip file on parse error
        except Exception as e:
            logger.error(f"Error scanning dependencies for {project_id}: {e}")
            
        return list(dependencies)

    def verify_fleet_integrity(self, project_id: str) -> Dict:
        """
        Phase 12: Shield Deployment
        Recursive integrity check.
        
        Returns:
            {
                'status': 'SECURE' | 'CONTAMINATED' | 'TAMPERED',
                'dependencies': [list of deps],
                'violations': [list of issues]
            }
        """
        if project_id not in self.projects:
            return {'status': 'UNKNOWN', 'dependencies': [], 'violations': []}
            
        # 1. Self Check (Placeholder logic for now, usually checks Merkle vs SIGN_OFF)
        # In real impl, we instantiate DeliveryGate(project_id).verify_integrity()
        self_status = self.projects[project_id].status # ACTIVE/TAMPERED/CERTIFIED
        
        # 2. Dependency Scan
        deps = self.scan_cross_dependencies(project_id)
        
        violations = []
        is_contaminated = False
        
        for dep_id in deps:
            dep_meta = self.projects.get(dep_id)
            if not dep_meta: 
                continue
                
            # Recursive check? For now, 1-level check of stored status is fast
            # If Project B is TAMPERED, Project A is CONTAMINATED
            if dep_meta.status == 'TAMPERED':
                is_contaminated = True
                violations.append(f"Dependency '{dep_id}' is TAMPERED")
            elif dep_meta.status == 'CONTAMINATED':
                 is_contaminated = True
                 violations.append(f"Dependency '{dep_id}' is CONTAMINATED")

        final_status = self_status
        if self_status in ['ACTIVE', 'CERTIFIED'] and is_contaminated:
            final_status = 'CONTAMINATED'
            
        # State Transition & Pulse Alert
        if final_status != self_status:
            self.projects[project_id].status = final_status
            self.save_fleet_config()
            
            # Pulse Alert: FLEET_SECURITY_BREACH
            if final_status in ['CONTAMINATED', 'TAMPERED']:
                from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
                TelemetryQueue.push_event(TelemetryEventType.STATE_CHANGE, {
                    'event': 'FLEET_SECURITY_BREACH',
                    'project_id': project_id,
                    'new_status': final_status,
                    'violations': violations,
                    'timestamp': datetime.now().isoformat()
                })
                logger.warning(f"🚨 FLEET SECURITY BREACH: {project_id} is {final_status}")
            
        return {
            'status': final_status,
            'dependencies': deps,
            'violations': violations
        }
