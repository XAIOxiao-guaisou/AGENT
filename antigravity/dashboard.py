import streamlit as st
import json
import time
import os
from antigravity.state_manager import StateManager
from antigravity.config import CONFIG

# Page Config
st.set_page_config(page_title="Antigravity Sheriff Dashboard", layout="wide", page_icon="🛡️")

st.title("🛡️ Antigravity Sheriff Monitor")

# Initialize StateManager
@st.cache_resource
def get_state_manager():
    return StateManager(".")

state_mgr = get_state_manager()

# Sidebar
st.sidebar.header("⚙️ System Control")

# Prompt Mode Selector
st.sidebar.subheader("🤖 AI Mode")
prompts = CONFIG.get("prompts", {})
modes = list(prompts.get("modes", {}).keys())
current_mode = CONFIG.get("ACTIVE_MODE", "executor")

selected_mode = st.sidebar.selectbox(
    "Select Prompt Mode",
    modes,
    index=modes.index(current_mode) if current_mode in modes else 0
)

if st.sidebar.button("🔄 Apply Mode"):
    # Note: This would require restarting the monitor to take effect
    # For now, just show a message
    st.sidebar.info(f"Mode changed to: {selected_mode}. Restart monitor to apply.")

# Environment Check Button
st.sidebar.subheader("🛡️ Environment")
if st.sidebar.button("Check Dependencies"):
    from antigravity.env_checker import check_dependencies
    if os.path.exists("PLAN.md"):
        with open("PLAN.md", "r", encoding='utf-8') as f:
            missing = check_dependencies(f.read())
        if missing:
            st.sidebar.warning(f"Missing: {', '.join(missing)}")
        else:
            st.sidebar.success("All dependencies satisfied!")

# System Status
st.sidebar.subheader("📊 Status")
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
st.sidebar.caption(f"Last update: {last_update[:19] if last_update != 'Never' else 'Never'}")

# Main Area
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Recent Audits")
    
    audits = state_mgr.get_recent_audits(limit=20)
    
    if not audits:
        st.info("No audit history yet")
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
    st.subheader("🔍 Live Audit Log")
    
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
        st.info("Waiting for agent activity...")
    
    # Show last error if any
    last_error = system_status.get("last_error_log")
    if last_error:
        st.error("**Last Error:**")
        st.code(last_error[:500], language="text")

# --- Task Launcher Section ---
st.markdown("---")
st.header("🚀 任务发射台 (One-Click Task Launcher)")

with st.container():
    t_col1, t_col2 = st.columns([1, 2])
    
    with t_col1:
        st.subheader("📦 任务定义")
        target_file = st.text_input(
            "目标文件名", 
            placeholder="src/your_module.py",
            help="文件必须位于 src/ 目录下且以 .py 结尾"
        )
        task_name = st.text_input(
            "任务简称", 
            placeholder="例如: 用户登录模块",
            help="简短描述此任务的功能"
        )
        
        # 可选: 自动创建测试文件
        create_test = st.checkbox("自动创建测试文件", value=True)
        
    with t_col2:
        st.subheader("📜 计划详情 (PLAN.md)")
        
        # 读取当前 PLAN.md 作为模板
        default_plan = ""
        if os.path.exists("PLAN.md"):
            try:
                with open("PLAN.md", "r", encoding='utf-8') as f:
                    default_plan = f.read()
            except Exception:
                default_plan = "# 任务计划\n\n## 目标文件\n\n## 核心逻辑\n\n## 技术要求\n"
        
        task_plan = st.text_area(
            "在该任务中需要遵循的规则", 
            value=default_plan, 
            height=250,
            help="详细描述功能需求、技术要求和测试要求"
        )

    # 一键启动按钮
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        launch_button = st.button("🔥 保存并启动", type="primary", use_container_width=True)
    
    with col_btn2:
        if st.button("💾 仅保存 PLAN", use_container_width=True):
            try:
                with open("PLAN.md", "w", encoding='utf-8') as f:
                    f.write(task_plan)
                st.success("✅ PLAN.md 已保存")
            except Exception as e:
                st.error(f"保存失败: {e}")
    
    # 一键启动逻辑
    if launch_button:
        # 验证输入
        if not target_file:
            st.error("❌ 错误: 请输入目标文件名")
        elif not target_file.endswith(".py"):
            st.error("❌ 错误: 目标文件必须以 .py 结尾")
        elif not target_file.startswith("src/"):
            st.error("❌ 错误: 目标文件必须位于 src/ 目录下")
        elif not task_plan.strip():
            st.error("❌ 错误: 请先在右侧输入任务计划")
        else:
            try:
                # 1. 更新 PLAN.md
                with open("PLAN.md", "w", encoding='utf-8') as f:
                    f.write(task_plan)
                st.success("✅ PLAN.md 已更新")
                
                # 2. 确保目录存在并创建目标空文件 (触发点)
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                file_created = False
                if not os.path.exists(target_file):
                    with open(target_file, "w", encoding='utf-8') as f:
                        f.write(f"# {task_name or 'Auto-generated by Antigravity'}\n# TODO: Implement\n")
                    file_created = True
                    st.success(f"✅ 已创建目标文件: {target_file}")
                else:
                    st.info(f"ℹ️ 文件已存在: {target_file}")
                
                # 3. (可选) 创建配套测试文件
                if create_test:
                    test_file = f"tests/test_{os.path.basename(target_file)}"
                    os.makedirs("tests", exist_ok=True)
                    
                    if not os.path.exists(test_file):
                        with open(test_file, "w", encoding='utf-8') as f:
                            f.write(f"""# Test for {target_file}
import unittest
from {target_file.replace('/', '.').replace('.py', '')} import *

class Test{task_name.replace(' ', '')}(unittest.TestCase):
    def test_placeholder(self):
        # TODO: Add actual tests
        pass

if __name__ == '__main__':
    unittest.main()
""")
                        st.success(f"✅ 已创建测试文件: {test_file}")
                    else:
                        st.info(f"ℹ️ 测试文件已存在: {test_file}")
                
                # 4. 显示成功消息
                st.balloons()
                st.success(f"""
                🎯 **任务已发射!**
                
                Monitor 将在 3 秒后检测到变化并自动接管 `{target_file}`
                
                **接下来会发生什么:**
                1. ✅ Monitor 检测到 PLAN.md 和新文件
                2. 🔍 Auditor 读取计划并分析需求
                3. 💻 Agent 自动编写完整代码
                4. 🧪 自动运行测试
                5. 🔄 如有错误,自动修复直至通过
                
                请在上方"Recent Audits"查看实时进度!
                """)
                
                # 记录到状态管理器
                state_mgr.log_audit(
                    target_file,
                    "task_launched",
                    f"Task '{task_name}' launched via dashboard",
                    "INFO"
                )
                
            except Exception as e:
                st.error(f"❌ 启动失败: {e}")
                import traceback
                st.code(traceback.format_exc(), language="python")



# Environment Check Results
st.subheader("🔧 Environment Status")
last_env_check = state_mgr.get_last_environment_check()

if last_env_check:
    success = last_env_check.get("success", False)
    missing_deps = last_env_check.get("missing_dependencies", [])
    timestamp = last_env_check.get("timestamp", "")[:19]
    
    if success:
        st.success(f"✅ All dependencies satisfied (checked: {timestamp})")
    else:
        st.warning(f"⚠️ Missing dependencies (checked: {timestamp})")
        for dep in missing_deps:
            st.code(f"pip install {dep}", language="bash")
else:
    st.info("No environment checks performed yet")

# Auto-refresh
if st.button("🔄 Refresh Dashboard"):
    st.rerun()

# Auto-refresh every 5 seconds
st.markdown("---")
st.caption("Powered by DeepSeek-R1 & Antigravity Agent | Auto-refresh: 5s")

# Add auto-refresh script
st.markdown("""
<script>
setTimeout(function() {
    window.location.reload();
}, 5000);
</script>
""", unsafe_allow_html=True)
