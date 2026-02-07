"""
Precision Healing System - 精准修复系统
====================================

Categorized deductions and ROI-based healing prioritization.
层级化扣分与基于 ROI 的修复优先级排序。

Phase 21 P2 Final Tuning (审查官 Enhancement):
- Categorized deductions (CRITICAL/WARNING/STYLE)
- ROI calculation for healing tasks
- Automatic prioritization of high-ROI fixes
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class IssueSeverity(Enum):
    """Issue severity levels / 问题严重级别"""
    CRITICAL = "CRITICAL"  # -25 points
    WARNING = "WARNING"    # -10 points
    STYLE = "STYLE"        # -3 points


@dataclass
class IssueDeduction:
    """Issue deduction details / 问题扣分详情"""
    severity: IssueSeverity
    points: int
    description: str
    category: str


@dataclass
class HealingTask:
    """Healing task with ROI / 带 ROI 的修复任务"""
    issue_type: str
    issue: str
    severity: IssueSeverity
    potential_gain: int  # Points to gain
    estimated_difficulty: int  # 1-10 scale
    roi: float  # potential_gain / estimated_difficulty
    healing_action: str


class PrecisionHealer:
    """
    Precision healing with categorized deductions / 精准修复与层级化扣分
    
    Phase 21 P2: 审查官's "自愈精准度与 Vibe 扣分细化"
    """
    
    # Deduction rules (审查官's 层级化扣分)
    DEDUCTION_RULES = {
        # CRITICAL (-25)
        'syntax_error': IssueDeduction(IssueSeverity.CRITICAL, -25, '语法错误', 'syntax'),
        'hardcoded_secret': IssueDeduction(IssueSeverity.CRITICAL, -25, '硬编码密钥', 'security'),
        'circular_dependency': IssueDeduction(IssueSeverity.CRITICAL, -25, '循环依赖', 'architecture'),
        'unsafe_function': IssueDeduction(IssueSeverity.CRITICAL, -25, '危险函数调用', 'security'),
        
        # WARNING (-10)
        'high_complexity': IssueDeduction(IssueSeverity.WARNING, -10, '复杂度过高 (>10)', 'quality'),
        'missing_core_test': IssueDeduction(IssueSeverity.WARNING, -10, '缺少核心模块测试', 'testing'),
        'low_coverage': IssueDeduction(IssueSeverity.WARNING, -10, '测试覆盖率不足', 'testing'),
        'race_condition': IssueDeduction(IssueSeverity.WARNING, -10, '潜在竞态条件', 'concurrency'),
        
        # STYLE (-3)
        'missing_docstring': IssueDeduction(IssueSeverity.STYLE, -3, '缺少文档字符串', 'documentation'),
        'unused_variable': IssueDeduction(IssueSeverity.STYLE, -3, '未使用变量', 'code_quality'),
        'poor_naming': IssueDeduction(IssueSeverity.STYLE, -3, '变量命名不规范', 'naming'),
    }
    
    # Difficulty estimates for healing actions
    DIFFICULTY_ESTIMATES = {
        'add_docstring': 1,
        'remove_unused_variable': 1,
        'improve_naming': 2,
        'add_test': 3,
        'fix_security': 4,
        'refactor_complexity': 5,
        'fix_race_condition': 7,
        'fix_circular_dependency': 8,
    }
    
    def __init__(self):
        """Initialize precision healer / 初始化精准修复器"""
        pass
    
    def analyze_blocking_issues(self, blocking_issues: List[str]) -> List[HealingTask]:
        """
        Analyze blocking issues and create prioritized healing tasks / 分析阻塞问题并创建优先级修复任务
        
        Phase 21 P2: ROI 排序修复
        
        Args:
            blocking_issues: List of blocking issues / 阻塞问题列表
            
        Returns:
            Prioritized healing tasks / 优先级修复任务列表
        """
        tasks = []
        
        for issue in blocking_issues:
            # Categorize issue
            issue_type, severity, potential_gain = self._categorize_issue(issue)
            
            # Estimate difficulty
            difficulty = self._estimate_difficulty(issue_type)
            
            # Calculate ROI
            roi = potential_gain / difficulty if difficulty > 0 else 0
            
            # Determine healing action
            healing_action = self._determine_healing_action(issue_type)
            
            tasks.append(HealingTask(
                issue_type=issue_type,
                issue=issue,
                severity=severity,
                potential_gain=potential_gain,
                estimated_difficulty=difficulty,
                roi=roi,
                healing_action=healing_action
            ))
        
        # Sort by ROI (highest first)
        tasks.sort(key=lambda t: t.roi, reverse=True)
        
        return tasks
    
    def _categorize_issue(self, issue: str) -> Tuple[str, IssueSeverity, int]:
        """
        Categorize issue and determine potential gain / 分类问题并确定潜在收益
        
        Args:
            issue: Issue description / 问题描述
            
        Returns:
            (issue_type, severity, potential_gain) / (问题类型, 严重级别, 潜在收益)
        """
        issue_lower = issue.lower()
        
        # Check for CRITICAL issues
        if 'syntax' in issue_lower or 'syntaxerror' in issue_lower:
            return ('syntax_error', IssueSeverity.CRITICAL, 25)
        elif 'secret' in issue_lower or 'api_key' in issue_lower or 'password' in issue_lower:
            return ('hardcoded_secret', IssueSeverity.CRITICAL, 25)
        elif 'eval' in issue_lower or 'exec' in issue_lower:
            return ('unsafe_function', IssueSeverity.CRITICAL, 25)
        elif 'circular' in issue_lower or 'dependency' in issue_lower:
            return ('circular_dependency', IssueSeverity.CRITICAL, 25)
        
        # Check for WARNING issues
        elif 'complexity' in issue_lower:
            return ('high_complexity', IssueSeverity.WARNING, 10)
        elif 'coverage' in issue_lower or 'test' in issue_lower:
            if 'core' in issue_lower:
                return ('missing_core_test', IssueSeverity.WARNING, 10)
            else:
                return ('low_coverage', IssueSeverity.WARNING, 10)
        elif 'race' in issue_lower or 'concurrency' in issue_lower:
            return ('race_condition', IssueSeverity.WARNING, 10)
        
        # Check for STYLE issues
        elif 'docstring' in issue_lower or 'documentation' in issue_lower:
            return ('missing_docstring', IssueSeverity.STYLE, 3)
        elif 'unused' in issue_lower or 'variable' in issue_lower:
            return ('unused_variable', IssueSeverity.STYLE, 3)
        elif 'naming' in issue_lower or 'name' in issue_lower:
            return ('poor_naming', IssueSeverity.STYLE, 3)
        
        # Default to STYLE
        return ('unknown', IssueSeverity.STYLE, 3)
    
    def _estimate_difficulty(self, issue_type: str) -> int:
        """
        Estimate difficulty of fixing issue / 估计修复问题的难度
        
        Args:
            issue_type: Issue type / 问题类型
            
        Returns:
            Difficulty (1-10) / 难度 (1-10)
        """
        # Map issue types to healing actions
        action_map = {
            'missing_docstring': 'add_docstring',
            'unused_variable': 'remove_unused_variable',
            'poor_naming': 'improve_naming',
            'low_coverage': 'add_test',
            'missing_core_test': 'add_test',
            'hardcoded_secret': 'fix_security',
            'unsafe_function': 'fix_security',
            'high_complexity': 'refactor_complexity',
            'race_condition': 'fix_race_condition',
            'circular_dependency': 'fix_circular_dependency',
        }
        
        action = action_map.get(issue_type, 'unknown')
        return self.DIFFICULTY_ESTIMATES.get(action, 5)
    
    def _determine_healing_action(self, issue_type: str) -> str:
        """
        Determine healing action for issue / 确定问题的修复动作
        
        Args:
            issue_type: Issue type / 问题类型
            
        Returns:
            Healing action / 修复动作
        """
        action_map = {
            'missing_docstring': '🧪 补充文档字符串',
            'unused_variable': '✨ 移除未使用变量',
            'poor_naming': '🎨 优化变量命名',
            'low_coverage': '🧪 补充测试用例',
            'missing_core_test': '🧪 补充核心模块测试',
            'hardcoded_secret': '🔒 迁移密钥到环境变量',
            'unsafe_function': '🔒 替换危险函数',
            'high_complexity': '🎨 重构复杂函数',
            'race_condition': '🎨 修复竞态条件',
            'circular_dependency': '🎨 解除循环依赖',
        }
        
        return action_map.get(issue_type, '🔧 通用修复')
    
    def get_recommended_fixes(self, tasks: List[HealingTask], max_tasks: int = 3) -> List[HealingTask]:
        """
        Get top recommended fixes based on ROI / 基于 ROI 获取推荐修复
        
        Phase 21 P2: 优先推荐"高 ROI"操作
        
        Args:
            tasks: All healing tasks / 所有修复任务
            max_tasks: Maximum tasks to recommend / 最大推荐任务数
            
        Returns:
            Top recommended tasks / 推荐任务列表
        """
        return tasks[:max_tasks]
    
    def format_healing_recommendation(self, task: HealingTask) -> str:
        """
        Format healing recommendation for display / 格式化修复推荐用于显示
        
        Args:
            task: Healing task / 修复任务
            
        Returns:
            Formatted recommendation / 格式化推荐
        """
        severity_emoji = {
            IssueSeverity.CRITICAL: '🚨',
            IssueSeverity.WARNING: '⚠️',
            IssueSeverity.STYLE: '💡'
        }
        
        return f"""
{severity_emoji[task.severity]} **{task.healing_action}**
- **问题**: {task.issue}
- **严重级别**: {task.severity.value}
- **潜在收益**: +{task.potential_gain} 分
- **难度**: {task.estimated_difficulty}/10
- **ROI**: {task.roi:.2f} (推荐指数)
"""
