
import sys
from pathlib import Path
sys.path.insert(0, r"d:\桌面\AGENT")

from antigravity.core.mission_orchestrator import MissionOrchestrator, AtomicTask, TaskState

# Init
print("Instantiating Orchestrator...")
orch = MissionOrchestrator(project_root=r"d:\桌面\AGENT")
print(f"Orchestrator Type: {type(orch)}")
print(f"Orchestrator Dir: {dir(orch)}")

# Create Task
task = AtomicTask(
    task_id="task_chronos_01", 
    goal="Simulate Universe Expansion",
    metadata={
        "file_path": r"d:\桌面\AGENT\universe.py",
        "content": "def expand():\n    return 'infinitely'"
    }
)
task.state = TaskState.ANALYZING

orch.current_task = task
orch.tasks.append(task)

print("\n🧪 Chronos Demonstration Started")

# TEST CASE 1: Valid Prediction
print("\n🔄 [TestCase 1] Valid Prediction...")
task1 = AtomicTask(
    task_id="task_chronos_valid",
    goal="Simulate Universe Expansion",
    metadata={
        'file_path': 'universe.py',
        'content': 'def expand():\n    return "Big Bang 2.0"'
    }
)
orch.tasks.append(task1)
orch.current_task = task1
task1.state = TaskState.PENDING

# Run through states
while task1.state != TaskState.EXECUTING and task1.state != TaskState.HEALING:
    orch.step()
    
# TEST CASE 2: Malicious Prediction (Consensus Failure)
print("\n🔄 [TestCase 2] Malicious Prediction (Consensus Failure)...")
task2 = AtomicTask(
    task_id="task_chronos_malicious",
    goal="Inject Malicious Code",
    metadata={
        'file_path': 'virus.py',
        'content': 'def virus():\n    return "Syntax Error" (' # INVALID SYNTAX
    }
)
orch.tasks.append(task2)
orch.current_task = task2
task2.state = TaskState.PENDING

# Run through states
steps = 0
while task2.state != TaskState.EXECUTING and task2.state != TaskState.HEALING and steps < 10:
    orch.step()
    steps += 1
    
print("\n✅ Chronos Demo Complete.")
