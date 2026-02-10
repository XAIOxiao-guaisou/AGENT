
import subprocess
import time
import sys
import os

def start_web_factory():
    """
    Antigravity Web Factory Startup Script
    Launches Dashboard (8501) and Cyberpunk HUD (8502) concurrently.
    """
    print("🛡️ Ignite: Antigravity Web Factory v2.0.0")
    
    # 0. Pre-Flight Check: Physical Editor
    editor_lnk = "D:\\桌面\\Antigravity.lnk"
    if not os.path.exists(editor_lnk):
        print(f"⚠️  WARNING: Physical Editor Link not found at {editor_lnk}")
        print("    Auto-dispatch features may fail. Please verify path in config/settings.json.")
    else:
        print(f"✅ Physical Editor Detected: {editor_lnk}")

    # 1. Launch Control Dashboard (Port 8501)
    print("   🚀 Launching Control Dashboard (8501)...")
    dashboard_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "antigravity/interface/dashboard.py", 
        "--server.port", "8501",
        "--theme.base", "dark"
    ]
    # Use Popen for non-blocking execution
    # On Windows, we refrain from creationflags=subprocess.CREATE_NEW_CONSOLE to keep them in one terminal or hidden
    # But user might want to see logs. Let's keep them attached or redirect to null?
    # The prompt implies a background launch '&'.
    
    dashboard_process = subprocess.Popen(
        dashboard_cmd,
        cwd=os.getcwd(),
        shell=False
    )
    
    # Wait a bit to prevent port race conditions or resource contention
    time.sleep(2)
    
    # 2. Launch Cyberpunk HUD (Port 8502)
    print("   🔮 Launching Cyberpunk Visual Cortex (8502)...")
    hud_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "antigravity/interface/cyberpunk_hud.py", 
        "--server.port", "8502",
        "--theme.base", "dark"
    ]
    
    hud_process = subprocess.Popen(
        hud_cmd,
        cwd=os.getcwd(),
        shell=False
    )

    # 3. Launch Backend Execution Engine (Monitor) - Triple Ignition
    print("   ⚙️ Launching Backend Execution Engine (Monitor)...")
    monitor_cmd = [sys.executable, "antigravity/infrastructure/monitor.py"]
    monitor_process = subprocess.Popen(
        monitor_cmd,
        cwd=os.getcwd(),
        shell=False
    )
    
    print("\n✅ Antigravity Web Factory Online:")
    print("   - 📊 Dashboard: http://localhost:8501")
    print("   - 🔮 HUD:       http://localhost:8502")
    print("\nPress Ctrl+C to shutdown both services.")
    
    try:
        # Keep main script alive to monitor child processes
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if dashboard_process.poll() is not None:
                print("⚠️ Dashboard process terminated unexpectedly.")
                break
            if hud_process.poll() is not None:
                print("⚠️ HUD process terminated unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Web Factory...")
        dashboard_process.terminate()
        hud_process.terminate()
        monitor_process.terminate()
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    start_web_factory()
