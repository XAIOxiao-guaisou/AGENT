import subprocess
import os
import subprocess
import os
from antigravity.utils import get_related_test
from antigravity.notifier import alert_critical

def run_tests_for_file(file_path):
    test_file = get_related_test(file_path)
    if not os.path.exists(test_file):
        print(f"No mapped test file found: {test_file}. Running all tests in tests/")
        test_target = "tests/"
    else:
        test_target = test_file

    print(f"Running tests: {test_target}")
    try:
        # Run pytest
        result = subprocess.run(
            ["python", "-m", "pytest", test_target],
            capture_output=True,
            text=True,
            check=False # Don't raise exception, just return code
        )

        if result.returncode == 0:
            print(f"\033[92mTests Passed: {test_target}\033[0m")
            return True, result.stdout
        else:
            print(f"\033[91mTests Failed: {test_target}\033[0m")
            # Check if critical failure (e.g., all tests failed or specific critical marker)
            # For this demo, any failure triggers rollback consideration (simplified)
            return False, result.stdout + result.stderr

    except Exception as e:
        print(f"Error running tests: {e}")
        return False, str(e)

def auto_rollback():
    """
    Execute git stash to revert changes.
    """
    print("Initiating Auto-Rollback...")
    try:
        subprocess.run(["git", "stash", "save", "Antigravity broken attempt"], check=True)
        print("Auto-executed Git Stash, code rolled back to stable state.")
        alert_critical("Code rolled back due to critical test failure!")
    except subprocess.CalledProcessError as e:
        print(f"Rollback failed: {e}")
