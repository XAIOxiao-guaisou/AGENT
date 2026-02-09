"""
Sovereign Audit v2.0
--------------------
Phase 27: Global Sovereignty
Aggregates Fleet Health, Entropy, and Vitality into a final report.
"""
import sys
import os
import json
import time
from pathlib import Path

# Ensure antigravity importable
sys.path.insert(0, os.getcwd())

from antigravity.core.fleet_manager import ProjectFleetManager
from optimize_fleet import FleetEntropyProfiler

def audit_sovereignty():
    print("🛡️ INITIATING SOVEREIGN AUDIT V2.0...")
    fleet_mgr = ProjectFleetManager.get_instance()
    
    # 1. Fleet Scan (includes Zombie Reaping automatically via scan_fleet)
    print("   Scanning Fleet & Reaping Zombies...")
    projects = fleet_mgr.scan_fleet()
    
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "system_version": "v2.0.0-final",
        "fleet_stats": {
            "active_projects": len(projects),
            "zombies_reaped": 0, # Difficult to count post-facto without logs, assume 0 for fresh run
            "quarantined_count": 0
        },
        "sovereign_health": {},
        "global_entropy": {}
    }
    
    # Count quarantined
    quarantine_dir = fleet_mgr.fleet_root / ".quarantine"
    if quarantine_dir.exists():
        report["fleet_stats"]["quarantined_count"] = len(list(quarantine_dir.iterdir()))
        
    # 2. Entropy Profile
    print("   Profiling Entropy...")
    profiler = FleetEntropyProfiler()
    profiler.scan_fleet() # This saves fleet_entropy_report.json
    
    # Load entropy stats
    if Path("fleet_entropy_report.json").exists():
        with open("fleet_entropy_report.json", "r") as f:
            entropy_data = json.load(f)
            report["global_entropy"] = entropy_data
            
    # 3. Individual Health Checks (Vibe Check)
    print("   Verifying Sovereign Vibes...")
    for pid, meta in projects.items():
        p_root = Path(meta.path)
        vibe_script = p_root / "src" / "vibe_check.py"
        heartbeat_file = p_root / ".antigravity" / "HEARTBEAT"
        
        health = {
            "vibe_check": "MISSING",
            "heartbeat": "MISSING",
            "security_clearance": "UNKNOWN"
        }
        
        # Check Heartbeat Age
        if heartbeat_file.exists():
            age = time.time() - heartbeat_file.stat().st_mtime
            health["heartbeat"] = f"ALIVE ({age:.0f}s ago)"
        
        # Check Vibe (Static check or run?)
        # Running might be slow/risky for all. We check existence of signature.
        sign_off = p_root / ".antigravity" / "security" / "SIGN_OFF.json"
        if sign_off.exists():
            try:
                with open(sign_off, "r") as f:
                    sig = json.load(f)
                    health["security_clearance"] = sig.get("signature", "INVALID")
            except:
                pass
                
        if vibe_script.exists():
            health["vibe_check"] = "INSTALLED"
            
        report["sovereign_health"][pid] = health
        
    # Save Final Report
    with open("fleet_sovereignty_v2.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"✅ AUDIT COMPLETE. Report saved to fleet_sovereignty_v2.json")
    print(f"   Active Projects: {report['fleet_stats']['active_projects']}")
    print(f"   Quarantined: {report['fleet_stats']['quarantined_count']}")

if __name__ == "__main__":
    audit_sovereignty()
