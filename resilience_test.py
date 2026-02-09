
import sys
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

# Ensure we can import antigravity
sys.path.insert(0, os.getcwd())

from antigravity.core.mission_orchestrator import MissionOrchestrator, AtomicTask, TaskState
from antigravity.core.local_reasoning import LocalReasoningEngine
import json

def test_stateless_resume():
    print("🛡️ TESTING ZERO-POINT RESILIENCE (Phase 21)...")
    
    # 0. Clean prior checkpoints
    checkpoint_dir = Path(".antigravity/checkpoints")
    if checkpoint_dir.exists():
        shutil.rmtree(checkpoint_dir)
    
    # 1. Setup Initial Orchestrator & Task
    print("\n[Phase 1] Initializing Task & Crash Simulation...")
    orch1 = MissionOrchestrator(os.getcwd())
    
    task = AtomicTask(
        task_id="RESILIENCE_TASK_001",
        goal="Test Persistence",
        state=TaskState.PREDICTING, 
        metadata={
            "file_path": "d:/simulated/test.py",
            "content": "print('Hello Persistence')"
        }
    )
    orch1.current_task = task
    
    # Mock Voting because we want to test Checkpoint, not Vote logic again
    # But checkpoint happens INSIDE step(), right before vote.
    # So we call _checkpoint_state directly to simulate "Saving at Zero Point"
    orch1._checkpoint_state(task)
    
    # Simulate CRASH (Just delete orch1 memory)
    del orch1
    print("💥 PROCESS CRASH SIMULATED (Memory Wiper)")
    
    # 2. Resurrection
    print("\n[Phase 2] System Restart & Auto-Recovery...")
    orch2 = MissionOrchestrator(os.getcwd())
    
    # 3. Verify
    found = False
    for t in orch2.tasks:
        if t.task_id == "RESILIENCE_TASK_001":
            print(f"✅ FOUND: Task {t.task_id} recovered in state {t.state}")
            found = True
            
            # Check content integrity
            if t.metadata.get('content') == "print('Hello Persistence')":
                 print("✅ INTEGRITY: Metadata preserved.")
            else:
                 print("❌ INTEGRITY: Metadata corrupted!")
                 sys.exit(1)
            break
            
    if not found:
        print("❌ FAILED: Task was not recovered from checkpoint.")
        sys.exit(1)
        
    print("\n✅ SUCCESS: Zero-Point Resilience Verified.")

if __name__ == "__main__":
    test_stateless_resume()
