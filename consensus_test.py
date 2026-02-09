
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure we can import antigravity
sys.path.insert(0, os.getcwd())

import antigravity.core.mission_orchestrator
print(f"DEBUG: Loaded MissionOrchestrator from {antigravity.core.mission_orchestrator.__file__}")

from antigravity.core.mission_orchestrator import MissionOrchestrator, AtomicTask, TaskState
from antigravity.core.local_reasoning import LocalReasoningEngine

def test_consensus_veto():
    print("🗳️ TESTING GLOBAL CONSENSUS VETO (Phase 20)...")
    
    # 1. Setup Orchestrator
    orchestrator = MissionOrchestrator()
    
    # 2. Create a "Poison Pill" Task
    task = AtomicTask(
        task_id="POISON_TASK_001",
        goal="Inject malicious code",
        state=TaskState.PREDICTING, # Start at predicting to trigger consensus
        metadata={
            "file_path": "d:/simulated/vortex_core/main.py",
            "content": "def hack():\n    print('POISON_PILL')\n    SECRET_KEY = '12345'"
        }
    )
    
    orchestrator.current_task = task
    
    # 3. Simulate Shadow Kernel Prediction (Mocking writes)
    # We mock the shadow kernel to return the poison content
    orchestrator.shadow_kernel.simulate_write = MagicMock(return_value={
        "predicted_lines": 10,
        "predicted_hash": "malicious_hash_123",
        "simulated_content": task.metadata["content"]
    })
    
    # 4. Execute Step (Should trigger Consensus Vote)
    # The step method calls consensus_voter.cast_votes
    # We expect Node B (Intent) and Node C (Security) to reject.
    
    print("\n⚡ Executing Orchestrator Step...")
    orchestrator.step()
    
    # 5. Verify Results
    voting_record = task.metadata.get('voting_record')
    if not voting_record:
        print("❌ FAILED: No voting record found!")
        sys.exit(1)
        
    print(f"\n📊 Consensus Result: {voting_record['status']}")
    print(f"   Approval Rate: {voting_record['rate']:.2f}")
    
    for v in voting_record['details']:
        icon = "✅" if v['approved'] else "❌"
        print(f"   {icon} [{v['node']}]: {v['reason']}")
        
    # Check if task was suspended (Circuit Breaker)
    # In v1.7.0 we don't have explicit SUSPENDED enum yet, but we check if we aborted.
    # If aborted, state should remain PREDICTING (or not EXECUTING)
    # And we should see the "CIRCUIT BREAKER" log in stdout (verified visually)
    
    if voting_record['status'] == 'CONSENSUS_FAILED':
        if task.state != TaskState.EXECUTING:
            print("\n✅ SUCCESS: Task was BLOCKED from Execution.")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Task proceeded to EXECUTING despite Veto!")
            sys.exit(1)
            
    else:
        print("\n❌ FAILURE: Poison Pill was APPROVED!")
        sys.exit(1)

if __name__ == "__main__":
    test_consensus_veto()
