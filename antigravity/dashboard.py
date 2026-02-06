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
        # 表格列标题 / Table column headers
        "col_time": "时间",
        "col_file": "文件",
        "col_event": "事件",
        "col_status": "状态",
        # 占位符文本 / Placeholder text
        "placeholder_file": "src/your_module.py",
        "placeholder_task": "用户登录模块",
        # 项目级发射台 / Project Launcher
        "project_launcher": "🚀 项目级发射台",
        "project_files": "📁 项目结构定义",
        "project_files_help": "输入项目涉及的文件路径 (每行一个)",
        "upload_plan": "📤 业务文档上传",
        "upload_plan_help": "上传需求文档 (.txt/.md),系统将自动更新至 PLAN.md",
        "file_uploaded": "✅ 文件已上传",
        "preview": "预览",
        "apply_to_plan": "应用到 PLAN.md",
        "plan_template": "📜 PLAN 模板",
        "template_source": "模板来源",
        "use_current": "使用当前",
        "use_default": "使用默认模板",
        "reset_template": "🔄 重置为默认模板",
        "template_reset": "✅ 模板已重置",
        "current_plan": "当前 PLAN",
        "launch_project": "🔥 启动项目级开发",
        "error_no_files": "❌ 请输入项目文件列表",
        "project_launched": "🎯 项目已发射! 共 {} 个文件",
        # P3 项目脚手架 / P3 Project Scaffolding
        "scaffolding_launcher": "🚀 项目全自动发射台",
        "project_name": "项目名称",
        "project_name_placeholder": "例如: XhsDataScraper",
        "project_name_help": "系统将为您自动创建独立目录",
        "error_no_project_name": "❌ 请输入项目名称",
        "project_structure": "项目内部结构",
        "project_structure_help": "每行一个文件路径 (相对路径)",
        "project_structure_placeholder": "main.py\nutils/parser.py\nconfig.json\ntests/test_main.py",
        "business_doc_upload": "📤 业务文档上传",
        "drag_drop_doc": "拖拽上传业务文档 (.txt/.md)",
        "apply_to_project_plan": "应用到项目计划",
        "project_plan": "📜 项目计划",
        "current_plan": "当前计划",
        "plan_placeholder": "# 项目计划\n\n请上传业务文档或手动编辑...",
        "create_and_launch": "🔥 创建项目并启动全自动接管",
        "error_no_structure": "❌ 请定义项目结构",
        "project_created": "✅ 项目 `{}` 已在独立文件夹中初始化成功!",
        "created_files": "📋 已创建文件",
        "project_auto_takeover": "🌐 Monitor 将在 3 秒后检测到新项目并自动接管",
        "project_creation_failed": "❌ 项目创建失败: {}",
        
        # P3 Phase 17: Multi-Project Selector
        "project_center": "项目指挥中心",
        "active_project": "活跃项目",
        "loading_project_context": "正在加载项目上下文...",
        "project_loaded": "项目已加载",
        "project_load_failed": "项目加载失败",
        "project_info": "项目信息",
        "no_plan_found": "⚠️ 未找到 PLAN.md",
        "files": "文件数",
        "last_sync": "最后同步",
        
        # P3 Phase 18: Vibe Polish
        "auto_focusing_project": "正在自动切换到新项目...",
        "project_auto_focused": "项目已自动聚焦",
        "vibe_check_button": "🩺 运行 Vibe Check",
        "generate_docs_button": "📄 生成文档",
        "docs_generated": "文档生成成功!",
        "vibe_check_running": "正在运行 Vibe Check...",
        "vibe_check_complete": "Vibe Check 完成!",
        "health_score": "健康度评分",
        "issues_found": "发现的问题",
        "recommendations": "改进建议",
        "generating_docs": "正在生成项目文档...",
        
        # Performance Monitor
        "performance_monitor": "性能监控",
        "performance_stats": "性能统计",
        "total_operations": "总操作数",
        "total_calls": "总调用次数",
        "avg_time": "平均耗时",
        "total_time": "总耗时",
        "slowest_operations": "最慢操作",
        "no_operations": "暂无操作记录",
        "token_usage": "Token 使用估算",
        "recent_executions": "最近执行",
        "success_rate": "成功率",
        
        # 项目配置 / Project Config
        "project_config": "⚙️ 项目配置",
        "allowed_roots": "允许的代码根目录 (用逗号分隔)",
        "allowed_roots_help": "出于安全考虑,Agent 只能在这些指定的目录下创建文件。例如: src, tests, docs",
        "current_allowed": "当前允许的路径前缀: {}",
        "drag_upload_hint": "(支持拖拽上传)",
        "unauthorized_path": "⚠️ 跳过未授权路径: {}\n(请在侧边栏配置中添加该目录)",
        "no_files_created": "没有创建任何新文件（可能路径不合法或文件已存在）。",
        "files_created_list": "📋 已创建文件列表",
        "monitor_will_detect": "🌐 Monitor 将在约 3 秒后检测到这些文件并触发项目级同步...",
        # P3 性能监控 / P3 Performance Monitor
        "p3_monitor": "📊 P3 性能监控",
        "total_operations_help": "已监控的操作总数",
        "total_calls_help": "所有操作的总调用次数",
        "total_time_help": "所有操作的总耗时",
        "token_estimated": "预估: {}/{} tokens ({:.1f}%) | PLAN: {} | 输出: {}",
        "token_high": "⚠️ Token 使用率很高。考虑减少 PLAN.md 复杂度或使用增量同步。",
        "token_moderate": "ℹ️ Token 使用率中等。P3 优化将帮助减少上下文大小。",
        "token_healthy": "✅ Token 使用率健康。P3 优化运行良好。",
        "token_error": "Token 估算失败: {}",
        "plan_not_found": "未找到 PLAN.md。Token 估算不可用。",
        "no_recent_exec": "暂无最近执行记录。",
        "perf_monitor_unavailable": "性能监控器不可用: {}",
        "perf_data_error": "加载性能数据失败: {}",
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
        # 表格列标题 / Table column headers
        "col_time": "Time",
        "col_file": "File",
        "col_event": "Event",
        "col_status": "Status",
        # 占位符文本 / Placeholder text
        "placeholder_file": "src/your_module.py",
        "placeholder_task": "User Login Module",
        # 项目级发射台 / Project Launcher
        "project_launcher": "🚀 Project Launcher",
        "project_files": "📁 Project Structure",
        "project_files_help": "Enter project file paths (one per line)",
        "upload_plan": "📤 Upload Plan",
        "upload_plan_help": "Upload requirement document (.txt/.md), will update PLAN.md",
        "file_uploaded": "✅ File uploaded",
        "preview": "Preview",
        "apply_to_plan": "Apply to PLAN.md",
        "plan_template": "📜 PLAN Template",
        "template_source": "Template Source",
        "use_current": "Use Current",
        "use_default": "Use Default Template",
        "reset_template": "🔄 Reset to Default",
        "template_reset": "✅ Template reset",
        "current_plan": "Current PLAN",
        "launch_project": "🔥 Launch Project Development",
        "error_no_files": "❌ Please enter project file list",
        "project_launched": "🎯 Project launched! {} files created",
        # P3 Project Scaffolding
        "scaffolding_launcher": "🚀 Automated Project Scaffolding",
        "project_name": "Project Name",
        "project_name_placeholder": "e.g: XhsDataScraper",
        "project_name_help": "System will auto-create dedicated directory",
        "error_no_project_name": "❌ Please enter project name",
        "project_structure": "Internal Structure",
        "project_structure_help": "One file path per line (relative paths)",
        "project_structure_placeholder": "main.py\\nutils/parser.py\\nconfig.json\\ntests/test_main.py",
        "business_doc_upload": "📤 Business Document Upload",
        "drag_drop_doc": "Drag & Drop Document (.txt/.md)",
        "apply_to_project_plan": "Apply to Project Plan",
        "project_plan": "📜 Project Plan",
        "current_plan": "Current Plan",
        "plan_placeholder": "# Project Plan\\n\\nPlease upload business document or edit manually...",
        "create_and_launch": "🔥 Create Project & Launch Auto-Takeover",
        "error_no_structure": "❌ Please define project structure",
        "project_created": "✅ Project `{}` initialized successfully in dedicated folder!",
        "created_files": "📋 Created Files",
        "project_auto_takeover": "🌐 Monitor will detect new project in ~3s and auto-takeover",
        "project_creation_failed": "❌ Project creation failed: {}",
        
        # P3 Phase 17: Multi-Project Selector
        "project_center": "Project Center",
        "active_project": "Active Project",
        "loading_project_context": "Loading project context...",
        "project_loaded": "Project loaded",
        "project_load_failed": "Project load failed",
        "project_info": "Project Info",
        "no_plan_found": "⚠️ No PLAN.md found",
        "files": "Files",
        "last_sync": "Last Sync",
        
        # P3 Phase 18: Vibe Polish
        "auto_focusing_project": "Auto-focusing on new project...",
        "project_auto_focused": "Project auto-focused",
        "vibe_check_button": "🩺 Run Vibe Check",
        "generate_docs_button": "📄 Generate Docs",
        "docs_generated": "Documentation generated successfully!",
        "vibe_check_running": "Running Vibe Check...",
        "vibe_check_complete": "Vibe Check Complete!",
        "health_score": "Health Score",
        "issues_found": "Issues Found",
        "recommendations": "Recommendations",
        "generating_docs": "Generating project documentation...",
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

# ============================================================
# P3 Phase 17: Multi-Project Selector (项目指挥中心)
# ============================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 " + t("project_center"))

# Import P3 components
from pathlib import Path
from antigravity.p3_state_manager import P3StateManager

# Get projects directory
projects_dir = Path(CONFIG.get("PROJECTS_DIR", "projects"))

# Scan for available projects
available_projects = []
project_status = {}

if projects_dir.exists():
    for project_path in projects_dir.iterdir():
        if project_path.is_dir():
            project_name = project_path.name
            
            # Check project health
            has_plan = (project_path / "PLAN.md").exists()
            has_state = (project_path / ".antigravity_state.json").exists()
            
            # Status indicator
            if has_plan and has_state:
                status = "🟢"  # Healthy
            elif has_plan:
                status = "🟡"  # Needs initialization
            else:
                status = "🔴"  # Broken (no PLAN.md)
            
            available_projects.append(project_name)
            project_status[project_name] = status

# Add "Global (Legacy)" option for backward compatibility
project_options = ["Global (Legacy)"] + available_projects

# Format options with status indicators
formatted_options = []
for opt in project_options:
    if opt == "Global (Legacy)":
        formatted_options.append("🌐 Global (Legacy)")
    else:
        status_icon = project_status.get(opt, "⚪")
        formatted_options.append(f"{status_icon} {opt}")

# Project selector dropdown
selected_index = st.sidebar.selectbox(
    t("active_project"),
    range(len(formatted_options)),
    format_func=lambda i: formatted_options[i],
    key="p3_project_selector"
)

selected_project = project_options[selected_index]

# Initialize session state for project switching
if 'last_selected_project' not in st.session_state:
    st.session_state.last_selected_project = None

# Detect project switch
if selected_project != st.session_state.last_selected_project:
    st.session_state.last_selected_project = selected_project
    
    # Show loading indicator
    with st.sidebar:
        with st.spinner(t("loading_project_context")):
            # P3: Reactive component mapping
            if selected_project != "Global (Legacy)":
                project_root = projects_dir / selected_project
                st.session_state.active_project_root = project_root
                
                # Initialize project-specific components
                try:
                    st.session_state.active_state_mgr = P3StateManager(project_root)
                    
                    # Load performance monitor if available
                    try:
                        from antigravity.performance_monitor import PerformanceMonitor
                        st.session_state.active_perf_monitor = PerformanceMonitor(str(project_root))
                    except:
                        st.session_state.active_perf_monitor = None
                    
                    st.sidebar.success(f"✅ {t('project_loaded')}: {selected_project}")
                    
                except Exception as e:
                    st.sidebar.error(f"⚠️ {t('project_load_failed')}: {e}")
                    st.session_state.active_project_root = Path(".")
                    st.session_state.active_state_mgr = None
            else:
                # Legacy mode
                st.session_state.active_project_root = Path(".")
                st.session_state.active_state_mgr = state_mgr  # Use global state manager
                st.session_state.active_perf_monitor = None

# Display project info
if selected_project != "Global (Legacy)":
    project_root = projects_dir / selected_project
    
    # Project metadata
    with st.sidebar.expander(f"📋 {t('project_info')}"):
        if (project_root / "PLAN.md").exists():
            plan_size = (project_root / "PLAN.md").stat().st_size
            st.text(f"PLAN.md: {plan_size} bytes")
        else:
            st.warning(t("no_plan_found"))
        
        # Count project files
        file_count = len(list(project_root.rglob("*.py"))) + len(list(project_root.rglob("*.js")))
        st.text(f"{t('files')}: {file_count}")
        
        # Last modified
        if (project_root / ".antigravity_state.json").exists():
            import time
            mtime = (project_root / ".antigravity_state.json").stat().st_mtime
            last_mod = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
            st.text(f"{t('last_sync')}: {last_mod}")
    
    # P3 Phase 18: Quick Actions Toolbox
    st.sidebar.markdown("### 🛠️ Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button(t("run_vibe_check"), use_container_width=True):
            from antigravity.vibe_check import VibeChecker
            
            with st.status(t("vibe_check_running"), expanded=True) as status:
                checker = VibeChecker(project_root)
                results = checker.diagnose()
                
                status.update(
                    label=f"{t('vibe_check_complete')}: {results['percentage']:.0f}%",
                    state="complete"
                )
            
            # Display results in sidebar
            st.sidebar.metric(
                t("health_score"),
                f"{results['percentage']:.0f}%",
                delta=results['grade']
            )
            
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
        if st.button(t("generate_docs"), use_container_width=True):
            from antigravity.doc_generator import DocGenerator
            
            with st.spinner(t("generating_docs")):
                gen = DocGenerator(project_root)
                
                # Generate README
                readme_content = gen.generate_readme()
                (project_root / "README.md").write_text(readme_content, encoding='utf-8')
                
                # Generate requirements.txt
                req_content = gen.generate_requirements()
                if req_content:
                    (project_root / "requirements.txt").write_text(req_content, encoding='utf-8')
                
                st.sidebar.success(t("docs_generated"))

st.sidebar.markdown("---")

# ===========================
# Project Configuration
# ===========================
st.sidebar.markdown("---")
st.sidebar.subheader(t("project_config"))

# 让用户自定义允许的代码根目录
# Allow users to customize allowed code root directories
allowed_roots_input = st.sidebar.text_input(
    t("allowed_roots"),
    value="src, tests",
    help=t("allowed_roots_help")
)

# 处理输入,生成标准化的目录前缀列表
# Process input to generate standardized directory prefix list
ALLOWED_ROOTS = [root.strip() + "/" for root in allowed_roots_input.split(",") if root.strip()]
st.sidebar.caption(t("current_allowed").format(', '.join(ALLOWED_ROOTS)))

# Store in session state for use in project launcher
st.session_state.allowed_roots = ALLOWED_ROOTS

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
                t("col_time"): audit.get("timestamp", "")[:19],
                t("col_file"): audit.get("file_path", ""),
                t("col_event"): audit.get("event_type", ""),
                t("col_status"): audit.get("status", "")
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
            placeholder=t("placeholder_file"),
            help=t("target_file_help")
        )
        task_name = st.text_input(
            t("task_name"), 
            placeholder=t("placeholder_task"),
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


# ============================================================
# Project-Level Launcher (P1)
# 项目级发射台 (P1)
# ============================================================

st.markdown("---")
st.header(t("project_launcher"))

with st.container():
    p_col1, p_col2 = st.columns([1, 2])
    
    with p_col1:
        st.subheader(t("project_files"))
        
        # 多文件输入 / Multi-file input
        project_files_input = st.text_area(
            t("project_files_help"),
            placeholder="src/main.py\nsrc/utils.py\nsrc/config.py",
            height=150,
            key="project_files_input"
        )
        
        # 文件上传 / File upload
        st.subheader(t("upload_plan"))
        uploaded_file = st.file_uploader(
            t("upload_plan_help"),
            type=['txt', 'md'],
            key="plan_uploader"
        )
        
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.success(t("file_uploaded"))
            
            # 预览 / Preview
            with st.expander(t("preview")):
                st.text(content[:500] + "..." if len(content) > 500 else content)
            
            # 应用到 PLAN.md / Apply to PLAN.md
            if st.button(t("apply_to_plan"), key="apply_plan_btn"):
                try:
                    with open("PLAN.md", "w", encoding='utf-8') as f:
                        f.write(content)
                    st.success(t("plan_updated"))
                    state_mgr.log_audit(
                        "PLAN.md",
                        "plan_upload",
                        f"Uploaded from {uploaded_file.name}",
                        "INFO"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(t("save_failed").format(e))
        
        # 重置模板 / Reset template
        if st.button(t("reset_template"), key="reset_template_btn"):
            try:
                import shutil
                if os.path.exists("config/PLAN_TEMPLATE.md"):
                    shutil.copy("config/PLAN_TEMPLATE.md", "PLAN.md")
                    st.success(t("template_reset"))
                    state_mgr.log_audit(
                        "PLAN.md",
                        "template_reset",
                        "Reset to default template",
                        "INFO"
                    )
                    st.rerun()
                else:
                    st.warning("⚠️ Template file not found: config/PLAN_TEMPLATE.md")
            except Exception as e:
                st.error(f"Reset failed: {e}")
    
    with p_col2:
        st.subheader(t("plan_template"))
        
        # 显示当前 PLAN / Display current PLAN
        if os.path.exists("PLAN.md"):
            with open("PLAN.md", "r", encoding='utf-8') as f:
                current_plan = f.read()
            st.text_area(
                t("current_plan"),
                value=current_plan,
                height=350,
                disabled=True,
                key="current_plan_display"
            )
        else:
            st.info("ℹ️ PLAN.md not found. Upload a file or reset to template.")
    
    # 项目级启动按钮 / Project-level launch button
    if st.button(t("launch_project"), type="primary", use_container_width=True, key="launch_project_btn"):
        if not project_files_input.strip():
            st.error(t("error_no_files"))
        else:
            files = [f.strip() for f in project_files_input.split('\n') if f.strip()]
            
            try:
                created_files = []
                
                # 创建所有占位文件 / Create all placeholder files
                for file_path in files:
                    # 确保路径安全 / Ensure path safety
                    if not file_path.startswith('src/') and not file_path.startswith('tests/'):
                        st.warning(f"⚠️ Skipping unsafe path: {file_path}")
                        continue
                    
                    full_path = os.path.join(".", file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    if not os.path.exists(full_path):
                        with open(full_path, "w", encoding='utf-8') as f:
                            f.write(f"# Auto-generated placeholder for Antigravity\n")
                            f.write(f"# File: {file_path}\n")
                            f.write(f"# TODO: Implement according to PLAN.md\n\n")
                        created_files.append(file_path)
                        
                        # 记录到状态管理器 / Log to state manager
                        state_mgr.log_audit(
                            file_path,
                            "project_file_created",
                            "Created placeholder for project launch",
                            "INFO"
                        )
                
                if created_files:
                    st.balloons()
                    st.success(t("project_launched").format(len(created_files)))
                    
                    # 显示创建的文件 / Show created files
                    with st.expander("📋 Created Files"):
                        for f in created_files:
                            st.text(f"✅ {f}")
                    
                    st.info("🌐 Monitor will detect these files and trigger project-level sync in ~3 seconds...")
                else:
                    st.warning("⚠️ No files created. Check file paths.")
                
            except Exception as e:
                st.error(t("launch_failed").format(e))

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

# P3 Phase 17: Project-Scoped Performance Monitor
# Replace the existing P3 Performance Monitor section in dashboard.py with this code

# ============================================================
# P3 性能监控 (Performance Monitor)
# ============================================================

st.markdown("---")

# Get active project context from session state
active_project_root = st.session_state.get('active_project_root', Path("."))

# Get active performance monitor with defensive initialization
perf_monitor = st.session_state.get('active_perf_monitor')

# Try to initialize if not available and we have a valid project root
if not perf_monitor and active_project_root:
    try:
        from antigravity.performance_monitor import PerformanceMonitor
        
        # Only initialize for non-Global projects
        if active_project_root != Path("."):
            perf_monitor = PerformanceMonitor(str(active_project_root))
            st.session_state.active_perf_monitor = perf_monitor
    except Exception as e:
        # Silently fail - performance monitoring is optional
        pass

active_state_mgr = st.session_state.get('active_state_mgr', state_mgr)
project_name = active_project_root.name if active_project_root != Path(".") else "Global"

# Display performance metrics if monitor is available
if perf_monitor:
    try:
        perf_data = perf_monitor.get_summary()
        
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
        st.warning(f"⚠️ Performance metrics unavailable: {str(e)}")
else:
    st.info(f"📊 Performance monitoring not available for {project_name} mode")
    st.caption("Switch to a project to enable performance tracking")



# ============================================================

st.markdown("---")
st.header(t("p3_monitor"))

with st.container():
    # 导入性能监控器
    try:
        from antigravity.performance_monitor import perf_monitor
        from antigravity.context_manager import ContextManager
        
        # 获取 Dashboard 数据
        dashboard_data = perf_monitor.get_dashboard_data()
        
        # 性能统计卡片
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=t("total_operations"),
                value=dashboard_data.get('total_operations', 0),
                help=t("total_operations_help")
            )
        
        with col2:
            st.metric(
                label=t("total_calls"),
                value=dashboard_data.get('total_calls', 0),
                help=t("total_calls_help")
            )
        
        with col3:
            total_time = dashboard_data.get('total_time', 0)
            st.metric(
                label=t("total_time"),
                value=f"{total_time:.2f}s",
                help=t("total_time_help")
            )
        
        # 最慢操作排行
        st.subheader(t("slowest_operations"))
        
        top_slowest = dashboard_data.get('top_slowest', [])
        if top_slowest:
            for i, op in enumerate(top_slowest[:5], 1):
                col_rank, col_name, col_time, col_calls = st.columns([0.5, 3, 1.5, 1])
                
                with col_rank:
                    st.text(f"#{i}")
                
                with col_name:
                    st.text(op['operation'])
                
                with col_time:
                    st.text(f"{op['avg_time']:.3f}s avg")
                
                with col_calls:
                    st.text(f"{op['call_count']} calls")
        else:
            st.info(t("no_perf_data"))
        
        # Token 使用估算
        st.subheader(t("token_usage"))
        
        # 读取 PLAN.md 估算
        plan_path = os.path.join(os.getcwd(), "PLAN.md")
        if os.path.exists(plan_path):
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_content = f.read()
                
                # 使用 ContextManager 估算
                ctx_mgr = ContextManager(max_tokens=16384)
                plan_tokens = ctx_mgr.count_tokens(plan_content)
                estimated_output = ctx_mgr.estimate_output_tokens(plan_content)
                
                # 进度条
                max_tokens = 16384
                total_estimated = plan_tokens + estimated_output
                usage_ratio = min(total_estimated / max_tokens, 1.0)
                
                st.progress(usage_ratio)
                st.caption(t("token_estimated").format(total_estimated, max_tokens, usage_ratio*100, plan_tokens, estimated_output))
                
                # 警告
                if usage_ratio > 0.9:
                    st.warning(t("token_high"))
                elif usage_ratio > 0.75:
                    st.info(t("token_moderate"))
                else:
                    st.success(t("token_healthy"))
                
            except Exception as e:
                st.error(t("token_error").format(e))
        else:
            st.info(t("plan_not_found"))
        
        # 最近执行
        st.subheader(t("recent_executions"))
        
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
                    color = "🟢" if rate >= 90 else "🟡" if rate >= 70 else "🔴"
                    st.text(f"{color} {rate:.0f}%")
        else:
            st.info(t("no_recent_exec"))
    
    except ImportError as e:
        st.warning(t("perf_monitor_unavailable").format(e))
    except Exception as e:
        st.error(t("perf_data_error").format(e))

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
