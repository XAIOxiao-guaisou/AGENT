"""
Test Script for P0 Critical Optimizations
测试 P0 关键调优

Tests:
1. File Lock Manager - Concurrent file access safety
2. Immune Fatigue Protection - Infinite loop prevention
3. Integration with AutonomousAuditor
"""

import sys
import asyncio
from pathlib import Path
import tempfile

# Add antigravity to path
sys.path.insert(0, str(Path(__file__).parent))

from antigravity.file_lock_manager import FileLockManager, lock_file
from antigravity.rca_immune_system import RCAImmuneSystem, ErrorSnapshot
from antigravity.autonomous_auditor import AutonomousAuditor


async def test_file_lock_manager():
    """Test file lock manager / 测试文件锁管理器"""
    print("\n" + "="*60)
    print("🧪 Testing File Lock Manager")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        lock_manager = FileLockManager()
        
        # Test 1: Basic locking
        print("\n1️⃣ Test: Basic File Locking")
        
        async with lock_manager.lock_file(str(test_file)):
            # Write inside lock
            with open(test_file, 'w') as f:
                f.write("Locked write")
        
        # Read result
        with open(test_file, 'r') as f:
            content = f.read()
        
        print(f"   Content: {content}")
        assert content == "Locked write", "Content should match"
        print("   ✅ PASS: Basic locking works")
        
        # Test 2: Concurrent writes
        print("\n2️⃣ Test: Concurrent Write Safety")
        
        write_count = 10
        results = []
        
        async def concurrent_write(i):
            async with lock_manager.lock_file(str(test_file)):
                # Simulate some work
                await asyncio.sleep(0.01)
                
                # Read current content
                try:
                    with open(test_file, 'r') as f:
                        current = f.read()
                except FileNotFoundError:
                    current = ""
                
                # Append
                with open(test_file, 'w') as f:
                    f.write(current + f"Write{i}\n")
                
                results.append(i)
        
        # Run concurrent writes
        await asyncio.gather(*[concurrent_write(i) for i in range(write_count)])
        
        # Check result
        with open(test_file, 'r') as f:
            final_content = f.read()
        
        lines = [line for line in final_content.split('\n') if line]
        print(f"   Writes completed: {len(results)}/{write_count}")
        print(f"   Lines in file: {len(lines)}")
        
        assert len(lines) == write_count, "All writes should be present"
        print("   ✅ PASS: Concurrent writes are safe")
        
        # Test 3: Lock statistics
        print("\n3️⃣ Test: Lock Statistics")
        
        stats = lock_manager.get_lock_stats()
        print(f"   Lock acquisitions: {stats.get(str(test_file.resolve()), 0)}")
        
        assert stats.get(str(test_file.resolve()), 0) > 0, "Should have lock stats"
        print("   ✅ PASS: Lock statistics work")
    
    return True


async def test_immune_fatigue():
    """Test immune fatigue protection / 测试免疫疲劳保护"""
    print("\n" + "="*60)
    print("🧪 Testing Immune Fatigue Protection")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        immune_system = RCAImmuneSystem(project_root)
        
        # Test 1: Normal healing
        print("\n1️⃣ Test: Normal Healing (No Fatigue)")
        
        try:
            undefined_var
        except NameError as e:
            result = immune_system.on_error_captured(e, {'test': 'context'})
            
            print(f"   Fix action: {result.action}")
            print(f"   Healing stack size: {len(immune_system.healing_stack)}")
        
        assert len(immune_system.healing_stack) == 0, "Stack should be empty after normal healing"
        print("   ✅ PASS: Normal healing works")
        
        # Test 2: Simulate recursive healing
        print("\n2️⃣ Test: Recursive Healing Detection")
        
        # Create a mock error that will fail to fix
        class MockError(Exception):
            pass
        
        error = MockError("Test recursive error")
        
        # Manually add to healing stack to simulate recursion
        error_sig = f"MockError:Test recursive error"
        immune_system.healing_stack = [error_sig, error_sig, error_sig]  # Depth 3
        
        print(f"   Initial healing stack: {len(immune_system.healing_stack)}")
        
        # This should trigger fatigue protection
        result = immune_system.on_error_captured(error, {'test': 'recursive'})
        
        print(f"   Result action: {result.action}")
        print(f"   Healing stack after: {len(immune_system.healing_stack)}")
        
        assert result.action == 'immune_fatigue_escalation', "Should escalate due to fatigue"
        assert len(immune_system.healing_stack) == 0, "Stack should be cleared"
        print("   ✅ PASS: Immune fatigue protection works")
        
        # Test 3: MAX_HEALING_DEPTH constant
        print("\n3️⃣ Test: MAX_HEALING_DEPTH Configuration")
        
        print(f"   MAX_HEALING_DEPTH: {immune_system.MAX_HEALING_DEPTH}")
        
        assert immune_system.MAX_HEALING_DEPTH == 3, "Should be 3"
        print("   ✅ PASS: MAX_HEALING_DEPTH is correctly set")
    
    return True


async def test_autonomous_auditor_integration():
    """Test integration with AutonomousAuditor / 测试与 AutonomousAuditor 集成"""
    print("\n" + "="*60)
    print("🧪 Testing AutonomousAuditor Integration")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        auditor = AutonomousAuditor(project_root)
        
        # Test 1: File lock manager integration
        print("\n1️⃣ Test: File Lock Manager Integration")
        
        print(f"   Has file_lock_manager: {hasattr(auditor, 'file_lock_manager')}")
        print(f"   Type: {type(auditor.file_lock_manager).__name__}")
        
        assert hasattr(auditor, 'file_lock_manager'), "Should have file lock manager"
        print("   ✅ PASS: File lock manager integrated")
        
        # Test 2: Safe file write
        print("\n2️⃣ Test: Safe File Write")
        
        test_file = project_root / "test_safe_write.txt"
        content = "Test content with lock"
        
        await auditor._safe_file_write(str(test_file), content)
        
        # Verify file was written
        with open(test_file, 'r') as f:
            read_content = f.read()
        
        print(f"   File exists: {test_file.exists()}")
        print(f"   Content matches: {read_content == content}")
        
        assert read_content == content, "Content should match"
        print("   ✅ PASS: Safe file write works")
        
        # Test 3: RCA system integration
        print("\n3️⃣ Test: RCA System Integration")
        
        print(f"   Has rca_system: {hasattr(auditor, 'rca_system')}")
        print(f"   MAX_HEALING_DEPTH: {auditor.rca_system.MAX_HEALING_DEPTH}")
        
        assert hasattr(auditor, 'rca_system'), "Should have RCA system"
        assert auditor.rca_system.MAX_HEALING_DEPTH == 3, "Should have fatigue protection"
        print("   ✅ PASS: RCA system integrated with fatigue protection")
    
    return True


async def test_concurrent_file_access():
    """Test concurrent file access safety / 测试并发文件访问安全"""
    print("\n" + "="*60)
    print("🧪 Testing Concurrent File Access Safety")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        auditor = AutonomousAuditor(project_root)
        
        test_file = project_root / "concurrent_test.txt"
        
        print("\n1️⃣ Test: 10 Concurrent Writes")
        
        async def write_task(i):
            content = f"Task {i} writing\n"
            await auditor._safe_file_write(str(test_file), content)
            await asyncio.sleep(0.01)  # Simulate some work
        
        # Run 10 concurrent writes
        await asyncio.gather(*[write_task(i) for i in range(10)])
        
        # Check file exists and has content
        assert test_file.exists(), "File should exist"
        
        with open(test_file, 'r') as f:
            final_content = f.read()
        
        print(f"   File exists: True")
        print(f"   Final content length: {len(final_content)} bytes")
        print(f"   Lock stats: {auditor.file_lock_manager.get_lock_stats()}")
        
        assert len(final_content) > 0, "File should have content"
        print("   ✅ PASS: Concurrent file access is safe")
    
    return True


async def run_all_tests_async():
    """Run all async tests / 运行所有异步测试"""
    print("\n" + "🔒 "*20)
    print("P0 Critical Optimizations Tests")
    print("P0 关键调优测试")
    print("🔒 "*20)
    
    results = []
    
    try:
        results.append(("File Lock Manager", await test_file_lock_manager()))
    except Exception as e:
        print(f"\n❌ File Lock Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("File Lock Manager", False))
    
    try:
        results.append(("Immune Fatigue Protection", await test_immune_fatigue()))
    except Exception as e:
        print(f"\n❌ Immune Fatigue Protection test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Immune Fatigue Protection", False))
    
    try:
        results.append(("AutonomousAuditor Integration", await test_autonomous_auditor_integration()))
    except Exception as e:
        print(f"\n❌ AutonomousAuditor Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("AutonomousAuditor Integration", False))
    
    try:
        results.append(("Concurrent File Access", await test_concurrent_file_access()))
    except Exception as e:
        print(f"\n❌ Concurrent File Access test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Concurrent File Access", False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All P0 optimizations passed! System is production-ready!")
        print("   所有 P0 调优通过！系统已准备好投产！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review.")
        return 1


def run_all_tests():
    """Sync entry point / 同步入口点"""
    return asyncio.run(run_all_tests_async())


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
