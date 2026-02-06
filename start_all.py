"""
Antigravity Parallel Startup Script
Launches both Monitor and Dashboard in parallel with health monitoring.
"""
import subprocess
import sys
import time
import os
import signal

def start_antigravity():
    """Start Antigravity system with parallel monitor and dashboard."""
    print("🚀 Starting Antigravity System...")
    print("=" * 60)
    
    # Get Python interpreter path
    python_exe = sys.executable
    
    # 1. Start Monitor Agent (background process)
    print("📡 Starting Monitor Agent...")
    monitor_proc = subprocess.Popen(
        [python_exe, "-m", "antigravity.monitor"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    print("✅ Monitor Agent started (PID: {})".format(monitor_proc.pid))
    
    # Give monitor a moment to initialize
    time.sleep(1)
    
    # 2. Start Dashboard (Streamlit)
    print("🌐 Starting Web Dashboard...")
    dashboard_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", 
         "antigravity/dashboard.py", 
         "--server.headless", "true",
         "--server.port", "8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    print("✅ Web Dashboard started (PID: {})".format(dashboard_proc.pid))
    
    print("=" * 60)
    print("🎯 Antigravity is now running!")
    print("📊 Dashboard: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # Send desktop notification if available
    try:
        from antigravity.notifier import send_notification
        send_notification("Antigravity System", "前后端已并行启动,接管模式就绪。")
    except Exception:
        pass  # Silent fail if notifier not available
    
    # Health monitoring loop
    try:
        while True:
            time.sleep(2)
            
            # Check if monitor died
            if monitor_proc.poll() is not None:
                print("❌ Monitor process exited unexpectedly (code: {})".format(monitor_proc.returncode))
                print("🔄 Attempting to restart monitor...")
                monitor_proc = subprocess.Popen(
                    [python_exe, "-m", "antigravity.monitor"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                print("✅ Monitor restarted (PID: {})".format(monitor_proc.pid))
            
            # Check if dashboard died
            if dashboard_proc.poll() is not None:
                print("❌ Dashboard process exited unexpectedly (code: {})".format(dashboard_proc.returncode))
                print("🔄 Attempting to restart dashboard...")
                dashboard_proc = subprocess.Popen(
                    [python_exe, "-m", "streamlit", "run", 
                     "antigravity/dashboard.py", 
                     "--server.headless", "true",
                     "--server.port", "8501"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT
                )
                print("✅ Dashboard restarted (PID: {})".format(dashboard_proc.pid))
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping Antigravity System...")
        
        # Graceful shutdown
        print("⏹️  Terminating Monitor...")
        monitor_proc.terminate()
        
        print("⏹️  Terminating Dashboard...")
        dashboard_proc.terminate()
        
        # Wait for processes to terminate
        try:
            monitor_proc.wait(timeout=5)
            dashboard_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  Force killing processes...")
            monitor_proc.kill()
            dashboard_proc.kill()
        
        print("✅ All services stopped.")
        print("👋 Goodbye!")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("antigravity"):
        print("❌ Error: Must run from project root directory")
        print("   Current directory: {}".format(os.getcwd()))
        sys.exit(1)
    
    # Check if required files exist
    if not os.path.exists("config/settings.json"):
        print("⚠️  Warning: config/settings.json not found")
    
    if not os.path.exists("config/prompts.yaml"):
        print("⚠️  Warning: config/prompts.yaml not found")
    
    start_antigravity()
