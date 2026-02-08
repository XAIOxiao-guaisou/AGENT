"""
Shadow Validation System - 影子验证系统
====================================

Ensures healing actions improve quality before committing changes.
确保修复动作在提交变更前真正提升质量。

Phase 21 P2 Final Tuning (审查官 Enhancement):
- Snapshot protection (Git-based or filesystem)
- Silent audit after healing
- Automatic rollback if score doesn't improve
- Result comparison and decision making
"""
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import shutil
import tempfile

class ShadowValidator:
    """
    Shadow validation for healing actions / 修复动作的影子验证
    
    Phase 21 P2: Ensures healing improves quality before committing.
    """

    def __init__(self, project_root: Path):
        """
        Initialize shadow validator / 初始化影子验证器
        
        Args:
            project_root: Project root directory / 项目根目录
        """
        self.project_root = project_root
        self.snapshots_dir = project_root / '.antigravity_snapshots'
        self.snapshots_dir.mkdir(exist_ok=True)

    async def shadow_heal_and_verify(self, healing_func, issue_type: str, issue: str, previous_score: float) -> Dict:
        """
        Execute healing with shadow validation / 执行带影子验证的修复
        
        Phase 21 P2: 审查官's "影子运行"逻辑
        
        Args:
            healing_func: Healing function to execute / 要执行的修复函数
            issue_type: Type of issue / 问题类型
            issue: Issue description / 问题描述
            previous_score: Previous quality score / 之前的质量分数
            
        Returns:
            Validation result / 验证结果
        """
        print('\n🔍 Shadow Validation - 影子验证启动')
        print(f'   Issue Type: {issue_type}')
        print(f'   Previous Score: {previous_score:.1f}')
        snapshot_id = await self._create_hot_snapshot()
        print(f'   ✅ Snapshot created: {snapshot_id}')
        try:
            print(f'   🔧 Executing healing...')
            healing_result = await healing_func(issue)
            if not healing_result.get('success'):
                print(f"   ❌ Healing failed: {healing_result.get('message')}")
                await self._restore_hot_snapshot(snapshot_id)
                return {'status': 'HEALING_FAILED', 'reason': healing_result.get('message'), 'rolled_back': True}
            print(f"   ✅ Healing completed: {healing_result.get('message')}")
            print(f'   🔍 Running silent audit...')
            new_score = await self._silent_audit()
            print(f'   📊 New Score: {new_score:.1f}')
            improvement = new_score - previous_score
            if new_score >= previous_score:
                print(f'   ✅ Score improved by {improvement:+.1f}!')
                print(f'   ✅ Changes committed')
                await self._cleanup_snapshot(snapshot_id)
                return {'status': 'SUCCESS', 'improvement': improvement, 'new_score': new_score, 'previous_score': previous_score, 'files_modified': healing_result.get('files_modified', []), 'rolled_back': False}
            else:
                print(f'   ⚠️ Score decreased by {improvement:.1f}')
                print(f'   🔄 Rolling back changes...')
                await self._restore_hot_snapshot(snapshot_id)
                return {'status': 'ROLLED_BACK', 'reason': f'Repair did not improve score (delta: {improvement:.1f})', 'new_score': new_score, 'previous_score': previous_score, 'rolled_back': True}
        except Exception as e:
            print(f'   ❌ Error during healing: {e}')
            print(f'   🔄 Rolling back changes...')
            await self._restore_hot_snapshot(snapshot_id)
            return {'status': 'ERROR', 'reason': str(e), 'rolled_back': True}

    async def _create_hot_snapshot(self) -> str:
        """
        Create hot snapshot (Git or filesystem) / 创建热快照
        
        Returns:
            Snapshot ID / 快照 ID
        """
        snapshot_id = f"shadow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if (self.project_root / '.git').exists():
            try:
                result = subprocess.run(['git', 'stash', 'push', '-u', '-m', snapshot_id], cwd=self.project_root, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f'   📦 Git snapshot created: {snapshot_id}')
                    return f'git:{snapshot_id}'
            except Exception as e:
                print(f'   ⚠️ Git snapshot failed: {e}')
        snapshot_dir = self.snapshots_dir / snapshot_id
        snapshot_dir.mkdir(exist_ok=True)
        for py_file in self.project_root.rglob('*.py'):
            if '.antigravity' in str(py_file) or '__pycache__' in str(py_file):
                continue
            rel_path = py_file.relative_to(self.project_root)
            target = snapshot_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, target)
        print(f'   📦 Filesystem snapshot created: {snapshot_id}')
        return f'fs:{snapshot_id}'

    async def _restore_hot_snapshot(self, snapshot_id: str):
        """
        Restore hot snapshot / 恢复热快照
        
        Args:
            snapshot_id: Snapshot ID / 快照 ID
        """
        if snapshot_id.startswith('git:'):
            stash_name = snapshot_id[4:]
            try:
                result = subprocess.run(['git', 'stash', 'list'], cwd=self.project_root, capture_output=True, text=True)
                stash_index = None
                for line in result.stdout.split('\n'):
                    if stash_name in line:
                        stash_index = line.split(':')[0]
                        break
                if stash_index:
                    subprocess.run(['git', 'stash', 'apply', stash_index], cwd=self.project_root, check=True)
                    print(f'   ✅ Git snapshot restored: {stash_name}')
            except Exception as e:
                print(f'   ❌ Git restore failed: {e}')
        elif snapshot_id.startswith('fs:'):
            snapshot_name = snapshot_id[3:]
            snapshot_dir = self.snapshots_dir / snapshot_name
            if snapshot_dir.exists():
                for snapshot_file in snapshot_dir.rglob('*.py'):
                    rel_path = snapshot_file.relative_to(snapshot_dir)
                    target = self.project_root / rel_path
                    shutil.copy2(snapshot_file, target)
                print(f'   ✅ Filesystem snapshot restored: {snapshot_name}')

    async def _cleanup_snapshot(self, snapshot_id: str):
        """
        Cleanup snapshot after successful healing / 成功修复后清理快照
        
        Args:
            snapshot_id: Snapshot ID / 快照 ID
        """
        if snapshot_id.startswith('git:'):
            stash_name = snapshot_id[4:]
            try:
                result = subprocess.run(['git', 'stash', 'list'], cwd=self.project_root, capture_output=True, text=True)
                stash_index = None
                for line in result.stdout.split('\n'):
                    if stash_name in line:
                        stash_index = line.split(':')[0]
                        break
                if stash_index:
                    subprocess.run(['git', 'stash', 'drop', stash_index], cwd=self.project_root)
            except Exception:
                pass
        elif snapshot_id.startswith('fs:'):
            snapshot_name = snapshot_id[3:]
            snapshot_dir = self.snapshots_dir / snapshot_name
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)

    async def _silent_audit(self) -> float:
        """
        Run silent audit to get new quality score / 运行静默审计获取新质量分数
        
        Returns:
            New quality score / 新质量分数
        """
        try:
            from antigravity.infrastructure.delivery_gate import DeliveryGate
            gate = DeliveryGate(self.project_root)
            project = {'root': str(self.project_root), 'name': self.project_root.name}
            static_result = gate._audit_static_baseline(project)
            return static_result.get('metrics', {}).get('vibe_score', 0)
        except Exception as e:
            print(f'   ⚠️ Silent audit failed: {e}')
            return 0.0