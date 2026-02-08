import sys
import os
import shutil
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from antigravity.core.fleet_manager import ProjectFleetManager
from antigravity.core.knowledge_graph import FleetKnowledgeGraph

def main():
    print("🧠 Starting Global Wisdom Distillation...")

    # 1. Initialize Fleet Manager
    fm = ProjectFleetManager.get_instance()
    
    # Ensure current project is registered if fleet is empty
    if not fm.projects:
        print("⚠️ Fleet empty. Registering current workspace...")
        current_path = Path.cwd()
        fm.register_project(current_path)

    # 2. Build Metrics
    fleet_metrics = []
    print(f"📊 Fleet Size: {len(fm.projects)} Projects")
    
    for pid, meta in fm.projects.items():
        print(f"   - {pid} ({meta.path})")
        fleet_metrics.append({
            'project_id': pid,
            'path': meta.path
        })

    # 3. Execute Scan
    gkg = FleetKnowledgeGraph.get_instance()
    try:
        gkg.scan_fleet_wisdom(fleet_metrics)
        print("✅ Wisdom Scan Complete.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Scan Failed: {e}")
        sys.exit(1)

    # 4. Git Mirror Audit (Copy GKG to Repo)
    # Source: ~/.antigravity/fleet_knowledge_graph.json
    source_path = Path.home() / ".antigravity" / "fleet_knowledge_graph.json"
    dest_path = Path("antigravity/infrastructure/fleet_knowledge_graph.json")
    
    if source_path.exists():
        try:
            shutil.copy2(source_path, dest_path)
            print(f"✅ GKG Snapshot Mirrored to: {dest_path}")
        except Exception as e:
            print(f"❌ Mirror Failed: {e}")
    else:
        print(f"⚠️ Source GKG not found at {source_path}")

if __name__ == "__main__":
    main()
