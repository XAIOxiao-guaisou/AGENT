
"""
P3 Root Detector (Phase 22 - Deduplication)
===========================================

Standardizes project root detection across the kernel.
Replaces ad-hoc logic in EnvScanner, FleetManager, and MissionOrchestrator.
"""

from pathlib import Path
from typing import Optional
import os

def find_project_root(start_path: Optional[str] = None) -> Path:
    """
    Find the project root by looking for marker files.
    Markers: .antigravity, task.md, requirements.txt, .git
    """
    if start_path:
        current = Path(start_path).resolve()
    else:
        current = Path(os.getcwd()).resolve()
        
    markers = ['.antigravity', 'task.md', 'requirements.txt', '.git']
    
    # Traverse up to root
    for _ in range(10): # Max depth 10
        if any((current / m).exists() for m in markers):
            return current
        
        parent = current.parent
        if parent == current: # Reached filesystem root
            break
        current = parent
        
    # Fallback to CWD if no marker found (Standard P3 behavior)
    return Path(os.getcwd())
