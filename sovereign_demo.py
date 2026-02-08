
import sys
import json
from pathlib import Path

# Add project root
sys.path.insert(0, r"d:\桌面\AGENT")

from antigravity.core.mission_orchestrator import MissionOrchestrator, ContextDriftError

# Load Snapshot
try:
    snapshot_path = Path(r"d:\桌面\AGENT\AST_SNAPSHOT.json")
    with open(snapshot_path, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)["files"]
        # Find io_utils
        # Note: snapshot path acts as key, might be relative
        io_utils_meta = next(f for f in snapshot_data if "io_utils.py" in f["path"])
        print(f"🧠 Mind (Snapshot): io_utils.py expects {io_utils_meta['line_count']} lines.")
except Exception as e:
    print(f"❌ Failed to load snapshot: {e}")
    sys.exit(1)

# Debug Import
import inspect
print(f"DEBUG: MissionOrchestrator file: {inspect.getfile(MissionOrchestrator)}")
print(f"DEBUG: Init signature: {inspect.signature(MissionOrchestrator.__init__)}")

# Initialize Orchestrator
try:
    # Try with project_root
    orchestrator = MissionOrchestrator(project_root=r"d:\桌面\AGENT")
except TypeError:
    print("⚠️ Init failed with args, trying no-args...")
    orchestrator = MissionOrchestrator()

# Target File
# Use absolute path as system runs in d:\桌面\AGENT
file_path = r"d:\桌面\AGENT\antigravity\utils\io_utils.py"

print(f"\n🧪 Demonstration: Orchestrator attempting access to {file_path}...")

try:
    # Attempt Audit
    # Passing expected_metadata derived from snapshot
    orchestrator.pre_edit_audit(file_path, expected_metadata=io_utils_meta)
    print("\n✅ SUCCESS: Iron Gate Authorized Access.")
except ContextDriftError as e:
    print(f"\n🔥 MELTDOWN: Hallucination Detected! {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
