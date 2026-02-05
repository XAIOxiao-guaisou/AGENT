import time
import os
import unittest
from unittest.mock import MagicMock, patch
from antigravity.monitor import AntigravityMonitor

class TestMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = AntigravityMonitor(".")
        self.monitor.auditor = MagicMock()
        self.monitor.debounce_seconds = 0.5 # Shorten for test

    def test_debouncing(self):
        """Monitor should debounce rapid events."""
        event = MagicMock()
        event.is_directory = False
        event.src_path = "test_file.py"
        
        # Simulate rapid firing
        self.monitor.on_modified(event)
        self.monitor.on_modified(event)
        self.monitor.on_modified(event)
        
        # Should not be called yet
        self.monitor.auditor.audit_file.assert_not_called()
        
        # Wait for debounce
        time.sleep(0.6)
        
        # Should be called ONCE
        self.monitor.auditor.audit_file.assert_called_once_with("test_file.py")

    def test_loop_prevention(self):
        """Monitor should ignore files with FIXME signature."""
        filename = "test_loop.py"
        with open(filename, "w") as f:
            f.write("# FIXME: DeepSeek Auditor identified a logic error.\ndef foo(): pass")
            
        try:
            event = MagicMock()
            event.is_directory = False
            event.src_path = filename
            
            self.monitor.on_modified(event)
            time.sleep(0.6) # Wait for debounce just in case
            
            # Should NOT be audited because of signature
            self.monitor.auditor.audit_file.assert_not_called()
        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()
