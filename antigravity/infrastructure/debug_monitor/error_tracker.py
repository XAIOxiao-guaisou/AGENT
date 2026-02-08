"""
Error Tracker Module / 错误追踪模块
==================================

Captures and enriches error information with full context.
捕获并丰富带有完整上下文的错误信息。
"""

import sys
import traceback
import inspect
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import json

from .storage import ErrorStorage


class ErrorTracker:
    """
    Error tracking manager / 错误追踪管理器
    
    Provides decorator and context manager for automatic error capture.
    提供装饰器和上下文管理器用于自动错误捕获。
    """
    
    def __init__(self, config_path: str = "antigravity/debug_monitor/config.json"):
        """
        Initialize error tracker / 初始化错误追踪器
        
        Args:
            config_path: Path to configuration file / 配置文件路径
        """
        # Load configuration / 加载配置
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except Exception:
            # Default configuration / 默认配置
            self.config = {
                "enabled": True,
                "storage_path": "debug_logs/",
                "privacy_settings": {
                    "exclude_vars": ["password", "token", "secret", "api_key"],
                    "max_var_length": 200
                },
                "performance_settings": {
                    "max_stack_depth": 10,
                    "capture_locals": True
                }
            }
        
        # Initialize storage / 初始化存储
        self.storage = ErrorStorage(self.config.get("storage_path", "debug_logs/"))
        
        # Session ID for tracking / 用于追踪的会话 ID
        import uuid
        self.session_id = str(uuid.uuid4())[:8]
    
    def capture_error(
        self,
        exc_type: type,
        exc_value: Exception,
        exc_traceback,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Capture error with full context / 捕获带有完整上下文的错误
        
        Args:
            exc_type: Exception type / 异常类型
            exc_value: Exception instance / 异常实例
            exc_traceback: Traceback object / 回溯对象
            context: Additional context / 额外上下文
            
        Returns:
            Error ID / 错误 ID
        """
        if not self.config.get("enabled", True):
            return ""
        
        # Extract stack trace / 提取堆栈跟踪
        stack_trace = self._extract_stack_trace(exc_traceback)
        
        # Get error location / 获取错误位置
        tb = traceback.extract_tb(exc_traceback)
        if tb:
            last_frame = tb[-1]
            file_path = last_frame.filename
            line_number = last_frame.lineno
            function_name = last_frame.name
        else:
            file_path = "unknown"
            line_number = 0
            function_name = "unknown"
        
        # Capture local variables / 捕获局部变量
        local_vars = {}
        if self.config.get("performance_settings", {}).get("capture_locals", True):
            local_vars = self._capture_locals(exc_traceback)
        
        # Determine severity / 确定严重性
        severity = self._determine_severity(exc_type)
        
        # Build error data / 构建错误数据
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "error_type": exc_type.__name__,
            "message": str(exc_value),
            "message_zh": self._translate_error_message(exc_type.__name__, str(exc_value)),
            "file": file_path,
            "line": line_number,
            "function": function_name,
            "stack_trace": stack_trace,
            "local_vars": local_vars,
            "severity": severity,
            "context": context or {}
        }
        
        # Save error / 保存错误
        error_id = self.storage.save_error(error_data)
        
        return error_id
    
    def _extract_stack_trace(self, exc_traceback) -> str:
        """
        Extract formatted stack trace / 提取格式化的堆栈跟踪
        
        Args:
            exc_traceback: Traceback object / 回溯对象
            
        Returns:
            Formatted stack trace / 格式化的堆栈跟踪
        """
        max_depth = self.config.get("performance_settings", {}).get("max_stack_depth", 10)
        
        tb_lines = traceback.format_tb(exc_traceback, limit=max_depth)
        return "".join(tb_lines)
    
    def _capture_locals(self, exc_traceback) -> Dict[str, str]:
        """
        Capture local variables from traceback / 从回溯中捕获局部变量
        
        Args:
            exc_traceback: Traceback object / 回溯对象
            
        Returns:
            Dictionary of local variables / 局部变量字典
        """
        local_vars = {}
        exclude_vars = self.config.get("privacy_settings", {}).get("exclude_vars", [])
        max_length = self.config.get("privacy_settings", {}).get("max_var_length", 200)
        
        if exc_traceback and hasattr(exc_traceback, 'tb_frame'):
            frame = exc_traceback.tb_frame
            for var_name, var_value in frame.f_locals.items():
                # Skip excluded variables / 跳过排除的变量
                if any(excluded in var_name.lower() for excluded in exclude_vars):
                    local_vars[var_name] = "<REDACTED>"
                    continue
                
                # Safely convert to string / 安全地转换为字符串
                try:
                    value_str = repr(var_value)
                    if len(value_str) > max_length:
                        value_str = value_str[:max_length] + "..."
                    local_vars[var_name] = value_str
                except Exception:
                    local_vars[var_name] = "<UNABLE_TO_SERIALIZE>"
        
        return local_vars
    
    def _determine_severity(self, exc_type: type) -> str:
        """
        Determine error severity / 确定错误严重性
        
        Args:
            exc_type: Exception type / 异常类型
            
        Returns:
            Severity level / 严重性级别
        """
        critical_errors = [SystemExit, KeyboardInterrupt, MemoryError]
        error_errors = [AttributeError, NameError, TypeError, ValueError, KeyError]
        
        if exc_type in critical_errors:
            return "CRITICAL"
        elif exc_type in error_errors:
            return "ERROR"
        elif issubclass(exc_type, Warning):
            return "WARNING"
        else:
            return "INFO"
    
    def _translate_error_message(self, error_type: str, message: str) -> str:
        """
        Translate error message to Chinese / 将错误消息翻译为中文
        
        Args:
            error_type: Error type / 错误类型
            message: Error message / 错误消息
            
        Returns:
            Translated message / 翻译后的消息
        """
        # Common error translations / 常见错误翻译
        translations = {
            "NameError": "名称错误",
            "TypeError": "类型错误",
            "ValueError": "值错误",
            "KeyError": "键错误",
            "AttributeError": "属性错误",
            "IndexError": "索引错误",
            "ImportError": "导入错误",
            "SyntaxError": "语法错误"
        }
        
        error_type_zh = translations.get(error_type, error_type)
        
        # Try to translate common patterns / 尝试翻译常见模式
        if "is not defined" in message:
            var_name = message.split("'")[1] if "'" in message else "unknown"
            return f"{error_type_zh}: 变量 '{var_name}' 未定义"
        elif "has no attribute" in message:
            return f"{error_type_zh}: 对象没有该属性"
        elif "missing" in message and "required" in message:
            return f"{error_type_zh}: 缺少必需的参数"
        else:
            return f"{error_type_zh}: {message}"
    
    def install_global_handler(self):
        """
        Install global exception handler / 安装全局异常处理器
        
        This captures all unhandled exceptions.
        这会捕获所有未处理的异常。
        """
        original_excepthook = sys.excepthook
        
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            # Capture error / 捕获错误
            self.capture_error(exc_type, exc_value, exc_traceback)
            
            # Call original handler / 调用原始处理器
            original_excepthook(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = custom_excepthook


# Decorator for function monitoring / 函数监控装饰器
def monitor(func: Callable) -> Callable:
    """
    Decorator to monitor function errors / 监控函数错误的装饰器
    
    Usage / 使用方法:
        @monitor
        def my_function():
            pass
    
    Args:
        func: Function to monitor / 要监控的函数
        
    Returns:
        Wrapped function / 包装后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get tracker instance / 获取追踪器实例
            from . import get_tracker
            tracker = get_tracker()
            
            if tracker:
                # Capture error with function context / 捕获带有函数上下文的错误
                tracker.capture_error(
                    type(e),
                    e,
                    e.__traceback__,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    }
                )
            
            # Re-raise exception / 重新抛出异常
            raise
    
    return wrapper


@contextmanager
def track(operation_name: str):
    """
    Context manager for tracking code blocks / 追踪代码块的上下文管理器
    
    Usage / 使用方法:
        with track("database_query"):
            # Code to track
            pass
    
    Args:
        operation_name: Name of the operation / 操作名称
    """
    try:
        yield
    except Exception as e:
        # Get tracker instance / 获取追踪器实例
        from . import get_tracker
        tracker = get_tracker()
        
        if tracker:
            # Capture error with operation context / 捕获带有操作上下文的错误
            tracker.capture_error(
                type(e),
                e,
                e.__traceback__,
                context={"operation": operation_name}
            )
        
        # Re-raise exception / 重新抛出异常
        raise
