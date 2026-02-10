import subprocess
import time
import sys
import os

def start_web_factory():
    print("🛡️ Ignite: Antigravity Web Factory v2.1.15")
    
    # 显式设置 PYTHONPATH 环境变量
    env_config = os.environ.copy()
    env_config["PYTHONPATH"] = os.getcwd()

    # 1. 启动 Monitor (后端引擎)
    print("   ⚙️ Launching Backend Execution Engine (Monitor)...")
    monitor_process = subprocess.Popen([sys.executable, "antigravity/infrastructure/monitor.py"], env=env_config)

    # 2. 启动 Dashboard (8501)
    print("   🚀 Launching Control Dashboard (8501)...")
    dash_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "antigravity/interface/dashboard.py", "--server.port", "8501"], env=env_config)

    # 3. 启动 HUD (8502)
    print("   🔮 Launching Cyberpunk Visual Cortex (8502)...")
    hud_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "antigravity/interface/cyberpunk_hud.py", "--server.port", "8502"], env=env_config)

    print("\n✅ Antigravity Factory Online (Namespace & Ports Aligned)")
    
    try:
        while True:
            time.sleep(2)
            if monitor_process.poll() is not None:
                print("⚠️ Monitor engine died. Auto-restarting...")
                monitor_process = subprocess.Popen([sys.executable, "antigravity/infrastructure/monitor.py"], env=env_config)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Factory...")
        for p in [monitor_process, dash_process, hud_process]: p.terminate()

if __name__ == "__main__":
    start_web_factory()
