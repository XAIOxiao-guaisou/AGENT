import streamlit as st
import json
import time
import os
from antigravity.infrastructure.state_manager import StateManager
from antigravity.utils.config import CONFIG
from pathlib import Path
try:
    from antigravity.infrastructure.debug_monitor import enable_monitoring, show_debug_panel
    enable_monitoring()
    DEBUG_MONITOR_ENABLED = True
except Exception as e:
    DEBUG_MONITOR_ENABLED = False
    print(f'Debug monitor initialization failed: {e}')
LANGUAGES = {'zh': {'page_title': 'Antigravity 监管面板', 'header': '🛡️ Antigravity 监管面板', 'sidebar_control': '⚙️ 系统控制', 'ai_mode': '🤖 AI 模式', 'select_mode': '选择提示词模式', 'apply_mode': '🔄 应用模式', 'mode_changed': '模式已切换为: {}. 重启监控器以应用。', 'environment': '🛡️ 环境', 'check_deps': '检查依赖', 'missing_deps': '缺失: {}', 'all_deps_ok': '所有依赖已满足!', 'status': '📊 状态', 'last_update': '最后更新: {}', 'recent_audits': '📋 最近审计', 'no_audits': '暂无审计历史', 'live_log': '🔍 实时审计日志', 'no_activity': '等待 Agent 活动...', 'last_error': '**最后错误:**', 'task_launcher': '🚀 任务发射台', 'task_definition': '📦 任务定义', 'target_file': '目标文件名', 'target_file_help': '文件必须位于 src/ 目录下且以 .py 结尾', 'task_name': '任务简称', 'task_name_help': '简短描述此任务的功能', 'auto_test': '自动创建测试文件', 'plan_details': '📜 计划详情 (PLAN.md)', 'plan_help': '详细描述功能需求、技术要求和测试要求', 'save_launch': '🔥 保存并启动', 'save_only': '💾 仅保存 PLAN', 'plan_saved': '✅ PLAN.md 已保存', 'save_failed': '保存失败: {}', 'error_no_file': '❌ 错误: 请输入目标文件名', 'error_not_py': '❌ 错误: 目标文件必须以 .py 结尾', 'error_not_src': '❌ 错误: 目标文件必须位于 src/ 目录下', 'error_no_plan': '❌ 错误: 请先在右侧输入任务计划', 'plan_updated': '✅ PLAN.md 已更新', 'file_created': '✅ 已创建目标文件: {}', 'file_exists': 'ℹ️ 文件已存在: {}', 'test_created': '✅ 已创建测试文件: {}', 'test_exists': 'ℹ️ 测试文件已存在: {}', 'task_launched': '🎯 **任务已发射!**\n\nMonitor 将在 3 秒后检测到变化并自动接管 `{}`\n\n**接下来会发生什么:**\n1. ✅ Monitor 检测到 PLAN.md 和新文件\n2. 🔍 Auditor 读取计划并分析需求\n3. 💻 Agent 自动编写完整代码\n4. 🧪 自动运行测试\n5. 🔄 如有错误,自动修复直至通过\n\n请在上方"最近审计"查看实时进度!', 'launch_failed': '❌ 启动失败: {}', 'env_status': '🔧 环境状态', 'env_ok': '✅ 所有依赖已满足 (检查时间: {})', 'env_missing': '⚠️ 缺失依赖 (检查时间: {})', 'no_env_check': '暂无环境检查记录', 'refresh': '🔄 刷新面板', 'powered_by': '由 DeepSeek-R1 & Antigravity Agent 驱动 | 自动刷新: 5秒', 'language': '🌐 语言 / Language', 'powered_by_p3': '由 P3 架构驱动', 'col_time': '时间', 'col_file': '文件', 'col_event': '事件', 'col_status': '状态', 'debug_monitor': '调试监控', 'today_errors': '今日错误', 'view_details': '查看详情', 'close_dashboard': '关闭仪表板', 'error_details': '错误详情', 'view_stack': '查看堆栈', 'view_similar': '查看相似', 'close': '关闭', 'error_analytics': '错误分析', 'total_errors': '总错误数', 'error_types': '错误类型', 'critical_errors': '严重错误', 'most_frequent': '最常见', 'error_trend': '错误趋势', 'error_list': '错误列表', 'no_errors': '没有错误记录', 'error_time': '时间', 'error_type': '类型', 'error_message': '消息', 'error_file': '文件', 'error_line': '行', 'error_severity': '严重性', 'scaffolding_launcher': '项目全自动发射台', 'project_name': '项目名称', 'project_name_placeholder': '例如: my_awesome_project', 'project_name_help': '输入项目名称,系统将自动创建标准 P3 结构', 'business_doc_upload': '业务文档上传', 'drag_drop_doc': '拖拽或点击上传文档', 'file_uploaded': '文件已上传', 'preview': '预览', 'project_plan': '项目计划', 'apply_to_project_plan': '应用到项目计划', 'plan_updated': '计划已更新', 'current_plan': '当前计划', 'plan_placeholder': '上传文档后显示计划内容...', 'create_and_launch': '创建并启动项目', 'error_no_project_name': '请输入项目名称', 'project_created': '项目 {} 创建成功!', 'created_files': '已创建的文件', 'auto_focusing_project': '正在自动聚焦到新项目...', 'project_auto_focused': '项目已自动聚焦', 'project_creation_failed': '项目创建失败: {}', 'placeholder_file': 'src/your_module.py', 'placeholder_task': '用户登录模块', 'project_launcher': '🚀 项目级发射台', 'project_files': '📁 项目结构定义', 'project_files_help': '输入项目涉及的文件路径 (每行一个)', 'upload_plan': '📤 业务文档上传', 'upload_plan_help': '上传需求文档 (.txt/.md),系统将自动更新至 PLAN.md', 'plan_template': '📜 PLAN 模板', 'template_source': '模板来源', 'use_current': '使用当前', 'use_default': '使用默认模板', 'reset_template': '🔄 重置为默认模板', 'template_reset': '✅ 模板已重置', 'launch_project': '🔥 启动项目级开发', 'error_no_files': '❌ 请输入项目文件列表', 'project_launched': '🎯 项目已发射! 共 {} 个文件', 'project_name_placeholder': '例如: XhsDataScraper', 'project_name_help': '系统将为您自动创建独立目录', 'project_structure': '项目内部结构', 'project_structure_help': '每行一个文件路径 (相对路径)', 'project_structure_placeholder': 'main.py\nutils/parser.py\nconfig.json\ntests/test_main.py', 'plan_placeholder': '# 项目计划\n\n请上传业务文档或手动编辑...', 'error_no_structure': '❌ 请定义项目结构', 'project_auto_takeover': '🌐 Monitor 将在 3 秒后检测到新项目并自动接管', 'project_center': '项目指挥中心', 'active_project': '活跃项目', 'loading_project_context': '正在加载项目上下文...', 'project_loaded': '项目已加载', 'project_load_failed': '项目加载失败', 'project_info': '项目信息', 'no_plan_found': '⚠️ 未找到 PLAN.md', 'files': '文件数', 'last_sync': '最后同步', 'auto_focusing_project': '正在自动切换到新项目...', 'project_auto_focused': '项目已自动聚焦', 'vibe_check_button': '🩺 运行 Vibe Check', 'generate_docs_button': '📄 生成文档', 'docs_generated': '文档生成成功!', 'vibe_check_running': '正在运行 Vibe Check...', 'vibe_check_complete': 'Vibe Check 完成!', 'health_score': '健康度评分', 'issues_found': '发现的问题', 'recommendations': '改进建议', 'generating_docs': '正在生成项目文档...', 'performance_monitor': '性能监控', 'performance_stats': '性能统计', 'total_operations': '总操作数', 'total_calls': '总调用次数', 'avg_time': '平均耗时', 'total_time': '总耗时', 'slowest_operations': '最慢操作', 'no_operations': '暂无操作记录', 'operation': '操作', 'calls': '调用次数', 'perf_not_available': '性能监控在全局模式下不可用', 'switch_to_project': '请切换到具体项目以查看性能数据', 'token_usage': 'Token 使用估算', 'recent_executions': '最近执行', 'success_rate': '成功率', 'project_config': '⚙️ 项目配置', 'allowed_roots': '允许的代码根目录 (用逗号分隔)', 'allowed_roots_help': '出于安全考虑,Agent 只能在这些指定的目录下创建文件。例如: src, tests, docs', 'current_allowed': '当前允许的路径前缀: {}', 'drag_upload_hint': '(支持拖拽上传)', 'unauthorized_path': '⚠️ 跳过未授权路径: {}\n(请在侧边栏配置中添加该目录)', 'no_files_created': '没有创建任何新文件（可能路径不合法或文件已存在）。', 'files_created_list': '📋 已创建文件列表', 'monitor_will_detect': '🌐 Monitor 将在约 3 秒后检测到这些文件并触发项目级同步...', 'p3_monitor': '📊 P3 性能监控', 'total_operations_help': '已监控的操作总数', 'total_calls_help': '所有操作的总调用次数', 'total_time_help': '所有操作的总耗时', 'token_estimated': '预估: {}/{} tokens ({:.1f}%) | PLAN: {} | 输出: {}', 'token_high': '⚠️ Token 使用率很高。考虑减少 PLAN.md 复杂度或使用增量同步。', 'token_moderate': 'ℹ️ Token 使用率中等。P3 优化将帮助减少上下文大小。', 'token_healthy': '✅ Token 使用率健康。P3 优化运行良好。', 'token_error': 'Token 估算失败: {}', 'plan_not_found': '未找到 PLAN.md。Token 估算不可用。', 'no_recent_exec': '暂无最近执行记录。', 'perf_monitor_unavailable': '性能监控器不可用: {}', 'perf_data_error': '加载性能数据失败: {}'}, 'en': {'page_title': 'Antigravity Dashboard', 'header': '🛡️ Antigravity Sheriff Monitor', 'sidebar_control': '⚙️ System Control', 'ai_mode': '🤖 AI Mode', 'select_mode': 'Select Prompt Mode', 'apply_mode': '🔄 Apply Mode', 'mode_changed': 'Mode changed to: {}. Restart monitor to apply.', 'environment': '🛡️ Environment', 'check_deps': 'Check Dependencies', 'missing_deps': 'Missing: {}', 'all_deps_ok': 'All dependencies satisfied!', 'status': '📊 Status', 'last_update': 'Last update: {}', 'recent_audits': '📋 Recent Audits', 'no_audits': 'No audit history yet', 'live_log': '🔍 Live Audit Log', 'no_activity': 'Waiting for agent activity...', 'last_error': '**Last Error:**', 'task_launcher': '🚀 Task Launcher', 'task_definition': '📦 Task Definition', 'target_file': 'Target File', 'target_file_help': 'File must be in src/ directory and end with .py', 'task_name': 'Task Name', 'task_name_help': 'Brief description of this task', 'auto_test': 'Auto-create test file', 'plan_details': '📜 Plan Details (PLAN.md)', 'plan_help': 'Describe requirements, technical specs, and testing needs', 'save_launch': '🔥 Save & Launch', 'save_only': '💾 Save PLAN Only', 'plan_saved': '✅ PLAN.md saved', 'save_failed': 'Save failed: {}', 'error_no_file': '❌ Error: Please enter target file name', 'error_not_py': '❌ Error: Target file must end with .py', 'error_not_src': '❌ Error: Target file must be in src/ directory', 'error_no_plan': '❌ Error: Please enter task plan first', 'plan_updated': '✅ PLAN.md updated', 'file_created': '✅ Created target file: {}', 'file_exists': 'ℹ️ File already exists: {}', 'test_created': '✅ Created test file: {}', 'test_exists': 'ℹ️ Test file already exists: {}', 'task_launched': '🎯 **Task Launched!**\n\nMonitor will detect changes in 3 seconds and auto-takeover `{}`\n\n**What happens next:**\n1. ✅ Monitor detects PLAN.md and new file\n2. 🔍 Auditor reads plan and analyzes requirements\n3. 💻 Agent auto-writes complete code\n4. 🧪 Auto-runs tests\n5. 🔄 Auto-fixes errors until passing\n\nCheck "Recent Audits" above for live progress!', 'launch_failed': '❌ Launch failed: {}', 'env_status': '🔧 Environment Status', 'env_ok': '✅ All dependencies satisfied (checked: {})', 'env_missing': '⚠️ Missing dependencies (checked: {})', 'no_env_check': 'No environment checks performed yet', 'refresh': '🔄 Refresh Dashboard', 'powered_by': 'Powered by DeepSeek-R1 & Antigravity Agent | Auto-refresh: 5s', 'language': '🌐 Language / 语言', 'powered_by_p3': 'Powered by P3 Architecture', 'col_time': 'Time', 'col_file': 'File', 'col_event': 'Event', 'col_status': 'Status', 'debug_monitor': 'Debug Monitor', 'today_errors': "Today's Errors", 'view_details': 'View Details', 'close_dashboard': 'Close Dashboard', 'error_details': 'Error Details', 'view_stack': 'View Stack', 'view_similar': 'View Similar', 'close': 'Close', 'error_analytics': 'Error Analytics', 'total_errors': 'Total Errors', 'error_types': 'Error Types', 'critical_errors': 'Critical', 'most_frequent': 'Most Frequent', 'error_trend': 'Error Trend', 'error_list': 'Error List', 'no_errors': 'No errors recorded', 'error_time': 'Time', 'error_type': 'Type', 'error_message': 'Message', 'error_file': 'File', 'error_line': 'Line', 'error_severity': 'Severity', 'scaffolding_launcher': 'Automated Project Scaffolding', 'project_name': 'Project Name', 'project_name_placeholder': 'e.g., my_awesome_project', 'project_name_help': 'Enter project name, system will auto-create standard P3 structure', 'business_doc_upload': 'Business Document Upload', 'drag_drop_doc': 'Drag and drop or click to upload', 'file_uploaded': 'File uploaded', 'preview': 'Preview', 'project_plan': 'Project Plan', 'apply_to_project_plan': 'Apply to Project Plan', 'plan_updated': 'Plan updated', 'current_plan': 'Current Plan', 'plan_placeholder': 'Plan content will appear after document upload...', 'create_and_launch': 'Create & Launch', 'error_no_project_name': 'Please enter project name', 'project_created': 'Project {} created successfully!', 'created_files': 'Created Files', 'auto_focusing_project': 'Auto-focusing on new project...', 'project_auto_focused': 'Project auto-focused', 'project_creation_failed': 'Project creation failed: {}', 'placeholder_file': 'src/your_module.py', 'placeholder_task': 'User Login Module', 'project_launcher': '🚀 Project Launcher', 'project_files': '📁 Project Structure', 'project_files_help': 'Enter project file paths (one per line)', 'upload_plan': '📤 Upload Plan', 'upload_plan_help': 'Upload requirement document (.txt/.md), will update PLAN.md', 'file_uploaded': '✅ File uploaded', 'preview': 'Preview', 'apply_to_plan': 'Apply to PLAN.md', 'plan_template': '📜 PLAN Template', 'template_source': 'Template Source', 'use_current': 'Use Current', 'use_default': 'Use Default Template', 'reset_template': '🔄 Reset to Default', 'template_reset': '✅ Template reset', 'current_plan': 'Current PLAN', 'launch_project': '🔥 Launch Project Development', 'error_no_files': '❌ Please enter project file list', 'project_launched': '🎯 Project launched! {} files created', 'scaffolding_launcher': '🚀 Automated Project Scaffolding', 'project_name': 'Project Name', 'project_name_placeholder': 'e.g: XhsDataScraper', 'project_name_help': 'System will auto-create dedicated directory', 'error_no_project_name': '❌ Please enter project name', 'project_structure': 'Internal Structure', 'project_structure_help': 'One file path per line (relative paths)', 'project_structure_placeholder': 'main.py\\nutils/parser.py\\nconfig.json\\ntests/test_main.py', 'business_doc_upload': '📤 Business Document Upload', 'drag_drop_doc': 'Drag & Drop Document (.txt/.md)', 'apply_to_project_plan': 'Apply to Project Plan', 'project_plan': '📜 Project Plan', 'current_plan': 'Current Plan', 'plan_placeholder': '# Project Plan\\n\\nPlease upload business document or edit manually...', 'create_and_launch': '🔥 Create Project & Launch Auto-Takeover', 'error_no_structure': '❌ Please define project structure', 'project_created': '✅ Project `{}` initialized successfully in dedicated folder!', 'created_files': '📋 Created Files', 'project_auto_takeover': '🌐 Monitor will detect new project in ~3s and auto-takeover', 'project_creation_failed': '❌ Project creation failed: {}', 'project_center': 'Project Center', 'active_project': 'Active Project', 'loading_project_context': 'Loading project context...', 'project_loaded': 'Project loaded', 'project_load_failed': 'Project load failed', 'project_info': 'Project Info', 'no_plan_found': '⚠️ No PLAN.md found', 'files': 'Files', 'last_sync': 'Last Sync', 'auto_focusing_project': 'Auto-focusing on new project...', 'project_auto_focused': 'Project auto-focused', 'vibe_check_button': '🩺 Run Vibe Check', 'generate_docs_button': '📄 Generate Docs', 'docs_generated': 'Documentation generated successfully!', 'vibe_check_running': 'Running Vibe Check...', 'vibe_check_complete': 'Vibe Check Complete!', 'health_score': 'Health Score', 'issues_found': 'Issues Found', 'recommendations': 'Recommendations', 'generating_docs': 'Generating project documentation...', 'performance_monitor': 'Performance Monitor', 'performance_stats': 'Performance Stats', 'total_operations': 'Total Operations', 'total_calls': 'Total Calls', 'avg_time': 'Avg Time', 'total_time': 'Total Time', 'slowest_operations': 'Slowest Operations', 'no_operations': 'No operations recorded yet', 'operation': 'Operation', 'calls': 'Calls', 'perf_not_available': 'Performance monitor not available in Global mode', 'switch_to_project': 'Please switch to a specific project to view performance data', 'token_usage': 'Token Usage Estimation', 'recent_executions': 'Recent Executions', 'success_rate': 'Success Rate', 'project_config': '⚙️ Project Config', 'allowed_roots': 'Allowed Code Root Directories (comma-separated)', 'allowed_roots_help': 'For security, Agent can only create files in these specified directories. E.g., src, tests, docs', 'current_allowed': 'Current allowed path prefixes: {}', 'drag_upload_hint': '(Drag & drop upload supported)', 'unauthorized_path': '⚠️ Skipping unauthorized path: {}\n(Please add this directory in sidebar config)', 'no_files_created': 'No new files created (path might be invalid or file already exists).', 'files_created_list': '📋 Created Files List', 'monitor_will_detect': '🌐 Monitor will detect these files in ~3 seconds and trigger project-level sync...', 'p3_monitor': '📊 P3 Performance Monitor', 'total_operations_help': 'Total number of operations monitored', 'total_calls_help': 'Total calls across all operations', 'total_time_help': 'Total time spent across all operations', 'token_estimated': 'Estimated: {}/{} tokens ({:.1f}%) | PLAN: {} | Output: {}', 'token_high': '⚠️ High token usage. Consider reducing PLAN.md complexity or using incremental sync.', 'token_moderate': 'ℹ️ Moderate token usage. P3 optimization helps reduce context size.', 'token_healthy': '✅ Healthy token usage. P3 optimization is working well.', 'token_error': 'Token estimation failed: {}', 'plan_not_found': 'PLAN.md not found. Token estimation unavailable.', 'no_recent_exec': 'No recent executions recorded.', 'perf_monitor_unavailable': 'Performance monitor unavailable: {}', 'perf_data_error': 'Failed to load performance data: {}'}}
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

def t(key):
    """翻译函数 / Translation function"""
    return LANGUAGES[st.session_state.language].get(key, key)
st.set_page_config(page_title=t('page_title'), layout='wide', page_icon='🛡️')
st.title(t('header'))

@st.cache_resource
def get_state_manager():
    return StateManager('.')
state_mgr = get_state_manager()
st.sidebar.header(t('sidebar_control'))
st.sidebar.subheader(t('language'))
lang_options = {'中文': 'zh', 'English': 'en'}
selected_lang = st.sidebar.radio('Language', options=list(lang_options.keys()), index=0 if st.session_state.language == 'zh' else 1, horizontal=True, label_visibility="collapsed")
if lang_options[selected_lang] != st.session_state.language:
    st.session_state.language = lang_options[selected_lang]
    st.rerun()
st.sidebar.subheader(t('ai_mode'))
prompts = CONFIG.get('prompts', {})
modes = list(prompts.get('modes', {}).keys())
current_mode = CONFIG.get('ACTIVE_MODE', 'executor')
selected_mode = st.sidebar.selectbox(t('select_mode'), modes, index=modes.index(current_mode) if current_mode in modes else 0)
if st.sidebar.button(t('apply_mode')):
    st.sidebar.info(t('mode_changed').format(selected_mode))
st.sidebar.subheader(t('environment'))
if st.sidebar.button(t('check_deps')):
    from antigravity.utils.env_checker import check_dependencies
    if os.path.exists('PLAN.md'):
        with open('PLAN.md', 'r', encoding='utf-8') as f:
            missing = check_dependencies(f.read())
        if missing:
            st.sidebar.warning(t('missing_deps').format(', '.join(missing)))
        else:

            st.sidebar.success(t('all_deps_ok'))
st.sidebar.markdown('---')
st.sidebar.subheader("🛠️ 物理调度 (Physical Dispatch)")

if st.sidebar.button("🎨 唤起 Antigravity 编辑器", use_container_width=True):
    editor_path = CONFIG.get('EDITOR_PATH', "D:\\桌面\\Antigravity.lnk")
    if os.path.exists(editor_path):
        os.startfile(editor_path)
        st.sidebar.success("✅ 已向物理层发送唤起指令")
    else:
        st.sidebar.error("❌ 未找到 Antigravity.lnk，请检查配置路径")

# 实时显示 DeepSeek 决策链
if 'active_state_mgr' in st.session_state:
    try:
        # Get current status from manager? Or just assume from session state if we had it.
        # But here we just want to show the warning if needed.
        # We can verify if system status says "GENERATING" (mapped from Orchestrator?)
        # For now, following user instruction "if st.session_state.get('current_state') ..."
        if st.session_state.get('current_state') == 'GENERATING':
             st.warning("⚠️ DeepSeek 正在操作 Antigravity 进行物理写入...")
    except:
        pass
st.sidebar.subheader('🚢 ' + t('project_center'))

# Phase 11: Fleet Commander Integration
from antigravity.core.fleet_manager import ProjectFleetManager
fleet_mgr = ProjectFleetManager.get_instance()

# 1. Scan Workspace (Heartbeat)
# In a real app, we might scan on startup or explicit refresh. 
# Here we scan periodically to discover new projects.
fleet_mgr.scan_workspace(CONFIG.get('PROJECTS_DIR', 'projects'))

# 2. Get Fleet Status
fleet_status = fleet_mgr.get_fleet_status()
project_options = ['Global (Legacy)'] + [p['project_id'] for p in fleet_status]
project_map = {p['project_id']: p for p in fleet_status}

formatted_options = []
for opt in project_options:
    if opt == 'Global (Legacy)':
        formatted_options.append('🌐 Global (Legacy)')
    else:
        # Fleet Integrity Indicators
        p_meta = project_map.get(opt, {})
        status = p_meta.get('status', 'ACTIVE')
        
        # Visual Mapping
        icon = '⚪'
        if status == 'CERTIFIED': icon = '🟢'
        elif status == 'TAMPERED': icon = '🔴'
        elif status == 'ACTIVE': icon = '🟡'
        elif status == 'PAUSED': icon = '⏸️'
        
        formatted_options.append(f'{icon} {opt}')

# 2.5 Fleet Integrity Check (Active Project)
current_active = fleet_mgr.active_project_id
if current_active and current_active != 'Global (Legacy)':
    integrity_data = fleet_mgr.verify_fleet_integrity(current_active)
    fleet_status_code = integrity_data.get('status', 'ACTIVE')
    
    if fleet_status_code == 'CONTAMINATED':
        st.sidebar.error(f"☣️ FLEET POLLUTION DETECTED!", icon="☣️")
        with st.sidebar.expander("📡 Dependency Radar (ALERT)", expanded=True):
            st.markdown(f"**Status**: {fleet_status_code}")
            st.markdown("**Violations**:")
            for v in integrity_data.get('violations', []):
                st.markdown(f"- 🔴 {v}")
            st.markdown("---")
            st.markdown(f"**Dependencies**: {len(integrity_data.get('dependencies', []))}")
            for d in integrity_data.get('dependencies', []):
                 st.code(d)
    elif fleet_status_code == 'TAMPERED':
        st.sidebar.error(f"🔴 SECURITY BREACH DETECTED!", icon="🔴")
    elif integrity_data.get('dependencies'):
        with st.sidebar.expander(f"📡 Dependency Radar ({len(integrity_data['dependencies'])})"):
             for d in integrity_data['dependencies']:
                 st.code(d)
current_active_id = fleet_mgr.active_project_id
default_index = 0
if current_active_id and current_active_id in project_options:
    default_index = project_options.index(current_active_id)

selected_index = st.sidebar.selectbox(
    t('active_project'), 
    range(len(formatted_options)), 
    format_func=lambda i: formatted_options[i], 
    index=default_index,
    key='fleet_project_selector'
)
selected_project_id = project_options[selected_index]

# 4. Atomic Switch Trigger
if selected_project_id != 'Global (Legacy)':
    # Check if we need to switch
    if selected_project_id != fleet_mgr.active_project_id:
        success = fleet_mgr.switch_project(selected_project_id)
        if success:
            st.toast(f"🚢 Fleet: Switched to {selected_project_id}", icon="✅")
            # Telemetry Flush handled by switch_project
            # Rerun to refresh UI context
            time.sleep(0.5) # Let visual toast linger
            st.rerun()
            
    # Load Context for Dashboard Views
    p_meta = project_map[selected_project_id]
    project_root = Path(p_meta['path'])
    st.session_state.active_project_root = project_root
    
    # Initialize/Get Managers
    try:
        if 'active_state_mgr' not in st.session_state or st.session_state.active_project_root != project_root:
             st.session_state.active_state_mgr = P3StateManager(project_root)
        
        # Performance Monitor
        try:
            from antigravity.infrastructure.performance_monitor import PerformanceMonitor
            st.session_state.active_perf_monitor = PerformanceMonitor(str(project_root))
        except:
            st.session_state.active_perf_monitor = None
            
    except Exception as e:
        st.sidebar.error(f"⚠️ {t('project_load_failed')}: {e}")
        st.session_state.active_project_root = Path('.')
        
else:
    # Legacy Global Mode
    st.session_state.active_project_root = Path('.')
    st.session_state.active_state_mgr = state_mgr
    st.session_state.active_perf_monitor = None

if selected_project_id != 'Global (Legacy)':
    project_root = st.session_state.active_project_root
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
    st.sidebar.markdown('### 🛠️ Quick Actions')
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button(t('vibe_check_button'), use_container_width=True):
            from antigravity.utils.vibe_check import VibeChecker
            with st.status(t('vibe_check_running'), expanded=True) as status:
                checker = VibeChecker(project_root)
                results = checker.diagnose()
                status.update(label=f"{t('vibe_check_complete')}: {results['percentage']:.0f}%", state='complete')
            st.sidebar.metric(t('health_score'), f"{results['percentage']:.0f}%", delta=results['grade'])
            st.sidebar.caption(f"**Status**: {results['status']}")
            if results['issues']:
                with st.sidebar.expander(f"⚠️ {t('issues_found')} ({len(results['issues'])})"):
                    for issue in results['issues']:
                        st.text(issue)
            if results['recommendations']:
                with st.sidebar.expander(f"💡 {t('recommendations')} ({len(results['recommendations'])})"):
                    for rec in results['recommendations']:
                        st.text(rec)
    with col2:
        if st.button(t('generate_docs_button'), use_container_width=True):
            from antigravity.utils.doc_generator import DocGenerator
            with st.spinner(t('generating_docs')):
                gen = DocGenerator(project_root)
                readme_content = gen.generate_readme()
                (project_root / 'README.md').write_text(readme_content, encoding='utf-8')
                req_content = gen.generate_requirements()
                if req_content:
                    (project_root / 'requirements.txt').write_text(req_content, encoding='utf-8')
                st.sidebar.success(t('docs_generated'))
st.sidebar.markdown('---')
st.sidebar.markdown('---')
st.sidebar.subheader(t('project_config'))
allowed_roots_input = st.sidebar.text_input(t('allowed_roots'), value='src, tests', help=t('allowed_roots_help'))
ALLOWED_ROOTS = [root.strip() + '/' for root in allowed_roots_input.split(',') if root.strip()]
st.sidebar.caption(t('current_allowed').format(', '.join(ALLOWED_ROOTS)))
st.session_state.allowed_roots = ALLOWED_ROOTS
st.sidebar.subheader(t('status'))
system_status = state_mgr.get_system_status()
takeover_status = system_status.get('takeover_status', 'Unknown')
status_colors = {'Idle': '🟢', 'Writing': '🟡', 'Testing': '🔵', 'Error': '🔴'}
st.sidebar.markdown(f"{status_colors.get(takeover_status, '⚪')} **{takeover_status}**")
last_update = system_status.get('last_update', 'Never')
st.sidebar.caption(t('last_update').format(last_update[:19] if last_update != 'Never' else 'Never'))
if st.session_state.get('show_audit_logs', False):
    col1, col2 = st.columns(2)
    with col1:
        audits = state_mgr.get_recent_audits(limit=20)
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.markdown(f"### 📋 {t('recent_audits')} ({len(audits)})")
        with header_col2:
            if st.button('🗑️ 清空', key='clear_audits_btn', help='清空所有审计日志'):
                try:
                    state_mgr.audit_log = []
                    state_mgr.save_state()
                    st.success('✅ 审计日志已清空')
                    st.rerun()
                except Exception as e:
                    st.error(f'清空失败: {e}')
        with st.expander(f'展开查看详情', expanded=False):
            if audits:
                for audit in reversed(audits[-15:]):
                    file_name = audit.get('file_path', 'Unknown').split('/')[-1]
                    event_type = audit.get('event_type', 'unknown')
                    timestamp = audit.get('timestamp', '')[:19]
                    status = audit.get('status', 'INFO')
                    icon = {'SUCCESS': '✅', 'ERROR': '❌', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(status, '📝')
                    with st.expander(f'{icon} {file_name} - {event_type}', expanded=False):
                        st.caption(f'⏰ {timestamp}')
                        st.text(audit.get('message', '')[:200])
            else:
                st.info(t('no_activity'))
    with col2:
        st.subheader(t('live_log'))
        if audits:
            import pandas as pd
            df_data = []
            for audit in reversed(audits[-10:]):
                df_data.append({t('col_time'): audit.get('timestamp', '')[:19], t('col_file'): audit.get('file_path', ''), t('col_event'): audit.get('event_type', ''), t('col_status'): audit.get('status', '')})
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, hide_index=True)
        else:
            st.info(t('no_activity'))
        last_error = system_status.get('last_error_log')
        if last_error:
            st.error(t('last_error'))
            st.code(last_error[:500], language='text')
st.header(t('task_launcher'))
with st.container():
    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        st.subheader(t('task_definition'))
        target_file = st.text_input(t('target_file'), placeholder=t('placeholder_file'), help=t('target_file_help'))
        task_name = st.text_input(t('task_name'), placeholder=t('placeholder_task'))
        create_test = st.checkbox(t('auto_test'), value=True)
    with t_col2:
        st.subheader(t('plan_details'))
        task_plan = st.text_area(t('plan_details'), placeholder=t('plan_placeholder'), height=200, help=t('plan_help'))
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        launch_button = st.button(t('save_launch'), type='primary', use_container_width=True)
    with col_btn2:
        if st.button(t('save_only'), use_container_width=True):
            try:
                with open('PLAN.md', 'w', encoding='utf-8') as f:
                    f.write(task_plan)
                st.success(t('plan_saved'))
            except Exception as e:
                st.error(t('save_failed').format(e))
    if launch_button:
        # 1. Get Active Project Root
        active_root = st.session_state.get('active_project_root', Path('.'))
        
        # 2. Check Authorization (Phase 26 Hardening)
        # Check if active_root is within allowed roots or if we are in Legacy Global Mode logic
        # For P3, we trust active_project_root if it was set via the selector.
        
        if not target_file:
            st.error(t('error_no_file'))
        elif not target_file.endswith('.py'):
            st.error(t('error_not_py'))
        # PHASE 26 FIX: Remove hardcoded startswith('src/') check.
        # Check if target is valid relative path
        elif '..' in target_file or target_file.startswith('/'):
             st.error("Invalid target file path.")
        elif not task_plan.strip():
            st.error(t('error_no_plan'))
        else:
            try:
                # Define full paths
                plan_path = active_root / 'PLAN.md'
                target_path = active_root / target_file
                
                # Write PLAN.md
                # Append or overwrite? Dashboard usually overwrites the "Current Plan".
                # But creating a *task* often implies updating the main plan or a task specific plan?
                # The generic logic writes to 'PLAN.md' in root.
                with open(plan_path, 'w', encoding='utf-8') as f:
                    f.write(task_plan)
                st.success(t('plan_updated'))
                
                # Create Target File
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if not target_path.exists():
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {task_name or 'Auto-generated by Antigravity'}\n# TODO: Implement\n")
                    st.success(t('file_created').format(target_file))
                else:
                    st.info(t('file_exists').format(target_file))
                
                # Test Creation (Optional)
                if create_test:
                    test_name = f'test_{target_path.stem}.py'
                    test_path = active_root / 'tests' / test_name
                    (active_root / 'tests').mkdir(exist_ok=True)
                    
                    if not test_path.exists():
                        with open(test_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Test for {target_file}\nimport unittest\n\nclass Test{task_name.replace(' ', '')}(unittest.TestCase):\n    def test_placeholder(self):\n        pass\n\nif __name__ == '__main__':\n    unittest.main()\n")
                        st.success(t('test_created').format(test_name))
                    else:
                        st.info(t('test_exists').format(test_name))
                
                # 4. Inject into Mission Orchestrator (Phase 26)
                from antigravity.core.mission_orchestrator import MissionOrchestrator, AtomicTask, TaskState
                from datetime import datetime
                
                orchestrator = MissionOrchestrator(str(active_root))
                # Try load existing state
                state_path = active_root / ".antigravity" / "mission_state.json"
                if state_path.exists():
                    try:
                        orchestrator.load_state(str(state_path))
                    except:
                        pass # Ignore corrupted state, start fresh or append
                
                new_task = AtomicTask(
                    task_id=f"task_{int(datetime.now().timestamp())}",
                    type='code',
                    goal=task_plan,
                    metadata={'file_path': target_file, 'created_via': 'dashboard'},
                    state=TaskState.PENDING
                )
                
                orchestrator.tasks.append(new_task)
                
                # Trigger First Step (PENDING -> ANALYZING)
                orchestrator.step(new_task)
                
                # Save State
                (active_root / ".antigravity").mkdir(exist_ok=True)
                orchestrator.save_state(str(state_path))
                
                st.balloons()
                st.success(t('task_launched').format(target_file))
                
                # Log to P3 Audit
                state_mgr.log_audit(str(target_path), 'task_launched', f"Task '{task_name}' injected into Orchestrator", 'INFO')
                
                # Phase 27: Telemetry Signal (Wake-up Alignment)
                try:
                    from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
                    TelemetryQueue.push_event(TelemetryEventType.TASK_INITIATED, {
                        "task_id": new_task.task_id,
                        "file": str(target_file),
                        "goal": task_name
                    })
                except Exception:
                    pass
                
            except Exception as e:
                st.error(t('launch_failed').format(e))
                import traceback
                st.code(traceback.format_exc(), language='python')
st.header('🚀 ' + t('scaffolding_launcher'))
with st.container():
    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        project_name = st.text_input(t('project_name'), placeholder=t('project_name_placeholder'), help=t('project_name_help'), key='p3_project_name')
        st.info('ℹ️ 系统将自动创建标准 P3 项目结构 / System will auto-create standard P3 project structure')
        st.caption('包含: main.py, core/, utils/, config/, tests/, data/ / Includes: main.py, core/, utils/, config/, tests/, data/')
        st.subheader('📤 ' + t('business_doc_upload'))
        uploaded_file = st.file_uploader(t('drag_drop_doc'), type=['txt', 'md'], key='p3_doc_uploader')
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.success('✅ ' + t('file_uploaded'))
            with st.expander('👁️ ' + t('preview')):
                st.text(content[:500] + '...' if len(content) > 500 else content)
            st.session_state.p3_plan_content = content
    with p_col2:
        st.subheader('📜 ' + t('project_plan'))
        if st.session_state.get('p3_plan_content') and st.button(t('apply_to_project_plan'), key='p3_apply_plan'):
            st.success(t('plan_updated'))
        plan_display = st.session_state.get('p3_plan_content', t('plan_placeholder'))
        st.text_area(t('current_plan'), value=plan_display, height=350, disabled=True, key='p3_plan_display')
    if st.button(t('create_and_launch'), type='primary', use_container_width=True, key='p3_create_btn'):
        st.session_state.show_audit_logs = True
        if not project_name:
            st.error(t('error_no_project_name'))
        else:
            try:
                project_path = os.path.join('projects', project_name)
                os.makedirs(project_path, exist_ok=True)
                standard_dirs = ['core', 'utils', 'config', 'tests', 'data']
                for dir_name in standard_dirs:
                    os.makedirs(os.path.join(project_path, dir_name), exist_ok=True)
                template_path = 'PLAN.md'
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    plan_content = template_content.replace('{{PROJECT_NAME}}', project_name)
                    plan_content = plan_content.replace('{{MODULE_NAME}}', f'{project_name.lower()}_core')
                    if st.session_state.get('p3_plan_content'):
                        plan_content += f'\n\n---\n\n## 用户需求文档\n\n{st.session_state.p3_plan_content}'
                else:
                    plan_content = st.session_state.get('p3_plan_content', f'# {project_name} Project Plan\n\nTODO: Define requirements')
                with open(os.path.join(project_path, 'PLAN.md'), 'w', encoding='utf-8') as f:
                    f.write(plan_content)
                standard_files = {'main.py': f'# {project_name} - Main Entry Point\n# Auto-generated by Antigravity P3\n\nfrom pathlib import Path\nimport sys\n\n# Add project root to path\nproject_root = Path(__file__).parent\nsys.path.insert(0, str(project_root))\n\ndef main():\n    """Main entry point"""\n    print(f"🚀 {project_name} starting...")\n    # TODO: Implement according to PLAN.md\n    pass\n\nif __name__ == "__main__":\n    main()\n', 'core/__init__.py': f'# {project_name} Core Module\n', f'core/{project_name.lower()}_core.py': f'# {project_name} - Core Logic\n# Auto-generated by Antigravity P3\n\nfrom typing import Dict, List, Optional\n\nclass {project_name}Core:\n    """Core business logic for {project_name}"""\n    \n    def __init__(self):\n        """Initialize core module"""\n        pass\n    \n    def process(self, data: Dict) -> Optional[Dict]:\n        """\n        Process data according to PLAN.md requirements\n        \n        Args:\n            data: Input data dictionary\n            \n        Returns:\n            Processed result or None\n        """\n        # TODO: Implement according to PLAN.md\n        return None\n', 'utils/__init__.py': f'# {project_name} Utilities\n', 'utils/helpers.py': f'''# {project_name} - Helper Functions\n# Auto-generated by Antigravity P3\n\nfrom typing import Any\nfrom pathlib import Path\n\ndef get_project_root() -> Path:\n    """Get project root directory"""\n    return Path(__file__).parent.parent\n\ndef load_config(config_path: str = "config/settings.json") -> dict:\n    """Load configuration from JSON file"""\n    import json\n    config_file = get_project_root() / config_path\n    if config_file.exists():\n        with open(config_file, 'r', encoding='utf-8') as f:\n            return json.load(f)\n    return {{}}\n''', 'config/settings.json': f'{{\n    "project_name": "{project_name}",\n    "version": "1.0.0",\n    "debug": true\n}}\n', 'tests/__init__.py': f'# {project_name} Tests\n', f'tests/test_{project_name.lower()}_core.py': f'''# Tests for {project_name} Core\n# Auto-generated by Antigravity P3\n\nimport unittest\nimport sys\nfrom pathlib import Path\n\n# Add project root to path\nproject_root = Path(__file__).parent.parent\nsys.path.insert(0, str(project_root))\n\n# Enable debug monitoring / 启用调试监控\nfrom antigravity.debug_monitor import enable_monitoring, show_debug_panel\nenable_monitoring()\n\nfrom antigravity.p3_state_manager import P3StateManager\nfrom antigravity.vibe_check import VibeChecker\nfrom antigravity.performance_monitor import PerformanceMonitor\nfrom core.{project_name.lower()}_core import {project_name}Core\n\nclass Test{project_name}Core(unittest.TestCase):\n    def setUp(self):\n        self.core = {project_name}Core()\n    \n    def test_initialization(self):\n        """Test core module initialization"""\n        self.assertIsNotNone(self.core)\n    \n    def test_process(self):\n        """Test process method"""\n        # TODO: Add real tests according to PLAN.md\n        result = self.core.process({{}})\n        self.assertIsNone(result)  # Placeholder\n\nif __name__ == '__main__':\n    unittest.main()\n''', 'data/.gitkeep': '# Data directory\n'}
                created_files = []
                for file_path, content in standard_files.items():
                    full_path = os.path.join(project_path, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created_files.append(file_path)
                    
                # ---------------------------------------------------------
                # Phase 28: Scaffolding Ignition (v2.1.4)
                # ---------------------------------------------------------
                
                # 1. Initialize Mission Orchestrator
                from antigravity.core.mission_orchestrator import MissionOrchestrator, AtomicTask, TaskState
                from datetime import datetime
                
                orch = MissionOrchestrator(project_path)
                
                # 1a. Record Scaffolding Task (DONE)
                scaffold_task = AtomicTask(
                    task_id=f"task_{int(datetime.now().timestamp())}_scaffold",
                    type="scaffold",
                    goal=f"Initialize {project_name} structure",
                    state=TaskState.DONE,
                    metadata={'created_via': 'scaffolding_launcher'}
                )
                orch.tasks.append(scaffold_task)
                
                # 1b. Create Initial Analysis Task (PENDING) -> Triggers Monitor
                # If user provided a plan, we should ANALYZE it.
                # If not, we still create a "Review Structure" task to test the loop.
                init_goal = "Analyze Project Requirements" if st.session_state.get('p3_plan_content') else "Review Project Structure"
                
                init_task = AtomicTask(
                    task_id=f"task_{int(datetime.now().timestamp())}_init",
                    type="plan",
                    goal=init_goal,
                    state=TaskState.PENDING,
                    metadata={'file_path': 'PLAN.md'}
                )
                orch.tasks.append(init_task)
                
                # Save State
                (Path(project_path) / ".antigravity").mkdir(exist_ok=True)
                orch.save_state(str(os.path.join(project_path, ".antigravity", "mission_state.json")))

                # v2.1.9: Heartbeat Pulse - Force Backend Reload
                # 强制清除旧 Checkpoint，迫使 Monitor 感知新任务
                checkpoint_path = Path(project_path) / ".antigravity" / "checkpoints" / f"{init_task.task_id}.json"
                if checkpoint_path.exists():
                    checkpoint_path.unlink()
                
                # 2. Register & Switch Context
                state_mgr.register_project(project_path)
                st.session_state.active_project_root = Path(project_path).resolve()
                
                # 3. Telemetry Ignition
                try:
                    from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
                    TelemetryQueue.push_event(TelemetryEventType.PROJECT_CREATED, {
                        "project": project_name,
                        "path": project_path
                    })
                    TelemetryQueue.push_event(TelemetryEventType.TASK_INITIATED, {
                        "task_id": init_task.task_id,
                        "goal": init_goal,
                        "project": project_name
                    })
                except Exception:
                    pass
                
                st.success(f"🚀 Project {project_name} Launched & Ignited!")
                st.balloons()
                time.sleep(1.0)
                st.rerun()

            except Exception as e:
                st.error(t('project_creation_failed').format(e))
                import traceback
                st.code(traceback.format_exc(), language='python')
st.subheader(t('env_status'))
last_env_check = state_mgr.get_last_environment_check()
if last_env_check:
    success = last_env_check.get('success', False)
    missing_deps = last_env_check.get('missing_dependencies', [])
    timestamp = last_env_check.get('timestamp', '')[:19]
    if success:
        st.success(t('env_ok').format(timestamp))
    else:
        st.warning(t('env_missing').format(timestamp))
        for dep in missing_deps:
            st.code(f'pip install {dep}', language='bash')
else:
    st.info(t('no_env_check'))
if st.button(t('refresh')):
    st.rerun()
st.markdown('---')
active_project_root = st.session_state.get('active_project_root', Path('.'))
perf_monitor = st.session_state.get('active_perf_monitor')
if not perf_monitor and active_project_root:
    try:
        from antigravity.infrastructure.performance_monitor import PerformanceMonitor
        if active_project_root != Path('.'):
            perf_monitor = PerformanceMonitor(str(active_project_root))
            st.session_state.active_perf_monitor = perf_monitor
    except Exception as e:
        pass
active_state_mgr = st.session_state.get('active_state_mgr', state_mgr)
project_name = active_project_root.name if active_project_root != Path('.') else 'Global'
if perf_monitor:
    try:
        perf_data = perf_monitor.get_summary()
        st.subheader(t('performance_stats'))
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t('total_operations'), perf_data.get('total_operations', 0))
        with col2:
            st.metric(t('total_calls'), perf_data.get('total_calls', 0))
        with col3:
            avg_time = perf_data.get('average_time', 0)
            st.metric(t('avg_time'), f'{avg_time:.2f}s')
        with col4:
            total_time = perf_data.get('total_time', 0)
            st.metric(t('total_time'), f'{total_time:.2f}s')
        st.subheader(t('slowest_operations'))
        slowest = perf_data.get('slowest_operations', [])
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
            st.info(t('no_operations'))
        st.subheader(t('token_usage'))
        plan_path = active_project_root / 'PLAN.md'
        if plan_path.exists():
            plan_content = plan_path.read_text(encoding='utf-8')
            estimated_tokens = len(plan_content) // 4
            max_tokens = CONFIG.get('MAX_TOKENS', 16000)
            usage_pct = min(100, estimated_tokens / max_tokens * 100)
            st.progress(usage_pct / 100)
            st.caption(f'{estimated_tokens:,} / {max_tokens:,} tokens ({usage_pct:.1f}%)')
        else:
            st.warning(t('no_plan_found'))
        st.subheader(t('recent_executions'))
        recent_audits = active_state_mgr.get_recent_audits(limit=10)
        if recent_audits:
            success_count = sum((1 for a in recent_audits if a.get('status') in ['PASS', 'FIXED']))
            success_rate = success_count / len(recent_audits) * 100
            st.metric(t('success_rate'), f'{success_rate:.1f}%')
            for audit in reversed(recent_audits[-5:]):
                timestamp = audit.get('timestamp', 'N/A')[:19]
                file_path = audit.get('file_path', 'Unknown')
                status = audit.get('status', 'INFO')
                status_icon = {'PASS': '✅', 'FIXED': '🔧', 'FAIL': '❌', 'INFO': 'ℹ️'}.get(status, '📝')
                st.text(f'{status_icon} {timestamp} | {file_path} | {status}')
        else:
            st.info(t('no_activity'))
    except Exception as e:
        st.warning(f'⚠️ Performance metrics unavailable: {str(e)}')
else:
    st.info(f"📊 {t('perf_not_available')}")
    st.caption(t('switch_to_project'))
st.markdown('---')
st.header(t('p3_monitor'))
with st.container():
    try:
        from antigravity.infrastructure.performance_monitor import perf_monitor
        from antigravity.services.context_manager import ContextManager
        dashboard_data = perf_monitor.get_dashboard_data()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=t('total_operations'), value=dashboard_data.get('total_operations', 0), help=t('total_operations_help'))
        with col2:
            st.metric(label=t('total_calls'), value=dashboard_data.get('total_calls', 0), help=t('total_calls_help'))
        with col3:
            total_time = dashboard_data.get('total_time', 0)
            st.metric(label=t('total_time'), value=f'{total_time:.2f}s', help=t('total_time_help'))
        st.subheader(t('slowest_operations'))
        top_slowest = dashboard_data.get('top_slowest', [])
        if top_slowest:
            for i, op in enumerate(top_slowest[:5], 1):
                col_rank, col_name, col_time, col_calls = st.columns([0.5, 3, 1.5, 1])
                with col_rank:
                    st.text(f'#{i}')
                with col_name:
                    st.text(op['operation'])
                with col_time:
                    st.text(f"{op['avg_time']:.3f}s avg")
                with col_calls:
                    st.text(f"{op['call_count']} calls")
        else:
            st.info(t('no_perf_data'))
        st.subheader(t('token_usage'))
        plan_path = os.path.join(os.getcwd(), 'PLAN.md')
        if os.path.exists(plan_path):
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_content = f.read()
                ctx_mgr = ContextManager(max_tokens=16384)
                plan_tokens = ctx_mgr.count_tokens(plan_content)
                estimated_output = ctx_mgr.estimate_output_tokens(plan_content)
                max_tokens = 16384
                total_estimated = plan_tokens + estimated_output
                usage_ratio = min(total_estimated / max_tokens, 1.0)
                st.progress(usage_ratio)
                st.caption(t('token_estimated').format(total_estimated, max_tokens, usage_ratio * 100, plan_tokens, estimated_output))
                if usage_ratio > 0.9:
                    st.warning(t('token_high'))
                elif usage_ratio > 0.75:
                    st.info(t('token_moderate'))
                else:
                    st.success(t('token_healthy'))
            except Exception as e:
                st.error(t('token_error').format(e))
        else:
            st.info(t('plan_not_found'))
        st.subheader(t('recent_executions'))
        recent = dashboard_data.get('recent_executions', [])
        if recent:
            for exec_info in recent[:5]:
                col_op, col_time, col_rate = st.columns([3, 2, 1.5])
                with col_op:
                    st.text(exec_info['operation'])
                with col_time:
                    st.text(exec_info.get('last_execution', 'N/A')[:19])
                with col_rate:
                    rate = exec_info.get('success_rate', 0)
                    color = '🟢' if rate >= 90 else '🟡' if rate >= 70 else '🔴'
                    st.text(f'{color} {rate:.0f}%')
        else:
            st.info(t('no_recent_exec'))
    except ImportError as e:
        st.warning(t('perf_monitor_unavailable').format(e))
    except Exception as e:
        st.error(t('perf_data_error').format(e))
st.markdown('---')
st.header('🏰 Quality Tower - 质量看板')
st.caption('Sheriff Brain 的最后一道防线 - The Last Line of Defense')
try:
    from antigravity.services.quality_tower import display_ceremonial_stamps, display_blocking_issues, display_trend_radar, display_healing_buttons, run_delivery_gate_audit, get_latest_audit_result
    from antigravity.infrastructure.audit_history import AuditHistoryManager
    from pathlib import Path
    st.subheader('📦 选择项目 (Select Project)')
    projects_dir = Path('projects')
    if projects_dir.exists():
        project_names = [p.name for p in projects_dir.iterdir() if p.is_dir() and (not p.name.startswith('.'))]
    else:
        project_names = []
    if not project_names:
        st.warning('未找到项目。请先创建项目。')
    else:
        selected_project_name = st.selectbox('项目', project_names, key='quality_tower_project')
        selected_project = {'name': selected_project_name, 'root': str(projects_dir / selected_project_name)}
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button('🔍 运行质量审计 (Run Audit)', type='primary', use_container_width=True):
                result = run_delivery_gate_audit(selected_project)
                if result:
                    st.success('✅ 审计完成！')
        with col2:
            history_manager = AuditHistoryManager(Path(selected_project['root']))
            stats = history_manager.get_directory_stats()
            st.caption(f"📊 历史: {stats['total_files']} 文件")
            st.caption(f"💾 {stats['total_size_mb']:.1f}/{stats['max_size_mb']}MB")
        result = get_latest_audit_result(selected_project)
        if result:
            st.markdown('---')
            display_ceremonial_stamps(result)
            st.markdown('---')
            display_blocking_issues(result)
            st.markdown('---')
            display_trend_radar(selected_project, history_manager)
            st.markdown('---')
            display_healing_buttons(result, selected_project)
        else:
            st.info('💡 点击上方按钮运行质量审计')
except ImportError as e:
    st.warning(f'⚠️ Quality Tower 模块未找到: {e}')
    st.caption('请确保 delivery_gate.py 和 quality_tower.py 已正确安装')
except Exception as e:
    st.error(f'❌ Quality Tower 错误: {e}')
    import traceback
    with st.expander('查看详细错误'):
        st.code(traceback.format_exc())
st.markdown('---')
st.header('🧠 Neural Nexus - 舰队神经枢纽')
st.caption('Global Knowledge Graph & Semantic Topology')

try:
    from antigravity.core.knowledge_graph import FleetKnowledgeGraph
    kg = FleetKnowledgeGraph.get_instance()
    
    # Auto-scan if empty
    if not kg.knowledge.get('projects'):
        from antigravity.core.fleet_manager import ProjectFleetManager
        fm = ProjectFleetManager.get_instance()
        kg.scan_fleet_wisdom(fm.get_fleet_status())
        
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Nodes", len(kg.knowledge.get('projects', {})))
    
    # Graph Visualization
    try:
        import graphviz
        graph = graphviz.Digraph()
        graph.attr(rankdir='LR', bgcolor='transparent')
        
        # Nodes
        for pid, data in kg.knowledge.get('projects', {}).items():
            label = f"{pid}\n({len(data.get('exports', []))} exports)"
            graph.node(pid, label, shape='box', style='filled', fillcolor='#2b2b2b', fontcolor='white', color='#00d2ff')
            
        # Edges (Dependencies)
        # We retrieve dependencies from GKG Relations (Phase 14: Pulse Strength)
        edge_count = 0
        relationships = kg.knowledge.get('relationships', [])
        
        # Fallback to FM scan if GKG relations empty (backward compatibility)
        if not relationships:
            from antigravity.core.fleet_manager import ProjectFleetManager
            fm = ProjectFleetManager.get_instance()
            for pid in kg.knowledge.get('projects', {}):
                deps = fm.scan_cross_dependencies(pid)
                for dep in deps:
                    graph.edge(pid, dep, color='#ff0055', style='dashed')
                    edge_count += 1
        else:
            for rel in relationships:
                src = rel.get('source')
                tgt = rel.get('target')
                strength = rel.get('strength', 1)
                # Pulse Visual: Thicker lines for stronger bonds
                width = str(max(1, strength / 2))
                graph.edge(src, tgt, color='#ff0055', style='dashed', penwidth=width)
                edge_count += 1
                
        with col2:
            st.metric("Active Synapses", edge_count)
            
        st.graphviz_chart(graph)
        
    except ImportError:
        with col2:
             st.metric("Active Synapses", "Visual Offline")
        st.info("💡 Install `graphviz` to visualize the dependency graph.")
    except Exception as e:
        st.warning(f"Graph Visualization Warning: {e}")
        
    with st.expander("🔍 Semantic Index (Exports)"):
        for pid, data in kg.knowledge.get('projects', {}).items():
            st.markdown(f"**{pid}**")
            for exp in data.get('exports', []):
                st.code(f"{exp['type']} {exp['name']} ({exp['file']})\n# {exp['docstring']}", language='python')

except Exception as e:
    st.error(f"Neural Nexus Offline: {e}")

st.markdown('---')
st.caption(t('powered_by'))
if DEBUG_MONITOR_ENABLED:
    try:
        show_debug_panel()
    except Exception as e:
        st.sidebar.error(f'Debug panel error: {e}')
st.markdown('\n<script>\nsetTimeout(function() {\n    window.location.reload();\n}, 5000);\n</script>\n', unsafe_allow_html=True)