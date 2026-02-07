"""
File Lock Manager - 文件锁管理器
==================================

Ensures async file operation safety in concurrent execution.
确保并发执行中的异步文件操作安全。

Core Features:
- File-level locking (文件级锁定)
- Async context manager (异步上下文管理器)
- Deadlock prevention (死锁预防)
- Lock statistics (锁统计)

Think of it as a "traffic cop" for file access!
把它想象成文件访问的"交通警察"！
"""

import asyncio
from typing import Dict, Optional
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileLockManager:
    """
    File Lock Manager - 文件锁管理器
    
    Manages file-level locks for async safety.
    管理文件级锁以确保异步安全。
    
    Example:
        async with lock_manager.lock_file("PLAN.md"):
            # Safe to write to PLAN.md
            # 安全地写入 PLAN.md
            with open("PLAN.md", "w") as f:
                f.write(content)
    """
    
    def __init__(self):
        """Initialize file lock manager / 初始化文件锁管理器"""
        self._locks: Dict[str, asyncio.Lock] = {}
        self._lock_stats: Dict[str, int] = {}  # Track lock acquisitions
        self._global_lock = asyncio.Lock()  # For thread-safe lock creation
    
    @asynccontextmanager
    async def lock_file(self, file_path: str):
        """
        Acquire file lock / 获取文件锁
        
        This is an async context manager that ensures exclusive access to a file.
        这是一个异步上下文管理器，确保对文件的独占访问。
        
        Args:
            file_path: Path to file (can be relative or absolute)
                      文件路径（可以是相对或绝对路径）
        
        Example:
            async with lock_manager.lock_file("config.json"):
                # Only one task can be here at a time
                # 同一时间只有一个任务可以在这里
                data = read_config()
                data['updated'] = True
                write_config(data)
        """
        # Normalize path to avoid different representations of same file
        normalized_path = str(Path(file_path).resolve())
        
        # Get or create lock for this file
        async with self._global_lock:
            if normalized_path not in self._locks:
                self._locks[normalized_path] = asyncio.Lock()
                self._lock_stats[normalized_path] = 0
                logger.debug(f"🔒 Created new lock for: {normalized_path}")
        
        # Acquire the file-specific lock
        file_lock = self._locks[normalized_path]
        
        logger.debug(f"⏳ Waiting for lock: {normalized_path}")
        async with file_lock:
            # Update statistics
            self._lock_stats[normalized_path] += 1
            logger.debug(f"✅ Lock acquired: {normalized_path} (count: {self._lock_stats[normalized_path]})")
            
            try:
                yield  # File is now safe to access
            finally:
                logger.debug(f"🔓 Lock released: {normalized_path}")
    
    def get_lock_stats(self) -> Dict[str, int]:
        """
        Get lock acquisition statistics / 获取锁获取统计
        
        Returns:
            Dictionary mapping file paths to acquisition counts
            文件路径到获取次数的字典映射
        """
        return self._lock_stats.copy()
    
    def get_active_locks(self) -> list[str]:
        """
        Get currently locked files / 获取当前锁定的文件
        
        Returns:
            List of file paths that are currently locked
            当前锁定的文件路径列表
        """
        active = []
        for path, lock in self._locks.items():
            if lock.locked():
                active.append(path)
        return active
    
    async def wait_for_all_locks(self, timeout: Optional[float] = None):
        """
        Wait for all locks to be released / 等待所有锁释放
        
        Useful for graceful shutdown.
        用于优雅关闭。
        
        Args:
            timeout: Maximum time to wait in seconds / 最大等待时间（秒）
        
        Raises:
            asyncio.TimeoutError: If timeout is reached
        """
        async def wait_for_lock(lock: asyncio.Lock):
            async with lock:
                pass  # Just acquire and release
        
        tasks = [wait_for_lock(lock) for lock in self._locks.values()]
        
        if timeout:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        else:
            await asyncio.gather(*tasks)
    
    def clear_stats(self):
        """Clear lock statistics / 清除锁统计"""
        self._lock_stats.clear()
        logger.info("📊 Lock statistics cleared")
    
    def __repr__(self) -> str:
        """String representation / 字符串表示"""
        active_count = len(self.get_active_locks())
        total_locks = len(self._locks)
        return f"FileLockManager(total_locks={total_locks}, active={active_count})"


# Global singleton instance for convenience
# 全局单例实例以便使用
_global_lock_manager: Optional[FileLockManager] = None


def get_global_lock_manager() -> FileLockManager:
    """
    Get global file lock manager / 获取全局文件锁管理器
    
    Returns:
        Global FileLockManager instance / 全局 FileLockManager 实例
    """
    global _global_lock_manager
    if _global_lock_manager is None:
        _global_lock_manager = FileLockManager()
    return _global_lock_manager


# Convenience function for direct use
# 便捷函数供直接使用
@asynccontextmanager
async def lock_file(file_path: str):
    """
    Convenience function to lock a file / 锁定文件的便捷函数
    
    Args:
        file_path: Path to file / 文件路径
    
    Example:
        from antigravity.file_lock_manager import lock_file
        
        async with lock_file("PLAN.md"):
            # Safe file operations
            pass
    """
    manager = get_global_lock_manager()
    async with manager.lock_file(file_path):
        yield
