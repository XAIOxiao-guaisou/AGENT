import subprocess
import time
import sys
import os

def start_web_factory():
    print("🛡️ Ignite: Antigravity Web Factory v2.1.13")
    
    # 1. 启动后端监听引擎 (Backend Engine) - 直接脚本模式
    print("   ⚙️ Launching Backend Execution Engine (Monitor)...")
    # v2.1.14: Avoid RuntimeWarning by running as script
    monitor_cmd = [sys.executable, "antigravity/infrastructure/monitor.py"]
    monitor_process = subprocess.Popen(monitor_cmd, cwd=os.getcwd(), shell=False)

    # 2. 启动控制面板 (Dashboard: 8501)
    print("   🚀 Launching Control Dashboard (8501)...")
    dashboard_cmd = [sys.executable, "-m", "streamlit", "run", "antigravity/interface/dashboard.py", "--server.port", "8501"]
    dashboard_process = subprocess.Popen(dashboard_cmd, cwd=os.getcwd(), shell=False)
    
    time.sleep(2)
    
    # 3. 启动赛博视觉 HUD (HUD: 8502)
    print("   🔮 Launching Cyberpunk Visual Cortex (8502)...")
    hud_cmd = [sys.executable, "-m", "streamlit", "run", "antigravity/interface/cyberpunk_hud.py", "--server.port", "8502"]
    hud_process = subprocess.Popen(hud_cmd, cwd=os.getcwd(), shell=False)
    
    print("\n✅ Antigravity Factory Online (Triple Ignition Successful)")
    try:
        while True:
            time.sleep(2)
            if monitor_process.poll() is not None:
                print("⚠️ Monitor engine died. Auto-restarting...")
                monitor_process = subprocess.Popen(monitor_cmd, cwd=os.getcwd(), shell=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Factory...")
        for p in [monitor_process, dashboard_process, hud_process]: p.terminate()

if __name__ == "__main__":
    start_web_factory()
