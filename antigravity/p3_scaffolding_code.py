# P3 Dashboard Scaffolding Implementation with Auto-Focus
# This file contains the new P3 project scaffolding UI code
# To be integrated into dashboard.py

# ============================================================
# P3: Automated Project Scaffolding (项目全自动发射台)
# ============================================================

st.markdown("---")
st.header(t("scaffolding_launcher"))

with st.container():
    p_col1, p_col2 = st.columns([1, 2])
    
    with p_col1:
        # 1. Project Name Input
        project_name = st.text_input(
            t("project_name"),
            placeholder=t("project_name_placeholder"),
            help=t("project_name_help"),
            key="p3_project_name"
        )
        
        # 2. Dynamic File Structure
        st.subheader(t("project_structure"))
        project_files_input = st.text_area(
            t("project_structure_help"),
            placeholder=t("project_structure_placeholder"),
            height=150,
            key="p3_project_structure"
        )
        
        # 3. Drag-Drop Upload
        st.subheader(t("business_doc_upload"))
        uploaded_file = st.file_uploader(
            t("drag_drop_doc"),
            type=['txt', 'md'],
            key="p3_doc_uploader"
        )
        
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.success(t("file_uploaded"))
            with st.expander(t("preview")):
                st.text(content[:500] + "..." if len(content) > 500 else content)
            
            # Store in session state
            st.session_state.p3_plan_content = content

    with p_col2:
        # PLAN.md Preview
        st.subheader(t("project_plan"))
        
        # Apply button
        if uploaded_file and st.button(t("apply_to_project_plan"), key="p3_apply_plan"):
            st.session_state.p3_plan_content = content
            st.success(t("plan_updated"))
        
        # Display current or uploaded plan
        plan_display = st.session_state.get('p3_plan_content', t("plan_placeholder"))
        st.text_area(
            t("current_plan"),
            value=plan_display,
            height=350,
            disabled=True,
            key="p3_plan_display"
        )

    # 4. One-Click Create & Launch
    if st.button(t("create_and_launch"), type="primary", use_container_width=True, key="p3_create_btn"):
        if not project_name:
            st.error(t("error_no_project_name"))
        elif not project_files_input.strip():
            st.error(t("error_no_structure"))
        else:
            try:
                # ===========================
                # P3 Core: Auto-create dedicated folder
                # ===========================
                project_path = os.path.join("projects", project_name)
                os.makedirs(project_path, exist_ok=True)
                
                # Create PLAN.md
                plan_content = st.session_state.get('p3_plan_content', f"# {project_name} Project Plan\n\nTODO: Define requirements")
                with open(os.path.join(project_path, "PLAN.md"), "w", encoding='utf-8') as f:
                    f.write(plan_content)
                
                # Parse and create file placeholders
                files = [f.strip() for f in project_files_input.split('\n') if f.strip()]
                created_files = []
                
                for file_rel_path in files:
                    full_path = os.path.join(project_path, file_rel_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    if not os.path.exists(full_path):
                        with open(full_path, "w", encoding='utf-8') as f:
                            f.write(f"# Project: {project_name}\n")
                            f.write(f"# File: {file_rel_path}\n")
                            f.write(f"# TODO: Implement according to PLAN.md\n\n")
                        created_files.append(file_rel_path)
                
                # Success feedback
                st.balloons()
                st.success(t("project_created").format(project_name))
                
                with st.expander(t("created_files")):
                    for f in created_files:
                        st.text(f"✅ projects/{project_name}/{f}")
                
                # P3 Phase 18: Auto-Focus on newly created project
                st.info("🎯 " + t("auto_focusing_project"))
                
                # Force session state update to switch to new project
                from pathlib import Path
                from antigravity.p3_state_manager import P3StateManager
                
                project_path_obj = Path("projects") / project_name
                
                # Update session state
                st.session_state.last_selected_project = None  # Force refresh
                st.session_state.active_project_root = project_path_obj
                
                # Initialize components immediately
                try:
                    st.session_state.active_state_mgr = P3StateManager(project_path_obj)
                    
                    # Try to initialize performance monitor
                    try:
                        from antigravity.performance_monitor import PerformanceMonitor
                        st.session_state.active_perf_monitor = PerformanceMonitor(str(project_path_obj))
                    except:
                        st.session_state.active_perf_monitor = None
                    
                    st.success("✅ " + t("project_auto_focused"))
                except Exception as e:
                    st.warning(f"⚠️ Auto-focus initialization: {e}")
                
                # Log to state manager
                state_mgr.log_audit(
                    f"projects/{project_name}",
                    "project_scaffolding",
                    f"Created project with {len(created_files)} files",
                    "INFO"
                )
                
                # Reactive reload to show new project
                st.rerun()
                
            except Exception as e:
                st.error(t("project_creation_failed").format(e))
                import traceback
                st.code(traceback.format_exc(), language="python")
