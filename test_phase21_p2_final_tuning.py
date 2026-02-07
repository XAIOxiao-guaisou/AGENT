"""
Test Suite for Phase 21 P2 Final Tuning
=======================================

Comprehensive tests for审查官's final tuning enhancements:
- Shadow Validation
- Precision Healing
- Strategist Protocol
"""

import pytest
import asyncio
import tempfile
import shutil
import json
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Mock imports for testing
class IssueSeverity:
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    STYLE = "STYLE"

class HealingTask:
    def __init__(self, issue: str, severity: str, gain: int, difficulty: int, roi: float):
        self.issue = issue
        self.severity = severity
        self.gain = gain
        self.difficulty = difficulty
        self.roi = roi

class StrategistAuditRequest:
    def __init__(self, project_name: str, project_root: str, code_snapshot: Dict[str, str], 
                 vibe_score: float, test_coverage: float, request_id: str):
        self.project_name = project_name
        self.project_root = project_root
        self.code_snapshot = code_snapshot
        self.vibe_score = vibe_score
        self.test_coverage = test_coverage
        self.request_id = request_id

class StrategistAuditResponse:
    def __init__(self, logic_score: int, approved: bool, debt_found: List[str], 
                 naming_vibe: str, expert_advice: str, race_condition_report: Optional[str] = None,
                 architectural_concerns: Optional[str] = None, request_id: str = ""):
        self.logic_score = logic_score
        self.approved = approved
        self.debt_found = debt_found
        self.naming_vibe = naming_vibe
        self.expert_advice = expert_advice
        self.race_condition_report = race_condition_report
        self.architectural_concerns = architectural_concerns
        self.request_id = request_id


class ShadowValidator:
    """Mock Shadow Validator for testing"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.snapshots_dir = project_root / ".snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
    
    async def _create_hot_snapshot(self) -> str:
        """Create a filesystem snapshot"""
        snapshot_id = f"fs:{uuid.uuid4().hex[:8]}"
        snapshot_file = self.snapshots_dir / snapshot_id[3:]
        snapshot_file.write_text(f"Snapshot of {self.project_root}")
        return snapshot_id
    
    async def _restore_hot_snapshot(self, snapshot_id: str) -> bool:
        """Restore a filesystem snapshot"""
        if snapshot_id.startswith("fs:"):
            snapshot_file = self.snapshots_dir / snapshot_id[3:]
            if snapshot_file.exists():
                return True
        return False
    
    async def _silent_audit(self) -> float:
        """Mock silent audit returning a score"""
        return 95.0
    
    async def shadow_heal_and_verify(self, healing_func, issue_type: str, 
                                     issue: str, previous_score: float) -> Dict[str, Any]:
        """Mock shadow healing and verification"""
        # Create snapshot
        snapshot_id = await self._create_hot_snapshot()
        
        # Apply healing
        healing_result = await healing_func(issue)
        
        # Run silent audit
        new_score = await self._silent_audit()
        
        # Determine if we should rollback
        improvement = new_score - previous_score
        if improvement > 0:
            status = "SUCCESS"
            rolled_back = False
        else:
            status = "ROLLED_BACK"
            rolled_back = True
            # In real implementation, would restore snapshot here
            await self._restore_hot_snapshot(snapshot_id)
        
        return {
            'status': status,
            'improvement': improvement,
            'rolled_back': rolled_back,
            'snapshot_id': snapshot_id,
            'new_score': new_score
        }


class PrecisionHealer:
    """Mock Precision Healer for testing"""
    
    def __init__(self):
        pass
    
    def _categorize_issue(self, issue: str) -> tuple:
        """Categorize issue by severity and calculate potential gain"""
        issue_lower = issue.lower()
        
        if any(keyword in issue_lower for keyword in ['syntaxerror', 'exception', 'error', 'critical']):
            severity = IssueSeverity.CRITICAL
            gain = 25
            difficulty = 1
        elif any(keyword in issue_lower for keyword in ['coverage', 'warning', 'test', 'performance']):
            severity = IssueSeverity.WARNING
            gain = 10
            difficulty = 3
        elif any(keyword in issue_lower for keyword in ['docstring', 'style', 'format', 'unused']):
            severity = IssueSeverity.STYLE
            gain = 3
            difficulty = 1
        else:
            severity = IssueSeverity.STYLE
            gain = 2
            difficulty = 1
        
        # Simple issue type detection
        if 'syntax' in issue_lower:
            issue_type = 'syntax'
        elif 'coverage' in issue_lower:
            issue_type = 'coverage'
        elif 'docstring' in issue_lower:
            issue_type = 'documentation'
        else:
            issue_type = 'general'
        
        return issue_type, severity, gain, difficulty
    
    def analyze_blocking_issues(self, issues: List[str]) -> List[HealingTask]:
        """Analyze issues and create healing tasks sorted by ROI"""
        tasks = []
        
        for issue in issues:
            issue_type, severity, gain, difficulty = self._categorize_issue(issue)
            roi = gain / difficulty if difficulty > 0 else gain
            
            task = HealingTask(
                issue=issue,
                severity=severity,
                gain=gain,
                difficulty=difficulty,
                roi=roi
            )
            tasks.append(task)
        
        # Sort by ROI (highest first)
        tasks.sort(key=lambda x: x.roi, reverse=True)
        return tasks
    
    def get_recommended_fixes(self, tasks: List[HealingTask], max_tasks: int = 3) -> List[HealingTask]:
        """Get top recommended fixes by ROI"""
        return tasks[:max_tasks]


class StrategistProtocol:
    """Mock Strategist Protocol for testing"""
    
    def __init__(self):
        pass
    
    def create_audit_request(self, project_name: str, project_root: str, 
                            code_snapshot: Dict[str, str], vibe_score: float, 
                            test_coverage: float) -> StrategistAuditRequest:
        """Create an audit request"""
        request_id = f"AUDIT-{uuid.uuid4().hex[:8]}"
        
        return StrategistAuditRequest(
            project_name=project_name,
            project_root=project_root,
            code_snapshot=code_snapshot,
            vibe_score=vibe_score,
            test_coverage=test_coverage,
            request_id=request_id
        )
    
    def format_prompt(self, request: StrategistAuditRequest) -> str:
        """Format the audit prompt"""
        prompt = f"""Sheriff Brain Audit Request
Project: {request.project_name}
Vibe Score: {request.vibe_score}
Test Coverage: {request.test_coverage}

Code Snapshot:
{request.code_snapshot}

Please analyze the code and provide:
1. logic_score (0-100)
2. approved (true/false)
3. debt_found (list)
4. naming_vibe (description)
5. expert_advice (string)
6. race_condition_report (optional)
7. architectural_concerns (optional)
"""
        return prompt
    
    def parse_response(self, response_text: str, request_id: str) -> Optional[StrategistAuditResponse]:
        """Parse response from strategist"""
        # Extract JSON from markdown code block
        json_match = re.search(r'