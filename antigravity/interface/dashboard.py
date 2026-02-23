import streamlit as st
import json
import time
from pathlib import Path
from antigravity.infrastructure.p3_state_manager import P3StateManager
from antigravity.core.mission_orchestrator import MissionOrchestrator, AtomicTask, TaskState

st.set_page_config(page_title="Antigravity 自动化开发产线", layout="wide", page_icon="🚀")

@st.cache_resource
def get_p3_manager():
    return P3StateManager('.')

p3_mgr = get_p3_manager()

# ==========================================
# 🗂️ 侧边栏：神经印记与清理中枢 (Phase 32)
# ==========================================
with st.sidebar:
    st.markdown("### 🗂️ 产线历史档案")
    history_records = p3_mgr.get_history()
    
    if not history_records:
        st.info("🕳️ 历史档案为空，等待首次点火。")
    else:
        for record in history_records:
            st.markdown(f"**📦 {record['name']}**")
            # 格式化时间戳显示
            fmt_time = record['timestamp'][:19].replace("T", " ")
            st.caption(f"⏱️ {fmt_time}")
            st.text(f"🎯 {record['vision']}")
            
            if st.button("🔥 唤醒 (Focus)", key=f"wake_{record['name']}", type="secondary", use_container_width=True):
                st.session_state["focused_project"] = record['name']
                st.rerun()
                
            st.divider()
            
    st.markdown("---")
    if st.button("🗑️ 清理历史缓存", type="secondary", use_container_width=True):
        p3_mgr.wipe_history_cache()
        if "focused_project" in st.session_state:
            del st.session_state["focused_project"]
        st.success("✅ 神经印记已格式化！")
        st.rerun()

# ==========================================
# 1. 顶部：Sentinel 哨兵警报 (免疫系统)
# ==========================================
def get_sentinel_errors(active_root):
    if not active_root: return []
    ckpt_dir = Path(active_root) / ".antigravity" / "checkpoints"
    if not ckpt_dir.exists(): return []
    return sorted(list(ckpt_dir.glob("debug_*.json")), key=lambda x: x.stat().st_mtime, reverse=True)

active_project = p3_mgr.global_state.get("last_active")
errors = get_sentinel_errors(active_project)

if errors:
    st.error(f"🛑 [Sentinel] 监测到 {len(errors)} 个运行异常！")
    with st.expander(f"🔍 展开检查最后一个异常的物理现场 ({errors[0].name})"):
        try:
            with open(errors[0], 'r', encoding='utf-8') as f:
                err_data = json.load(f)
            st.warning(f"Error: {err_data.get('error_type')} - {err_data.get('message')}")
            st.code(err_data.get('traceback'), language='python')
        except Exception as e:
            st.error(f"无法读取快照文件: {e}")
            
        if st.button("🗑️ 现场清理并重启执行", key="sentinel_clean_btn"):
            for f in errors:
                try: f.unlink()
                except: pass
            st.rerun()

st.title("🚀 Antigravity 自动化开发产线 (v3.0-lite)")

# ==========================================
# 2. 核心区：全自动发射台 (极简模式)
# ==========================================
# ==========================================
# 2. 核心区：全自动发射台 (极简模式 & 增量模式)
# ==========================================
st.subheader("📦 定义新项目愿景 / 迭代现有项目")
col1, col2 = st.columns([1, 1])

focused = st.session_state.get("focused_project")

with col1:
    if focused:
        project_name = st.text_input("项目名称 (聚焦模式)", value=focused, disabled=True)
        st.info("🔄 当前处于【增量迭代】模式。这会跳过骨架生成直接进行物理灌注。")
        if st.button("❌ 退出聚焦", size="small"):
            del st.session_state["focused_project"]
            st.rerun()
    else:
        project_name = st.text_input("项目名称 (如: TradingAgent)", placeholder="输入项目名...")

with col2:
    if focused:
        project_dir = Path("projects") / project_name
        plan_path = project_dir / "PLAN.md"
        old_plan = plan_path.read_text(encoding="utf-8") if plan_path.exists() else "无历史愿景"
        with st.expander("👁️ 查看历史愿景 (PLAN.md)", expanded=False):
            st.text(old_plan)
            
        project_plan = st.text_area("📜 追加迭代指令 (Delta Requirements)", height=150, placeholder="在此处输入新的迭代需求，将自动追加到物理 PLAN.md 的尾部...")
    else:
        uploaded_file = st.file_uploader("📤 上传需求文档 (.txt/.md)", type=['txt', 'md'])
        plan_content = uploaded_file.getvalue().decode('utf-8') if uploaded_file else ""
        project_plan = st.text_area("📜 核心愿景 (PLAN.md)", value=plan_content, height=150, placeholder="描述系统要实现什么功能？大脑将自动推演文件树并注入代码...")

# ==========================================
# 3. 发射机制 (神经互联与挂载)
# ==========================================
ignition_label = "🔥 增量推演并接管" if focused else "🔥 物理点火：自动推演并接管"
if st.button(ignition_label, use_container_width=True, type="primary"):
    if not project_name or not project_plan.strip():
        st.error("❌ 项目名称与愿景指令不能为空！")
    else:
        if focused:
            if not p3_mgr.check_project_exists(project_name):
                st.error("🚨 物理现场已遗失！(项目目录不存在)。请点侧边栏清理历史缓存。")
            else:
                project_dir = Path("projects") / project_name
                plan_path = project_dir / "PLAN.md"
                
                # Append Mode
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                append_text = f"\n\n## [{timestamp}] 迭代需求 (Iteration)\n{project_plan}\n"
                with open(plan_path, "a", encoding="utf-8") as f:
                    f.write(append_text)
                
                # Register globally and historically
                project_rel_path = f"projects/{project_name}"
                p3_mgr.global_state["last_active"] = project_rel_path
                p3_mgr._save_global_state()
                p3_mgr.record_project_history(project_name, project_plan)
                
                # Collect existing code files for bypass
                existing_files = []
                for ext in ["*.py", "*.js", "*.ts", "*.tsx", "*.html", "*.css"]:
                    for pf in project_dir.rglob(ext):
                        if ".antigravity" not in pf.parts:
                            rel_path = str(pf.relative_to(project_dir)).replace("\\", "/")
                            existing_files.append(rel_path)
                
                if not existing_files:
                    existing_files = ["main.py"]
                
                try:
                    orch = MissionOrchestrator(str(project_dir))
                    task = AtomicTask(
                        task_id=f"ITER_{project_name}_{int(time.time())}", 
                        type="code",
                        goal=f"Iteration: {project_plan[:50]}...", 
                        metadata={
                            "created_via": "dashboard", 
                            "file_path": "PLAN.md", 
                            "is_iteration": True,
                            "remaining_files": existing_files
                        },
                        state=TaskState.CODING_LOOP # Bypass BLUEPRINTING
                    )
                    orch.tasks.append(task)
                    
                    ag_dir = project_dir / ".antigravity"
                    orch.save_state(str(ag_dir / "mission_state.json"))
                    
                    st.success(f"✅ {project_name} 历史项目已唤醒！引擎已直接跳入 CODING_LOOP 开始增量推演。")
                    time.sleep(1)
                    if "focused_project" in st.session_state:
                        del st.session_state["focused_project"]
                    st.rerun()
                except Exception as e:
                    st.error(f"引擎通信异常: {e}")
        else:
            # ORIGINAL LOGIC FOR NEW PROJECT
            project_dir = Path("projects") / project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "PLAN.md").write_text(project_plan, encoding="utf-8")
            
            project_rel_path = f"projects/{project_name}"
            p3_mgr.register_project(project_rel_path)
            p3_mgr.global_state["last_active"] = project_rel_path
            
            p3_mgr.record_project_history(project_name, project_plan)
            
            try:
                orch = MissionOrchestrator(str(project_dir))
                task = AtomicTask(
                    task_id=f"INIT_{project_name}", 
                    type="code",
                    goal=f"Init project from Blueprint for {project_name}", 
                    metadata={"created_via": "dashboard", "file_path": "PLAN.md"},
                    state=TaskState.PENDING
                )
                orch.tasks.append(task)
                
                ag_dir = project_dir / ".antigravity"
                ag_dir.mkdir(parents=True, exist_ok=True)
                orch.save_state(str(ag_dir / "mission_state.json"))
                
                st.success(f"✅ {project_name} 神经链路挂载完毕！记录已固化。等待大脑接管...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"引擎通信异常: {e}")