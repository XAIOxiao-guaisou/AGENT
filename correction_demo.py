
import sys
import json
from pathlib import Path

# Add project root
sys.path.insert(0, r"d:\桌面\AGENT")

from antigravity.core.mission_orchestrator import MissionOrchestrator, ContextDriftError
from antigravity.utils.io_utils import safe_read
# write_file not in io_utils, using Path.write_text

# Setup
file_path = Path(r"d:\桌面\AGENT\antigravity\utils\io_utils.py")
snapshot_path = Path(r"d:\桌面\AGENT\AST_SNAPSHOT.json")

# Load Snapshot Metadata
try:
    with open(snapshot_path, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)["files"]
        io_utils_meta = next(f for f in snapshot_data if "io_utils.py" in f["path"])
        # Ensure we have the original counting
        original_lines = io_utils_meta['line_count']
        print(f"🧠 Mind (Snapshot): io_utils.py expects {original_lines} lines.")
except Exception as e:
    print(f"❌ Failed to load snapshot: {e}")
    sys.exit(1)

# Initialize Orchestrator
try:
    orchestrator = MissionOrchestrator(project_root=r"d:\桌面\AGENT")
except TypeError:
    orchestrator = MissionOrchestrator()

print(f"\n🧪 Demonstration: Context Drift & Correction Loop")
print(f"Objective: Verify system heals when Mind ({original_lines}) != Physical.")

# 1. Tamper (Create Drift)
print("\n🔧 Action: Tampering with physical file...")
original_content = safe_read(file_path)
tampered_content = original_content + "\n# Tampered Line for Phase 14.3 Test"
file_path.write_text(tampered_content, encoding='utf-8')

try:
    # 2. Audit (Expect Drift -> Healing)
    print("🛡️ Iron Gate: Auditing...")
    result = orchestrator.pre_edit_audit(str(file_path), expected_metadata=io_utils_meta)
    
    if result:
        print("\n✅ SUCCESS: Auto-Healing verified. Access Authorized.")
    else:
        print("\n❌ FAILURE: Access Denied.")

except Exception as e:
    print(f"\n❌ UNEXPECTED FAIL: {e}")

finally:
    # Cleanup
    print("\n🧹 Cleanup: Restoring physical file...")
    file_path.write_text(original_content, encoding='utf-8')
