
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, r"d:\桌面\AGENT")

from antigravity.core.fleet_manager import ProjectFleetManager
from antigravity.core.fleet_refactor_manager import FleetRefactorManager

# 1. Initialize Fleet Manager and Scan Pilot Projects
fm = ProjectFleetManager.get_instance()
# Force add our pilot projects since they might not be in default scan path or need explicit registration
# Note: register_project expects Path object (project_id is derived from dir name)
fm.register_project(Path(r"d:\桌面\AGENT\projects\vortex_core"))
fm.register_project(Path(r"d:\桌面\AGENT\projects\vortex_scraper"))

print("✅ Pilot Fleet Registered.")

# 2. Trigger Refactor Manager
refactor_mgr = FleetRefactorManager()
print("🏥 Propagation Update for 'vortex_core'...")

# Simulate "Breaking Change in Request Signature"
try:
    refactor_mgr.propagate_update(
        provider_id="vortex_core", 
        change_summary="API Breaking Change: Added 'timeout' parameter to AsyncConnectionPool.request()"
    )
except TypeError as e:
    # Fallback if signature mismatch (during dev)
    print(f"⚠️ Call failed: {e}")
    # Try positional
    refactor_mgr.propagate_update(
        "vortex_core", 
        "API Breaking Change: Added 'timeout' parameter to AsyncConnectionPool.request()"
    )

# 3. Verify Intention
intention_file = Path(r"d:\桌面\AGENT\projects\vortex_scraper\INTENTION.md")
if intention_file.exists():
    print(f"✅ SUCCESS: INTENTION.md generated at {intention_file}")
    print("📄 Content Preview:")
    print(intention_file.read_text(encoding='utf-8')[:300] + "...")
else:
    print("❌ FAILURE: INTENTION.md not found.")
