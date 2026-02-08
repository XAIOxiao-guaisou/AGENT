import time
import sys
import unittest
from unittest.mock import patch, MagicMock
from antigravity.core.local_reasoning import LocalReasoningEngine
from antigravity.core.fleet_module_loader import FleetModuleLoader
from antigravity.infrastructure.telemetry_queue import TelemetryQueue

def test_swarm_intelligence():
    print("\n🐝 TESTING SWARM INTELLIGENCE...")
    engine = LocalReasoningEngine()
    
    # Complex Intent
    complex_idea = "I need to scrape data from web, store it in database, and visualize it on a dashboard"
    print(f"📥 Input Idea: '{complex_idea}'")
    
    plan = engine.draft_plan(complex_idea)
    
    if plan.get('type') == 'swarm_composite':
        print("✅ SWARM ACTIVATED: Composite Plan Generated")
        for i, sub in enumerate(plan['subtasks']):
            print(f"   [{i+1}] Intent: '{sub['intent']}' -> Node: {sub['assigned_node']} (Conf: {sub['confidence']:.2f})")
    else:
        print("❌ SWARM FAILED: Normal Plan Generated")
        print(plan)

def test_synaptic_latency():
    print("\n⚡ TESTING SYNAPTIC LATENCY THRESHOLDS...")
    
    # Robust Mock for time.perf_counter
    # Ensures sufficient delay regardless of call count
    perf_counter_mock = MagicMock()
    perf_counter_mock.side_effect = [100.0, 100.5, 101.0, 101.5, 102.0] # Ensure at least 0.5s diff between first two calls if used sequentially
    
    # Alternative: use a generator
    def time_gen():
        t = 100.0
        while True:
            yield t
            t += 0.5
            
    with patch('time.perf_counter', side_effect=time_gen()):
        # Mock importlib to avoid actual loading
        with patch('importlib.util.spec_from_file_location') as mock_spec:
            mock_spec.return_value = MagicMock()
            
            # Use FleetModuleLoader
            loader = FleetModuleLoader()
            try:
                # Mock finding the module logic via FleetManager
                # Since we cannot easily mock logic inside static method efficiently without complex setup,
                # let's try to mock ProjectFleetManager.get_instance().projects
                from antigravity.core.fleet_manager import ProjectFleetManager, ProjectMetadata
                
                # Ensure vortex_core exists in FleetManager
                fleet_mgr = ProjectFleetManager.get_instance()
                if 'vortex_core' not in fleet_mgr.projects:
                    # Inject dummy
                    fleet_mgr.projects['vortex_core'] = ProjectMetadata(
                        project_id='vortex_core',
                        path='d:/simulated/vortex_core',
                        name='Vortex Core',
                        status='ACTIVE',
                        last_active='2026-01-01',
                        vibe_score=100
                    )

                # Disable DeliveryGate for this test
                import antigravity.core.fleet_module_loader as fml
                original_gate = fml.DeliveryGate
                fml.DeliveryGate = None
                
                # Mock Path.exists to return True
                with patch('pathlib.Path.exists', return_value=True):
                    loader.load_fleet_module("vortex_core", "main")
                
                fml.DeliveryGate = original_gate
            except Exception as e:
                print(f"⚠️ Load Failed [Expected or Unexpected]: {e}")
                import traceback
                traceback.print_exc()
                
    # Check Telemetry for SYNAPTIC_DRAG
    found_drag = False
    print("   Inspection Telemetry Queue...")
    while True:
        event_dict = TelemetryQueue.pull_event(timeout=0.2)
        if event_dict is None:
            break
            
        data = event_dict['data']
        # Check for PERFORMANCE_KNOB / SYNAPTIC_DRAG
        if event_dict['event_type'] == 'performance_knob' and data.get('event') == 'SYNAPTIC_DRAG':
            print(f"✅ SYNAPTIC DRAG DETECTED: {data['latency_ms']:.2f}ms > 300ms")
            print(f"   Suggestion: {data['suggestion']}")
            found_drag = True
            break
            
    if not found_drag:
        print("❌ LATENCY CHECK FAILED: No warning generated.")

if __name__ == "__main__":
    test_swarm_intelligence()
    test_synaptic_latency()
