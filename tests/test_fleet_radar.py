import unittest
import shutil
import os
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path("d:/桌面/AGENT")))
from antigravity.core.fleet_manager import ProjectFleetManager, ProjectMetadata

# Setup paths
TEST_ROOT = Path("d:/桌面/AGENT/test_radar_workspace")
PROJECTS_ROOT = TEST_ROOT / "projects"

class TestFleetRadar(unittest.TestCase):
    def setUp(self):
        # Clean workspace
        if TEST_ROOT.exists():
            shutil.rmtree(TEST_ROOT)
        TEST_ROOT.mkdir(parents=True)
        PROJECTS_ROOT.mkdir()
        
        # Initialize Fleet Manager
        self.fleet_mgr = ProjectFleetManager.get_instance()
        # Mock global config path to avoid messing with real config
        self.fleet_mgr.global_config_path = TEST_ROOT / "fleet_config.json"
        self.fleet_mgr.projects = {} # Reset state

    def create_project(self, name, files):
        p_path = PROJECTS_ROOT / name
        p_path.mkdir()
        
        for fname, content in files.items():
            fpath = p_path / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding='utf-8')
            
        # Register
        self.fleet_mgr.register_project(p_path)
        return p_path

    def test_contamination_propagation(self):
        print("\n📡 Testing Dependency Radar & Contamination Propagation...")
        
        # 1. Create Lib Project (The Dependency)
        lib_name = "security_core"
        self.create_project(lib_name, {
            "security_core/__init__.py": "def secure_func(): pass",
            "PLAN.md": "# Security Core"
        })
        
        # 2. Create App Project (The Dependent)
        app_name = "banking_app"
        self.create_project(app_name, {
            "banking_app/__init__.py": "",
            "banking_app/main.py": "import security_core\ndef main(): security_core.secure_func()",
            "PLAN.md": "# Banking App"
        })
        
        # 3. Verify Map
        pkg_map = self.fleet_mgr._build_package_map()
        print(f"📦 Package Map: {pkg_map}")
        self.assertIn("security_core", pkg_map)
        
        # 4. Verify Dependency
        deps = self.fleet_mgr.scan_cross_dependencies(app_name)
        print(f"🔗 Dependencies for {app_name}: {deps}")
        self.assertIn(lib_name, deps)
        
        # 5. Test Status Propagation
        # Case A: All Active
        status = self.fleet_mgr.verify_fleet_integrity(app_name)
        print(f"🟢 Initial Status: {status['status']}")
        self.assertEqual(status['status'], 'ACTIVE')
        
        # Case B: Lib TAMPERED -> App CONTAMINATED
        print("🔓 Simulating Tamper on Lib...")
        self.fleet_mgr.projects[lib_name].status = 'TAMPERED'
        
        status = self.fleet_mgr.verify_fleet_integrity(app_name)
        print(f"☢️  Post-Tamper Status: {status['status']}")
        self.assertEqual(status['status'], 'CONTAMINATED')
        self.assertIn(f"Dependency '{lib_name}' is TAMPERED", status['violations'])

if __name__ == '__main__':
    unittest.main()
