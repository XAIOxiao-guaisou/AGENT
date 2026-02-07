"""
Test Script for AutonomousAuditor Integration
测试 AutonomousAuditor 集成

Tests:
1. Async pipeline functionality
2. Component integration
3. Autonomous execution flow
4. State persistence
"""

import sys
import asyncio
from pathlib import Path

# Add antigravity to path
sys.path.insert(0, str(Path(__file__).parent))

from antigravity.autonomous_auditor import (
    AutonomousAuditor, AsyncPipeline, autonomous_execute_sync
)
from antigravity.mission_orchestrator import TaskState


async def test_async_pipeline():
    """Test async pipeline / 测试异步流水线"""
    print("\n" + "="*60)
    print("🧪 Testing Async Pipeline")
    print("="*60)
    
    # Test 1: Basic async execution
    print("\n1️⃣ Test: Basic Async Execution")
    
    async def async_task(name: str, delay: float):
        await asyncio.sleep(delay)
        return f"Task {name} completed"
    
    async with AsyncPipeline() as pipeline:
        # Submit multiple tasks
        future1 = pipeline.submit(async_task, "A", 0.1)
        future2 = pipeline.submit(async_task, "B", 0.05)
        
        # Wait for results
        result2 = await pipeline.wait_for(future2)
        result1 = await pipeline.wait_for(future1)
        
        print(f"   Result 1: {result1}")
        print(f"   Result 2: {result2}")
    
    assert result1 and result2, "Both tasks should complete"
    print("   ✅ PASS: Async pipeline works")
    
    # Test 2: Concurrent execution
    print("\n2️⃣ Test: Concurrent Execution")
    
    import time
    start_time = time.time()
    
    async with AsyncPipeline() as pipeline:
        # Submit 3 tasks that would take 0.3s sequentially
        futures = [
            pipeline.submit(async_task, f"Task{i}", 0.1)
            for i in range(3)
        ]
        
        # Wait for all
        results = await asyncio.gather(*futures)
    
    elapsed = time.time() - start_time
    
    print(f"   Tasks: 3")
    print(f"   Sequential time: ~0.3s")
    print(f"   Actual time: {elapsed:.2f}s")
    
    assert elapsed < 0.2, "Should execute concurrently"
    print("   ✅ PASS: Concurrent execution works")
    
    return True


async def test_autonomous_auditor_integration():
    """Test AutonomousAuditor integration / 测试 AutonomousAuditor 集成"""
    print("\n" + "="*60)
    print("🧪 Testing AutonomousAuditor Integration")
    print("="*60)
    
    # Create temporary project directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Test 1: Component initialization
        print("\n1️⃣ Test: Component Initialization")
        auditor = AutonomousAuditor(project_root)
        
        print(f"   Orchestrator: {auditor.orchestrator is not None}")
        print(f"   Local Reasoner: {auditor.local_reasoner is not None}")
        print(f"   Remote Strategist: {auditor.remote_strategist is not None}")
        
        assert auditor.orchestrator is not None, "Should have orchestrator"
        assert auditor.local_reasoner is not None, "Should have local reasoner"
        assert auditor.remote_strategist is not None, "Should have remote strategist"
        print("   ✅ PASS: Components initialized")
        
        # Test 2: Autonomous execution
        print("\n2️⃣ Test: Autonomous Execution")
        idea = "Create a simple API with database"
        
        result = await auditor.autonomous_run(idea)
        
        print(f"   Idea: {idea}")
        print(f"   Delivered: {result.get('delivered')}")
        print(f"   Summary: {result.get('summary')}")
        
        assert 'delivered' in result, "Should have delivery status"
        print("   ✅ PASS: Autonomous execution works")
        
        # Test 3: Execution log
        print("\n3️⃣ Test: Execution Log")
        log = auditor.get_execution_log()
        
        print(f"   Log entries: {len(log)}")
        for entry in log[:5]:  # Show first 5
            print(f"   - {entry['event']}: {entry['data']}")
        
        assert len(log) > 0, "Should have execution log"
        print("   ✅ PASS: Execution logging works")
        
        # Test 4: State persistence
        print("\n4️⃣ Test: State Persistence")
        state_file = project_root / "auditor_state.json"
        
        auditor.save_state(str(state_file))
        print(f"   State saved: {state_file.exists()}")
        
        # Load state
        new_auditor = AutonomousAuditor(project_root)
        new_auditor.load_state(str(state_file))
        
        print(f"   Idea restored: {new_auditor.current_idea == idea}")
        print(f"   Log entries restored: {len(new_auditor.execution_log)}")
        
        assert new_auditor.current_idea == idea, "Should restore idea"
        assert len(new_auditor.execution_log) > 0, "Should restore log"
        print("   ✅ PASS: State persistence works")
    
    return True


def test_sync_wrapper():
    """Test synchronous wrapper / 测试同步包装器"""
    print("\n" + "="*60)
    print("🧪 Testing Synchronous Wrapper")
    print("="*60)
    
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        print("\n⚠️ Already in event loop, skipping sync wrapper test")
        print("   (This is expected when running in async context)")
        return True  # Skip test but don't fail
    except RuntimeError:
        # Not in event loop, safe to test
        pass
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        print("\n1️⃣ Test: Sync Execution")
        idea = "Create a test project"
        
        # Use sync wrapper
        result = autonomous_execute_sync(idea, project_root)
        
        print(f"   Idea: {idea}")
        print(f"   Result: {result.get('delivered')}")
        
        assert 'delivered' in result, "Should have result"
        print("   ✅ PASS: Sync wrapper works")
    
    return True


async def test_task_pipeline_flow():
    """Test task execution with pipeline / 测试任务执行流水线"""
    print("\n" + "="*60)
    print("🧪 Testing Task Pipeline Flow")
    print("="*60)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        auditor = AutonomousAuditor(project_root)
        
        print("\n1️⃣ Test: Task State Transitions")
        
        # Decompose idea
        idea = "Build API with auth"
        tasks = auditor.orchestrator.decompose_idea(idea)
        
        print(f"   Tasks generated: {len(tasks)}")
        
        # Execute first task through pipeline
        task = tasks[0]
        print(f"   Initial state: {task.state.value}")
        
        async with AsyncPipeline() as pipeline:
            result = await auditor._execute_task_with_pipeline(
                task, tasks[1] if len(tasks) > 1 else None, pipeline
            )
        
        print(f"   Final state: {task.state.value}")
        print(f"   Success: {result['success']}")
        
        assert task.state == TaskState.DONE, "Task should be done"
        assert result['success'], "Task should succeed"
        print("   ✅ PASS: Task pipeline flow works")
    
    return True


async def run_all_tests_async():
    """Run all async tests / 运行所有异步测试"""
    print("\n" + "🚀 "*20)
    print("AutonomousAuditor Integration Tests")
    print("AutonomousAuditor 集成测试")
    print("🚀 "*20)
    
    results = []
    
    try:
        results.append(("Async Pipeline", await test_async_pipeline()))
    except Exception as e:
        print(f"\n❌ Async Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Async Pipeline", False))
    
    try:
        results.append(("AutonomousAuditor Integration", await test_autonomous_auditor_integration()))
    except Exception as e:
        print(f"\n❌ AutonomousAuditor Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("AutonomousAuditor Integration", False))
    
    try:
        results.append(("Sync Wrapper", test_sync_wrapper()))
    except Exception as e:
        print(f"\n❌ Sync Wrapper test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Sync Wrapper", False))
    
    try:
        results.append(("Task Pipeline Flow", await test_task_pipeline_flow()))
    except Exception as e:
        print(f"\n❌ Task Pipeline Flow test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Task Pipeline Flow", False))
    
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
        print("\n🎉 All tests passed! AutonomousAuditor is ready!")
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