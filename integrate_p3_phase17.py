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
    
    print("\n" + "=" * 50)
    print("🎉 Integration complete!")
    print("\nNext steps:")
    print("1. Review changes in antigravity/dashboard.py")
    print("2. Test project selector in Dashboard")
    print("3. Verify project switching works")
