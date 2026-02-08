
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
        sys.path.insert(0, r"d:\桌面\AGENT")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Apply changes")
    args = parser.parse_args()
    
    scan_and_clean(r"d:\桌面\AGENT", clean_mode=args.clean)
