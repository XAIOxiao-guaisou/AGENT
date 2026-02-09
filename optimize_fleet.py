"""
Fleet Entropy Optimizer
-----------------------
Phase 25: Global Fleet Profile
Scans all sovereign projects for redundant imports and dead synapses.
"""
import sys
import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Set

# Ensure antigravity importable
sys.path.insert(0, os.getcwd())

from antigravity.core.fleet_manager import ProjectFleetManager
from antigravity.utils.p3_root_detector import find_project_root

class FleetEntropyProfiler:
    def __init__(self):
        self.fleet_mgr = ProjectFleetManager.get_instance()
        self.report = {
            "total_projects": 0,
            "total_files_scanned": 0,
            "redundant_imports": [],
            "dead_synapses": [],
            "duplication_ratio": 0.0
        }

    def scan_fleet(self):
        print("🧠 STARTING FLEET ENTROPY AUDIT...")
        projects = self.fleet_mgr.projects
        self.report["total_projects"] = len(projects)
        
        all_imports = []
        
        for project_id, meta in projects.items():
            print(f"   Scanning {project_id}...")
            project_root = Path(meta.path)
            src_dir = project_root / "src"
            
            if not src_dir.exists():
                continue
                
            for py_file in src_dir.rglob("*.py"):
                self.report["total_files_scanned"] += 1
                self._analyze_file(project_id, py_file, all_imports)
                
        # Calculate global duplication
        unique_imports = set(all_imports)
        if len(all_imports) > 0:
            self.report["duplication_ratio"] = 1.0 - (len(unique_imports) / len(all_imports))
            
        print(f"✅ AUDIT COMPLETE. Duplication Ratio: {self.report['duplication_ratio']:.2%}")
        self._save_report()

    def _analyze_file(self, project_id: str, file_path: Path, all_imports: List[str]):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = None
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            module = n.name
                            all_imports.append(module)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module
                        all_imports.append(module)
                        
                    if module:
                        self._check_dead_synapse(project_id, str(file_path), module)
                        
        except Exception as e:
            print(f"   ⚠️ Error scanning {file_path}: {e}")

    def _check_dead_synapse(self, project_id: str, file_path: str, module: str):
        # Check if importing from a fleet project that doesn't exist
        if module and module.startswith("fleet."):
            target_project = module.split('.')[1]
            if target_project not in self.fleet_mgr.projects:
                self.report["dead_synapses"].append({
                    "source_project": project_id,
                    "file": file_path,
                    "target": target_project,
                    "module": module
                })
                print(f"   💀 DEAD SYNAPSE: {project_id} -> {target_project}")

    def _save_report(self):
        with open("fleet_entropy_report.json", "w") as f:
            json.dump(self.report, f, indent=2)
        print("📝 Report saved to fleet_entropy_report.json")

if __name__ == "__main__":
    profiler = FleetEntropyProfiler()
    profiler.scan_fleet()
