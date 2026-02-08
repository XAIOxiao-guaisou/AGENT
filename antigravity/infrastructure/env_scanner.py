import sys
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Configure Logger
logger = logging.getLogger("antigravity.env_scanner")

class EnvScanner:
    """
    Antigravity v1.1.0 Feature 2: Environment Awareness
    
    Capabilities:
    1. Perception: Detect Python path and installed packages.
    2. Control Loop: Request permission to fix environment.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_path = sys.executable
        
    def scan_environment(self) -> Dict:
        """
        Scan the host environment.
        """
        return {
            "python_path": self.python_path,
            "os_platform": sys.platform,
            "pip_version": self._get_pip_version(),
            "cpu_count": self._get_cpu_count(),
        }

    def _get_cpu_count(self) -> int:
        import os
        return os.cpu_count() or 1

    def _get_pip_version(self) -> str:
        try:
            result = subprocess.run(
                [self.python_path, "-m", "pip", "--version"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.split()[1]
        except Exception:
            return "unknown"

    def check_dependency(self, package_name: str) -> bool:
        """
        Check if a package is installed.
        """
        try:
            # We use import check as definitive source in current env
            subprocess.run(
                [self.python_path, "-c", f"import {package_name}"],
                capture_output=True, check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def request_fix(self, package_name: str) -> bool:
        """
        The Control Loop: Request permission to install a missing dependency.
        Loads dynamic whitelist from config/settings.json.
        """
        logger.info(f"🚨 ENV_FIX_REQUEST: Missing dependency '{package_name}'")
        logger.info("   Waiting for Chief Reviewer approval...")
        
        whitelist = self._load_whitelist()
        
        if package_name in whitelist:
            logger.info(f"✅ APPROVED: '{package_name}' is whitelisted.")
            # Telemetry Pulse
            # In real system: self.telemetry.emit("ENV_FIX_APPROVED", package=package_name)
            return self._silent_install(package_name)
        else:
            logger.warning(f"❌ DENIED: '{package_name}' requires manual intervention.")
            logger.warning(f"   (Not in whitelist: {whitelist})")
            return False

    def _load_whitelist(self) -> List[str]:
        import json
        settings_path = self.project_root / 'config' / 'settings.json'
        default_whitelist = ["numpy", "httpx", "pandas"]
        
        if not settings_path.exists():
            return default_whitelist
            
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("env_scanner", {}).get("whitelist", default_whitelist)
        except Exception:
            return default_whitelist

    def _silent_install(self, package_name: str) -> bool:
        """
        Execute "Silent Install"
        """
        logger.info(f"🛠️ Executing Silent Install for {package_name}...")
        try:
            # Use --quiet to be truly silent
            subprocess.run(
                [self.python_path, "-m", "pip", "install", package_name, "--quiet"],
                check=True, capture_output=True
            )
            logger.info(f"✅ INSTALLED: {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ INSTALL FAILED: {e}")
            return False
