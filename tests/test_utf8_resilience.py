import os
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from antigravity.utils.io_utils import safe_read

class TestUTF8Resilience(unittest.TestCase):
    def setUp(self):
        self.binary_file = Path("test_binary.bin")
        self.text_file = Path("test_text.txt")
        self.mixed_file = Path("test_mixed.txt")
        
        # Create binary file with invalid UTF-8 sequence (0xFF)
        with open(self.binary_file, "wb") as f:
            f.write(b"\xff\xff\xff\xff")
            
        # Create clean text file
        self.text_file.write_text("Hello World", encoding="utf-8")
        
        # Create mixed file (invalid UTF-8 but .txt extension)
        # safe_read should use 'replace' handler
        with open(self.mixed_file, "wb") as f:
            f.write(b"Hello \xff World")

    def tearDown(self):
        if self.binary_file.exists():
            self.binary_file.unlink()
        if self.text_file.exists():
            self.text_file.unlink()
        if self.mixed_file.exists():
            self.mixed_file.unlink()

    def test_binary_exclusion_by_extension(self):
        """Test that .bin extension is skipped"""
        result = safe_read(self.binary_file)
        self.assertEqual(result, "[BINARY_FILE_SKIPPED]")

    def test_clean_text_read(self):
        """Test normal UTF-8 reading"""
        result = safe_read(self.text_file)
        self.assertEqual(result, "Hello World")

    def test_mixed_encoding_resilience(self):
        """Test that invalid bytes are replaced, not crashing"""
        result = safe_read(self.mixed_file)
        # Expect replacement character ()
        self.assertIn("Hello", result)
        self.assertIn("World", result)
        # Should NOT raise UnicodeDecodeError

    def test_large_file_truncation(self):
        """Test that files > 5MB are truncated"""
        large_file = Path("test_large.txt")
        try:
            # Create ~6MB file
            with open(large_file, "w", encoding="utf-8") as f:
                f.write("A" * 6 * 1024 * 1024)
            
            result = safe_read(large_file)
            self.assertIn("[...TRUNCATED DUE TO SIZE]", result)
            self.assertLess(len(result), 200 * 1024) # Should be around 100KB + suffix
        finally:
            if large_file.exists():
                large_file.unlink()

    def test_large_file_truncation(self):
        """Test that files > 5MB are truncated"""
        large_file = Path("test_large.txt")
        try:
            # Create ~6MB file
            with open(large_file, "w", encoding="utf-8") as f:
                f.write("A" * 6 * 1024 * 1024)
            
            result = safe_read(large_file)
            self.assertIn("[...TRUNCATED DUE TO SIZE]", result)
            self.assertLess(len(result), 200 * 1024) # Should be around 100KB + suffix
        finally:
            if large_file.exists():
                large_file.unlink()

if __name__ == "__main__":
    unittest.main()
