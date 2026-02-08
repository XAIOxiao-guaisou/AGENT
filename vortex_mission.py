
import os
import sys
import time
import logging
from pathlib import Path

# Setup Project Root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Adjust imports to match project structure
try:
    from antigravity.core.mission_orchestrator import MissionOrchestrator, TaskState
except ImportError:
    # Minimal mock for imports if not fully resolved
    # But in this environment they should be
    pass

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ProjectVortex")

def main():
    print("""
    =======================================================
       PROJECT VORTEX: AUTONOMOUS MISSION LAUNCH
       v1.1.0 Deep Tuning Verification
    =======================================================
    """)
    
    orchestrator = MissionOrchestrator(project_root=str(PROJECT_ROOT))
    
    # 1. Define the Mission Idea
    # "Build an async web scraper that saves to SQLite and handles errors"
    # Deliberately complex to force multiple component creations
    mission_idea = """
    Create a robust asynchronous web scraper system.
    It should have:
    1. A `ScraperEngine` using `httpx` (missing dependency test!) to fetch pages.
    2. A `DataParser` using `BeautifulSoup` to extract titles and links.
    3. A `StorageManager` using `sqlite3` to save results.
    4. A `MainController` to coordinate them.
    5. Handle network errors with retries.
    """
    
    # Mocking decompose_idea since we don't have a real LLM here to generate tasks dynamically
    # We will manually seed tasks to simulate the decomposition result
    from antigravity.core.mission_orchestrator import AtomicTask
    
    print(f"🧠 Decomposing Mission: {mission_idea.strip().splitlines()[0]}...")
    
    # Manually creating tasks to simulate decomposition for this test run
    tasks = [
        AtomicTask(task_id="task_001", goal="Check environment & install dependencies (httpx)", files_affected=["requirements.txt"], dependencies=[], metadata={'component_type': 'setup'}),
        AtomicTask(task_id="task_002", goal="Create ScraperEngine with httpx", files_affected=["scraper_engine.py"], dependencies=[], metadata={'component_type': 'scraper'}),
        AtomicTask(task_id="task_003", goal="Create DataParser with BeautifulSoup", files_affected=["data_parser.py"], dependencies=[], metadata={'component_type': 'parser'}),
        AtomicTask(task_id="task_004", goal="Create StorageManager with SQLite", files_affected=["storage_manager.py"], dependencies=[], metadata={'component_type': 'storage'}),
        AtomicTask(task_id="task_005", goal="Create MainController to link components", files_affected=["main_controller.py"], dependencies=["scraper", "parser", "storage"], metadata={'component_type': 'controller'})
    ]
    orchestrator.tasks = tasks
    
    print(f"📋 Generated {len(tasks)} Atomic Tasks:")
    for t in tasks:
        print(f"   - [{t.task_id}] {t.goal}")
        
    # 3. Execution Loop
    print("\n🚀 Initiating Mission Execution...\n")
    
    completed = False
    max_steps = 20
    step = 0
    
    # Ensure current task is set
    orchestrator.current_task = tasks[0]
    
    while not completed and step < max_steps:
        # Check overall status
        pending = [t for t in tasks if t.state != TaskState.DONE]
        if not pending:
            print("\n✅ MISSION ACCOMPLISHED: All tasks complete.")
            completed = True
            break
            
        current_task = orchestrator.current_task
        
        # Advance to next task if current is done
        if current_task and current_task.state == TaskState.DONE:
             # Simple logic: find next PENDING task
             next_task = next((t for t in tasks if t.state == TaskState.PENDING), None)
             if next_task:
                 orchestrator.current_task = next_task
                 current_task = next_task
             else:
                 break

        if current_task:
            print(f"▶️ [STEP {step+1}] Processing: {current_task.task_id} ({current_task.state.value})")
            
            # SIMULATE TAMPERING at Step 3
            if step == 3:
                 print("\n😈 SIMULATING ATTACK: Tampering with 'antigravity/utils/io_utils.py'...")
                 target = PROJECT_ROOT / 'antigravity/utils/io_utils.py'
                 if target.exists():
                     with open(target, 'a', encoding='utf-8') as f:
                         f.write("\n# TAMPERED\n")
                     print("   Tampering complete. DeliveryGate should detect this on next hash check.\n")

            # Orchestrate Step
            # Simulate state progression for the test without real code generation
            # We want to verify state transitions and healing triggers
            
            # Start -> Strategy Review
            if current_task.state == TaskState.PENDING:
                current_task.state = TaskState.STRATEGY_REVIEW
                print(f"   Status: pending -> {current_task.state.value}")
                
            # Strategy Review -> Executing (triggers health check!)
            elif current_task.state == TaskState.STRATEGY_REVIEW:
                new_state = orchestrator.step(current_task) # Should run health check
                print(f"   Status: strategy_review -> {new_state.value}")
                
                # If stuck in healing, simulate fix
                if new_state == TaskState.HEALING:
                    print("   (Test Overlay) Simulating manual environment fix...")
                    # Mock fix
                    pass
            
            # Executing -> Done
            elif current_task.state == TaskState.EXECUTING:
                current_task.state = TaskState.DONE
                print(f"   Status: executing -> {current_task.state.value}")
                print(f"   Task {current_task.task_id} Completed.")
                
            # Healing -> Executing
            elif current_task.state == TaskState.HEALING:
                new_state = orchestrator.step(current_task)
                print(f"   Status: healing -> {new_state.value}")

        step += 1
        time.sleep(1)
        
    if not completed:
        print("\n⚠️ Mission timed out or stalled.")
        
    print("\n🏁 Project Vortex Execution Finished.")

if __name__ == "__main__":
    main()
