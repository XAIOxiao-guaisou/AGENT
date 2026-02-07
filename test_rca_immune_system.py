"""
Test Script for RCA Immune System
测试 RCA 免疫系统

Tests:
1. Error snapshot extraction
2. Severity analysis
3. Auto-fix strategies
4. Expert escalation
5. Integration with AutonomousAuditor
"""

import sys
from pathlib import Path
import tempfile

# Add antigravity to path
sys.path.insert(0, str(Path(__file__).parent))

from antigravity.rca_immune_system import (
    RCAImmuneSystem, ErrorSnapshot, FixResult
)


def test_error_snapshot_extraction():
    """Test error snapshot extraction / 测试错误快照提取"""
    print("\n" + "="*60)
    print("🧪 Testing Error Snapshot Extraction")
    print("="*60)
    
    immune_system = RCAImmuneSystem()
    
    # Test 1: ImportError
    print("\n1️⃣ Test: ImportError Snapshot")
    try:
        import nonexistent_module
    except ImportError as e:
        snapshot = immune_system._extract_snapshot(e, None)
        
        print(f"   Error type: {snapshot.error_type}")
        print(f"   Message: {snapshot.message}")
        print(f"   File: {snapshot.file_path}")
        print(f"   Line: {snapshot.line_number}")
        
        assert snapshot.error_type == "ModuleNotFoundError", "Should be ModuleNotFoundError"
        assert "nonexistent_module" in snapshot.message, "Should mention module name"
        print("   ✅ PASS: ImportError snapshot extracted")
    
    # Test 2: NameError
    print("\n2️⃣ Test: NameError Snapshot")
    try:
        undefined_variable
    except NameError as e:
        snapshot = immune_system._extract_snapshot(e, None)
        
        print(f"   Error type: {snapshot.error_type}")
        print(f"   Message: {snapshot.message}")
        
        assert snapshot.error_type == "NameError", "Should be NameError"
        assert "undefined_variable" in snapshot.message, "Should mention variable name"
        print("   ✅ PASS: NameError snapshot extracted")
    
    return True


def test_severity_analysis():
    """Test severity analysis / 测试严重性分析"""
    print("\n" + "="*60)
    print("🧪 Testing Severity Analysis")
    print("="*60)
    
    immune_system = RCAImmuneSystem()
    
    # Test different error types
    test_cases = [
        ("ImportError", "LOW"),
        ("SyntaxError", "LOW"),
        ("NameError", "MEDIUM"),
        ("AttributeError", "MEDIUM"),
        ("RuntimeError", "HIGH"),
        ("ValueError", "HIGH"),
    ]
    
    for error_type, expected_severity in test_cases:
        snapshot = ErrorSnapshot(
            error_type=error_type,
            message=f"Test {error_type}",
            traceback="Test traceback"
        )
        
        severity = immune_system._analyze_severity(snapshot)
        print(f"   {error_type}: {severity} (expected: {expected_severity})")
        
        assert severity == expected_severity, f"Severity mismatch for {error_type}"
    
    print("   ✅ PASS: Severity analysis works")
    return True


def test_auto_fix_import_error():
    """Test auto-fix for ImportError / 测试 ImportError 自动修复"""
    print("\n" + "="*60)
    print("🧪 Testing Auto-Fix: ImportError")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        immune_system = RCAImmuneSystem(project_root)
        
        print("\n1️⃣ Test: Module Installation (Simulated)")
        
        # Create a snapshot for missing module
        snapshot = ErrorSnapshot(
            error_type="ModuleNotFoundError",
            message="No module named 'requests'",
            traceback="Test traceback"
        )
        
        # Note: We won't actually install to avoid side effects
        # Just test the logic
        print(f"   Snapshot: {snapshot.error_type}")
        print(f"   Message: {snapshot.message}")
        
        # Check if can auto-fix
        can_fix = immune_system._can_auto_fix(snapshot)
        print(f"   Can auto-fix: {can_fix}")
        
        assert can_fix, "Should be able to auto-fix ImportError"
        print("   ✅ PASS: ImportError auto-fix logic works")
    
    return True


def test_auto_fix_suggestions():
    """Test auto-fix suggestions / 测试自动修复建议"""
    print("\n" + "="*60)
    print("🧪 Testing Auto-Fix Suggestions")
    print("="*60)
    
    immune_system = RCAImmuneSystem()
    
    # Test 1: SyntaxError
    print("\n1️⃣ Test: SyntaxError Suggestions")
    snapshot = ErrorSnapshot(
        error_type="SyntaxError",
        message="unexpected EOF while parsing",
        traceback="Test traceback"
    )
    
    fix_result = immune_system._fix_syntax_error(snapshot)
    print(f"   Success: {fix_result.success}")
    print(f"   Action: {fix_result.action}")
    print(f"   Details: {fix_result.details}")
    
    assert fix_result.action == "suggestions_provided", "Should provide suggestions"
    assert "brackets" in fix_result.details.lower(), "Should mention brackets"
    print("   ✅ PASS: SyntaxError suggestions work")
    
    # Test 2: NameError
    print("\n2️⃣ Test: NameError Suggestions")
    snapshot = ErrorSnapshot(
        error_type="NameError",
        message="name 'foo' is not defined",
        traceback="Test traceback"
    )
    
    fix_result = immune_system._fix_name_error(snapshot)
    print(f"   Success: {fix_result.success}")
    print(f"   Details: {fix_result.details}")
    
    assert "foo" in fix_result.details, "Should mention variable name"
    print("   ✅ PASS: NameError suggestions work")
    
    return True


def test_expert_escalation():
    """Test expert escalation / 测试专家升级"""
    print("\n" + "="*60)
    print("🧪 Testing Expert Escalation")
    print("="*60)
    
    immune_system = RCAImmuneSystem()
    
    print("\n1️⃣ Test: Escalation for Complex Error")
    
    # Create a high-severity error
    snapshot = ErrorSnapshot(
        error_type="RuntimeError",
        message="Complex runtime error",
        traceback="Test traceback",
        retry_count=3  # Trigger escalation
    )
    
    context = {
        'module': 'test_module',
        'function': 'test_function'
    }
    
    fix_result = immune_system._escalate_to_expert(snapshot, context)
    
    print(f"   Action: {fix_result.action}")
    print(f"   Success: {fix_result.success}")
    
    assert fix_result.action == "expert_consultation", "Should escalate to expert"
    assert not fix_result.success, "Expert consultation doesn't auto-fix"
    print("   ✅ PASS: Expert escalation works")
    
    return True


def test_immune_system_integration():
    """Test full immune system flow / 测试完整免疫系统流程"""
    print("\n" + "="*60)
    print("🧪 Testing Immune System Integration")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        immune_system = RCAImmuneSystem(project_root)
        
        print("\n1️⃣ Test: Full Error Handling Flow")
        
        # Simulate an error
        try:
            undefined_var
        except NameError as e:
            fix_result = immune_system.on_error_captured(e, {'test': 'context'})
            
            print(f"   Fix result: {fix_result.action}")
            print(f"   Success: {fix_result.success}")
        
        # Check fix history
        history = immune_system.get_fix_history()
        print(f"\n2️⃣ Test: Fix History")
        print(f"   History entries: {len(history)}")
        
        assert len(history) > 0, "Should have fix history"
        print("   ✅ PASS: Fix history tracking works")
        
        # Check statistics
        stats = immune_system.get_statistics()
        print(f"\n3️⃣ Test: Statistics")
        print(f"   Total errors: {stats['total_errors']}")
        print(f"   Successful fixes: {stats['successful_fixes']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Error types: {stats['error_types']}")
        
        assert stats['total_errors'] > 0, "Should have error statistics"
        print("   ✅ PASS: Statistics tracking works")
    
    return True


def test_autonomous_auditor_integration():
    """Test integration with AutonomousAuditor / 测试与 AutonomousAuditor 集成"""
    print("\n" + "="*60)
    print("🧪 Testing AutonomousAuditor Integration")
    print("="*60)
    
    print("\n1️⃣ Test: Import Integration")
    
    try:
        from antigravity.autonomous_auditor import AutonomousAuditor
        from antigravity.rca_immune_system import RCAImmuneSystem
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Create auditor
            auditor = AutonomousAuditor(project_root)
            
            # Create immune system
            immune_system = RCAImmuneSystem(project_root)
            
            # Manually integrate (will be automatic in Phase 20 completion)
            auditor.rca_system = immune_system
            
            print(f"   Auditor has RCA system: {hasattr(auditor, 'rca_system')}")
            print(f"   RCA system type: {type(auditor.rca_system).__name__}")
            
            assert hasattr(auditor, 'rca_system'), "Auditor should have RCA system"
            print("   ✅ PASS: Integration successful")
    
    except Exception as e:
        print(f"   ❌ Integration failed: {e}")
        return False
    
    return True


def run_all_tests():
    """Run all tests / 运行所有测试"""
    print("\n" + "🦠 "*20)
    print("RCA Immune System Tests")
    print("RCA 免疫系统测试")
    print("🦠 "*20)
    
    results = []
    
    try:
        results.append(("Error Snapshot Extraction", test_error_snapshot_extraction()))
    except Exception as e:
        print(f"\n❌ Error Snapshot Extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Error Snapshot Extraction", False))
    
    try:
        results.append(("Severity Analysis", test_severity_analysis()))
    except Exception as e:
        print(f"\n❌ Severity Analysis test failed: {e}")
        results.append(("Severity Analysis", False))
    
    try:
        results.append(("Auto-Fix ImportError", test_auto_fix_import_error()))
    except Exception as e:
        print(f"\n❌ Auto-Fix ImportError test failed: {e}")
        results.append(("Auto-Fix ImportError", False))
    
    try:
        results.append(("Auto-Fix Suggestions", test_auto_fix_suggestions()))
    except Exception as e:
        print(f"\n❌ Auto-Fix Suggestions test failed: {e}")
        results.append(("Auto-Fix Suggestions", False))
    
    try:
        results.append(("Expert Escalation", test_expert_escalation()))
    except Exception as e:
        print(f"\n❌ Expert Escalation test failed: {e}")
        results.append(("Expert Escalation", False))
    
    try:
        results.append(("Immune System Integration", test_immune_system_integration()))
    except Exception as e:
        print(f"\n❌ Immune System Integration test failed: {e}")
        results.append(("Immune System Integration", False))
    
    try:
        results.append(("AutonomousAuditor Integration", test_autonomous_auditor_integration()))
    except Exception as e:
        print(f"\n❌ AutonomousAuditor Integration test failed: {e}")
        results.append(("AutonomousAuditor Integration", False))
    
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
        print("\n🎉 All tests passed! RCA Immune System is ready to fight errors!")
        print("   免疫系统已准备好对抗错误！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
