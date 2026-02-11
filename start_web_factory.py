import subprocess
import time
import sys
import os

def start_web_factory():
    print("🛡️ Ignite: Antigravity Web Factory v2.1.15")
    
    # 显式设置 PYTHONPATH 环境变量 & Streamlit 配置 (Suppress Welcome Prompt)
    env_config = os.environ.copy()
    env_config["PYTHONPATH"] = os.getcwd()
    env_config["STREAMLIT_SERVER_HEADLESS"] = "true"
    env_config["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # Port Selection Logic
    def find_free_port(start_port):
        import socket
        port = start_port
        while port < start_port + 100:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(('localhost', port))
                if res != 0: # Port is free
                    return port
            port += 1
        raise RuntimeError(f"No free ports found starting from {start_port}")

    dashboard_port = find_free_port(8501)
    hud_port = find_free_port(dashboard_port + 1)

    # 1. 启动 Monitor (后端引擎)
    print("   ⚙️ Launching Backend Execution Engine (Monitor)...")
    monitor_process = subprocess.Popen([sys.executable, "-m", "antigravity.infrastructure.monitor"], env=env_config)

    # 2. 启动 Dashboard
    print(f"   🚀 Launching Control Dashboard ({dashboard_port})...")
    dash_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "antigravity/interface/dashboard.py", "--server.port", str(dashboard_port)], env=env_config)

    # 3. 启动 HUD
    print(f"   🔮 Launching Cyberpunk Visual Cortex ({hud_port})...")
    hud_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "antigravity/interface/cyberpunk_hud.py", "--server.port", str(hud_port)], env=env_config)

    print("\n✅ Antigravity Factory Online (Namespace & Ports Aligned)")
    
    # 4. Auto-Open Browser (v2.1.16: Smart Wait)
    def wait_for_port(port, timeout=15):
        import socket
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection(("localhost", port), timeout=1):
                    return True
            except (OSError, ConnectionRefusedError):
                time.sleep(1)
        return False

    try:
        import webbrowser
        print("   🌐 Waiting for services to initialize...")
        
        # Parallel-ish wait not strictly necessary, sequential is fine for usability
        if wait_for_port(dashboard_port):
            print(f"   ✅ Dashboard ready! Opening http://localhost:{dashboard_port}")
            webbrowser.open(f"http://localhost:{dashboard_port}")
        else:
            print(f"   ⚠️ Dashboard ({dashboard_port}) startup timed out.")

        if wait_for_port(hud_port):
            print(f"   ✅ HUD ready! Opening http://localhost:{hud_port}")
            webbrowser.open(f"http://localhost:{hud_port}")
        else:
            print(f"   ⚠️ HUD ({hud_port}) startup timed out.")
            
    except Exception as e:
        print(f"⚠️ Browser auto-launch failed: {e}")

    try:
        while True:
            time.sleep(2)
            if monitor_process.poll() is not None:
                print("⚠️ Monitor engine died. Auto-restarting...")
                monitor_process = subprocess.Popen([sys.executable, "-m", "antigravity.infrastructure.monitor"], env=env_config)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Factory...")
        for p in [monitor_process, dash_process, hud_process]: p.terminate()

if __name__ == "__main__":
    start_web_factory()
