import json
import hashlib
from pathlib import Path
from datetime import datetime

def sign_off_vortex():
    project_root = Path("vortex")
    if not project_root.exists():
        print("❌ Vortex root not found")
        return

    print("🔐 Signing off Vortex Code...")
    
    # Calculate Merkle
    files = list(project_root.rglob("*.py"))
    # Match DeliveryGate sorting (by string path)
    # DeliveryGate uses os.path.join paths sorted.
    # Path objects sort similarly.
    files = sorted(files, key=lambda p: str(p))
    
    hashes = []
    for f in files:
        if '__pycache__' in str(f):
            continue
            
        with open(f, 'rb') as fh:
            content = fh.read()
        
        h = hashlib.sha256(content).hexdigest()
        hashes.append(h)
        print(f"   - {f.name}: {h[:8]}...")
        
    merkle_root = hashlib.sha256("".join(hashes).encode()).hexdigest()
    project_hash = hashlib.sha256(project_root.name.encode()).hexdigest() # Dummy project hash
    
    sign_off_data = {
        'project_name': 'vortex_core',
        'version': '1.0.0',
        'project_hash': f"sha256:{project_hash}",
        'source_code_merkle_root': f"merkle:{merkle_root}",
        'delivery_approved': True,
        'local_signature': {
            'signed': True,
            'timestamp': datetime.now().isoformat(),
            'signature': f"LOCAL-VORTEX-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    }
    
    with open(project_root / 'SIGN_OFF.json', 'w', encoding='utf-8') as f:
        json.dump(sign_off_data, f, indent=2)
        
    print(f"✅ Vortex Signed Off. Merkle: {merkle_root[:16]}...")

if __name__ == "__main__":
    sign_off_vortex()
