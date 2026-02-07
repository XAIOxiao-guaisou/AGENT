"""
I/O Utilities for Antigravity v1.0.1 (Hotfix)
=============================================
Provides robust file reading capabilities with Protobuf-compatible
encoding safety nets.
"""

from pathlib import Path
from typing import Union

import logging

logger = logging.getLogger("antigravity.io")

def safe_read(file_path: Union[str, Path]) -> str:
    """
    Safely read a file with strict UTF-8 enforcement and Protobuf compatibility.
    
    Features:
    - Automatic fallback to 'replace' for invalid bytes (Logs Warning)
    - Protobuf-safe re-encoding (ensures no lone surrogates)
    - Binary file skipping (heuristic)
    - Large file truncation (>5MB)
    
    Args:
        file_path: Path to the file
        
    Returns:
        Content string, or "[BINARY_FILE_SKIPPED]" if binary/unreadable
    """
    path = Path(file_path)
    
    # 1. Extension Check (Fast Fail)
    # v1.0.1 Hotfix: Strict binary exclusion
    if path.suffix.lower() in ['.db', '.pyc', '.bin', '.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.ico']:
        return "[BINARY_FILE_SKIPPED]"
    
    # 2. Large File Truncation (v1.0.1 Polish)
    try:
        if path.stat().st_size > 5 * 1024 * 1024: # 5MB
            logger.warning(f"Large file detected: {path.name} (>5MB). Truncating.")
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(100 * 1024) # 100KB
                return content + "\n[...TRUNCATED DUE TO SIZE]"
            except Exception:
                return "[BINARY_FILE_SKIPPED]"
    except OSError:
        pass # File might not exist or be accessible
        
    try:
        # 3. Try strict UTF-8 first
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # 4. Fallback to replace
        try:
            logger.warning(f"Non-standard encoding detected in {path.name}, auto-sanitized for stability.")
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            # 5. Protobuf Safety Net
            # Re-encode to strictly compliant UTF-8 to catch any edge cases
            # capable of crashing C++ protobuf implementation
            return content.encode('utf-8', 'replace').decode('utf-8')
            
        except Exception:
            return "[BINARY_FILE_SKIPPED]"
    except Exception:
        return "[FILE_READ_ERROR]"
