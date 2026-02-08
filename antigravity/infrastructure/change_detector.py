"""
Antigravity 变更检测器
Change Detector

功能 / Features:
- 文件哈希计算 / File hash calculation (MD5)
- 快照保存/加载 / Snapshot save/load
- 检测变更/新增/删除 / Detect changed/new/deleted files
- 增量同步策略 / Incremental sync strategy
"""

import hashlib
import json
import os
from typing import Dict, List, Set, Optional
from datetime import datetime


class ChangeDetector:
    """
    文件变更检测器
    File Change Detector
    
    通过哈希对比实现增量同步,减少 API 调用成本
    Implement incremental sync through hash comparison to reduce API costs
    """
    
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.snapshot_file = os.path.join(project_root, ".antigravity_snapshot.json")
        self.current_snapshot = {}
        self.previous_snapshot = self._load_snapshot()
    
    def _compute_hash(self, file_path: str) -> str:
        """
        计算文件哈希 (MD5)
        Compute file hash using MD5
        
        Args:
            file_path: 文件路径 (相对于 project_root)
        
        Returns:
            MD5 哈希字符串
        """
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            with open(full_path, 'rb') as f:
                file_hash = hashlib.md5()
                # 分块读取,避免大文件内存溢出
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except FileNotFoundError:
            return ""
        except Exception as e:
            print(f"⚠️ Failed to hash {file_path}: {e}")
            return ""
    
    def _load_snapshot(self) -> Dict[str, str]:
        """
        加载上次的快照
        Load previous snapshot
        
        Returns:
            {file_path: hash} 字典
        """
        if os.path.exists(self.snapshot_file):
            try:
                with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容旧格式和新格式
                    if isinstance(data, dict) and "snapshots" in data:
                        return data["snapshots"]
                    return data
            except Exception as e:
                print(f"⚠️ Failed to load snapshot: {e}")
                return {}
        return {}
    
    def save_snapshot(self, metadata: Optional[Dict] = None):
        """
        保存当前快照
        Save current snapshot
        
        Args:
            metadata: 可选的元数据 (如时间戳, 提交信息等)
        """
        snapshot_data = {
            "snapshots": self.current_snapshot,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.current_snapshot)
        }
        
        try:
            with open(self.snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Snapshot saved: {len(self.current_snapshot)} files")
        except Exception as e:
            print(f"⚠️ Failed to save snapshot: {e}")
    
    def scan_files(self, file_paths: List[str]):
        """
        扫描文件并更新快照
        Scan files and update snapshot
        
        Args:
            file_paths: 要扫描的文件路径列表 (相对于 project_root)
        """
        print(f"🔍 Scanning {len(file_paths)} files...")
        
        # v1.0.1 Hotfix: Binary Exclusion
        binary_extensions = {'.db', '.pyc', '.bin', '.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.ico'}
        
        for file_path in file_paths:
            # Check extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext in binary_extensions:
                continue
                
            file_hash = self._compute_hash(file_path)
            if file_hash:  # 只记录成功计算哈希的文件
                self.current_snapshot[file_path] = file_hash
        
        print(f"✅ Scan complete: {len(self.current_snapshot)} files in snapshot")
    
    def get_changed_files(self) -> Set[str]:
        """
        获取变更的文件 (内容变化)
        Get changed files (content modified)
        
        Returns:
            变更文件路径集合
        """
        changed = set()
        
        for file, current_hash in self.current_snapshot.items():
            previous_hash = self.previous_snapshot.get(file)
            
            # 文件存在于上次快照,但哈希不同
            if previous_hash and previous_hash != current_hash:
                changed.add(file)
        
        return changed
    
    def get_new_files(self) -> Set[str]:
        """
        获取新增的文件
        Get newly added files
        
        Returns:
            新增文件路径集合
        """
        current_files = set(self.current_snapshot.keys())
        previous_files = set(self.previous_snapshot.keys())
        
        return current_files - previous_files
    
    def get_deleted_files(self) -> Set[str]:
        """
        获取删除的文件
        Get deleted files
        
        Returns:
            删除文件路径集合
        """
        current_files = set(self.current_snapshot.keys())
        previous_files = set(self.previous_snapshot.keys())
        
        return previous_files - current_files
    
    def get_unchanged_files(self) -> Set[str]:
        """
        获取未变更的文件
        Get unchanged files
        
        Returns:
            未变更文件路径集合
        """
        unchanged = set()
        
        for file, current_hash in self.current_snapshot.items():
            previous_hash = self.previous_snapshot.get(file)
            
            # 文件存在于上次快照,且哈希相同
            if previous_hash and previous_hash == current_hash:
                unchanged.add(file)
        
        return unchanged
    
    def has_changes(self) -> bool:
        """
        检查是否有任何变更
        Check if there are any changes
        
        Returns:
            True if there are changes, False otherwise
        """
        changed = self.get_changed_files()
        new = self.get_new_files()
        deleted = self.get_deleted_files()
        
        return len(changed) > 0 or len(new) > 0 or len(deleted) > 0
    
    def get_change_summary(self) -> Dict[str, any]:
        """
        获取变更摘要
        Get change summary
        
        Returns:
            变更摘要字典
        """
        changed = self.get_changed_files()
        new = self.get_new_files()
        deleted = self.get_deleted_files()
        unchanged = self.get_unchanged_files()
        
        return {
            "changed": list(changed),
            "new": list(new),
            "deleted": list(deleted),
            "unchanged": list(unchanged),
            "total_changes": len(changed) + len(new) + len(deleted),
            "total_files": len(self.current_snapshot)
        }
    
    def should_use_incremental_sync(self, threshold: int = 3) -> bool:
        """
        判断是否应该使用增量同步
        Determine if incremental sync should be used
        
        Args:
            threshold: 变更文件数阈值,小于等于此值使用增量同步
        
        Returns:
            True if incremental sync is recommended
        """
        changed = self.get_changed_files()
        new = self.get_new_files()
        
        total_changes = len(changed) + len(new)
        
        return total_changes > 0 and total_changes <= threshold
    
    def is_file_changed(self, file_path: str) -> bool:
        """
        检查单个文件是否变更
        Check if a single file has changed
        
        Args:
            file_path: 文件路径 (相对于 project_root)
        
        Returns:
            True if file changed, False otherwise
        """
        current_hash = self._compute_hash(file_path)
        previous_hash = self.previous_snapshot.get(file_path)
        
        return current_hash != previous_hash
    
    def reset_snapshot(self):
        """
        重置快照 (清空当前和历史快照)
        Reset snapshot (clear current and previous)
        """
        self.current_snapshot = {}
        self.previous_snapshot = {}
        
        if os.path.exists(self.snapshot_file):
            os.remove(self.snapshot_file)
            print("✅ Snapshot reset")


if __name__ == "__main__":
    # 测试变更检测器
    print("🧪 Testing Change Detector...")
    
    detector = ChangeDetector(".")
    
    # 扫描项目文件
    test_files = [
        "antigravity/auditor.py",
        "antigravity/monitor.py",
        "antigravity/dashboard.py",
        "antigravity/dependency_analyzer.py",
        "antigravity/context_manager.py"
    ]
    
    detector.scan_files(test_files)
    
    # 获取变更摘要
    summary = detector.get_change_summary()
    
    print(f"\n📊 Change Summary:")
    print(f"  Changed: {len(summary['changed'])} files")
    print(f"  New: {len(summary['new'])} files")
    print(f"  Deleted: {len(summary['deleted'])} files")
    print(f"  Unchanged: {len(summary['unchanged'])} files")
    print(f"  Total changes: {summary['total_changes']}")
    
    # 判断是否使用增量同步
    if detector.should_use_incremental_sync():
        print(f"\n✅ Recommend incremental sync (≤3 changes)")
    else:
        print(f"\n📊 Recommend full sync ({summary['total_changes']} changes)")
    
    # 保存快照
    detector.save_snapshot({"test": "initial_scan"})
    
    print(f"\n✅ Test complete!")
