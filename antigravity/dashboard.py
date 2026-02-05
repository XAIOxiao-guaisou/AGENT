import streamlit as st
import json
import time
import os

# Page Config
st.set_page_config(page_title="Antigravity Sheriff Dashboard", layout="wide")

st.title("🛡️ Antigravity Sheriff Monitor")
st.sidebar.header("System Status")

# 1. System Metrics (Sidebar)
status_placeholder = st.sidebar.empty()
status_placeholder.success("🟢 System Running")

# 2. Main Area
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Task Board")
    try:
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                tasks = data.get("tasks", []) 
                if not tasks:
                     st.info("No tasks in tasks.json")
                for task in tasks:
                    # Simple Task Visualization
                    status_icon = "✅" if task.get('status') == 'Done' else "⏳"
                    st.markdown(f"{status_icon} **{task.get('name', 'Unnamed Task')}**")
        else:
            st.warning("tasks.json not found")
    except Exception as e:
        st.error(f"Error reading tasks: {e}")

with col2:
    st.subheader("🔍 Live Audit Log")
    log_area = st.empty()
    
    def tail_logs():
        if os.path.exists("vibe_audit.log"):
            try:
                with open("vibe_audit.log", "r", encoding='utf-8') as f:
                    return f.readlines()[-20:] # Last 20 lines
            except Exception:
                return []
        return ["Waiting for audit signals..."]

    # Auto-refresh loop using Streamlit reruns usually controlled by outside env, 
    # but here we use a placeholder update loop if running in script mode, 
    # actually Streamlit handles refresh via interaction. 
    # For auto-refresh, we can use empty + sleep, but native Streamlit way is st.empty()
    
    logs = tail_logs()
    log_content = "".join(logs)
    
    # Simple color highlighting
    if "[SYSTEM CRITICAL]" in log_content:
        st.error("⚠️ SYSTEM CRITICAL ERROR DETECTED")
    
    log_content = log_content.replace("[SYSTEM CRITICAL]", "🔴 **[SYSTEM CRITICAL]**")
    log_content = log_content.replace("STATUS: PASS", "🟢 **STATUS: PASS**")
    
    log_area.markdown(f"{log_content}")

    if st.button("Refresh Logs"):
        st.rerun()

st.markdown("---")
st.caption("Powered by deepseek-r1 & Antigravity Agent")
