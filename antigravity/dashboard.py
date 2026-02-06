import streamlit as st
import json
import time
import os
from antigravity.state_manager import StateManager
from antigravity.config import CONFIG

# 语言配置 / Language Configuration
LANGUAGES = {
    "zh": {
        "page_title": "Antigravity 监管面板",
        "header": "🛡️ Antigravity 监管面板",
        "sidebar_control": "⚙️ 系统控制",
        "ai_mode": "🤖 AI 模式",
        "select_mode": "选择提示词模式",
        "apply_mode": "🔄 应用模式",
        "mode_changed": "模式已切换为: {}. 重启监控器以应用。",
        "environment": "🛡️ 环境",
        "check_deps": "检查依赖",
        "missing_deps": "缺失: {}",
        "all_deps_ok": "所有依赖已满足!",
        "status": "📊 状态",
        "last_update": "最后更新: {}",
        "recent_audits": "📋 最近审计",
        "no_audits": "暂无审计历史",
        "live_log": "🔍 实时审计日志",
        "no_activity": "等待 Agent 活动...",
        "last_error": "**最后错误:**",
        "task_launcher": "🚀 任务发射台",
        "task_definition": "📦 任务定义",
        "target_file": "目标文件名",
        "target_file_help": "文件必须位于 src/ 目录下且以 .py 结尾",
        "task_name": "任务简称",
        "task_name_help": "简短描述此任务的功能",
        "auto_test": "自动创建测试文件",
        "plan_details": "📜 计划详情 (PLAN.md)",
        "plan_help": "详细描述功能需求、技术要求和测试要求",
        "save_launch": "🔥 保存并启动",
        "save_only": "💾 仅保存 PLAN",
        "plan_saved": "✅ PLAN.md 已保存",
        "save_failed": "保存失败: {}",
        "error_no_file": "❌ 错误: 请输入目标文件名",
        "error_not_py": "❌ 错误: 目标文件必须以 .py 结尾",
        "error_not_src": "❌ 错误: 目标文件必须位于 src/ 目录下",
        "error_no_plan": "❌ 错误: 请先在右侧输入任务计划",
        "plan_updated": "✅ PLAN.md 已更新",
        "file_created": "✅ 已创建目标文件: {}",
        "file_exists": "ℹ️ 文件已存在: {}",
        "test_created": "✅ 已创建测试文件: {}",
        "test_exists": "ℹ️ 测试文件已存在: {}",
        "task_launched": "🎯 **任务已发射!**\n\nMonitor 将在 3 秒后检测到变化并自动接管 `{}`\n\n**接下来会发生什么:**\n1. ✅ Monitor 检测到 PLAN.md 和新文件\n2. 🔍 Auditor 读取计划并分析需求\n3. 💻 Agent 自动编写完整代码\n4. 🧪 自动运行测试\n5. 🔄 如有错误,自动修复直至通过\n\n请在上方\"最近审计\"查看实时进度!",
        "launch_failed": "❌ 启动失败: {}",
        "env_status": "🔧 环境状态",
        "env_ok": "✅ 所有依赖已满足 (检查时间: {})",
        "env_missing": "⚠️ 缺失依赖 (检查时间: {})",
        "no_env_check": "暂无环境检查记录",
        "refresh": "🔄 刷新面板",
        "powered_by": "由 DeepSeek-R1 & Antigravity Agent 驱动 | 自动刷新: 5秒",
        "language": "🌐 语言 / Language",
    },
    "en": {
        "page_title": "Antigravity Dashboard",
        "header": "🛡️ Antigravity Sheriff Monitor",
        "sidebar_control": "⚙️ System Control",
        "ai_mode": "🤖 AI Mode",
        "select_mode": "Select Prompt Mode",
        "apply_mode": "🔄 Apply Mode",
        "mode_changed": "Mode changed to: {}. Restart monitor to apply.",
        "environment": "🛡️ Environment",
        "check_deps": "Check Dependencies",
        "missing_deps": "Missing: {}",
        "all_deps_ok": "All dependencies satisfied!",
        "status": "📊 Status",
        "last_update": "Last update: {}",
        "recent_audits": "📋 Recent Audits",
        "no_audits": "No audit history yet",
        "live_log": "🔍 Live Audit Log",
        "no_activity": "Waiting for agent activity...",
        "last_error": "**Last Error:**",
        "task_launcher": "🚀 Task Launcher",
        "task_definition": "📦 Task Definition",
        "target_file": "Target File",
        "target_file_help": "File must be in src/ directory and end with .py",
        "task_name": "Task Name",
        "task_name_help": "Brief description of this task",
        "auto_test": "Auto-create test file",
        "plan_details": "📜 Plan Details (PLAN.md)",
        "plan_help": "Describe requirements, technical specs, and testing needs",
        "save_launch": "🔥 Save & Launch",
        "save_only": "💾 Save PLAN Only",
        "plan_saved": "✅ PLAN.md saved",
        "save_failed": "Save failed: {}",
        "error_no_file": "❌ Error: Please enter target file name",
        "error_not_py": "❌ Error: Target file must end with .py",
        "error_not_src": "❌ Error: Target file must be in src/ directory",
        "error_no_plan": "❌ Error: Please enter task plan first",
        "plan_updated": "✅ PLAN.md updated",
        "file_created": "✅ Created target file: {}",
        "file_exists": "ℹ️ File already exists: {}",
        "test_created": "✅ Created test file: {}",
        "test_exists": "ℹ️ Test file already exists: {}",
        "task_launched": "🎯 **Task Launched!**\n\nMonitor will detect changes in 3 seconds and auto-takeover `{}`\n\n**What happens next:**\n1. ✅ Monitor detects PLAN.md and new file\n2. 🔍 Auditor reads plan and analyzes requirements\n3. 💻 Agent auto-writes complete code\n4. 🧪 Auto-runs tests\n5. 🔄 Auto-fixes errors until passing\n\nCheck \"Recent Audits\" above for live progress!",
        "launch_failed": "❌ Launch failed: {}",
        "env_status": "🔧 Environment Status",
        "env_ok": "✅ All dependencies satisfied (checked: {})",
        "env_missing": "⚠️ Missing dependencies (checked: {})",
        "no_env_check": "No environment checks performed yet",
        "refresh": "🔄 Refresh Dashboard",
        "powered_by": "Powered by DeepSeek-R1 & Antigravity Agent | Auto-refresh: 5s",
        "language": "🌐 Language / 语言",
    }
}

# 初始化语言设置 / Initialize language setting
if 'language' not in st.session_state:
    st.session_state.language = 'zh'  # 默认中文 / Default Chinese

def t(key):
    """翻译函数 / Translation function"""
    return LANGUAGES[st.session_state.language].get(key, key)

# Page Config
st.set_page_config(page_title=t("page_title"), layout="wide", page_icon="🛡️")

st.title(t("header"))

# Initialize StateManager
@st.cache_resource
def get_state_manager():
    return StateManager(".")

state_mgr = get_state_manager()

# Sidebar
st.sidebar.header(t("sidebar_control"))

# 语言选择器 / Language Selector
st.sidebar.subheader(t("language"))
lang_options = {"中文": "zh", "English": "en"}
selected_lang = st.sidebar.radio(
    "",
    options=list(lang_options.keys()),
    index=0 if st.session_state.language == 'zh' else 1,
    horizontal=True
)
if lang_options[selected_lang] != st.session_state.language:
    st.session_state.language = lang_options[selected_lang]
    st.rerun()

# Prompt Mode Selector
st.sidebar.subheader(t("ai_mode"))
prompts = CONFIG.get("prompts", {})
modes = list(prompts.get("modes", {}).keys())
current_mode = CONFIG.get("ACTIVE_MODE", "executor")

selected_mode = st.sidebar.selectbox(
    t("select_mode"),
    modes,
    index=modes.index(current_mode) if current_mode in modes else 0
)

if st.sidebar.button(t("apply_mode")):
    st.sidebar.info(t("mode_changed").format(selected_mode))

# Environment Check Button
st.sidebar.subheader(t("environment"))
if st.sidebar.button(t("check_deps")):
    from antigravity.env_checker import check_dependencies
    if os.path.exists("PLAN.md"):
        with open("PLAN.md", "r", encoding='utf-8') as f:
            missing = check_dependencies(f.read())
        if missing:
            st.sidebar.warning(t("missing_deps").format(', '.join(missing)))
        else:
            st.sidebar.success(t("all_deps_ok"))

# System Status
st.sidebar.subheader(t("status"))
system_status = state_mgr.get_system_status()
takeover_status = system_status.get("takeover_status", "Unknown")

status_colors = {
    "Idle": "🟢",
    "Writing": "🟡",
    "Testing": "🔵",
    "Error": "🔴"
}

st.sidebar.markdown(f"{status_colors.get(takeover_status, '⚪')} **{takeover_status}**")

last_update = system_status.get("last_update", "Never")
st.sidebar.caption(t("last_update").format(last_update[:19] if last_update != 'Never' else 'Never'))

# Main Area
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(t("recent_audits"))
    
    audits = state_mgr.get_recent_audits(limit=20)
    
    if not audits:
        st.info(t("no_audits"))
    else:
        for audit in reversed(audits):  # Show newest first
            status = audit.get("status", "INFO")
            file_name = audit.get("file_path", "Unknown")
            timestamp = audit.get("timestamp", "")[:19]
            event_type = audit.get("event_type", "")
            
            # Status icon
            icon = {
                "PASS": "✅",
                "FIXED": "🔧",
                "FAIL": "❌",
                "INFO": "ℹ️",
                "CRITICAL": "🔴"
            }.get(status, "📝")
            
            with st.expander(f"{icon} {file_name} - {event_type}", expanded=False):
                st.caption(f"⏰ {timestamp}")
                st.text(audit.get("message", "")[:200])

with col2:
    st.subheader(t("live_log"))
    
    # Display structured audit data
    if audits:
        # Create a table view
        import pandas as pd
        
        df_data = []
        for audit in reversed(audits[-10:]):  # Last 10
            df_data.append({
                "Time": audit.get("timestamp", "")[:19],
                "File": audit.get("file_path", ""),
                "Event": audit.get("event_type", ""),
                "Status": audit.get("status", "")
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(t("no_activity"))
    
    # Show last error if any
    last_error = system_status.get("last_error_log")
    if last_error:
        st.error(t("last_error"))
        st.code(last_error[:500], language="text")

# --- Task Launcher Section ---
st.markdown("---")
st.header(t("task_launcher"))

with st.container():
    t_col1, t_col2 = st.columns([1, 2])
    
    with t_col1:
        st.subheader(t("task_definition"))
        target_file = st.text_input(
            t("target_file"), 
            placeholder="src/your_module.py",
            help=t("target_file_help")
        )
        task_name = st.text_input(
            t("task_name"), 
            placeholder="User Login Module" if st.session_state.language == 'en' else "用户登录模块",
            help=t("task_name_help")
        )
        
        # Auto-create test file option
        create_test = st.checkbox(t("auto_test"), value=True)
        
    with t_col2:
        st.subheader(t("plan_details"))
        
        # Read current PLAN.md as template
        default_plan = ""
        if os.path.exists("PLAN.md"):
            try:
                with open("PLAN.md", "r", encoding='utf-8') as f:
                    default_plan = f.read()
            except Exception:
                default_plan = "# Task Plan\n\n## Target File\n\n## Core Logic\n\n## Technical Requirements\n"
        
        task_plan = st.text_area(
            t("plan_help"), 
            value=default_plan, 
            height=250,
            label_visibility="collapsed"
        )

    # Launch buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        launch_button = st.button(t("save_launch"), type="primary", use_container_width=True)
    
    with col_btn2:
        if st.button(t("save_only"), use_container_width=True):
            try:
                with open("PLAN.md", "w", encoding='utf-8') as f:
                    f.write(task_plan)
                st.success(t("plan_saved"))
            except Exception as e:
                st.error(t("save_failed").format(e))
    
    # Launch logic
    if launch_button:
        # Validation
        if not target_file:
            st.error(t("error_no_file"))
        elif not target_file.endswith(".py"):
            st.error(t("error_not_py"))
        elif not target_file.startswith("src/"):
            st.error(t("error_not_src"))
        elif not task_plan.strip():
            st.error(t("error_no_plan"))
        else:
            try:
                # 1. Update PLAN.md
                with open("PLAN.md", "w", encoding='utf-8') as f:
                    f.write(task_plan)
                st.success(t("plan_updated"))
                
                # 2. Create target file
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                if not os.path.exists(target_file):
                    with open(target_file, "w", encoding='utf-8') as f:
                        f.write(f"# {task_name or 'Auto-generated by Antigravity'}\n# TODO: Implement\n")
                    st.success(t("file_created").format(target_file))
                else:
                    st.info(t("file_exists").format(target_file))
                
                # 3. Create test file
                if create_test:
                    test_file = f"tests/test_{os.path.basename(target_file)}"
                    os.makedirs("tests", exist_ok=True)
                    
                    if not os.path.exists(test_file):
                        with open(test_file, "w", encoding='utf-8') as f:
                            f.write(f"""# Test for {target_file}
import unittest

class Test{task_name.replace(' ', '')}(unittest.TestCase):
    def test_placeholder(self):
        pass

if __name__ == '__main__':
    unittest.main()
""")
                        st.success(t("test_created").format(test_file))
                    else:
                        st.info(t("test_exists").format(test_file))
                
                # 4. Success message
                st.balloons()
                st.success(t("task_launched").format(target_file))
                
                # Log to state manager
                state_mgr.log_audit(
                    target_file,
                    "task_launched",
                    f"Task '{task_name}' launched via dashboard",
                    "INFO"
                )
                
            except Exception as e:
                st.error(t("launch_failed").format(e))
                import traceback
                st.code(traceback.format_exc(), language="python")


# Environment Check Results
st.subheader(t("env_status"))
last_env_check = state_mgr.get_last_environment_check()

if last_env_check:
    success = last_env_check.get("success", False)
    missing_deps = last_env_check.get("missing_dependencies", [])
    timestamp = last_env_check.get("timestamp", "")[:19]
    
    if success:
        st.success(t("env_ok").format(timestamp))
    else:
        st.warning(t("env_missing").format(timestamp))
        for dep in missing_deps:
            st.code(f"pip install {dep}", language="bash")
else:
    st.info(t("no_env_check"))

# Auto-refresh
if st.button(t("refresh")):
    st.rerun()

# Auto-refresh every 5 seconds
st.markdown("---")
st.caption(t("powered_by"))

# Add auto-refresh script
st.markdown("""
<script>
setTimeout(function() {
    window.location.reload();
}, 5000);
</script>
""", unsafe_allow_html=True)
