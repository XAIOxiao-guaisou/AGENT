"""
Error Storage Module / 错误存储模块
==================================

Handles persistence of error data to JSON files.
处理错误数据到 JSON 文件的持久化。
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import uuid


class ErrorStorage:
    """
    Error storage manager / 错误存储管理器
    
    Stores errors in JSON format with date-based organization.
    以基于日期的组织方式将错误存储为 JSON 格式。
    """
    
    def __init__(self, storage_path: str = "debug_logs/"):
        """
        Initialize error storage / 初始化错误存储
        
        Args:
            storage_path: Base directory for error logs / 错误日志的基础目录
        """
        self.storage_path = Path(storage_path)
        self.errors_dir = self.storage_path / "errors"
        self.analysis_dir = self.storage_path / "analysis"
        
        # Create directories / 创建目录
        self.errors_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_error_id(self) -> str:
        """
        Generate unique error ID / 生成唯一错误 ID
        
        Returns:
            Error ID in format: err_YYYYMMDD_HHMMSS_UUID
            格式为 err_YYYYMMDD_HHMMSS_UUID 的错误 ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"err_{timestamp}_{unique_id}"
    
    def save_error(self, error_data: Dict) -> str:
        """
        Save error to JSON file / 保存错误到 JSON 文件
        
        Args:
            error_data: Error information dictionary / 错误信息字典
            
        Returns:
            Error ID / 错误 ID
        """
        # Generate error ID / 生成错误 ID
        error_id = self.generate_error_id()
        error_data["error_id"] = error_id
        
        # Get date-based directory / 获取基于日期的目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = self.errors_dir / date_str
        date_dir.mkdir(exist_ok=True)
        
        # Save to file / 保存到文件
        file_path = date_dir / f"{error_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        return error_id
    
    def load_error(self, error_id: str) -> Optional[Dict]:
        """
        Load error by ID / 通过 ID 加载错误
        
        Args:
            error_id: Error ID / 错误 ID
            
        Returns:
            Error data or None if not found / 错误数据,如果未找到则返回 None
        """
        # Search in all date directories / 在所有日期目录中搜索
        for date_dir in self.errors_dir.iterdir():
            if date_dir.is_dir():
                file_path = date_dir / f"{error_id}.json"
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
        
        return None
    
    def load_errors(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Load errors with filtering / 加载带过滤的错误
        
        Args:
            start_date: Start date filter / 开始日期过滤
            end_date: End date filter / 结束日期过滤
            severity: Severity filter / 严重性过滤
            limit: Maximum number of errors / 最大错误数量
            
        Returns:
            List of error data / 错误数据列表
        """
        errors = []
        
        # Default to last 7 days / 默认为最近 7 天
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        # Iterate through date directories / 遍历日期目录
        for date_dir in sorted(self.errors_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            
            # Check date range / 检查日期范围
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date < start_date or dir_date > end_date:
                    continue
            except ValueError:
                continue
            
            # Load errors from this date / 从此日期加载错误
            for error_file in sorted(date_dir.glob("*.json"), reverse=True):
                if len(errors) >= limit:
                    return errors
                
                try:
                    with open(error_file, "r", encoding="utf-8") as f:
                        error_data = json.load(f)
                    
                    # Apply severity filter / 应用严重性过滤
                    if severity and error_data.get("severity") != severity:
                        continue
                    
                    errors.append(error_data)
                except Exception:
                    continue
        
        return errors
    
    def cleanup_old_errors(self, days: int = 7):
        """
        Delete errors older than specified days / 删除超过指定天数的错误
        
        Args:
            days: Number of days to keep / 保留的天数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for date_dir in self.errors_dir.iterdir():
            if not date_dir.is_dir():
                continue
            
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date < cutoff_date:
                    # Delete entire directory / 删除整个目录
                    import shutil
                    shutil.rmtree(date_dir)
            except ValueError:
                continue
    
    def get_error_count(self, date: Optional[datetime] = None) -> int:
        """
        Get error count for a specific date / 获取特定日期的错误数量
        
        Args:
            date: Date to count (default: today) / 要计数的日期(默认:今天)
            
        Returns:
            Number of errors / 错误数量
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        date_dir = self.errors_dir / date_str
        
        if not date_dir.exists():
            return 0
        
        return len(list(date_dir.glob("*.json")))
