"""
Alert Manager Module / 告警管理模块
==================================

Handles real-time error notifications and alerts.
处理实时错误通知和告警。
"""

import streamlit as st
from typing import Dict, Optional
from datetime import datetime, timedelta


class AlertManager:
    """
    Alert manager for real-time notifications / 实时通知的告警管理器
    
    Provides toast notifications and popup modals for errors.
    为错误提供提示通知和弹出模态框。
    """
    
    def __init__(self):
        """Initialize alert manager / 初始化告警管理器"""
        self.last_alert_time = {}  # Throttling / 节流
        self.alert_history = []
    
    def notify(
        self,
        error_data: Dict,
        show_toast: bool = True,
        show_popup: bool = False
    ):
        """
        Send error notification / 发送错误通知
        
        Args:
            error_data: Error information / 错误信息
            show_toast: Show toast notification / 显示提示通知
            show_popup: Show popup modal / 显示弹出模态框
        """
        severity = error_data.get("severity", "ERROR")
        error_id = error_data.get("error_id", "unknown")
        
        # Throttle alerts / 节流告警
        if not self._should_alert(error_id, severity):
            return
        
        # Show toast / 显示提示
        if show_toast:
            self._show_toast(error_data)
        
        # Show popup / 显示弹窗
        if show_popup:
            self._show_popup(error_data)
        
        # Record alert / 记录告警
        self.alert_history.append({
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "severity": severity
        })
    
    def _should_alert(self, error_id: str, severity: str) -> bool:
        """
        Check if should send alert (throttling) / 检查是否应该发送告警(节流)
        
        Args:
            error_id: Error ID / 错误 ID
            severity: Severity level / 严重性级别
            
        Returns:
            True if should alert / 如果应该告警则返回 True
        """
        # Always alert CRITICAL / 总是告警 CRITICAL
        if severity == "CRITICAL":
            return True
        
        # Throttle by error ID / 按错误 ID 节流
        last_time = self.last_alert_time.get(error_id)
        if last_time:
            # Don't alert if within 30 seconds / 如果在 30 秒内则不告警
            if datetime.now() - last_time < timedelta(seconds=30):
                return False
        
        self.last_alert_time[error_id] = datetime.now()
        return True
    
    def _show_toast(self, error_data: Dict):
        """
        Show toast notification / 显示提示通知
        
        Args:
            error_data: Error information / 错误信息
        """
        severity = error_data.get("severity", "ERROR")
        message_zh = error_data.get("message_zh", error_data.get("message", ""))
        error_type = error_data.get("error_type", "Error")
        
        # Severity icons / 严重性图标
        icons = {
            "CRITICAL": "🔴",
            "ERROR": "🟠",
            "WARNING": "🟡",
            "INFO": "🔵"
        }
        
        icon = icons.get(severity, "📝")
        
        # Show toast / 显示提示
        try:
            st.toast(
                f"{icon} **{error_type}**: {message_zh[:100]}",
                icon=icon
            )
        except Exception:
            pass  # Silently fail if toast not available / 如果提示不可用则静默失败
    
    def _show_popup(self, error_data: Dict):
        """
        Show popup modal / 显示弹出模态框
        
        Args:
            error_data: Error information / 错误信息
        """
        # Store in session state for display / 存储在会话状态中以供显示
        if "error_popup_data" not in st.session_state:
            st.session_state.error_popup_data = []
        
        st.session_state.error_popup_data.append(error_data)
