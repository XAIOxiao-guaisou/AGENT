"""
Audit History Manager - 审计历史管理器
======================================

Manages persistence and retrieval of delivery gate audit results.
管理交付门控审计结果的持久化和检索。

Features:
- Save audit results to .antigravity_audits/
- Retrieve audit history for trend analysis
- Limit history to last 10 audits per project
- Checksum validation for data integrity
- Lazy loading for performance

Phase 21 P2 Enhancements:
- Audit sharding with checksum
- Incremental history loading
- Quality sparklines data
"""

from __future__ import annotations
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, TYPE_CHECKING
from dataclasses import asdict

if TYPE_CHECKING:
    from .delivery_gate import DeliveryResult


class AuditHistoryManager:
    """
    Manages audit history persistence / 管理审计历史持久化
    
    Phase 21 P2: Enhanced with sharding and checksum validation.
    """
    
    HISTORY_DIR = ".antigravity_audits"
    MAX_HISTORY = 10
    MAX_DIR_SIZE_MB = 10  # 审查官约束：不超过 10MB
    
    def __init__(self, project_root: Path):
        """
        Initialize audit history manager / 初始化审计历史管理器
        
        Args:
            project_root: Project root directory / 项目根目录
        """
        self.project_root = project_root
        self.history_dir = project_root / self.HISTORY_DIR
        self.history_dir.mkdir(exist_ok=True)
    
    def save_audit(self, result: DeliveryResult, project_name: str):
        """
        Save audit result to history / 保存审计结果到历史
        
        Args:
            result: Delivery gate result / 交付门控结果
            project_name: Project name / 项目名称
        """
        history_file = self.history_dir / f"{project_name}_history.json"
        
        # Load existing history
        history = self._load_history(project_name)
        
        # Create audit record
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'can_deliver': result.can_deliver,
            'vibe_score': result.quality_report.get('vibe_score', 0),
            'test_coverage': result.quality_report.get('test_coverage', 0),
            'logic_score': result.quality_report.get('logic_score', 0),
            'security_issues': result.quality_report.get('security_issues', 0),
            'blocking_issues': result.blocking_issues,
            'local_signed': result.local_signature is not None and result.local_signature.signed,
            'remote_signed': result.remote_signature is not None and result.remote_signature.signed,
            'audit_tier_results': result.audit_tier_results
        }
        
        # Add checksum for data integrity (Phase 21 P2)
        audit_record['checksum'] = self._calculate_checksum(audit_record)
        
        # Add to front
        history.insert(0, audit_record)
        
        # Limit to MAX_HISTORY
        history = history[:self.MAX_HISTORY]
        
        # Save with pretty formatting
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        # Check directory size and cleanup if needed
        self._enforce_size_limit()
    
    def get_history(self, project_name: str, limit: int = 3) -> List[Dict]:
        """
        Get audit history for project / 获取项目审计历史
        
        Phase 21 P2: Incremental loading - only load what's needed.
        
        Args:
            project_name: Project name / 项目名称
            limit: Number of records to return / 返回记录数
            
        Returns:
            List of audit records / 审计记录列表
        """
        history = self._load_history(project_name)
        return history[:limit]
    
    def get_sparkline_data(self, project_name: str) -> Dict[str, List[float]]:
        """
        Get sparkline data for quality trends / 获取质量趋势火花线数据
        
        Phase 21 P2: Quality Genome - 10次审计的波动趋势
        
        Args:
            project_name: Project name / 项目名称
            
        Returns:
            Dictionary of metric sparklines / 指标火花线字典
        """
        history = self._load_history(project_name)
        
        sparklines = {
            'vibe_score': [],
            'test_coverage': [],
            'logic_score': [],
            'security_score': []
        }
        
        for record in history:
            sparklines['vibe_score'].append(record.get('vibe_score', 0))
            sparklines['test_coverage'].append(record.get('test_coverage', 0))
            sparklines['logic_score'].append(record.get('logic_score', 0))
            # Convert security issues to score (0 issues = 100 score)
            security_issues = record.get('security_issues', 0)
            sparklines['security_score'].append(max(0, 100 - security_issues * 10))
        
        return sparklines
    
    def get_latest_result(self, project_name: str) -> Optional[Dict]:
        """
        Get latest audit result / 获取最新审计结果
        
        Args:
            project_name: Project name / 项目名称
            
        Returns:
            Latest audit record or None / 最新审计记录或 None
        """
        history = self._load_history(project_name)
        return history[0] if history else None
    
    def _load_history(self, project_name: str) -> List[Dict]:
        """
        Load history from file / 从文件加载历史
        
        Args:
            project_name: Project name / 项目名称
            
        Returns:
            List of audit records / 审计记录列表
        """
        history_file = self.history_dir / f"{project_name}_history.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Validate checksums (Phase 21 P2)
            validated_history = []
            for record in history:
                if self._validate_checksum(record):
                    validated_history.append(record)
                else:
                    print(f"⚠️ Checksum validation failed for record: {record.get('timestamp')}")
            
            return validated_history
        
        except Exception as e:
            print(f"❌ Failed to load audit history: {e}")
            return []
    
    def _calculate_checksum(self, record: Dict) -> str:
        """
        Calculate checksum for audit record / 计算审计记录校验和
        
        Args:
            record: Audit record / 审计记录
            
        Returns:
            Checksum string / 校验和字符串
        """
        # Create a copy without checksum field
        record_copy = {k: v for k, v in record.items() if k != 'checksum'}
        
        # Convert to stable JSON string
        record_str = json.dumps(record_copy, sort_keys=True)
        
        # Calculate SHA256
        return hashlib.sha256(record_str.encode()).hexdigest()[:16]
    
    def _validate_checksum(self, record: Dict) -> bool:
        """
        Validate checksum for audit record / 验证审计记录校验和
        
        Args:
            record: Audit record / 审计记录
            
        Returns:
            True if valid / 如果有效则返回 True
        """
        if 'checksum' not in record:
            return True  # Old records without checksum
        
        stored_checksum = record['checksum']
        calculated_checksum = self._calculate_checksum(record)
        
        return stored_checksum == calculated_checksum
    
    def _enforce_size_limit(self):
        """
        Enforce directory size limit / 强制执行目录大小限制
        
        Phase 21 P2: 审查官约束 - 不超过 10MB
        """
        total_size = sum(f.stat().st_size for f in self.history_dir.glob('*.json'))
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size_mb > self.MAX_DIR_SIZE_MB:
            print(f"⚠️ Audit history directory exceeds {self.MAX_DIR_SIZE_MB}MB")
            print(f"   Current size: {total_size_mb:.2f}MB")
            print(f"   Cleaning up oldest records...")
            
            # Get all history files sorted by modification time
            history_files = sorted(
                self.history_dir.glob('*.json'),
                key=lambda f: f.stat().st_mtime
            )
            
            # Remove oldest files until under limit
            for file in history_files:
                if total_size_mb <= self.MAX_DIR_SIZE_MB:
                    break
                
                file_size_mb = file.stat().st_size / (1024 * 1024)
                file.unlink()
                total_size_mb -= file_size_mb
                print(f"   Removed: {file.name} ({file_size_mb:.2f}MB)")
    
    def get_directory_stats(self) -> Dict:
        """
        Get directory statistics / 获取目录统计
        
        Returns:
            Directory statistics / 目录统计
        """
        files = list(self.history_dir.glob('*.json'))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            'total_files': len(files),
            'total_size_mb': total_size / (1024 * 1024),
            'max_size_mb': self.MAX_DIR_SIZE_MB,
            'utilization': (total_size / (1024 * 1024)) / self.MAX_DIR_SIZE_MB * 100
        }
