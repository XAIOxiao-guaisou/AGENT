"""
P3 Monitor Extensions: Dynamic Project Root Detection
Vibe Coding: pathlib-first, zero hardcoding, pattern matching
"""
from pathlib import Path
from typing import Optional


def find_project_root(file_path: Path, watch_root: Path) -> Path:
    """
    Dynamically find project root by searching upward for PLAN.md.
    
    Priority:
    1. Look for PLAN.md in parent directories (up to 5 levels)
    2. Look for projects/{name}/ pattern
    3. Fall back to watch_root
    
    Args:
        file_path: Path to the file that triggered the event
        watch_root: Root directory being watched
    
    Returns:
        Path to project root
    
    Examples:
        >>> find_project_root(Path("projects/MyScraper/main.py"), Path("."))
        Path("projects/MyScraper")
        
        >>> find_project_root(Path("projects/WebApp/utils/parser.py"), Path("."))
        Path("projects/WebApp")
    """
    current = file_path.parent if file_path.is_file() else file_path
    
    # Search upward for PLAN.md (max 5 levels)
    for _ in range(5):
        if (current / "PLAN.md").exists():
            return current
        
        # Check if we're in a projects/{name}/ structure
        if current.parent.name == "projects":
            return current
        
        if current == watch_root:
            break
        
        current = current.parent
    
    return watch_root


# Example integration into Monitor class:
"""
class AntigravityMonitor(FileSystemEventHandler):
    def __init__(self, watch_root="."):
        self.watch_root = Path(watch_root).resolve()
        # ... existing init code ...
    
    def trigger_takeover(self, file_path):
        '''Trigger with dynamic project root detection'''
        file_path = Path(file_path)
        project_root = find_project_root(file_path, self.watch_root)
        
        print(f"🎯 P3: Detected project root: {project_root}")
        
        # Initialize project-specific components
        from antigravity.p3_state_manager import P3StateManager
        state_mgr = P3StateManager(project_root)
        auditor = Auditor(project_root, state_manager=state_mgr)
        
        # ... rest of takeover logic ...
"""
