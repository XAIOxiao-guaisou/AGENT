"""
Debug Monitor Module / 调试监控模块
====================================

A comprehensive error tracking and analysis system for development phase.
开发阶段的综合错误追踪和分析系统。

Features / 功能:
- Automatic error capture / 自动错误捕获
- Pattern analysis / 模式分析
- Real-time alerts / 实时告警
- Independent design / 独立设计

Usage / 使用方法:
    from antigravity.debug_monitor import enable_monitoring
    enable_monitoring()
"""

from .error_tracker import ErrorTracker, monitor, track
from .alert_manager import AlertManager
from .storage import ErrorStorage

__version__ = "1.0.0"
__all__ = [
    "ErrorTracker",
    "AlertManager", 
    "ErrorStorage",
    "monitor",
    "track",
    "enable_monitoring"
]

# Global instances / 全局实例
_tracker = None
_alert_manager = None

def enable_monitoring():
    """
    Enable global error monitoring / 启用全局错误监控
    
    This installs a global exception handler that captures all errors.
    这会安装一个全局异常处理器来捕获所有错误。
    """
    global _tracker, _alert_manager
    
    if _tracker is None:
        _tracker = ErrorTracker()
        _alert_manager = AlertManager()
        _tracker.install_global_handler()
        
    return _tracker

def get_tracker():
    """Get the global error tracker / 获取全局错误追踪器"""
    return _tracker

def get_alert_manager():
    """Get the global alert manager / 获取全局告警管理器"""
    return _alert_manager
