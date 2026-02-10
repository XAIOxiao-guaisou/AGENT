"""
Self-Awareness Diagnostic Tool
Phase 24: Agent Sovereignty
"""
import json
import sys
from pathlib import Path

def vibe_check():
    print(f"🧘 VIBE CHECK: {Path.cwd().name}")
    score = 100
    
    # Check P3 Structure
    required = [".antigravity/security/SIGN_OFF.json", "config/settings.json", "src/main.py"]
    for r in required:
        if not Path(r).exists():
            print(f"❌ MISSING ORGANS: {r}")
            score -= 30
            
    # Check Iron Gate
    try:
        with open(".antigravity/security/SIGN_OFF.json", "r") as f:
            data = json.load(f)
            if "IRON_GATE" not in data.get("security_protocols", []):
                print("❌ SECURITY BREACH: Iron Gate missing")
                score -= 50
    except Exception as e:
        print(f"❌ BRAIN DAMAGE: {e}")
        score = 0
        
    print(f"✨ VIBE SCORE: {score}/100")
    if score < 90:
        print("   ⚠️  Self-Healing Required.")
        sys.exit(1)
    else:
        print("   ✅  I am Sovereign.")
        
if __name__ == "__main__":
    vibe_check()
