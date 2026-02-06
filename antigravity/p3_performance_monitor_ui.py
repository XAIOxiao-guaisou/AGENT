# P3 Phase 17: Project-Scoped Performance Monitor
# Replace the existing P3 Performance Monitor section in dashboard.py with this code

# ============================================================
# P3: Performance Monitor (性能监控中枢) - Project-Scoped
# ============================================================

st.markdown("---")

# Get active project context from session state
active_project_root = st.session_state.get('active_project_root', Path("."))
active_perf_monitor = st.session_state.get('active_perf_monitor', None)
active_state_mgr = st.session_state.get('active_state_mgr', state_mgr)
project_name = active_project_root.name if active_project_root != Path(".") else "Global"

st.header(f"📊 {t('performance_monitor')} - {project_name}")

if active_perf_monitor:
    try:
        perf_data = active_perf_monitor.get_summary()
        
        # Performance Statistics Cards
        st.subheader(t("performance_stats"))
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                t("total_operations"),
                perf_data.get("total_operations", 0)
            )
        
        with col2:
            st.metric(
                t("total_calls"),
                perf_data.get("total_calls", 0)
            )
        
        with col3:
            avg_time = perf_data.get("average_time", 0)
            st.metric(
                t("avg_time"),
                f"{avg_time:.2f}s"
            )
        
        with col4:
            total_time = perf_data.get("total_time", 0)
            st.metric(
                t("total_time"),
                f"{total_time:.2f}s"
            )
        
        # Slowest Operations
        st.subheader(t("slowest_operations"))
        slowest = perf_data.get("slowest_operations", [])
        
        if slowest:
            for op in slowest[:5]:
                col_op, col_time, col_calls = st.columns([3, 1, 1])
                with col_op:
                    st.text(f"📌 {op['operation']}")
                with col_time:
                    st.text(f"⏱️ {op['avg_time']:.2f}s")
                with col_calls:
                    st.text(f"🔢 {op['calls']}x")
        else:
            st.info(t("no_operations"))
        
        # Token Usage Estimation (Project-Specific)
        st.subheader(t("token_usage"))
        
        # Load PLAN.md from active project
        plan_path = active_project_root / "PLAN.md"
        if plan_path.exists():
            plan_content = plan_path.read_text(encoding='utf-8')
            
            # Estimate tokens (rough: 1 token ≈ 4 characters)
            estimated_tokens = len(plan_content) // 4
            max_tokens = CONFIG.get("MAX_TOKENS", 16000)
            usage_pct = min(100, (estimated_tokens / max_tokens) * 100)
            
            st.progress(usage_pct / 100)
            st.caption(f"{estimated_tokens:,} / {max_tokens:,} tokens ({usage_pct:.1f}%)")
        else:
            st.warning(t("no_plan_found"))
        
        # Recent Executions Timeline (Project-Specific)
        st.subheader(t("recent_executions"))
        
        # Get audit logs from active state manager
        recent_audits = active_state_mgr.get_recent_audits(limit=10)
        
        if recent_audits:
            success_count = sum(1 for a in recent_audits if a.get('status') in ['PASS', 'FIXED'])
            success_rate = (success_count / len(recent_audits)) * 100
            
            st.metric(t("success_rate"), f"{success_rate:.1f}%")
            
            # Timeline
            for audit in reversed(recent_audits[-5:]):
                timestamp = audit.get('timestamp', 'N/A')[:19]
                file_path = audit.get('file_path', 'Unknown')
                status = audit.get('status', 'INFO')
                
                status_icon = {
                    'PASS': '✅',
                    'FIXED': '🔧',
                    'FAIL': '❌',
                    'INFO': 'ℹ️'
                }.get(status, '📝')
                
                st.text(f"{status_icon} {timestamp} | {file_path} | {status}")
        else:
            st.info(t("no_activity"))
    
    except Exception as e:
        st.error(f"Performance monitor error: {e}")
else:
    # Fallback: Try to initialize performance monitor
    try:
        from antigravity.performance_monitor import PerformanceMonitor
        perf_monitor = PerformanceMonitor(str(active_project_root))
        st.session_state.active_perf_monitor = perf_monitor
        st.rerun()
    except Exception as e:
        st.warning(f"⚠️ Performance monitor not available for this project: {e}")
        st.info("Performance monitoring requires initialization. Create some activity in this project first.")
