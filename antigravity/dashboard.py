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
    st.subheader("🔍 Live Audit & Executor Log")
    log_area = st.empty()
    
    def tail_logs():
        if os.path.exists("vibe_audit.log"):
            try:
                with open("vibe_audit.log", "r", encoding='utf-8') as f:
                    lines = f.readlines()
                    # Reverse to show newest first
                    return lines[::-1][:50] 
            except Exception:
                return []
        return ["Waiting for agent signals..."]

    # Dashboard Loop
    log_lines = tail_logs()
    
    # Process logs for events
    retry_count = 0
    for line in log_lines:
        if "Verification Attempt" in line: # Need to log this in monitor.py or auditor.py to see it here? 
            # Actually monitor prints to stdout. We should redirect stdout or log to file.
            pass

    # Render
    content = ""
    for line in log_lines:
        if "[SYSTEM CRITICAL]" in line:
            content += f"🔴 {line}  \n"
        elif "STATUS: PASS" in line:
            content += f"🟢 {line}  \n"
        elif "[AGENT TAKEOVER]" in line:
            content += f"✨ **{line.strip()}**  \n"
        else:
            content += f"{line}  \n"
            
    log_area.markdown(content)

    if st.button("Refresh Logs"):
        st.rerun()

st.markdown("---")
st.caption("Powered by deepseek-r1 & Antigravity Agent")
