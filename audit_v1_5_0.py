
import os
import sys
import json
import ast
import hashlib
from pathlib import Path
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Use built-in safe read or fallback
try:
    from antigravity.utils.io_utils import safe_read
except ImportError:
    def safe_read(path):
        return Path(path).read_text(encoding='utf-8', errors='replace')

def generate_ast_hash(content):
    try:
        tree = ast.parse(content)
        # Dump AST to string and hash it (stable structure check)
        dump = ast.dump(tree, include_attributes=False)
        return hashlib.sha256(dump.encode('utf-8')).hexdigest()[:16]
    except Exception:
        return "PARSE_ERROR"

def audit_project(root_dir):
    snapshot = []
    print(f"🛡️  Iron Gate Global Audit: {root_dir}")
    print(f"{'Path':<60} | {'MTime':<20} | {'Lines':<5} | {'AST Hash':<16}")
    print("-" * 110)

    # Core Antigravity + Projects
    scan_paths = [Path(root_dir) / "antigravity", Path(root_dir) / "projects"]
    
    for base_path in scan_paths:
        if not base_path.exists():
            continue
            
        for path in base_path.rglob("*.py"):
            if "site-packages" in str(path) or ".venv" in str(path) or "__pycache__" in str(path):
                continue
                
            try:
                # Physical read with 'safe_content_for_protobuf' equivalent (safe_read)
                content = safe_read(path)
                
                # Stats
                stat = path.stat()
                mtime = stat.st_mtime
                line_count = len(content.splitlines())
                
                # AST Fingerprint
                ast_hash = generate_ast_hash(content)
                
                rel_path = str(path.relative_to(root_dir))
                
                record = {
                    "path": rel_path,
                    "mtime": mtime,
                    "line_count": line_count,
                    "ast_hash": ast_hash
                }
                snapshot.append(record)
                
                print(f"{rel_path:<60} | {mtime:<20} | {line_count:<5} | {ast_hash:<16}")
                
            except Exception as e:
                print(f"❌ Error auditing {path}: {e}")

    # Generate AST_SNAPSHOT.json
    snapshot_path = Path(root_dir) / "AST_SNAPSHOT.json"
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump({"timestamp": datetime.now().isoformat(), "files": snapshot}, f, indent=2)
        
    print("-" * 110)
    print(f"✅ AST Snapshot generated at {snapshot_path}")

if __name__ == "__main__":
    audit_project(r"d:\桌面\AGENT")
