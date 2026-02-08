import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from antigravity.core.mission_orchestrator import MissionOrchestrator, TaskState
from antigravity.infrastructure.env_scanner import EnvScanner

class TestAutoHealing(unittest.TestCase):
    def setUp(self):
        self.orchestrator = MissionOrchestrator()
        # Mock the EnvScanner inside the orchestrator
        self.orchestrator.env_scanner = MagicMock(spec=EnvScanner)
        
        # Setup specific mock behaviors
        self.orchestrator.env_scanner.project_root = Path(".")
        # Default behavior: dependency check fails for 'numpy', passes for others
        self.orchestrator.env_scanner.check_dependency.side_effect = \
            lambda pkg: False if pkg == 'numpy' else True
            
        # Mock request_fix to succeed
        self.orchestrator.env_scanner.request_fix.return_value = True

    def test_healing_trigger(self):
        print("\n🧪 Testing Autonomous Healing Protocol...")
        
        # 1. Create a dummy requirements.txt
        with open("requirements.txt", "w") as f:
            f.write("numpy>=1.20.0\nrequests")
            
        try:
            # 2. ongoing task in PENDING
            idea = "Calculate heavy math using numpy"
            tasks = self.orchestrator.decompose_idea(idea)
            task = tasks[0]
            
            print(f"   Task State: {task.state}")
            
            # 3. Step 1: PENDING -> STRATEGY_REVIEW
            new_state = self.orchestrator.step(task)
            print(f"   Step 1 -> {new_state}")
            self.assertEqual(new_state, TaskState.STRATEGY_REVIEW)
            
            # 4. Step 2: STRATEGY_REVIEW -> HEALING (because numpy is missing)
            # The orchestrated logic calls _check_environment_health, which fails.
            # Then triggers healing.
            new_state = self.orchestrator.step(task)
            print(f"   Step 2 -> {new_state}")
            self.assertEqual(new_state, TaskState.HEALING)
            
            # Check if check_dependency was called
            # self.orchestrator.env_scanner.check_dependency.assert_any_call('numpy')
            
            # 5. Step 3: HEALING -> EXECUTING (Healing attempt)
            # This calls _attempt_healing -> env_scanner.request_fix('numpy')
            new_state = self.orchestrator.step(task)
            print(f"   Step 3 -> {new_state}")
            self.assertEqual(new_state, TaskState.EXECUTING)
            
            # Verify request_fix was called
            self.orchestrator.env_scanner.request_fix.assert_called_with('numpy')
            print("   ✅ Verified: request_fix('numpy') was triggered.")
            
        finally:
            if Path("requirements.txt").exists():
                Path("requirements.txt").unlink()

if __name__ == "__main__":
    unittest.main()
