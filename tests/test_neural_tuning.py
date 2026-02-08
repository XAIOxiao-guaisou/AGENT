
import unittest
import shutil
import sys
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("d:/桌面/AGENT")
sys.path.insert(0, str(PROJECT_ROOT))

# Mock DeliveryGate because it's hard to setup full cryptographic env in unit test
from unittest.mock import MagicMock, patch

from antigravity.core.fleet_manager import ProjectFleetManager
from antigravity.core.fleet_module_loader import FleetModuleLoader, ProjectSecurityError

TEST_ROOT = Path("d:/桌面/AGENT/test_neural_tuning_ws")

class TestNeuralTuning(unittest.TestCase):
    def setUp(self):
        if TEST_ROOT.exists():
            shutil.rmtree(TEST_ROOT)
        TEST_ROOT.mkdir(parents=True)
        
        self.fm = ProjectFleetManager.get_instance()
        self.fm.projects = {}

    def test_namespace_guard_and_security(self):
        print("\n🛡️ Testing Namespace Guard & Physical Anchor...")
        
        # 1. Setup Safe Project
        safe_p = TEST_ROOT / "safe_project"
        safe_p.mkdir()
        (safe_p / "core").mkdir()
        (safe_p / "core" / "utils.py").write_text("def ping(): return 'pong'", encoding='utf-8')
        
        # Register in FM
        with patch('antigravity.core.fleet_manager.ProjectFleetManager.verify_fleet_integrity') as mock_verify:
            # Mock FM Status
            # Fix: register_project takes (path: Path), infers ID from folder name
            self.fm.register_project(safe_p)
            # Inferred ID will be "safe_project"
            
            # Mock DeliveryGate for Physical Anchor
            # Patch target updated to match module-level import
            with patch('antigravity.core.fleet_module_loader.DeliveryGate') as MockGate:
                instance = MockGate.return_value
                instance.verify_integrity.return_value = True # Secure
                
                # Action: Load
                module = FleetModuleLoader.load_fleet_module("safe_project", "core.utils")
                
                # Check 1: Return value
                self.assertEqual(module.ping(), 'pong')
                
                # Check 2: Namespace Guard (sys.modules)
                self.assertIn('fleet.safe_project.core.utils', sys.modules)
                print(f"✅ Namespace Guard Verified: fleet.safe_project.core.utils loaded.")
                
                # Check 3: Logic Isolation
                self.assertNotIn(str(safe_p), sys.path)
                print("✅ Path Isolation Verified")

    def test_physical_anchor_blocking(self):
        print("\n🚫 Testing Physical Anchor Blocking...")
        
        bad_p = TEST_ROOT / "bad_project"
        bad_p.mkdir()
        # Fix: Pass Path object
        self.fm.register_project(bad_p)
        # Inferred ID: "bad_project"
        
        with patch('antigravity.core.fleet_module_loader.DeliveryGate') as MockGate:
            instance = MockGate.return_value
            # Simulate Tampered (verify_integrity returns False)
            instance.verify_integrity.return_value = False
            
            with self.assertRaises(ProjectSecurityError):
                FleetModuleLoader.load_fleet_module("bad_project", "core.utils")
                
            print("✅ Physical Anchor Blocked TAMPERED project.")

if __name__ == '__main__':
    unittest.main()
