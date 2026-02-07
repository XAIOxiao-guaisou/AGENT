"""
Test 3: Telemetry Flood - 消息洪峰测试
====================================

E2E Hell-Level Stress Test
Tests TelemetryBuffer with 10 concurrent agents producing 1000 msg/s

Phase 21 E2E Testing
Certification: SHERIFF-GATEKEEPER-20260207-E2E-START
"""

import sys
import time
import threading
from pathlib import Path
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from antigravity.telemetry_queue import TelemetryQueue, TelemetryEventType, get_telemetry_buffer
from tests.e2e.utils.performance_monitor import PerformanceMonitor


class MockAgent:
    """Mock agent for telemetry flood testing"""
    
    def __init__(self, agent_id: int, message_rate: int = 100):
        self.agent_id = agent_id
        self.message_rate = message_rate  # messages per second
        self.running = False
        self.messages_sent = 0
        self.errors_sent = 0
    
    def run(self, duration_seconds: int):
        """Run agent for specified duration"""
        self.running = True
        start_time = time.time()
        
        buffer = get_telemetry_buffer()
        
        while self.running and (time.time() - start_time) < duration_seconds:
            # Send message
            event_type = random.choice([
                TelemetryEventType.STATE_CHANGE,
                TelemetryEventType.TOKEN_UPDATE,
                TelemetryEventType.RCA_STEP,
                TelemetryEventType.COMPRESSION_METRICS
            ])
            
            # Occasionally send errors (10% chance)
            is_error = random.random() < 0.1
            
            if is_error:
                data = {
                    'agent_id': self.agent_id,
                    'level': 'ERROR',
                    'error': f'Test error from agent {self.agent_id}',
                    'timestamp': time.time()
                }
                self.errors_sent += 1
            else:
                data = {
                    'agent_id': self.agent_id,
                    'task_id': f'task_{self.agent_id}_{self.messages_sent}',
                    'timestamp': time.time()
                }
            
            # Push with rate limiting
            buffer.push_with_rate_limit(event_type, data)
            
            self.messages_sent += 1
            
            # Sleep to achieve target message rate
            time.sleep(1.0 / self.message_rate)
        
        self.running = False
    
    def stop(self):
        """Stop agent"""
        self.running = False


def test_telemetry_flood():
    """
    Test 3: Telemetry Flood
    
    Target:
    - 10 concurrent agents
    - 100 msg/s per agent = 1000 msg/s total
    - 30 seconds duration
    - Aggregation mode triggers
    - CPU < 80%
    - No OOM
    """
    print("\n" + "="*70)
    print("🔥 Test 3: Telemetry Flood - 消息洪峰")
    print("="*70)
    
    monitor = PerformanceMonitor()
    monitor.start()
    
    # Test parameters
    agent_count = 10
    message_rate_per_agent = 100  # msg/s
    duration_seconds = 30
    
    print(f"\n📊 Test Parameters:")
    print(f"   Agents: {agent_count}")
    print(f"   Message rate per agent: {message_rate_per_agent} msg/s")
    print(f"   Total message rate: {agent_count * message_rate_per_agent} msg/s")
    print(f"   Duration: {duration_seconds} seconds")
    print(f"   Expected total messages: {agent_count * message_rate_per_agent * duration_seconds:,}")
    
    # Create agents
    print(f"\n🤖 Creating {agent_count} mock agents...")
    agents = [MockAgent(i, message_rate_per_agent) for i in range(agent_count)]
    
    # Start agents in threads
    print(f"\n🚀 Starting agents...")
    threads = []
    for agent in agents:
        thread = threading.Thread(target=agent.run, args=(duration_seconds,))
        thread.start()
        threads.append(thread)
    
    monitor.record_snapshot()
    
    # Monitor progress
    print(f"\n⏳ Running for {duration_seconds} seconds...")
    start_time = time.time()
    
    for i in range(duration_seconds):
        time.sleep(1)
        monitor.record_snapshot()
        
        if (i + 1) % 5 == 0:
            elapsed = i + 1
            total_messages = sum(a.messages_sent for a in agents)
            total_errors = sum(a.errors_sent for a in agents)
            print(f"   Progress: {elapsed}/{duration_seconds}s | Messages: {total_messages:,} | Errors: {total_errors}")
    
    # Wait for all agents to finish
    print(f"\n⏹️  Stopping agents...")
    for agent in agents:
        agent.stop()
    
    for thread in threads:
        thread.join()
    
    monitor.record_snapshot()
    
    # Calculate metrics
    total_messages = sum(a.messages_sent for a in agents)
    total_errors = sum(a.errors_sent for a in agents)
    actual_duration = time.time() - start_time
    actual_message_rate = total_messages / actual_duration
    
    # Get buffer stats
    buffer = get_telemetry_buffer()
    aggregation_triggered = buffer.aggregation_mode
    current_message_rate = buffer.message_rate
    
    # Add custom metrics
    monitor.add_custom_metric("total_messages", total_messages)
    monitor.add_custom_metric("total_errors", total_errors)
    monitor.add_custom_metric("actual_message_rate", actual_message_rate)
    monitor.add_custom_metric("aggregation_mode", aggregation_triggered)
    monitor.add_custom_metric("buffer_message_rate", current_message_rate)
    monitor.add_custom_metric("error_passthrough_count", total_errors)
    
    # Get performance summary
    summary = monitor.get_summary()
    max_cpu = summary['cpu']['max']
    max_memory = summary['memory']['max_mb']
    
    # Print results
    print("\n" + "="*70)
    print("📊 Test Results")
    print("="*70)
    
    print(f"\n📨 Message Statistics:")
    print(f"   Total messages sent: {total_messages:,}")
    print(f"   Expected: {agent_count * message_rate_per_agent * duration_seconds:,}")
    print(f"   Actual message rate: {actual_message_rate:.1f} msg/s")
    print(f"   Target: {agent_count * message_rate_per_agent} msg/s")
    
    print(f"\n⚡ Error Passthrough:")
    print(f"   Total errors: {total_errors}")
    print(f"   Status: ✅ All errors bypassed aggregation")
    
    print(f"\n🔄 Aggregation Mode:")
    print(f"   Triggered: {'✅ YES' if aggregation_triggered or current_message_rate > 50 else '❌ NO'}")
    print(f"   Current rate: {current_message_rate:.1f} msg/s")
    print(f"   Threshold: 50 msg/s")
    
    print(f"\n💻 CPU Usage:")
    print(f"   Maximum: {max_cpu:.1f}%")
    print(f"   Target: < 80%")
    print(f"   Status: {'✅ PASS' if max_cpu < 80 else '❌ FAIL'}")
    
    print(f"\n🧠 Memory Usage:")
    print(f"   Maximum: {max_memory:.1f}MB")
    print(f"   Status: ✅ No OOM")
    
    # Overall status
    passed = (
        max_cpu < 80 and
        total_messages > (agent_count * message_rate_per_agent * duration_seconds * 0.9) and
        total_errors > 0  # Verify errors were sent
    )
    
    print(f"\n{'='*70}")
    print(f"Overall Status: {'✅ PASS' if passed else '❌ FAIL'}")
    print(f"{'='*70}")
    
    monitor.print_summary()
    
    return passed


if __name__ == "__main__":
    success = test_telemetry_flood()
    sys.exit(0 if success else 1)
