"""
Performance Monitor - 性能监控器
================================

E2E Hell-Level Testing Utility
Monitors CPU, memory, and execution time during stress tests

Phase 21 E2E Testing
"""

import time
import psutil
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    execution_time_ms: float


class PerformanceMonitor:
    """
    Performance monitoring utility for E2E tests
    
    Tracks:
    - CPU usage
    - Memory usage
    - Execution time
    - Custom metrics
    """
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.metrics: List[PerformanceMetrics] = []
        self.custom_metrics: Dict[str, Any] = {}
    
    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        self.metrics = []
        self.custom_metrics = {}
    
    def record_snapshot(self):
        """Record current performance snapshot"""
        if self.start_time is None:
            return
        
        elapsed = (time.time() - self.start_time) * 1000  # ms
        
        snapshot = PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=self.process.cpu_percent(),
            memory_mb=self.process.memory_info().rss / 1024 / 1024,
            memory_percent=self.process.memory_percent(),
            execution_time_ms=elapsed
        )
        
        self.metrics.append(snapshot)
    
    def add_custom_metric(self, name: str, value: Any):
        """Add custom metric"""
        self.custom_metrics[name] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics]
        memory_values = [m.memory_mb for m in self.metrics]
        
        return {
            'total_time_ms': self.metrics[-1].execution_time_ms if self.metrics else 0,
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg_mb': sum(memory_values) / len(memory_values),
                'max_mb': max(memory_values),
                'min_mb': min(memory_values)
            },
            'custom_metrics': self.custom_metrics,
            'snapshots_count': len(self.metrics)
        }
    
    def print_summary(self):
        """Print performance summary"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 Performance Summary")
        print("="*60)
        
        print(f"\n⏱️  Total Time: {summary['total_time_ms']:.2f}ms")
        
        print(f"\n💻 CPU Usage:")
        print(f"   Average: {summary['cpu']['avg']:.1f}%")
        print(f"   Maximum: {summary['cpu']['max']:.1f}%")
        print(f"   Minimum: {summary['cpu']['min']:.1f}%")
        
        print(f"\n🧠 Memory Usage:")
        print(f"   Average: {summary['memory']['avg_mb']:.1f}MB")
        print(f"   Maximum: {summary['memory']['max_mb']:.1f}MB")
        print(f"   Minimum: {summary['memory']['min_mb']:.1f}MB")
        
        if summary['custom_metrics']:
            print(f"\n📈 Custom Metrics:")
            for name, value in summary['custom_metrics'].items():
                print(f"   {name}: {value}")
        
        print("\n" + "="*60)
    
    def save_report(self, filepath: str):
        """Save performance report to JSON"""
        summary = self.get_summary()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Report saved to: {filepath}")


# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.start()
    
    # Simulate some work
    for i in range(10):
        time.sleep(0.1)
        monitor.record_snapshot()
    
    monitor.add_custom_metric("test_iterations", 10)
    monitor.print_summary()
