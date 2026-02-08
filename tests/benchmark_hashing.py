import shutil
import time
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from antigravity.infrastructure.delivery_gate import DeliveryGate

def run_benchmark():
    repo_dir = Path("bench_repo")
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    repo_dir.mkdir()
    
    print("🚀 Preparing Benchmark: Generating 5000 files...")
    # Generate 5000 files
    # To be fast, we write minimal content
    for i in range(5000):
        (repo_dir / f"file_{i}.py").write_text(f"print('hello {i}')")
        
    print("📂 Files generated. Warming up...")
    gate = DeliveryGate(repo_dir)
    
    # Warmup
    gate._calculate_merkle_root()
    
    print("⏱️ Starting Measurement (Adaptive Batching)...")
    start_time = time.perf_counter()
    merkle = gate._calculate_merkle_root()
    end_time = time.perf_counter()
    
    duration = (end_time - start_time) * 1000
    print(f"✅ Benchmark Complete.")
    print(f"   Files: 5000")
    print(f"   Merkle Root: {merkle[:16]}...")
    print(f"   Time: {duration:.2f} ms")
    
    target = 100.0
    if duration < target:
        print(f"🎉 SUCCCESS: {duration:.2f}ms < {target}ms")
    else:
        print(f"⚠️ WARNING: {duration:.2f}ms > {target}ms (Optimization needed?)")

    # Cleanup
    import gc
    gc.collect()
    
    retries = 3
    for k in range(retries):
        try:
            shutil.rmtree(repo_dir)
            break
        except PermissionError:
            time.sleep(1)
            if k == retries - 1:
                print("⚠️ Failed to cleanup repo dir (safe to ignore for next run)")

if __name__ == "__main__":
    run_benchmark()
