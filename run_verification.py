import sys
import os
import unittest

# Add project root to sys.path
sys.path.append(os.getcwd())

print(f"Added {os.getcwd()} to sys.path")

# Discover and run tests
loader = unittest.TestLoader()
start_dir = 'tests/antigravity'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if result.wasSuccessful():
    sys.exit(0)
else:
    sys.exit(1)
