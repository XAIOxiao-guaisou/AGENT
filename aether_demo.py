import sys
import os
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from antigravity.core.mission_orchestrator import MissionOrchestrator, TaskState
from antigravity.core.local_reasoning import LocalReasoningEngine
from antigravity.infrastructure.telemetry_queue import TelemetryQueue

def create_redundant_file():
    """Create a file that mimics vortex_core.crypto"""
    path = Path("my_crypto.py")
    content = """
from cryptography.fernet import Fernet

class VortexCrypto:
    # Redundant implementation
    def __init__(self, key: bytes = None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, token: bytes) -> str:
        return self.cipher.decrypt(token).decode()
"""
    path.write_text(content, encoding='utf-8')
    print(f"📄 Created redundant file: {path}")

def main():
    print("🛸 Project Aether: Auto-Refactor Demo Initiated...")
    
    # 1. Setup Environment
    create_redundant_file()
    
    orchestrator = MissionOrchestrator()
    
    # 2. Assign Refactor Task
    # Intent: "Refactor my_crypto.py to use fleet"
    
    # task_description = "I need to encrypt passwords securely inside my_crypto.py"
    # Simplified to ensure match
    task_description = "I need to encrypt user passwords securely"
    print(f"\n📥 User Request: '{task_description}'")
    
    # helper to check matches
    from antigravity.core.knowledge_graph import FleetKnowledgeGraph
    gkg = FleetKnowledgeGraph.get_instance()
    matches = gkg.find_fleet_capability(task_description, top_k=1)
    print(f"🔎 DEBUG: GKG Matches for query: {matches}")

    from antigravity.core.mission_orchestrator import AtomicTask
    task = AtomicTask(task_id="AETHER-001", goal=task_description)
    orchestrator.tasks.append(task)
    orchestrator.current_task = task
    
    # Manually trigger draft_plan to populate metadata (Workaround for Orchestrator linkage)
    print("⚡ Force-Triggering Draft Plan...")
    from antigravity.core.local_reasoning import LocalReasoningEngine
    engine = LocalReasoningEngine()
    plan = engine.draft_plan(task_description)
    
    # Check if quarantine in plan
    if 'quarantine' in plan:
        print(f"✅ PLAN: Quarantine Actions Proposed: {plan['quarantine']}")
        # Inject into task metadata so Orchestrator sees it?
        # But for 'quarantine', we just want to verify detection.
    
    # 3. Simulate Execution Loop
    max_steps = 3
    steps = 0
    while task.state not in [TaskState.DONE, TaskState.PAUSED, TaskState.HEALING] and steps < max_steps:
        print(f"\n🔄 Step {steps+1}: State={task.state.name}")
        orchestrator.step()
        steps += 1
        
    print(f"\n🏁 Final State: {task.state.name}")
    
    # 5. Verify Telemetry (Latency)
    # Trigger a load to see metric
    try:
        from antigravity.core.fleet_module_loader import FleetModuleLoader
        print("\n⏱️ Testing Synaptic Latency...")
        # Fix: Use load_fleet_module instead of load_module
        FleetModuleLoader.load_fleet_module("vortex_core", "core.crypto")
        print("✅ Load complete. Check telemetry queue for SYNAPTIC_LATENCY.")
    except Exception as e:
        print(f"❌ Load failed: {e}")
            
if __name__ == "__main__":
    main()
