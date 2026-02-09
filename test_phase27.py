"""
Phase 27 Verification: Global Sovereignty
-----------------------------------------
Tests Zombie Reaper and Sovereign Audit Report.
"""
import sys
import os
import shutil
import time
import json
from pathlib import Path

# Ensure antigravity importable
sys.path.insert(0, os.getcwd())

from antigravity.core.fleet_manager import ProjectFleetManager
import sovereign_audit

def test_sovereignty_final():
    print("🏁 TESTING GLOBAL SOVEREIGNTY (Phase 27)...")
    
    fleet_mgr = ProjectFleetManager.get_instance()
    
    # 1. Setup Test Fleet
    print("\n[1/3] Seeding Test Fleet...")
    # Clean up previous runs
    for p in ["ZOMBIE_V1", "SURVIVOR_V1"]:
        if (fleet_mgr.fleet_root / p).exists():
            shutil.rmtree(fleet_mgr.fleet_root / p)
        q_path = fleet_mgr.fleet_root / ".quarantine" / f"{p}_ZOMBIE"
        if q_path.exists():
            shutil.rmtree(q_path)

    # Create SURVIVOR (Fresh Heartbeat)
    survivor = fleet_mgr.create_sovereign_project("SURVIVOR_V1", "Survivor Node")
    (survivor / ".antigravity" / "HEARTBEAT").touch()
    
    # Create ZOMBIE (Stale Heartbeat > 1hr)
    zombie = fleet_mgr.create_sovereign_project("ZOMBIE_V1", "Zombie Node")
    beat_file = zombie / ".antigravity" / "HEARTBEAT"
    beat_file.touch()
    
    # Modify mtime to be 2 hours ago
    past_time = time.time() - 7200
    os.utime(beat_file, (past_time, past_time))
    
    print("   seeds planted: SURVIVOR_V1 (Fresh), ZOMBIE_V1 (Stale)")
    
    # 2. Run Audit (Triggers Reaper)
    print("\n[2/3] Executing Sovereign Audit...")
    try:
        sovereign_audit.audit_sovereignty()
    except Exception as e:
        print(f"❌ Audit Crashed: {e}")
        sys.exit(1)
        
    # 3. Verify Reaper
    print("\n[3/3] Verifying Aftermath...")
    
    # Check Survivor
    if (fleet_mgr.fleet_root / "SURVIVOR_V1").exists():
        print("   ✅ SURVIVOR_V1 is alive.")
    else:
        print("   ❌ SURVIVOR_V1 was mistaken for a zombie!")
        sys.exit(1)
        
    # Check Zombie
    if (fleet_mgr.fleet_root / "ZOMBIE_V1").exists():
        print("   ❌ ZOMBIE_V1 is still walking!")
        sys.exit(1)
    
    zombie_corpse = fleet_mgr.fleet_root / ".quarantine" / "ZOMBIE_V1_ZOMBIE"
    if zombie_corpse.exists():
        print("   ✅ ZOMBIE_V1 successfully quarantined.")
    else:
        print(f"   ❌ ZOMBIE_V1 vanished but not in quarantine? ({zombie_corpse})")
        sys.exit(1)
        
    # Check Report
    if Path("fleet_sovereignty_v2.json").exists():
        with open("fleet_sovereignty_v2.json", "r") as f:
            data = json.load(f)
            stats = data.get("fleet_stats", {})
            if stats.get("active_projects") >= 1: # Survivor + maybe others
                print(f"   ✅ Report generated. Active Projects: {stats['active_projects']}")
            else:
                 print("   ⚠️ Report stats look low.")
    else:
        print("   ❌ Report fleet_sovereignty_v2.json missing.")
        sys.exit(1)

    print("\n🏁 GLOBAL SOVEREIGNTY VERIFIED.")

if __name__ == "__main__":
    test_sovereignty_final()
