import importlib
import sys
import subprocess
import os

def check_dependencies(plan_content):
    """
    Scan PLAN.md for keywords and check if required packages are installed.
    """
    missing_packages = []
    
    # Mapping keywords to package names
    dependency_map = {
        "playwright": "playwright",
        "selenium": "selenium",
        "pandas": "pandas",
        "numpy": "numpy",
        "requests": "requests",
        "bs4": "beautifulsoup4"
    }
    
    for keyword, package in dependency_map.items():
        if keyword in plan_content.lower():
            if not is_installed(package):
                missing_packages.append(package)
                
    if missing_packages:
        print(f"\n[ENV SAFETY] Missing dependencies detected for PLAN: {', '.join(missing_packages)}")
        print("installing automatically...")
        install_packages(missing_packages)

def is_installed(package_name):
    try:
        # Special handling for packages with different import names
        import_name = package_name
        if package_name == "beautifulsoup4":
            import_name = "bs4"
            
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_packages(packages):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("Dependencies installed successfully.")
        
        # Post-install hooks (e.g. playwright install)
        if "playwright" in packages:
             print("Running 'playwright install'...")
             subprocess.check_call([sys.executable, "-m", "playwright", "install"])
             
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)
