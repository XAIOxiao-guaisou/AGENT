import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from antigravity.core.local_reasoning import LocalReasoningEngine

def main():
    print("🧠 Synapse Probe Test Sequence Initiated...")
    
    engine = LocalReasoningEngine()
    
    # Test Idea: "Encrypt user password"
    # Expected: 
    # 1. Intent mapped to "auth" or "crypto"
    # 2. Probe queries GKG
    # 3. Probe finds 'vortex_core' (if scanning works or simulated matches)
    
    idea = "I need to encrypt user passwords securely"
    print(f"\n📥 User Idea: '{idea}'")
    
    plan = engine.draft_plan(idea)
    
    print("\n📋 Drafted Plan:")
    print(f"   Intent: {plan.get('intent')}")
    print(f"   Dependencies: {plan.get('dependencies')}")

    # Debug GKG
    try:
        from antigravity.core.knowledge_graph import FleetKnowledgeGraph
        gkg = FleetKnowledgeGraph.get_instance()
        print(f"\n🔍 GKG Stats:")
        print(f"   Total Docs in Index: {gkg.semantic_index.total_docs}")
        print(f"   Projects: {list(gkg.knowledge.get('projects', {}).keys())}")
        
        # Manual Search
        search_q = intent = plan.get('intent')
        results = gkg.find_fleet_capability(search_q, top_k=5)
        print(f"\n🔍 Manual Search Results for '{search_q}':")
        for r in results:
            print(f"   - {r.get('id')} (Score: {r.get('score')})")
            
    except Exception as e:
        print(f"⚠️ Debug Error: {e}")
    
    # Check for Synapse Injection
    linked = any('vortex_core' in dep or 'fleet.' in dep for dep in plan.get('dependencies', []))
    
    if linked:
        print("\n✅ SYNAPSE SUCCESS: Auto-linked fleet dependency.")
    else:
        print("\n⚠️ SYNAPSE WARNING: No fleet dependency linked (GKG might be empty or no match).")
        # In this environment, GKG might not have 'vortex_core' indexed yet if 'wisdom_scan.py' didn't index it fully.
        # But let's see.

if __name__ == "__main__":
    main()
