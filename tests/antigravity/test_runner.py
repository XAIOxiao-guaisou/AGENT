import unittest
from unittest.mock import MagicMock, patch
from antigravity.utils import get_related_test
from antigravity.test_runner import auto_rollback

class TestRunner(unittest.TestCase):
    def test_test_mapping(self):
        """Test heuristic mapping."""
        self.assertEqual(get_related_test("src/auth.py"), "tests/test_auth.py")
        self.assertEqual(get_related_test("src/core/login.py"), "tests/core/test_login.py") # Note: utils implementation simple mapping might need adjustment if structure is complex, but for demo it just prefixes tests/

    @patch('subprocess.run')
    @patch('antigravity.test_runner.alert_critical')
    def test_auto_rollback(self, mock_alert, mock_run):
        """Verify git stash command."""
        auto_rollback()
        mock_run.assert_called_with(["git", "stash", "save", "Antigravity broken attempt"], check=True)

if __name__ == '__main__':
    unittest.main()
