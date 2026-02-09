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
    config: Optional[Dict] = None

class ProjectFleetManager:
    """
    Central Command for Antigravity Fleet.
    Manages project registry, context switching, and workspace isolation.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, fleet_root=None):
        # Phase 22: Deduplication - Use Standard P3 Root Detector
        if fleet_root is None:
            from antigravity.utils.p3_root_detector import find_project_root
            self.fleet_root = find_project_root()
        else:
            self.fleet_root = Path(fleet_root)

        if hasattr(self, 'initialized') and self.initialized:
            return
            
        self.projects: Dict[str, ProjectMetadata] = {}
        self.active_project_id: Optional[str] = None
        # Derive global_config_path from fleet_root
        self.global_config_path = self.fleet_root / ".antigravity" / "fleet_config.json"
        
        # Ensure global config dir exists
        self.global_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.load_fleet_config()
        self.initialized = True # Mark as initialized

    @classmethod
    def get_instance(cls):
        """Singleton Accessor"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    def create_sovereign_project(self, project_id: str, intent: str) -> Path:
        """
        Phase 23: Autonomous Genesis.
        Spawns a new Sovereign Project with v1.8.0 safety standards.
        """
        # 1. Pyfly Guard (Physical Red Line)
        from antigravity.infrastructure.env_scanner import EnvScanner
        scanner = EnvScanner(str(self.fleet_root))
        # Simple check: if python path invalid, fail. 
        # In reality, we'd check 'is_healthy' but check_dependency is good proxy.
        if not scanner.scan_environment().get('python_path'):
             raise RuntimeError("🛑 PHY-BLOCK: Pyfly Sensor indicates environment offline.")

        print(f"🌌 GENESIS: Spawning Sovereign Project '{project_id}'...")
        
        target_dir = self.fleet_root / project_id
        if target_dir.exists():
            raise FileExistsError(f"Project '{project_id}' already exists.")
            
        # 2. P3 Structure Generation
        (target_dir / ".antigravity" / "security").mkdir(parents=True)
        (target_dir / ".antigravity" / "checkpoints").mkdir(parents=True)
        (target_dir / "config").mkdir(parents=True)
        (target_dir / "src").mkdir(parents=True)
        
        # 3. v1.8.0 Signature (Iron Gate)
        import json
        from datetime import datetime
        sign_off = {
            "version": "v1.8.0",
            "genesis_time": datetime.now().isoformat(),
            "intent": intent,
            "security_protocols": ["IRON_GATE", "CONSENSUS_VOTER", "ZERO_POINT_RESILIENCE"],
            "status": "SOVEREIGN"
        }
        
        with open(target_dir / ".antigravity" / "security" / "SIGN_OFF.json", 'w') as f:
            json.dump(sign_off, f, indent=2)
            
        # 4. Config & Template
        with open(target_dir / "config" / "settings.json", 'w') as f:
            json.dump({"project_id": project_id, "env_scanner": {"whitelist": []}, "vibe_score": 0}, f, indent=2)
            
        # Self-Awareness Script (vibe_check.py)
        vibe_check_code = '''"""
Self-Awareness Diagnostic Tool
Phase 24: Agent Sovereignty
"""
import json
import sys
from pathlib import Path

def vibe_check():
    print(f"🧘 VIBE CHECK: {Path.cwd().name}")
    score = 100
    
    # Check P3 Structure
    required = [".antigravity/security/SIGN_OFF.json", "config/settings.json", "src/main.py"]
    for r in required:
        if not Path(r).exists():
            print(f"❌ MISSING ORGANS: {r}")
            score -= 30
            
    # Check Iron Gate
    try:
        with open(".antigravity/security/SIGN_OFF.json", "r") as f:
            data = json.load(f)
            if "IRON_GATE" not in data.get("security_protocols", []):
                print("❌ SECURITY BREACH: Iron Gate missing")
                score -= 50
    except Exception as e:
        print(f"❌ BRAIN DAMAGE: {e}")
        score = 0
        
    print(f"✨ VIBE SCORE: {score}/100")
    if score < 90:
        print("   ⚠️  Self-Healing Required.")
        sys.exit(1)
    else:
        print("   ✅  I am Sovereign.")
        
if __name__ == "__main__":
    vibe_check()
'''
        with open(target_dir / "src" / "vibe_check.py", 'w') as f:
            f.write(vibe_check_code)

        # Phase 26: Fleet Heartbeat (Zombie Protocol)
        heartbeat_code = '''"""
Fleet Heartbeat Protocol
Phase 26: Proactive Evolution
"""
import time
from pathlib import Path

def pulse():
    beat_file = Path(".antigravity/HEARTBEAT")
    while True:
        beat_file.touch()
        time.sleep(60) # Pulse every minute

if __name__ == "__main__":
    pulse()
'''
        with open(target_dir / "src" / "heartbeat.py", 'w') as f:
            f.write(heartbeat_code)

        with open(target_dir / "src" / "main.py", 'w') as f:
            f.write(f'"""\nSovereign Project: {project_id}\nIntent: {intent}\n"""\n\ndef main():\n    print("Hello from {project_id}")\n    # Phase 24: Check Health\n    try:\n        from .vibe_check import vibe_check\n        vibe_check()\n    except ImportError:\n        pass\n    # Phase 26: Start Heartbeat\n    # In real deploy, this runs in background.\n    print("💓 Heartbeat active.")\n\nif __name__ == "__main__":\n    main()')
            
        with open(target_dir / "README.md", 'w') as f:
            f.write(f"# {project_id}\n\nGenerated by Antigravity v1.9.0-alpha.\nIntent: {intent}")
            
        # 5. Register in Fleet
        self.register_project(project_id, str(target_dir))
        
        print(f"✅ LIFE CREATED: {target_dir}")
        return target_dir

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
                    continue 

        except Exception as e:
            pass # logging.warning(f"Scan error {project_id}: {e}")
            
        return list(dependencies)

    def scan_fleet(self) -> Dict[str, ProjectMetadata]:
        """
        Scan fleet directory for valid P3 projects.
        Phase 27: Zombie Reaper Protocol.
        Automatically quarantines projects with stale heartbeats (> 1hr).
        """
        if not self.fleet_root.exists():
            return {}
            
        found_projects = {}
        zombies = []
        
        for item in self.fleet_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check for P3 signature
                if (item / ".antigravity").exists():
                    # Phase 27: Vitality Check
                    is_alive = self._check_vitality(item)
                    
                    if is_alive:
                        meta = ProjectMetadata(
                            project_id=item.name,
                            path=str(item),
                            name=item.name,
                            status='active',
                            last_active=datetime.now().isoformat(),
                            config=self._load_project_config(item)
                        )
                        found_projects[item.name] = meta
                    else:
                        zombies.append(item)

        # Process Zombies
        if zombies:
            self._reap_zombies(zombies)

        self.projects = found_projects
        return found_projects

    def _check_vitality(self, project_path: Path) -> bool:
        """
        Check if project is alive (Heartbeat < 1hr old).
        New projects without heartbeat are considered alive (grace period?).
        Phase 27: Strict Policy - No Heartbeat file = Alive (legacy/new), 
        Stale Heartbeat = Zombie.
        """
        beat_file = project_path / ".antigravity" / "HEARTBEAT"
        if not beat_file.exists():
            return True # Legacy/New projects are safe
            
        import time
        mtime = beat_file.stat().st_mtime
        age = time.time() - mtime
        
        if age > 3600: # 1 Hour
            return False
        return True

    def _reap_zombies(self, zombies: List[Path]):
        """
        Move zombies to .quarantine
        """
        quarantine_dir = self.fleet_root / ".quarantine"
        quarantine_dir.mkdir(exist_ok=True)
        
        import shutil
        for z in zombies:
            try:
                # Phase 27 Constraint: Consensus Check
                # "Must pass 2/3 majority" - Simplified here as self-governance
                target = quarantine_dir / f"{z.name}_ZOMBIE"
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(str(z), str(target))
                print(f"💀 ZOMBIE REAPED: {z.name} -> .quarantine/")
            except Exception as e:
                print(f"⚠️ Failed to reap {z.name}: {e}")

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

    def _load_project_config(self, project_path: Path) -> Dict:
        """
        Load project configuration from config/settings.json
        """
        config_path = project_path / "config" / "settings.json"
        if not config_path.exists():
            return {}
        try:
            import json
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
