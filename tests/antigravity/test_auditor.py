import unittest
import os
from unittest.mock import MagicMock, patch
from antigravity.auditor import Auditor

class TestAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = Auditor(".")
        self.test_file_path = "test_auth_hallucination.py"
        self.plan_path = "PLAN.md"

        # Create dummy PLAN.md
        with open(self.plan_path, 'w') as f:
            f.write("# Plan\nImplement real auth.")

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.plan_path):
            os.remove(self.plan_path)
        if os.path.exists("VIBE_FIX.md"):
            os.remove("VIBE_FIX.md")

    @patch('antigravity.auditor.requests.post')
    @patch('antigravity.utils.get_git_diff')
    @patch('antigravity.auditor.alert_critical')
    def test_hallucination_induction(self, mock_alert, mock_diff, mock_api):
        """Simulate hallucination and verify SYSTEM CRITICAL response."""
        # Setup hallucinated code
        code = "def authenticate(user): return True # TODO: Implement real auth"
        with open(self.test_file_path, 'w') as f:
            f.write(code)
            
        # Mock diff
        mock_diff.return_value = "+ def authenticate(user): return True"
        
        # Test "Mock" mode (no API key) logic specifically or mock API return
        # Here we test the Auditor's logic when it receives a CRITICAL response
        critical_response = "[SYSTEM CRITICAL]\nERROR: Hallucination.\nFIX: Fix it."
        
        # If API Key is not set, it uses internal mock logic which detects 'TODO' and 'return True'
        # let's rely on that internal mock logic for this test to be self-contained without mocking requests if key is missing
        # But to be safe, let's force the mock logic response if we were capturing stdout, 
        # but here we can check if VIBE_FIX is created.
        
        # Let's force-feed a failure for the sake of unit testing the *handling* of failure
        self.auditor.handle_failure(self.test_file_path, critical_response)
        
        # Check VIBE_FIX.md
        self.assertTrue(os.path.exists("VIBE_FIX.md"))
        with open("VIBE_FIX.md", 'r') as f:
            self.assertIn("[SYSTEM CRITICAL]", f.read())
            
        # Check Injection
        with open(self.test_file_path, 'r') as f:
            first_line = f.readline()
            self.assertIn("# FIXME: DeepSeek Auditor", first_line)

    @patch('antigravity.auditor.alert_critical')
    def test_circuit_breaker(self, mock_alert):
        """Verify manual mode after 3 failures."""
        self.auditor.failure_counts[self.test_file_path] = 3
        
        with patch('builtins.print') as mock_print:
            self.auditor.audit_file(self.test_file_path)
            # Should print "Skipping ... Manual Mode"
            # We can check if it returns early (audit logic not reached)
            # But relying on print capture for this demo
            args, _ = mock_print.call_args
            self.assertIn("Manual Mode", args[0])
            mock_alert.assert_called()

if __name__ == '__main__':
    unittest.main()
