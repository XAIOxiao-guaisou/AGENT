"""
File Lock Manager - 文件锁管理器
==================================

Ensures async file operation safety in concurrent execution.
确保并发执行中的异步文件操作安全。

Core Features:
- File-level locking (文件级锁定)
- Async context manager (异步上下文管理器)
- LRU cache for lock lifecycle (LRU 缓存管理锁生命周期)
- Timeout mechanism (超时机制)
- Lock statistics (锁统计)

Think of it as a "traffic cop" for file access!
把它想象成文件访问的"交通警察"！
"""

import asyncio
from typing import Dict, Optional
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class FileLockManager:
    """
    File Lock Manager - 文件锁管理器
    
    Enhanced with LRU cache and timeout mechanism.
    增强版：支持 LRU 缓存和超时机制。
    
    Example:
        async with lock_manager.lock_file("PLAN.md", timeout=10.0):
            # Safe to write to PLAN.md
            # 安全地写入 PLAN.md
            with open("PLAN.md", "w") as f:
                f.write(content)
    """
    
    MAX_LOCKS = 1000  # LRU cache size / LRU 缓存大小
    
    def __init__(self, max_locks: int = MAX_LOCKS):
        """
        Initialize file lock manager / 初始化文件锁管理器
        
        Args:
            max_locks: Maximum number of locks to cache / 最大缓存锁数量
        """
        self._locks: OrderedDict[str, asyncio.Lock] = OrderedDict()
        self._lock_stats: Dict[str, int] = {}  # Track lock acquisitions
        self._global_lock = asyncio.Lock()  # For thread-safe lock creation
        self._timeout_events: list[Dict] = []  # Track timeout events
        self.max_locks = max_locks
    
    async def _get_or_create_lock(self, normalized_path: str) -> asyncio.Lock:
        """
        Get or create lock with LRU eviction / 获取或创建锁（带 LRU 驱逐）
        
        Args:
            normalized_path: Normalized file path / 规范化的文件路径
            
        Returns:
            Lock for the file / 文件的锁
        """
        async with self._global_lock:
            # Move to end if exists (mark as recently used)
            if normalized_path in self._locks:
                self._locks.move_to_end(normalized_path)
                return self._locks[normalized_path]
            
            # Evict oldest if at capacity
            if len(self._locks) >= self.max_locks:
                oldest_path, oldest_lock = self._locks.popitem(last=False)
                logger.info(f"🗑️ LRU evicted lock for: {oldest_path}")
            
            # Create new lock
            new_lock = asyncio.Lock()
            self._locks[normalized_path] = new_lock
            self._lock_stats[normalized_path] = 0
            logger.debug(f"🔒 Created new lock for: {normalized_path}")
            
            return new_lock
    
    @asynccontextmanager
    async def lock_file(self, file_path: str, timeout: Optional[float] = None):
        """
        Acquire file lock with optional timeout / 获取文件锁（可选超时）
        
        This is an async context manager that ensures exclusive access to a file.
        这是一个异步上下文管理器，确保对文件的独占访问。
        
        Args:
            file_path: Path to file (can be relative or absolute)
                      文件路径（可以是相对或绝对路径）
            timeout: Maximum wait time in seconds (None = infinite)
                    最大等待时间（秒）（None = 无限）
        
        Raises:
            asyncio.TimeoutError: If timeout is reached / 如果超时
        
        Example:
            async with lock_manager.lock_file("config.json", timeout=10.0):
                # Only one task can be here at a time
                # 同一时间只有一个任务可以在这里
                data = read_config()
                data['updated'] = True
                write_config(data)
        """
        # Normalize path to avoid different representations of same file
        normalized_path = str(Path(file_path).resolve())
        
        # Get or create lock for this file
        file_lock = await self._get_or_create_lock(normalized_path)
        
        logger.debug(f"⏳ Waiting for lock: {normalized_path}")
        
        lock_acquired = False
        try:
            if timeout:
                # Wait with timeout
                await asyncio.wait_for(file_lock.acquire(), timeout=timeout)
            else:
                # Wait indefinitely
                await file_lock.acquire()
            
            lock_acquired = True
            
            # Update statistics
            self._lock_stats[normalized_path] += 1
            logger.debug(f"✅ Lock acquired: {normalized_path} (count: {self._lock_stats[normalized_path]})")
            
            yield  # File is now safe to access
            
        except asyncio.TimeoutError:
            logger.error(f"🚨 Lock timeout for: {normalized_path} (timeout: {timeout}s)")
            
            # Log timeout event for Sheriff-Eye monitoring
            self._log_timeout_event(normalized_path, timeout)
            
            raise
        
        finally:
            if lock_acquired and file_lock.locked():
                file_lock.release()
                logger.debug(f"🔓 Lock released: {normalized_path}")
    
    def _log_timeout_event(self, file_path: str, timeout: float):
        """
        Log timeout event for monitoring / 记录超时事件以供监控
        
        Args:
            file_path: File path that timed out / 超时的文件路径
            timeout: Timeout duration / 超时时长
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'lock_timeout',
            'file_path': file_path,
            'timeout': timeout,
            'severity': 'HIGH'
        }
        
        self._timeout_events.append(event)
        
        # TODO: Integrate with Sheriff-Eye monitoring system
        logger.warning(f"⚠️ Lock timeout event logged: {event}")
    
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
    
    def get_timeout_events(self) -> list[Dict]:
        """
        Get timeout events for monitoring / 获取超时事件以供监控
        
        Returns:
            List of timeout events / 超时事件列表
        """
        return self._timeout_events.copy()
    
    def get_cache_stats(self) -> Dict:
        """
        Get LRU cache statistics / 获取 LRU 缓存统计
        
        Returns:
            Cache statistics / 缓存统计
        """
        return {
            'total_locks': len(self._locks),
            'max_locks': self.max_locks,
            'cache_utilization': len(self._locks) / self.max_locks * 100,
            'active_locks': len(self.get_active_locks())
        }
    
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
        self._timeout_events.clear()
        logger.info("📊 Lock statistics cleared")
    
    def __repr__(self) -> str:
        """String representation / 字符串表示"""
        active_count = len(self.get_active_locks())
        total_locks = len(self._locks)
        return f"FileLockManager(total_locks={total_locks}, active={active_count}, max={self.max_locks})"


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
