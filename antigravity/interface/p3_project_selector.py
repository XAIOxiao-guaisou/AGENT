st.sidebar.markdown('---')
st.sidebar.subheader('🎯 ' + t('project_center'))
from pathlib import Path
from antigravity.infrastructure.p3_state_manager import P3StateManager
from antigravity.utils.config import CONFIG
projects_dir = Path(CONFIG.get('PROJECTS_DIR', 'projects'))
available_projects = []
project_status = {}
if projects_dir.exists():
    for project_path in projects_dir.iterdir():
        if project_path.is_dir():
            project_name = project_path.name
            has_plan = (project_path / 'PLAN.md').exists()
            has_state = (project_path / '.antigravity_state.json').exists()
            if has_plan and has_state:
                status = '🟢'
            elif has_plan:
                status = '🟡'
            else:
                status = '🔴'
            available_projects.append(project_name)
            project_status[project_name] = status
project_options = ['Global (Legacy)'] + available_projects
formatted_options = []
for opt in project_options:
    if opt == 'Global (Legacy)':
        formatted_options.append('🌐 Global (Legacy)')
    else:
        status_icon = project_status.get(opt, '⚪')
        formatted_options.append(f'{status_icon} {opt}')
selected_index = st.sidebar.selectbox(t('active_project'), range(len(formatted_options)), format_func=lambda i: formatted_options[i], key='p3_project_selector')
selected_project = project_options[selected_index]
if 'last_selected_project' not in st.session_state:
    st.session_state.last_selected_project = None
if selected_project != st.session_state.last_selected_project:
    st.session_state.last_selected_project = selected_project
    with st.sidebar:
        with st.spinner(t('loading_project_context')):
            if selected_project != 'Global (Legacy)':
                project_root = projects_dir / selected_project
                st.session_state.active_project_root = project_root
                try:
                    st.session_state.active_state_mgr = P3StateManager(project_root)
                    try:
                        from antigravity.infrastructure.performance_monitor import PerformanceMonitor
                        st.session_state.active_perf_monitor = PerformanceMonitor(str(project_root))
                    except:
                        st.session_state.active_perf_monitor = None
                    st.sidebar.success(f"✅ {t('project_loaded')}: {selected_project}")
                except Exception as e:
                    st.sidebar.error(f"⚠️ {t('project_load_failed')}: {e}")
                    st.session_state.active_project_root = Path('.')
                    st.session_state.active_state_mgr = None
            else:
                st.session_state.active_project_root = Path('.')
                st.session_state.active_state_mgr = state_mgr
                st.session_state.active_perf_monitor = None
if selected_project != 'Global (Legacy)':
    project_root = projects_dir / selected_project
    with st.sidebar.expander(f"📋 {t('project_info')}"):
        if (project_root / 'PLAN.md').exists():
            plan_size = (project_root / 'PLAN.md').stat().st_size
            st.text(f'PLAN.md: {plan_size} bytes')
        else:
            st.warning(t('no_plan_found'))
        file_count = len(list(project_root.rglob('*.py'))) + len(list(project_root.rglob('*.js')))
        st.text(f"{t('files')}: {file_count}")
        if (project_root / '.antigravity_state.json').exists():
            import time
            mtime = (project_root / '.antigravity_state.json').stat().st_mtime
            last_mod = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
            st.text(f"{t('last_sync')}: {last_mod}")
st.sidebar.markdown('---')