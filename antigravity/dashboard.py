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
