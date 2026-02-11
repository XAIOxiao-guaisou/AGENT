
import sys
import argparse
from pathlib import Path

# Add root
sys.path.insert(0, str(Path(__file__).parents[2]))

# Import safe_read and sanitize_for_protobuf
# write_file is not in io_utils, use Path.write_text
try:
    from antigravity.utils.io_utils import safe_read, sanitize_for_protobuf
except ImportError:
    # Fallback if path insert fails or running from wrong dir
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from antigravity.utils.io_utils import safe_read, sanitize_for_protobuf
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        sys.exit(1)

def scan_and_clean(root_dir, clean_mode=False):
    print(f"🧹 Full Project Scan (Clean Mode: {clean_mode})")
    root = Path(root_dir)
    cleaned_files = []
    
    for path in root.rglob("*.py"):
        if "site-packages" in str(path) or ".git" in str(path) or "__pycache__" in str(path):
            continue
            
        try:
            # 1. Read (Safe)
            content = safe_read(path)
            
            # 2. Sanitize
            safe_content = sanitize_for_protobuf(content)
            
            # 3. Write Config
            if content != safe_content:
                if clean_mode:
                    path.write_text(safe_content, encoding='utf-8')
                    cleaned_files.append(str(path))
                    print(f"   ✨ Sanitized: {path.name}")
                else:
                    print(f"   ⚠️ Dirty File (Dry Run): {path.name}")
            else:
                pass # Clean
                
        except Exception as e:
            print(f"   ❌ Error {path.name}: {e}")
            
    print(f"\n📊 Summary: {len(cleaned_files)} files sanitized.")
    return cleaned_files

def scan_semantic(root_dir, output_file="fleet_knowledge_graph.json"):
    print(f"🧠 Semantic Topology Scan initiated...")
    print(f"   Target: {root_dir}")
    print(f"   Output: {output_file}")
    
    try:
        from antigravity.core.knowledge_graph import FleetKnowledgeGraph
        from pathlib import Path
        
        # Initialize KG
        kg = FleetKnowledgeGraph.get_instance()
        
        # Override output path so save_graph writes where we want
        kg.graph_path = Path(output_file)
        
        # Construct metrics for the current project to trigger scan
        # We treat the current root as a single project "antigravity_v2"
        fleet_metrics = [{
            "project_id": "antigravity_v2",
            "path": str(root_dir)
        }]
        
        # Scan and Save
        # scan_fleet_wisdom will internally call save_graph()
        kg.scan_fleet_wisdom(fleet_metrics)
            
        print(f"✅ Semantic Scan Complete. Topology saved to {output_file}")
        
    except ImportError:
        print("❌ FleetKnowledgeGraph not found. Cannot perform semantic scan.")
    except Exception as e:
        print(f"❌ Semantic Scan Failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Apply changes in clean mode")
    parser.add_argument("--mode", type=str, default="clean", choices=["clean", "semantic"], help="Scan mode")
    parser.add_argument("--output", type=str, default="fleet_knowledge_graph.json", help="Output file for semantic scan")
    
    args = parser.parse_args()
    
    if args.mode == "semantic":
        scan_semantic(r"d:\桌面\AGENT", args.output)
    else:
        scan_and_clean(r"d:\桌面\AGENT", clean_mode=args.clean)
