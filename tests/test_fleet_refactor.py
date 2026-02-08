
import unittest
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to sys.path
PROJECT_ROOT = Path("d:/桌面/AGENT")
sys.path.insert(0, str(PROJECT_ROOT))

from antigravity.core.fleet_refactor_manager import FleetRefactorManager
from antigravity.core.fleet_manager import ProjectMetadata

TEST_ROOT = Path("d:/桌面/AGENT/test_refactor_ws")

class TestFleetRefactor(unittest.TestCase):
    def setUp(self):
        if TEST_ROOT.exists():
            shutil.rmtree(TEST_ROOT)
        TEST_ROOT.mkdir(parents=True)
        
        # Create Provider and Consumer projects
        self.provider_path = TEST_ROOT / "vortex"
        self.provider_path.mkdir()
        
        self.consumer_path = TEST_ROOT / "legacy_app"
        self.consumer_path.mkdir()
        
    def test_propagate_update(self):
        print("\n🏥 Testing Fleet Self-Healing...")
        
        with patch('antigravity.core.fleet_manager.ProjectFleetManager.get_instance') as MockFM:
            fm = MockFM.return_value
            
            # Mock Projects
            fm.projects = {
                "vortex": ProjectMetadata(
                    project_id="vortex", path=str(self.provider_path), 
                    name="Vortex", status="ACTIVE", last_active="", workspace_root=""
                ),
                "legacy_app": ProjectMetadata(
                    project_id="legacy_app", path=str(self.consumer_path),
                    name="Legacy App", status="ACTIVE", last_active="", workspace_root=""
                )
            }
            
            # Mock Dependency Scanner: Legacy App depends on Vortex
            def mock_scan(pid):
                if pid == "legacy_app":
                    return ["vortex"]
                return []
            
            fm.scan_cross_dependencies.side_effect = mock_scan
            
            # Action: Propagate Update
            manager = FleetRefactorManager()
            manager.fleet_mgr = fm # Inject mock
            
            manager.propagate_update("vortex", "Breaking change in Crypto API")
            
            # Verify INTENTION.md
            intention_file = self.consumer_path / "INTENTION.md"
            self.assertTrue(intention_file.exists())
            content = intention_file.read_text(encoding='utf-8')
            
            print(f"   ✅ INTENTION.md created in {self.consumer_path}")
            print(f"   📄 Content Check: 'Alert' in content? {'Refactoring Required' in content}")
            
            self.assertIn("Refactoring Required", content)
            self.assertIn("vortex", content)
            self.assertIn("Breaking change", content)

if __name__ == '__main__':
    unittest.main()
