"""
Antigravity 并行启动脚本
Antigravity Parallel Startup Script

并行启动 Monitor 和 Dashboard,带健康监控
Launches both Monitor and Dashboard in parallel with health monitoring
"""
import subprocess
import sys
import time
import os
import signal

def start_antigravity():
    """
    启动 Antigravity 系统,并行运行监控器和面板
    Start Antigravity system with parallel monitor and dashboard
    """
    print("🚀 正在启动 Antigravity 系统...")
    print("🚀 Starting Antigravity System...")
    print("=" * 60)
    
    # 获取 Python 解释器路径
    # Get Python interpreter path
    python_exe = sys.executable
    
    # 1. 启动 Monitor Agent (后台进程)
    # 1. Start Monitor Agent (background process)
    print("📡 正在启动监控代理...")
    print("📡 Starting Monitor Agent...")
    monitor_proc = subprocess.Popen(
        [python_exe, "-m", "antigravity.monitor"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    print("✅ 监控代理已启动 (进程ID: {})".format(monitor_proc.pid))
    print("✅ Monitor Agent started (PID: {})".format(monitor_proc.pid))
    
    # 给监控器一点时间初始化
    # Give monitor a moment to initialize
    time.sleep(1)
    
    # 2. 启动 Dashboard (Streamlit)
    # 2. Start Dashboard (Streamlit)
    print("🌐 正在启动 Web 面板...")
    print("🌐 Starting Web Dashboard...")
    dashboard_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", 
         "antigravity/dashboard.py", 
         "--server.headless", "true",
         "--server.port", "8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    print("✅ Web 面板已启动 (进程ID: {})".format(dashboard_proc.pid))
    print("✅ Web Dashboard started (PID: {})".format(dashboard_proc.pid))
    
    print("=" * 60)
    print("🎯 Antigravity 正在运行!")
    print("🎯 Antigravity is now running!")
    print("📊 面板地址 / Dashboard: http://localhost:8501")
    print("🛑 按 Ctrl+C 停止所有服务 / Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # 如果可用,发送桌面通知
    # Send desktop notification if available
    try:
        from antigravity.notifier import send_notification
        send_notification("Antigravity System", "前后端已并行启动,接管模式就绪。")
    except Exception:
        pass  # 如果通知器不可用,静默失败 / Silent fail if notifier not available
    
    # 健康监控循环
    # Health monitoring loop
    try:
        while True:
            time.sleep(2)
            
            # 检查监控器是否意外退出
            # Check if monitor died
            if monitor_proc.poll() is not None:
                print("❌ 监控进程意外退出 (退出码: {})".format(monitor_proc.returncode))
                print("❌ Monitor process exited unexpectedly (code: {})".format(monitor_proc.returncode))
                print("🔄 正在尝试重启监控器...")
                print("🔄 Attempting to restart monitor...")
                monitor_proc = subprocess.Popen(
                    [python_exe, "-m", "antigravity.monitor"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                print("✅ 监控器已重启 (进程ID: {})".format(monitor_proc.pid))
                print("✅ Monitor restarted (PID: {})".format(monitor_proc.pid))
            
            # 检查面板是否意外退出
            # Check if dashboard died
            if dashboard_proc.poll() is not None:
                print("❌ 面板进程意外退出 (退出码: {})".format(dashboard_proc.returncode))
                print("❌ Dashboard process exited unexpectedly (code: {})".format(dashboard_proc.returncode))
                print("🔄 正在尝试重启面板...")
                print("🔄 Attempting to restart dashboard...")
                dashboard_proc = subprocess.Popen(
                    [python_exe, "-m", "streamlit", "run", 
                     "antigravity/dashboard.py", 
                     "--server.headless", "true",
                     "--server.port", "8501"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT
                )
                print("✅ 面板已重启 (进程ID: {})".format(dashboard_proc.pid))
                print("✅ Dashboard restarted (PID: {})".format(dashboard_proc.pid))
                
    except KeyboardInterrupt:
        print("\n🛑 正在停止 Antigravity 系统...")
        print("🛑 Stopping Antigravity System...")
        
        # 优雅关闭
        # Graceful shutdown
        print("⏹️  正在终止监控器...")
        print("⏹️  Terminating Monitor...")
        monitor_proc.terminate()
        
        print("⏹️  正在终止面板...")
        print("⏹️  Terminating Dashboard...")
        dashboard_proc.terminate()
        
        # 等待进程终止
        # Wait for processes to terminate
        try:
            monitor_proc.wait(timeout=5)
            dashboard_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  强制结束进程...")
            print("⚠️  Force killing processes...")
            monitor_proc.kill()
            dashboard_proc.kill()
        
        print("✅ 所有服务已停止 / All services stopped.")
        print("👋 再见! / Goodbye!")

if __name__ == "__main__":
    # 检查是否在正确的目录
    # Check if we're in the right directory
    if not os.path.exists("antigravity"):
        print("❌ 错误: 必须从项目根目录运行")
        print("❌ Error: Must run from project root directory")
        print("   当前目录 / Current directory: {}".format(os.getcwd()))
        sys.exit(1)
    
    # 检查必需文件是否存在
    # Check if required files exist
    if not os.path.exists("config/settings.json"):
        print("⚠️  警告: 未找到 config/settings.json")
        print("⚠️  Warning: config/settings.json not found")
    
    if not os.path.exists("config/prompts.yaml"):
        print("⚠️  警告: 未找到 config/prompts.yaml")
        print("⚠️  Warning: config/prompts.yaml not found")
    
    start_antigravity()
