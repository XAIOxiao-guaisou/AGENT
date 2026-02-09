
import sys
import os
import shutil
from pathlib import Path
import json

# Ensure we can import antigravity
sys.path.insert(0, os.getcwd())

from antigravity.core.fleet_manager import ProjectFleetManager

def test_autonomous_genesis():
    print("🌌 TESTING AUTONOMOUS GENESIS (Phase 23)...")
    
    fleet_mgr = ProjectFleetManager.get_instance()
    project_id = "GENESIS_V1"
    intent = "Verify Sovereign Creation Protocol"
    
    # Clean up if exists
    target_dir = fleet_mgr.fleet_root / project_id
    if target_dir.exists():
        print(f"🧹 Cleaning up existing {project_id}...")
        try:
            shutil.rmtree(target_dir)
        except PermissionError:
             print("⚠️ Permission denied during cleanup. Please close files.")
             return

    # 1. Trigger Genesis
    try:
        path = fleet_mgr.create_sovereign_project(project_id, intent)
    except Exception as e:
        print(f"❌ Genesis Failed: {e}")
        sys.exit(1)
        
    # 2. Verify P3 Structure
    expected_paths = [
        path / ".antigravity" / "security" / "SIGN_OFF.json",
        path / ".antigravity" / "checkpoints",
        path / "config" / "settings.json",
        path / "src" / "main.py",
        path / "README.md"
    ]
    
    for p in expected_paths:
        if not p.exists():
            print(f"❌ P3 Violation: Missing {p.name}")
            sys.exit(1)
            
    # 3. Verify Iron Gate Signature
    sign_off_path = path / ".antigravity" / "security" / "SIGN_OFF.json"
    with open(sign_off_path, 'r') as f:
        sig = json.load(f)
        
    if sig.get('version') != "v1.8.0":
        print(f"❌ Signature Violation: Expected v1.8.0, got {sig.get('version')}")
        sys.exit(1)
        
    if "IRON_GATE" not in sig.get('security_protocols', []):
        print("❌ Protocol Violation: IRON_GATE missing.")
        sys.exit(1)
        
    print(f"✅ SUCCESS: Sovereign Project '{project_id}' created with v1.8.0 DNA.")
    print(f"   path: {path}")

if __name__ == "__main__":
    test_autonomous_genesis()
