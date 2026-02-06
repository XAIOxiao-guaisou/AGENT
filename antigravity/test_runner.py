import subprocess
import os
import re
from antigravity.utils import get_related_test
from antigravity.notifier import alert_critical

def run_tests_for_file(file_path):
    """
    运行单个文件的相关测试
    Run tests for a single file
    """
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

# ============================================================
# Project-Level Full Test Suite Support (P1)
# 项目级全量测试支持 (P1)
# ============================================================

def run_full_suite(project_root="."):
    """
    运行全量 pytest 测试套件
    Run full pytest test suite
    
    Returns:
        (success: bool, output: str, failed_files: list)
    """
    print("🧪 正在执行集成测试套件...")
    print("🧪 Executing integration test suite...")
    
    try:
        # 使用 -v 获取详细输出,用于后续解析失败文件路径
        # Use -v for detailed output to parse failed file paths
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short", "--color=no"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=project_root
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        # 解析失败的测试文件
        # Parse failed test files
        failed_files = _parse_failed_tests(output)
        
        if success:
            print("✅ 所有测试通过! / All tests passed!")
        else:
            print(f"❌ {len(failed_files)} 个测试文件失败 / test files failed")
            for file in failed_files:
                print(f"   - {file}")
        
        return success, output, failed_files
        
    except FileNotFoundError:
        print("⚠️ pytest 未安装 / pytest not found")
        return False, "pytest not installed", []
    except subprocess.TimeoutExpired:
        print("⚠️ 测试超时 (300秒) / Test timeout (300s)")
        return False, "Test timeout after 300s", []
    except Exception as e:
        print(f"❌ 测试执行失败: {e} / Test execution failed: {e}")
        return False, str(e), []

def _parse_failed_tests(pytest_output):
    """
    解析 pytest 输出,提取失败的测试文件
    Parse pytest output to extract failed test files
    
    用于精准反馈给 Agent
    For precise feedback to Agent
    
    Returns:
        List of failed test file paths
    """
    # 匹配 FAILED tests/test_xxx.py::TestClass::test_method
    # Match FAILED tests/test_xxx.py::TestClass::test_method
    pattern = r"FAILED (tests/test_[^\s:]+\.py)"
    matches = re.findall(pattern, pytest_output)
    
    return sorted(list(set(matches)))

def run_with_coverage(project_root="."):
    """
    运行测试并生成覆盖率报告 (可选)
    Run tests with coverage report (optional)
    
    需要安装 pytest-cov: pip install pytest-cov
    Requires pytest-cov: pip install pytest-cov
    """
    print("🧪 运行测试并生成覆盖率报告...")
    print("🧪 Running tests with coverage report...")
    
    try:
        result = subprocess.run(
            ["pytest", "tests/", "--cov=src", "--cov-report=term-missing"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=project_root
        )
        
        print(result.stdout)
        return result.returncode == 0
        
    except FileNotFoundError:
        print("⚠️ pytest-cov 未安装 / pytest-cov not found")
        print("💡 安装: pip install pytest-cov / Install: pip install pytest-cov")
        return False
    except Exception as e:
        print(f"❌ 覆盖率测试失败: {e} / Coverage test failed: {e}")
        return False
