"""
P3 Phase 17.5: Automated Integration Script
This script performs surgical injection of P3 components into dashboard.py
"""

import re
from pathlib import Path

def inject_project_selector():
    """Inject project selector after environment check button"""
    dashboard_path = Path("antigravity/dashboard.py")
    selector_path = Path("antigravity/p3_project_selector.py")
    
    # Read files
    dashboard_content = dashboard_path.read_text(encoding='utf-8')
    selector_content = selector_path.read_text(encoding='utf-8')
    
    # Remove the comment header from selector
    selector_code = '\n'.join([
        line for line in selector_content.split('\n')
        if not line.strip().startswith('#') or 'P3 Phase 17' in line
    ])
    
    # Find injection point
    pattern = r'(# Environment Check Button\s+if st\.sidebar\.button.*?\n\s+st\.session_state\.trigger_env_check = True)'
    
    match = re.search(pattern, dashboard_content, re.DOTALL)
    if match:
        injection_point = match.end()
        
        # Inject selector code
        new_content = (
            dashboard_content[:injection_point] +
            '\n\n' + selector_code +
            dashboard_content[injection_point:]
        )
        
        # Write back
        dashboard_path.write_text(new_content, encoding='utf-8')
        print("✅ Project selector injected successfully")
        return True
    else:
        print("❌ Could not find injection point")
        return False

def inject_performance_monitor():
    """Replace old performance monitor with project-scoped version"""
    dashboard_path = Path("antigravity/dashboard.py")
    perf_ui_path = Path("antigravity/p3_performance_monitor_ui.py")
    
    dashboard_content = dashboard_path.read_text(encoding='utf-8')
    perf_ui_content = perf_ui_path.read_text(encoding='utf-8')
    
    # Remove comment header
    perf_ui_code = '\n'.join([
        line for line in perf_ui_content.split('\n')
        if not (line.strip().startswith('#') and 'P3 Phase 17' in line and 'Replace' in line)
    ])
    
    # Find and replace performance monitor section
    pattern = r'# ={60,}\s+# P3: Performance Monitor.*?(?=# ={60,}|$)'
    
    match = re.search(pattern, dashboard_content, re.DOTALL)
    if match:
        new_content = (
            dashboard_content[:match.start()] +
            perf_ui_code +
            '\n\n' +
            dashboard_content[match.end():]
        )
        
        dashboard_path.write_text(new_content, encoding='utf-8')
        print("✅ Performance monitor replaced successfully")
        return True
    else:
        print("❌ Could not find performance monitor section")
        return False

def inject_auth_system():
    """Inject real authentication system into dashboard.py"""
    dashboard_path = Path("antigravity/dashboard.py")
    auth_path = Path("antigravity/p3_auth_system.py")
    
    # Read files
    dashboard_content = dashboard_path.read_text(encoding='utf-8')
    auth_content = auth_path.read_text(encoding='utf-8')
    
    # Remove comment header from auth system
    auth_code = '\n'.join([
        line for line in auth_content.split('\n')
        if not (line.strip().startswith('#') and 'P3 Phase 17' in line and 'Authentication' in line)
    ])
    
    # Find injection point - after imports but before any Streamlit code
    # Look for the first occurrence of st.set_page_config
    pattern = r'(st\.set_page_config\()'
    
    match = re.search(pattern, dashboard_content)
    if match:
        injection_point = match.start()
        
        # Find the imports section
        # Get the line before st.set_page_config
        lines = dashboard_content.split('\n')
        line_index = 0
        for i, line in enumerate(lines):
            if 'st.set_page_config' in line:
                line_index = i
                break
        
        # Insert auth system right before st.set_page_config
        new_lines = lines[:line_index] + ['\n' + auth_code + '\n'] + lines[line_index:]
        new_content = '\n'.join(new_lines)
        
        # Write back
        dashboard_path.write_text(new_content, encoding='utf-8')
        print("✅ Authentication system injected successfully")
        return True
    else:
        print("❌ Could not find injection point for auth system")
        return False

def update_auth_integration():
    """Update dashboard to use the new auth system"""
    dashboard_path = Path("antigravity/dashboard.py")
    
    dashboard_content = dashboard_path.read_text(encoding='utf-8')
    
    # Replace old auth placeholder with actual auth check
    # Look for the old auth placeholder pattern
    old_auth_pattern = r'# Authentication placeholder.*?\n.*?if True:  # Replace with real auth'
    
    # New auth check code
    new_auth_check = """# Authentication check
    if not st.session_state.get('authenticated'):
        st.warning("🔒 Please authenticate to access the dashboard")
        st.stop()
    
    # User info display
    if st.session_state.get('user_info'):
        user_info = st.session_state.user_info
        st.sidebar.markdown(f"**👤 User:** {user_info.get('username', 'Unknown')}")
        st.sidebar.markdown(f"**🏢 Organization:** {user_info.get('organization', 'Unknown')}")
    
    # Logout button
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()"""
    
    # Replace the old auth placeholder
    new_content = re.sub(old_auth_pattern, new_auth_check, dashboard_content, flags=re.DOTALL)
    
    if new_content != dashboard_content:
        dashboard_path.write_text(new_content, encoding='utf-8')
        print("✅ Authentication integration updated successfully")
        return True
    else:
        print("⚠️  No old auth placeholder found - may already be updated")
        return False

if __name__ == "__main__":
    print("🚀 P3 Phase 17.5: Automated Integration")
    print("=" * 50)
    
    # Step 1: Inject project selector
    print("\n📍 Step 1: Injecting project selector...")
    if inject_project_selector():
        print("   ✅ Selector injection complete")
    
    # Step 2: Replace performance monitor
    print("\n📍 Step 2: Replacing performance monitor...")
    if inject_performance_monitor():
        print("   ✅ Performance monitor replacement complete")
    
    # Step 3: Inject auth system
    print("\n📍 Step 3: Injecting authentication system...")
    if inject_auth_system():
        print("   ✅ Auth system injection complete")
    
    # Step 4: Update auth integration
    print("\n📍 Step 4: Updating auth integration...")
    if update_auth_integration():
        print("   ✅ Auth integration update complete")
    
    print("\n" + "=" * 50)
    print("🎉 Integration complete!")
    print("\nNext steps:")
    print("1. Review changes in antigravity/dashboard.py")
    print("2. Test authentication system in Dashboard")
    print("3. Verify login/logout functionality works")
    print("4. Test project switching with authentication")