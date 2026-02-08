"""
Test Script for Sheriff Brain Upgrade Components
测试 Sheriff Brain Upgrade 组件

Tests:
1. Mission Orchestrator - State machine and task decomposition
2. Local Reasoning Engine - Intent mapping and plan generation
3. Sheriff Strategist - Plan tuning and audit
"""

import sys
from pathlib import Path

# Add antigravity to path
sys.path.insert(0, str(Path(__file__).parent))

from antigravity.mission_orchestrator import (
    MissionOrchestrator, AtomicTask, TaskState
)
from antigravity.local_reasoning import (
    LocalReasoningEngine, IntentMapper, ConstraintSet
)
from antigravity.sheriff_strategist import (
    SheriffStrategist, OptimizedPlan, SignOffResult
)


def test_mission_orchestrator():
    """Test Mission Orchestrator / 测试任务编排器"""
    print("\n" + "="*60)
    print("🧪 Testing Mission Orchestrator")
    print("="*60)
    
    orchestrator = MissionOrchestrator()
    
    # Test 1: Decompose idea
    print("\n1️⃣ Test: Decompose Idea")
    idea = "Create a web app with database, API, and authentication"
    tasks = orchestrator.decompose_idea(idea)
    
    print(f"   Idea: {idea}")
    print(f"   Generated {len(tasks)} tasks:")
    for task in tasks:
        print(f"   - {task.task_id}: {task.goal}")
    
    assert len(tasks) > 0, "Should generate at least one task"
    print("   ✅ PASS: Task decomposition works")
    
    # Test 2: Build dependency graph
    print("\n2️⃣ Test: Build Dependency Graph")
    graph = orchestrator.build_dependency_graph()
    
    print(f"   Nodes: {graph.number_of_nodes()}")
    print(f"   Edges: {graph.number_of_edges()}")
    
    assert graph.number_of_nodes() == len(tasks), "Graph should have all tasks"
    print("   ✅ PASS: Dependency graph built")
    
    # Test 3: State machine
    print("\n3️⃣ Test: State Machine Transitions")
    task = tasks[0]
    print(f"   Initial state: {task.state.value}")
    
    # Transition through states
    orchestrator.current_task = task
    new_state = orchestrator.step(task)
    print(f"   After step 1: {new_state.value}")
    assert new_state == TaskState.STRATEGY_REVIEW, "Should move to STRATEGY_REVIEW"
    
    new_state = orchestrator.step(task)
    print(f"   After step 2: {new_state.value}")
    assert new_state == TaskState.EXECUTING, "Should move to EXECUTING"
    
    print("   ✅ PASS: State machine works")
    
    # Test 4: Execution summary
    print("\n4️⃣ Test: Execution Summary")
    summary = orchestrator.get_execution_summary()
    print(f"   Total tasks: {summary['total_tasks']}")
    print(f"   State distribution: {summary['state_distribution']}")
    print(f"   Completion rate: {summary['completion_rate']:.1%}")
    
    print("   ✅ PASS: Execution summary works")
    
    return True


def test_local_reasoning_engine():
    """Test Local Reasoning Engine / 测试本地推理引擎"""
    print("\n" + "="*60)
    print("🧪 Testing Local Reasoning Engine")
    print("="*60)
    
    engine = LocalReasoningEngine()
    
    # Test 1: Intent mapping
    print("\n1️⃣ Test: Intent Mapping")
    idea = "Build a REST API with JWT authentication and PostgreSQL database"
    intent = engine.intent_mapper.map(idea)
    
    print(f"   Idea: {idea}")
    print(f"   Detected:")
    print(f"   - Database: {intent.requires_database}")
    print(f"   - API: {intent.requires_api}")
    print(f"   - Auth: {intent.requires_auth}")
    print(f"   - Framework: {intent.framework}")
    
    assert intent.requires_database, "Should detect database requirement"
    assert intent.requires_api, "Should detect API requirement"
    assert intent.requires_auth, "Should detect auth requirement"
    print("   ✅ PASS: Intent mapping works")
    
    # Test 2: Draft plan
    print("\n2️⃣ Test: Draft Plan")
    plan = engine.draft_plan(idea)
    
    print(f"   Files to create: {len(plan['files_to_create'])}")
    for file in plan['files_to_create'][:5]:  # Show first 5
        print(f"   - {file}")
    print(f"   Dependencies: {plan['dependencies']}")
    print(f"   Tasks: {plan['tasks']}")
    
    assert len(plan['files_to_create']) > 0, "Should generate files"
    assert len(plan['dependencies']) > 0, "Should have dependencies"
    print("   ✅ PASS: Plan generation works")
    
    # Test 3: Constraint validation
    print("\n3️⃣ Test: Constraint Validation")
    
    # Test code with violations
    bad_code = """
def very_long_function():
    # This function is too long
    """ + "\n    pass" * 60
    
    violations = engine.constraint_set.validate_code(bad_code, "test.py")
    print(f"   Violations found: {len(violations)}")
    for v in violations:
        print(f"   - {v}")
    
    assert len(violations) > 0, "Should detect violations"
    print("   ✅ PASS: Constraint validation works")
    
    # Test 4: Escalation decision
    print("\n4️⃣ Test: Escalation Decision")
    
    simple_error = {'type': 'SyntaxError', 'retry_count': 0}
    should_escalate = engine.should_escalate_to_remote(simple_error)
    print(f"   Simple error escalation: {should_escalate}")
    assert not should_escalate, "Simple errors should not escalate"
    
    complex_error = {'type': 'DesignError', 'retry_count': 0}
    should_escalate = engine.should_escalate_to_remote(complex_error)
    print(f"   Complex error escalation: {should_escalate}")
    assert should_escalate, "Complex errors should escalate"
    
    print("   ✅ PASS: Escalation logic works")
    
    return True


def test_sheriff_strategist():
    """Test Sheriff Strategist / 测试远程战略官"""
    print("\n" + "="*60)
    print("🧪 Testing Sheriff Strategist")
    print("="*60)
    
    strategist = SheriffStrategist()
    
    # Test 1: Plan tuning
    print("\n1️⃣ Test: Plan Tuning")
    plan = {
        'intent': 'Create API',
        'files_to_create': ['api.py'],
        'dependencies': ['fastapi', 'uvicorn'],
        'tasks': ['Implement endpoints']
    }
    
    optimized = strategist.tune_plan(plan)
    
    print(f"   Original plan: {plan['intent']}")
    print(f"   Quality score: {optimized.quality_score}/100")
    print(f"   Approved: {optimized.approved}")
    print(f"   Optimizations: {len(optimized.optimizations)}")
    for opt in optimized.optimizations:
        print(f"   - {opt}")
    
    assert optimized.quality_score > 0, "Should have quality score"
    print("   ✅ PASS: Plan tuning works")
    
    # Test 2: Logic audit
    print("\n2️⃣ Test: Logic Audit")
    project = {
        'test_coverage': 95,
        'vibe_score': 92,
        'dependency_graph_closed': True
    }
    
    sign_off = strategist.final_sign_off(project)
    
    print(f"   Approved: {sign_off.approved}")
    print(f"   Score: {sign_off.score}/100")
    print(f"   Signature: {sign_off.signature}")
    print(f"   Issues: {sign_off.issues}")
    
    assert sign_off.approved, "Good project should be approved"
    assert sign_off.score > 90, "Score should be high"
    print("   ✅ PASS: Logic audit works")
    
    # Test 3: Expert consultation
    print("\n3️⃣ Test: Expert Consultation")
    error = {
        'type': 'DesignError',
        'message': 'Circular dependency detected',
        'retry_count': 3
    }
    context = {'module': 'auth', 'dependencies': ['database']}
    
    consultation = strategist.expert_consultation(error, context)
    
    print(f"   Root cause: {consultation['root_cause']}")
    print(f"   Fix approach: {consultation['fix_approach']}")
    print(f"   Prevention: {consultation['prevention']}")
    
    assert 'root_cause' in consultation, "Should provide root cause"
    print("   ✅ PASS: Expert consultation works")
    
    # Test 4: Audit history
    print("\n4️⃣ Test: Audit History")
    history = strategist.get_audit_history()
    
    print(f"   Audit records: {len(history)}")
    for record in history:
        print(f"   - {record['type']} at {record['timestamp'][:19]}")
    
    assert len(history) > 0, "Should have audit history"
    print("   ✅ PASS: Audit history tracking works")
    
    return True


def run_all_tests():
    """Run all tests / 运行所有测试"""
    print("\n" + "🚀 "*20)
    print("Sheriff Brain Upgrade - Component Tests")
    print("Sheriff Brain Upgrade - 组件测试")
    print("🚀 "*20)
    
    results = []
    
    try:
        results.append(("Mission Orchestrator", test_mission_orchestrator()))
    except Exception as e:
        print(f"\n❌ Mission Orchestrator test failed: {e}")
        results.append(("Mission Orchestrator", False))
    
    try:
        results.append(("Local Reasoning Engine", test_local_reasoning_engine()))
    except Exception as e:
        print(f"\n❌ Local Reasoning Engine test failed: {e}")
        results.append(("Local Reasoning Engine", False))
    
    try:
        results.append(("Sheriff Strategist", test_sheriff_strategist()))
    except Exception as e:
        print(f"\n❌ Sheriff Strategist test failed: {e}")
        results.append(("Sheriff Strategist", False))
    
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
        print("\n🎉 All tests passed! Sheriff Brain components are ready!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)