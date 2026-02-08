
import unittest
import shutil
import tempfile
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, r'd:\桌面\AGENT')

from antigravity.core.fleet_manager import ProjectFleetManager
from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType

class TestFleetIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temp workspace
        self.test_dir = tempfile.mkdtemp()
        self.workspace_root = Path(self.test_dir)
        
        # Create Project A
        self.proj_a = self.workspace_root / "Project_Alpha"
        self.proj_a.mkdir()
        (self.proj_a / ".antigravity").mkdir()
        (self.proj_a / "PLAN.md").write_text("# Plan A", encoding='utf-8')
        
        # Create Project B
        self.proj_b = self.workspace_root / "Project_Beta"
        self.proj_b.mkdir()
        (self.proj_b / ".antigravity").mkdir()
        (self.proj_b / "PLAN.md").write_text("# Plan B", encoding='utf-8')
        
        # Create Workspace Marker
        (self.workspace_root / ".antigravity_workspace").touch()
        
        # Reset Fleet Manager
        if ProjectFleetManager._instance:
            ProjectFleetManager._instance.projects = {}
            ProjectFleetManager._instance._instance = None
            
        self.fleet = ProjectFleetManager.get_instance()
        # Mock global config to point to a temp file
        self.fleet.global_config_path = self.workspace_root / "fleet_config.json"
        
        # Reset Queue
        TelemetryQueue.clear_queue()

    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except Exception as e:
            print(f"Warning: Could not remove temp dir: {e}")

    def test_scan_and_register(self):
        print("\n🧪 Testing Workspace Scanning...")
        self.fleet.scan_workspace(str(self.workspace_root))
        
        status = self.fleet.get_fleet_status()
        project_ids = [p['project_id'] for p in status]
        
        print(f"   Found Projects: {project_ids}")
        self.assertTrue("project_alpha" in project_ids)
        self.assertTrue("project_beta" in project_ids)
        self.assertEqual(len(status), 2)
        
        # Verify Workspace Root
        meta_a = self.fleet.projects["project_alpha"]
        self.assertEqual(meta_a.workspace_root, str(self.workspace_root))

    def test_switch_logic(self):
        print("\n🧪 Testing Atomic Context Switch Logic...")
        self.fleet.scan_workspace(str(self.workspace_root))
        
        # 1. Switch to A
        print("   Switching to Project Alpha...")
        success = self.fleet.switch_project("project_alpha")
        self.assertTrue(success)
        self.assertEqual(self.fleet.active_project_id, "project_alpha")
        
        # 2. Check Telemetry Flush
        # Since we just flushed, check if appropriate events are in buffer
        # TelemetryQueue inside switch_project puts BEGIN -> COMPLETE -> MARK
        # We need to peek into the queue
        
        q = TelemetryQueue.get_queue()
        events = []
        while not q.empty():
            events.append(q.get())
            
        event_names = [e['data'].get('event') for e in events if isinstance(e['data'], dict)]
        print(f"   Queue Events: {event_names}")
        
        self.assertIn("CONTEXT_SWITCH_BEGIN", event_names)
        self.assertIn("CONTEXT_SWITCH_COMPLETE", event_names)
        self.assertIn("MARK_FLUSH_COMPLETE", event_names)

if __name__ == '__main__':
    unittest.main()
