"""
UI Components Module / UI 组件模块
=================================

Streamlit UI components for error display and analytics.
用于错误显示和分析的 Streamlit UI 组件。
"""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

from .storage import ErrorStorage


class ErrorUI:
    """
    Error UI components / 错误 UI 组件
    
    Provides Streamlit widgets for error visualization.
    提供用于错误可视化的 Streamlit 小部件。
    """
    
    def __init__(self, storage: ErrorStorage):
        """
        Initialize error UI / 初始化错误 UI
        
        Args:
            storage: Error storage instance / 错误存储实例
        """
        self.storage = storage
    
    def show_error_popup(self):
        """
        Show error popup modal / 显示错误弹出模态框
        
        Displays errors stored in session state.
        显示存储在会话状态中的错误。
        """
        if "error_popup_data" not in st.session_state:
            return
        
        errors = st.session_state.error_popup_data
        if not errors:
            return
        
        # Show most recent error / 显示最新错误
        error_data = errors[-1]
        
        # Create modal / 创建模态框
        with st.expander("🔴 错误详情 / Error Details", expanded=True):
            self._render_error_detail(error_data)
            
            # Action buttons / 操作按钮
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 查看堆栈 / View Stack", key=f"stack_{error_data.get('error_id')}"):
                    st.code(error_data.get("stack_trace", ""), language="python")
            
            with col2:
                if st.button("🔍 查看相似 / View Similar", key=f"similar_{error_data.get('error_id')}"):
                    st.info("模式分析功能即将推出 / Pattern analysis coming soon")
            
            with col3:
                if st.button("✖️ 关闭 / Close", key=f"close_{error_data.get('error_id')}"):
                    st.session_state.error_popup_data = []
                    st.rerun()
    
    def show_error_dashboard(self, days: int = 7):
        """
        Show error analytics dashboard / 显示错误分析仪表板
        
        Args:
            days: Number of days to analyze / 要分析的天数
        """
        st.markdown("## 📊 错误分析 / Error Analytics")
        
        # Load errors / 加载错误
        start_date = datetime.now() - timedelta(days=days)
        errors = self.storage.load_errors(start_date=start_date, limit=1000)
        
        if not errors:
            st.info("✅ 没有错误记录 / No errors recorded")
            return
        
        # Summary metrics / 摘要指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "总错误数 / Total Errors",
                len(errors),
                help=f"过去 {days} 天的错误总数 / Total errors in last {days} days"
            )
        
        with col2:
            unique_types = len(set(e.get("error_type") for e in errors))
            st.metric(
                "错误类型 / Error Types",
                unique_types,
                help="不同的错误类型数量 / Number of unique error types"
            )
        
        with col3:
            critical_count = sum(1 for e in errors if e.get("severity") == "CRITICAL")
            st.metric(
                "严重错误 / Critical",
                critical_count,
                delta="🔴" if critical_count > 0 else "✅",
                help="严重级别的错误数量 / Number of critical errors"
            )
        
        with col4:
            # Most common error / 最常见错误
            from collections import Counter
            error_types = [e.get("error_type") for e in errors]
            most_common = Counter(error_types).most_common(1)
            if most_common:
                st.metric(
                    "最常见 / Most Frequent",
                    most_common[0][0],
                    f"{most_common[0][1]} 次 / times",
                    help="出现次数最多的错误类型 / Most frequently occurring error type"
                )
        
        # Error timeline / 错误时间线
        st.markdown("### 📈 错误趋势 / Error Trend")
        self._show_error_timeline(errors)
        
        # Error list / 错误列表
        st.markdown("### 📋 错误列表 / Error List")
        self._show_error_list(errors)
    
    def _render_error_detail(self, error_data: Dict):
        """
        Render error detail view / 渲染错误详情视图
        
        Args:
            error_data: Error information / 错误信息
        """
        severity = error_data.get("severity", "ERROR")
        
        # Severity badge / 严重性徽章
        severity_colors = {
            "CRITICAL": "🔴",
            "ERROR": "🟠",
            "WARNING": "🟡",
            "INFO": "🔵"
        }
        
        icon = severity_colors.get(severity, "📝")
        
        # Error header / 错误标题
        st.markdown(f"### {icon} {error_data.get('error_type', 'Error')}")
        
        # Bilingual message / 双语消息
        st.error(f"**EN**: {error_data.get('message', '')}")
        st.error(f"**ZH**: {error_data.get('message_zh', '')}")
        
        # Error location / 错误位置
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("📁 文件 / File")
            st.code(error_data.get("file", "unknown"), language="text")
            
            st.caption("🔢 行号 / Line")
            st.code(str(error_data.get("line", 0)), language="text")
        
        with col2:
            st.caption("⚙️ 函数 / Function")
            st.code(error_data.get("function", "unknown"), language="text")
            
            st.caption("⏰ 时间 / Time")
            timestamp = error_data.get("timestamp", "")
            st.code(timestamp[:19] if timestamp else "unknown", language="text")
        
        # Local variables / 局部变量
        local_vars = error_data.get("local_vars", {})
        if local_vars:
            with st.expander("🔍 局部变量 / Local Variables"):
                for var_name, var_value in local_vars.items():
                    st.text(f"{var_name} = {var_value}")
    
    def _show_error_timeline(self, errors: List[Dict]):
        """
        Show error timeline chart / 显示错误时间线图表
        
        Args:
            errors: List of errors / 错误列表
        """
        # Group by date / 按日期分组
        from collections import defaultdict
        
        date_counts = defaultdict(int)
        for error in errors:
            timestamp = error.get("timestamp", "")
            if timestamp:
                date = timestamp[:10]  # YYYY-MM-DD
                date_counts[date] += 1
        
        # Create dataframe / 创建数据框
        df = pd.DataFrame([
            {"日期 / Date": date, "错误数 / Errors": count}
            for date, count in sorted(date_counts.items())
        ])
        
        if not df.empty:
            st.line_chart(df.set_index("日期 / Date"))
        else:
            st.info("没有足够的数据显示趋势 / Not enough data to show trend")
    
    def _show_error_list(self, errors: List[Dict]):
        """
        Show error list table / 显示错误列表表格
        
        Args:
            errors: List of errors / 错误列表
        """
        # Create dataframe / 创建数据框
        df_data = []
        for error in errors[-50:]:  # Last 50 / 最近 50 个
            df_data.append({
                "时间 / Time": error.get("timestamp", "")[:19],
                "类型 / Type": error.get("error_type", ""),
                "消息 / Message": error.get("message_zh", "")[:50] + "...",
                "文件 / File": error.get("file", "").split("/")[-1],
                "行 / Line": error.get("line", 0),
                "严重性 / Severity": error.get("severity", "")
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("没有错误记录 / No errors recorded")


def show_debug_panel():
    """
    Show debug monitoring panel in sidebar / 在侧边栏显示调试监控面板
    
    This is a convenience function for quick integration.
    这是一个用于快速集成的便捷函数。
    """
    from . import get_tracker
    from .storage import ErrorStorage
    
    tracker = get_tracker()
    if not tracker:
        return
    
    storage = tracker.storage
    ui = ErrorUI(storage)
    
    # Show popup if errors exist / 如果存在错误则显示弹窗
    ui.show_error_popup()
    
    # Detect project switch / 检测项目切换
    current_project = st.session_state.get("active_project_root")
    last_project = st.session_state.get("_debug_monitor_last_project")
    
    # If project changed, clear error popup data / 如果项目改变,清除错误弹窗数据
    if current_project != last_project:
        st.session_state.error_popup_data = []
        st.session_state._debug_monitor_last_project = current_project
    
    # Sidebar debug info / 侧边栏调试信息
    with st.sidebar:
        with st.expander("🐛 调试监控 / Debug Monitor"):
            # Show current project / 显示当前项目
            if current_project:
                project_name = str(current_project).split("/")[-1] if "/" in str(current_project) else str(current_project).split("\\")[-1]
                st.caption(f"📁 当前项目 / Current: **{project_name}**")
            
            today_count = storage.get_error_count()
            st.metric(
                "今日错误 / Today's Errors",
                today_count,
                help="今天捕获的错误总数 / Total errors captured today"
            )
            
            if st.button("📊 查看详情 / View Details", use_container_width=True):
                st.session_state.show_debug_dashboard = True
    
    # Show dashboard if requested / 如果请求则显示仪表板
    if st.session_state.get("show_debug_dashboard", False):
        ui.show_error_dashboard()
        
        if st.button("✖️ 关闭仪表板 / Close Dashboard"):
            st.session_state.show_debug_dashboard = False
            st.rerun()
