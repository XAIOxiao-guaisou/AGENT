"""
Antigravity 性能监控器
Performance Monitor

功能 / Features:
- 执行时间追踪 / Execution time tracking
- 性能指标收集 / Performance metrics collection
- 装饰器模式 / Decorator pattern
- 报告生成 / Report generation
"""

import time
import json
from functools import wraps
from typing import Dict, List, Callable
from datetime import datetime


class PerformanceMonitor:
    """
    性能监控器
    Performance Monitor
    
    追踪关键函数的执行时间和性能指标
    Track execution time and performance metrics of key functions
    """
    
    def __init__(self, project_root: str = None):
        """
        Initialize Performance Monitor
        
        Args:
            project_root: Optional project root path for project-scoped monitoring
        """
        self.project_root = project_root
        self.metrics = {}  # {operation_name: [durations]}
        self.call_counts = {}  # {operation_name: count}
        self.last_execution = {}  # {operation_name: timestamp}
    
    def measure(self, operation_name: str):
        """
        装饰器: 测量函数执行时间
        Decorator: Measure function execution time
        
        Usage:
            @perf_monitor.measure("my_operation")
            def my_function():
                pass
        
        Args:
            operation_name: 操作名称 (用于标识)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    
                    # 记录成功执行
                    self._record_metric(operation_name, duration, success=True)
                    
                    # 打印执行时间
                    print(f"⏱️ {operation_name}: {duration:.2f}s")
                    
                    return result
                
                except Exception as e:
                    duration = time.time() - start
                    
                    # 记录失败执行
                    self._record_metric(operation_name, duration, success=False)
                    
                    print(f"⏱️ {operation_name}: {duration:.2f}s (FAILED)")
                    raise e
            
            return wrapper
        return decorator
    
    def _record_metric(self, operation_name: str, duration: float, success: bool = True):
        """记录性能指标"""
        # 记录执行时间
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        
        self.metrics[operation_name].append({
            "duration": duration,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # 记录调用次数
        if operation_name not in self.call_counts:
            self.call_counts[operation_name] = 0
        self.call_counts[operation_name] += 1
        
        # 记录最后执行时间
        self.last_execution[operation_name] = datetime.now().isoformat()
    
    def get_stats(self, operation_name: str = None) -> Dict:
        """
        获取性能统计
        Get performance statistics
        
        Args:
            operation_name: 如果指定,只返回该操作的统计;否则返回所有
        
        Returns:
            统计字典
        """
        if operation_name:
            return self._compute_stats(operation_name)
        
        # 返回所有操作的统计
        all_stats = {}
        for op_name in self.metrics.keys():
            all_stats[op_name] = self._compute_stats(op_name)
        
        return all_stats
    
    def _compute_stats(self, operation_name: str) -> Dict:
        """计算单个操作的统计信息"""
        if operation_name not in self.metrics:
            return {}
        
        records = self.metrics[operation_name]
        durations = [r["duration"] for r in records]
        successes = [r for r in records if r["success"]]
        failures = [r for r in records if not r["success"]]
        
        if not durations:
            return {}
        
        return {
            "operation": operation_name,
            "call_count": len(records),
            "success_count": len(successes),
            "failure_count": len(failures),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "min_time": min(durations),
            "max_time": max(durations),
            "last_execution": self.last_execution.get(operation_name),
            "success_rate": len(successes) / len(records) * 100 if records else 0
        }
    
    def report(self, top_n: int = None) -> str:
        """
        生成性能报告
        Generate performance report
        
        Args:
            top_n: 只显示耗时最多的 N 个操作
        
        Returns:
            格式化的报告字符串
        """
        all_stats = self.get_stats()
        
        if not all_stats:
            return "📊 No performance data collected yet."
        
        # 按总耗时排序
        sorted_stats = sorted(
            all_stats.items(),
            key=lambda x: x[1].get("total_time", 0),
            reverse=True
        )
        
        if top_n:
            sorted_stats = sorted_stats[:top_n]
        
        # 生成报告
        lines = ["📊 Performance Report", "=" * 80]
        
        for op_name, stats in sorted_stats:
            lines.append(f"\n🔹 {op_name}")
            lines.append(f"   Calls: {stats['call_count']} | Success: {stats['success_count']} | Failed: {stats['failure_count']}")
            lines.append(f"   Total: {stats['total_time']:.2f}s | Avg: {stats['avg_time']:.2f}s | Min: {stats['min_time']:.2f}s | Max: {stats['max_time']:.2f}s")
            lines.append(f"   Success Rate: {stats['success_rate']:.1f}%")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)
    
    def export_report(self, filename: str = "performance_report.json"):
        """
        导出性能报告为 JSON
        Export performance report to JSON
        
        Args:
            filename: 输出文件名
        """
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "statistics": self.get_stats(),
            "raw_metrics": self.metrics
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Performance report exported to {filename}")
        return filename
    
    def reset(self):
        """重置所有性能数据"""
        self.metrics = {}
        self.call_counts = {}
        self.last_execution = {}
        print("✅ Performance monitor reset")
    
    def get_dashboard_data(self) -> Dict:
        """
        获取 Dashboard 展示数据
        Get data for Dashboard display
        
        Returns:
            适合 Dashboard 展示的数据结构
        """
        all_stats = self.get_stats()
        
        # 按平均耗时排序
        sorted_by_avg = sorted(
            all_stats.items(),
            key=lambda x: x[1].get("avg_time", 0),
            reverse=True
        )
        
        return {
            "total_operations": len(all_stats),
            "total_calls": sum(s["call_count"] for s in all_stats.values()),
            "total_time": sum(s["total_time"] for s in all_stats.values()),
            "top_slowest": [
                {
                    "operation": op,
                    "avg_time": stats["avg_time"],
                    "call_count": stats["call_count"]
                }
                for op, stats in sorted_by_avg[:5]
            ],
            "recent_executions": [
                {
                    "operation": op,
                    "last_execution": stats["last_execution"],
                    "success_rate": stats["success_rate"]
                }
                for op, stats in all_stats.items()
            ]
        }
    
    def get_summary(self) -> Dict:
        """
        Get summary of performance metrics (alias for get_dashboard_data)
        For backward compatibility with dashboard
        
        Returns:
            Performance summary dictionary
        """
        dashboard_data = self.get_dashboard_data()
        
        # Calculate average time across all operations
        all_stats = self.get_stats()
        total_time = sum(s["total_time"] for s in all_stats.values()) if all_stats else 0
        total_calls = sum(s["call_count"] for s in all_stats.values()) if all_stats else 0
        avg_time = total_time / total_calls if total_calls > 0 else 0
        
        return {
            "total_operations": dashboard_data["total_operations"],
            "total_calls": total_calls,
            "total_time": total_time,
            "average_time": avg_time,
            "slowest_operations": [
                {
                    "operation": op["operation"],
                    "avg_time": op["avg_time"],
                    "calls": op["call_count"]
                }
                for op in dashboard_data["top_slowest"]
            ]
        }
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict]:
        """
        Get recent operations for dashboard display
        
        Args:
            limit: Maximum number of operations to return
        
        Returns:
            List of recent operation dictionaries
        """
        all_stats = self.get_stats()
        
        # Sort by last execution time
        sorted_ops = sorted(
            all_stats.items(),
            key=lambda x: x[1].get("last_execution", ""),
            reverse=True
        )
        
        return [
            {
                "operation": op,
                "duration": stats["avg_time"],
                "calls": stats["call_count"],
                "success_rate": stats["success_rate"],
                "last_execution": stats["last_execution"]
            }
            for op, stats in sorted_ops[:limit]
        ]



# 全局实例
perf_monitor = PerformanceMonitor()


if __name__ == "__main__":
    # 测试性能监控器
    print("🧪 Testing Performance Monitor...")
    
    # 测试装饰器
    @perf_monitor.measure("test_operation")
    def test_function():
        time.sleep(0.1)
        return "success"
    
    @perf_monitor.measure("fast_operation")
    def fast_function():
        time.sleep(0.01)
        return "fast"
    
    # 执行测试
    for i in range(5):
        test_function()
    
    for i in range(10):
        fast_function()
    
    # 打印报告
    print("\n" + perf_monitor.report())
    
    # 导出报告
    perf_monitor.export_report()
    
    # 获取 Dashboard 数据
    dashboard_data = perf_monitor.get_dashboard_data()
    print(f"\n📊 Dashboard Data:")
    print(f"  Total operations: {dashboard_data['total_operations']}")
    print(f"  Total calls: {dashboard_data['total_calls']}")
    print(f"  Total time: {dashboard_data['total_time']:.2f}s")
    
    print("\n✅ Test complete!")
