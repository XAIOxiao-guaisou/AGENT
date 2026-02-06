# Step-by-step integration guide for P3 Phase 17.5

## Step 1: ✅ Translations Added
- Added P3 Phase 17 keys to both zh and en sections
- Keys: project_center, active_project, loading_project_context, etc.

## Step 2: Insert Project Selector in Sidebar
Location: After environment check button (around line 310)

Find this section:
```python
# Environment Check Button
if st.sidebar.button("🔍 " + t("check_env"), use_container_width=True):
    st.session_state.trigger_env_check = True
```

Insert the entire content of `antigravity/p3_project_selector.py` right after it.

## Step 3: Update Performance Monitor Section
Location: Search for "# P3: Performance Monitor" (around line 460-500)

Replace the entire P3 Performance Monitor section with content from:
`antigravity/p3_performance_monitor_ui.py`

## Step 4: Add Auto-Focus to Scaffolding
Location: In the project creation success block (around line 650)

After:
```python
st.balloons()
st.success(t("project_created").format(project_name))
```

Add:
```python
# P3 Phase 17: Auto-focus on newly created project
st.session_state.last_selected_project = None  # Force refresh
st.session_state.active_project_root = Path(project_path)
st.rerun()  # Reactive reload
```

## Verification Checklist
- [ ] Translations appear in both languages
- [ ] Project selector shows in sidebar
- [ ] Status indicators work (🟢🟡🔴)
- [ ] Performance metrics update on project switch
- [ ] New project auto-focuses after creation
- [ ] Legacy mode still works
