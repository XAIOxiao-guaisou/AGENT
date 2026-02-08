"""
Telemetry Queue - 遥测队列
==========================

Phase 21 Step 3: Real-time telemetry streaming
Real-time event streaming for Cyberpunk HUD

Event Types:
- state_change: 8-State lifecycle transitions
- token_update: Token consumption updates
- rca_step: RCA immune system diagnosis steps
- memory_warning: Memory guardian warnings
- compression_metrics: Compression performance data
- ghost_task_detected: Paused task detection

Phase 21 Enhancements:
- Queue overflow handling (maxsize=100)
- LIFO cleanup for stale messages
- Non-blocking push/pull operations
"""

import multiprocessing as mp
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class TelemetryEventType(Enum):
    """Telemetry event types"""
    STATE_CHANGE = "state_change"
    TOKEN_UPDATE = "token_update"
    RCA_STEP = "rca_step"
    MEMORY_WARNING = "memory_warning"
    COMPRESSION_METRICS = "compression_metrics"
    GHOST_TASK_DETECTED = "ghost_task_detected"
    AGGREGATED_SUMMARY = "aggregated_summary"  # Phase 21 Polishing: High-frequency aggregation


@dataclass
class TelemetryEvent:
    """
    Single telemetry event
    
    Attributes:
        event_type: Type of event
        timestamp: ISO format timestamp
        data: Event-specific data
    """
    event_type: str
    timestamp: str
    data: Dict[str, Any]


class TelemetryQueue:
    """
    Real-time telemetry streaming using multiprocessing.Queue
    
    Phase 21 Enhancement: Non-blocking event streaming with overflow handling
    
    Features:
    - maxsize=100 to prevent memory bloat
    - LIFO cleanup when queue is full
    - Non-blocking push/pull operations
    
    Producers: AutonomousAuditor, RCAImmuneSystem, MemoryGuardian, ContextCompressor
    Consumer: Dashboard (Streamlit)
    """
    
    _instance: Optional[mp.Queue] = None
    _max_size = 100  # Phase 21: Prevent queue bloat
    
    @classmethod
    def get_queue(cls) -> mp.Queue:
        """
        Get singleton queue instance
        
        Phase 21 Enhancement: maxsize=100 for overflow protection
        """
        if cls._instance is None:
            cls._instance = mp.Queue(maxsize=cls._max_size)
        return cls._instance
    
    @classmethod
    def push_event(cls, event_type: TelemetryEventType, data: Dict[str, Any]):
        """
        Push telemetry event to queue
        
        Phase 21 Enhancement: LIFO cleanup when queue is full
        Ensures HUD always shows Sheriff Brain's latest "pulse"
        Phase 16: Global Sanitation
        
        Args:
            event_type: Type of telemetry event
            data: Event-specific data
        """
        # Phase 16: Global Sanitation via io_utils
        try:
            from antigravity.utils.io_utils import sanitize_for_protobuf
            sanitized_data = sanitize_for_protobuf(data)
        except ImportError:
            sanitized_data = data # Fallback if utils not available

        event = TelemetryEvent(
            event_type=event_type.value,
            timestamp=datetime.now().isoformat(),
            data=sanitized_data
        )
        
        queue = cls.get_queue()
        try:
            # Non-blocking put
            queue.put_nowait(asdict(event))
        except:
            # Queue full - drop oldest event (LIFO cleanup)
            try:
                queue.get_nowait()  # Remove oldest
                queue.put_nowait(asdict(event))  # Add newest
                logger.debug("Telemetry queue full - dropped oldest event")
            except:
                logger.warning("Failed to push telemetry event - queue operations failed")
    
    @classmethod
    def pull_event(cls, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Pull telemetry event from queue
        
        Non-blocking with timeout
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            Event dict or None if queue is empty
        """
        queue = cls.get_queue()
        try:
            return queue.get(timeout=timeout)
        except:
            return None
    
    @classmethod
    def push_state_change(cls, task_id: str, old_state: str, new_state: str):
        """
        Push state change event
        
        Args:
            task_id: Unique task identifier
            old_state: Previous state
            new_state: New state
        """
        cls.push_event(TelemetryEventType.STATE_CHANGE, {
            'task_id': task_id,
            'old_state': old_state,
            'new_state': new_state
        })
    
    @classmethod
    def push_token_update(cls, tokens_used: int, tokens_limit: int):
        """
        Push token update event
        
        Args:
            tokens_used: Current token usage
            tokens_limit: Token limit
        """
        percentage = (tokens_used / tokens_limit * 100) if tokens_limit > 0 else 0
        cls.push_event(TelemetryEventType.TOKEN_UPDATE, {
            'tokens_used': tokens_used,
            'tokens_limit': tokens_limit,
            'percentage': percentage
        })
    
    @classmethod
    def push_rca_step(cls, step_name: str, step_number: int, total_steps: int, result: str):
        """
        Push RCA diagnosis step event
        
        Args:
            step_name: Name of RCA step
            step_number: Current step number (1-4)
            total_steps: Total number of steps
            result: Step result/diagnosis
        """
        cls.push_event(TelemetryEventType.RCA_STEP, {
            'step_name': step_name,
            'step_number': step_number,
            'total_steps': total_steps,
            'result': result
        })
    
    @classmethod
    def push_compression_metrics(
        cls,
        original_size: int,
        compressed_size: int,
        compression_ratio: float,
        token_savings: int
    ):
        """
        Push compression metrics event
        
        Phase 21 Enhancement: Compression loss/gain visualization
        
        Args:
            original_size: Original context size in bytes
            compressed_size: Compressed context size in bytes
            compression_ratio: Compression ratio (0-1)
            token_savings: Estimated token savings
        """
        savings_percent = (1 - compression_ratio) * 100
        cls.push_event(TelemetryEventType.COMPRESSION_METRICS, {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'savings_percent': savings_percent,
            'token_savings': token_savings
        })
    
    @classmethod
    def push_memory_warning(cls, memory_mb: float, threshold_mb: float, level: int):
        """
        Push memory warning event
        
        Phase 21 Enhancement: Memory guardian visual feedback
        
        Args:
            memory_mb: Current memory usage in MB
            threshold_mb: Warning threshold in MB
            level: Warning level (1=80%, 2=100%)
        """
        percentage = (memory_mb / threshold_mb * 100) if threshold_mb > 0 else 0
        cls.push_event(TelemetryEventType.MEMORY_WARNING, {
            'memory_mb': memory_mb,
            'threshold_mb': threshold_mb,
            'percentage': percentage,
            'level': level
        })
    
    @classmethod
    def push_ghost_task(
        cls,
        task_id: str,
        tokens_used: int,
        completed_tasks: int,
        total_tasks: int,
        context_checksum: str,
        state: str
    ):
        """
        Push ghost task detected event
        
        Phase 21 Enhancement: Ghost task detection with checksum
        
        Args:
            task_id: Task identifier
            tokens_used: Tokens consumed so far
            completed_tasks: Number of completed tasks
            total_tasks: Total number of tasks
            context_checksum: Context checksum for verification
            state: Current task state (usually PAUSED)
        """
        cls.push_event(TelemetryEventType.GHOST_TASK_DETECTED, {
            'task_id': task_id,
            'tokens_used': tokens_used,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'context_checksum': context_checksum,
            'state': state
        })
    
    @classmethod
    def clear_queue(cls):
        """Clear all events from queue"""
        queue = cls.get_queue()
        while not queue.empty():
            try:
                queue.get_nowait()
            except:
                break
                
    @classmethod
    def flush_queue(cls) -> List[Dict[str, Any]]:
        """
        Phase 11 Tuning: Atomic Hot-Swap Support
        Drain queue and return all pending events.
        Used by FleetManager during context switch.
        """
        queue = cls.get_queue()
        events = []
        while not queue.empty():
            try:
                events.append(queue.get_nowait())
            except:
                break
        return events


class TelemetryBuffer:
    """
    Telemetry buffer with auto-aggregation
    
    Phase 21 Polishing: Prevent OOM and I/O blocking under high load
    
    Features:
    - Message rate detection (msg/s)
    - Auto-switch to aggregation mode (> 50 msg/s)
    - Summary dispatch every 500ms
    - Non-blocking operation
    
    This is a SURVIVAL LOGIC patch, not a cosmetic improvement.
    Without this, Dashboard can OOM or freeze under stress.
    """
    
    def __init__(self):
        self.message_rate = 0.0
        self.last_rate_check = time.time()
        self.message_count = 0
        self.aggregation_mode = False
        self.pending_summary = {}
        self.last_summary_dispatch = time.time()
    
    def push_with_rate_limit(self, event_type: TelemetryEventType, data: Dict[str, Any]):
        """
        Push event with rate limiting and auto-aggregation
        
        Phase 21 Polishing: Critical survival logic
        Phase 21 Pre-E2E: Error passthrough for immediate visibility
        
        Args:
            event_type: Type of telemetry event
            data: Event-specific data
        """
        # Phase 21 Pre-E2E: Error passthrough
        # Critical errors bypass aggregation for immediate visibility
        is_critical_error = self._is_critical_error(data)
        
        if is_critical_error:
            # Passthrough - send immediately, don't aggregate
            TelemetryQueue.push_event(event_type, data)
            logger.warning(f"⚠️ Critical error passthrough: {data.get('error', 'unknown')}")
            return
        
        # Update rate
        self._update_rate()
        
        # Check if should aggregate
        if self.message_rate > 50:
            if not self.aggregation_mode:
                self._enter_aggregation_mode()
        elif self.aggregation_mode and self.message_rate < 30:
            # Exit aggregation mode if rate drops
            self._exit_aggregation_mode()
        
        if self.aggregation_mode:
            self._aggregate_event(event_type, data)
            
            # Dispatch summary every 500ms
            now = time.time()
            if now - self.last_summary_dispatch >= 0.5:
                self.dispatch_summary()
                self.last_summary_dispatch = now
        else:
            TelemetryQueue.push_event(event_type, data)
    
    def _update_rate(self):
        """
        Calculate current message rate
        
        Updates message_rate in msg/s
        """
        now = time.time()
        elapsed = now - self.last_rate_check
        
        if elapsed >= 1.0:
            self.message_rate = self.message_count / elapsed
            self.message_count = 0
            self.last_rate_check = now
        
        self.message_count += 1
    
    def _enter_aggregation_mode(self):
        """
        Enter aggregation mode
        
        Phase 21 Polishing: Prevent I/O blocking
        """
        self.aggregation_mode = True
        logger.warning(
            f"⚠️ High telemetry rate ({self.message_rate:.1f} msg/s) - "
            f"entering aggregation mode to prevent OOM"
        )
    
    def _exit_aggregation_mode(self):
        """
        Exit aggregation mode
        
        Rate has dropped below threshold
        """
        self.aggregation_mode = False
        logger.info(
            f"✅ Telemetry rate normalized ({self.message_rate:.1f} msg/s) - "
            f"exiting aggregation mode"
        )
        
        # Dispatch any pending summary
        if self.pending_summary:
            self.dispatch_summary()
    
    def _aggregate_event(self, event_type: TelemetryEventType, data: Dict[str, Any]):
        """
        Aggregate events into summary
        
        Stores latest state for each event type
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Store latest state for each event type
        self.pending_summary[event_type.value] = data
    
    def _is_critical_error(self, data: Dict[str, Any]) -> bool:
        """
        Check if event contains critical error
        
        Phase 21 Pre-E2E: Error passthrough logic
        Errors must bypass aggregation for immediate visibility
        
        Args:
            data: Event data
        
        Returns:
            True if event is a critical error
        """
        # Check for error indicators
        if 'level' in data and data['level'] == 'ERROR':
            return True
        
        if 'error' in data or 'exception' in data:
            return True
        
        if 'traceback' in data or 'stack_trace' in data:
            return True
        
        # Check for failure states
        if 'status' in data and data['status'] in ['FAILED', 'ERROR', 'CRITICAL']:
            return True
        
        return False
    
    def dispatch_summary(self):
        """
        Dispatch aggregated summary
        
        Phase 21 Polishing: Send summary instead of individual events
        Called every 500ms in aggregation mode
        """
        if self.pending_summary:
            TelemetryQueue.push_event(
                TelemetryEventType.AGGREGATED_SUMMARY,
                {
                    'summary': self.pending_summary.copy(),
                    'aggregation_mode': True,
                    'message_rate': self.message_rate,
                    'event_count': len(self.pending_summary)
                }
            )
            self.pending_summary = {}


# Global buffer instance
_global_buffer: Optional[TelemetryBuffer] = None


def get_telemetry_buffer() -> TelemetryBuffer:
    """
    Get global telemetry buffer instance
    
    Phase 21 Polishing: Singleton pattern
    """
    global _global_buffer
    if _global_buffer is None:
        _global_buffer = TelemetryBuffer()
    return _global_buffer


# Example usage
if __name__ == "__main__":
    # Test telemetry queue
    print("🧪 Testing Telemetry Queue...")
    
    # Push some events
    TelemetryQueue.push_state_change("task_001", "PENDING", "ANALYZING")
    TelemetryQueue.push_token_update(5000, 20000)
    TelemetryQueue.push_compression_metrics(100000, 8000, 0.08, 15000)
    TelemetryQueue.push_memory_warning(800, 1000, 1)
    
    # Pull events
    print("\n📥 Pulling events:")
    while True:
        event = TelemetryQueue.pull_event(timeout=0.1)
        if event is None:
            break
        print(f"  - {event['event_type']}: {event['data']}")
    
    print("\n✅ Telemetry queue test complete!")
