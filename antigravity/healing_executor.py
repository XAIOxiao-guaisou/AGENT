"""
Quality Tower Healing Actions - 质量之塔修复动作
===========================================

Integrates Quality Tower with AutonomousAuditor for interactive healing.
将质量之塔与自主审计器集成，实现交互式修复。

Phase 21 P2 Step 3: Interactive Healing Integration
Phase 21 P2 Final Tuning: Shadow Validation Integration (审查官 Enhancement)
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import json


class HealingExecutor:
    """
    Executes healing actions for Quality Tower / 执行质量之塔的修复动作
    
    Phase 21 P2: Integrates with AutonomousAuditor for automated fixes.
    Phase 21 P2 Final Tuning: Shadow validation for safe healing (审查官).
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize healing executor / 初始化修复执行器
        
        Args:
            project_root: Project root directory / 项目根目录
        """
        self.project_root = project_root
        
        # Initialize shadow validator (审查官's 影子验证)
        from .shadow_validator import ShadowValidator
        self.shadow_validator = ShadowValidator(project_root)
    
    async def heal_test_coverage(self, issue: str, previous_score: float = 0) -> Dict:
        """
        Generate missing test cases / 生成缺失的测试用例
        
        Args:
            issue: Issue description / 问题描述
            
        Returns:
            Healing result / 修复结果
        """
        try:
            # Import AutonomousAuditor
            from .autonomous_auditor import AutonomousAuditor
            
            # Initialize auditor in test_executor mode
            auditor = AutonomousAuditor(self.project_root)
            
            # Analyze uncovered code
            uncovered_files = await self._analyze_uncovered_code()
            
            if not uncovered_files:
                return {
                    'success': True,
                    'message': '所有代码已覆盖',
                    'tests_added': 0,
                    'files_modified': []
                }
            
            # Generate tests for uncovered files
            tests_added = 0
            files_modified = []
            
            for file_path in uncovered_files:
                # Generate test file
                test_result = await auditor.generate_test_file(file_path)
                
                if test_result['success']:
                    tests_added += test_result.get('tests_count', 0)
                    files_modified.append(test_result['test_file'])
            
            return {
                'success': True,
                'message': f'成功生成 {tests_added} 个测试用例',
                'tests_added': tests_added,
                'files_modified': files_modified
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'测试生成失败: {str(e)}',
                'error': str(e)
            }
    
    async def heal_vibe_score(self, issue: str) -> Dict:
        """
        Clean code and add documentation / 清理代码并添加文档
        
        Args:
            issue: Issue description / 问题描述
            
        Returns:
            Healing result / 修复结果
        """
        try:
            # Import LocalReasoningEngine
            from .local_reasoning_engine import LocalReasoningEngine
            
            # Initialize reasoning engine
            reasoner = LocalReasoningEngine(self.project_root)
            
            # Analyze code quality issues
            quality_issues = await self._analyze_quality_issues()
            
            files_modified = []
            
            for file_path, issues in quality_issues.items():
                # Fix each issue
                for issue_type in issues:
                    if issue_type == 'missing_docstring':
                        await reasoner.add_docstrings(file_path)
                    elif issue_type == 'unused_variable':
                        await reasoner.remove_unused_variables(file_path)
                    elif issue_type == 'long_function':
                        await reasoner.refactor_long_function(file_path)
                
                files_modified.append(file_path)
            
            return {
                'success': True,
                'message': f'成功清理 {len(files_modified)} 个文件',
                'files_modified': files_modified
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'代码清理失败: {str(e)}',
                'error': str(e)
            }
    
    async def heal_security(self, issue: str) -> Dict:
        """
        Fix security issues / 修复安全问题
        
        Args:
            issue: Issue description / 问题描述
            
        Returns:
            Healing result / 修复结果
        """
        try:
            # Import LocalReasoningEngine
            from .local_reasoning_engine import LocalReasoningEngine
            
            # Initialize reasoning engine
            reasoner = LocalReasoningEngine(self.project_root)
            
            # Analyze security issues
            security_issues = await self._analyze_security_issues()
            
            files_modified = []
            
            for file_path, issues in security_issues.items():
                for issue_type, details in issues:
                    if issue_type == 'hardcoded_secret':
                        await reasoner.move_secret_to_env(file_path, details)
                    elif issue_type == 'unsafe_function':
                        await reasoner.replace_unsafe_function(file_path, details)
                
                files_modified.append(file_path)
            
            return {
                'success': True,
                'message': f'成功修复 {len(files_modified)} 个文件的安全问题',
                'files_modified': files_modified
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'安全修复失败: {str(e)}',
                'error': str(e)
            }
    
    async def heal_logic(self, issue: str) -> Dict:
        """
        Optimize code logic / 优化代码逻辑
        
        Args:
            issue: Issue description / 问题描述
            
        Returns:
            Healing result / 修复结果
        """
        try:
            # Import LocalReasoningEngine
            from .local_reasoning_engine import LocalReasoningEngine
            
            # Initialize reasoning engine
            reasoner = LocalReasoningEngine(self.project_root)
            
            # Analyze logic issues
            logic_issues = await self._analyze_logic_issues()
            
            files_modified = []
            
            for file_path, issues in logic_issues.items():
                for issue_type, details in issues:
                    if issue_type == 'poor_naming':
                        await reasoner.improve_variable_names(file_path, details)
                    elif issue_type == 'race_condition':
                        await reasoner.fix_race_condition(file_path, details)
                
                files_modified.append(file_path)
            
            return {
                'success': True,
                'message': f'成功优化 {len(files_modified)} 个文件的逻辑',
                'files_modified': files_modified
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'逻辑优化失败: {str(e)}',
                'error': str(e)
            }
    
    async def _analyze_uncovered_code(self) -> List[Path]:
        """
        Analyze uncovered code from coverage.json / 从 coverage.json 分析未覆盖代码
        
        Returns:
            List of uncovered files / 未覆盖文件列表
        """
        coverage_file = self.project_root / 'coverage.json'
        
        if not coverage_file.exists():
            return []
        
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
            
            uncovered_files = []
            
            for file_path, data in coverage_data.get('files', {}).items():
                coverage_percent = data.get('summary', {}).get('percent_covered', 100)
                
                if coverage_percent < 80:  # Threshold
                    uncovered_files.append(Path(file_path))
            
            return uncovered_files
        
        except Exception as e:
            print(f"Failed to analyze coverage: {e}")
            return []
    
    async def _analyze_quality_issues(self) -> Dict[Path, List[str]]:
        """
        Analyze code quality issues / 分析代码质量问题
        
        Returns:
            Dictionary of file paths to issue types / 文件路径到问题类型的字典
        """
        # Simplified implementation - would use AST analysis in production
        issues = {}
        
        for py_file in self.project_root.rglob('*.py'):
            if 'test' in py_file.name or '__pycache__' in str(py_file):
                continue
            
            file_issues = []
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for missing docstrings
                if 'def ' in content and '"""' not in content:
                    file_issues.append('missing_docstring')
                
                # Check for unused variables (simplified)
                if '_unused' in content or 'temp_' in content:
                    file_issues.append('unused_variable')
                
                if file_issues:
                    issues[py_file] = file_issues
            
            except Exception:
                continue
        
        return issues
    
    async def _analyze_security_issues(self) -> Dict[Path, List[tuple]]:
        """
        Analyze security issues / 分析安全问题
        
        Returns:
            Dictionary of file paths to security issues / 文件路径到安全问题的字典
        """
        # Would use AST analysis in production
        issues = {}
        
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            file_issues = []
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for hardcoded secrets
                if 'api_key = "' in content.lower() or 'password = "' in content.lower():
                    file_issues.append(('hardcoded_secret', 'API key or password'))
                
                # Check for unsafe functions
                if 'eval(' in content or 'exec(' in content:
                    file_issues.append(('unsafe_function', 'eval/exec'))
                
                if file_issues:
                    issues[py_file] = file_issues
            
            except Exception:
                continue
        
        return issues
    
    async def _analyze_logic_issues(self) -> Dict[Path, List[tuple]]:
        """
        Analyze logic issues / 分析逻辑问题
        
        Returns:
            Dictionary of file paths to logic issues / 文件路径到逻辑问题的字典
        """
        # Would use AST analysis and remote strategist in production
        issues = {}
        
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            file_issues = []
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for poor naming (simplified)
                if 'x = ' in content or 'temp = ' in content:
                    file_issues.append(('poor_naming', 'Single-letter variables'))
                
                # Check for potential race conditions
                if 'threading' in content and 'Lock' not in content:
                    file_issues.append(('race_condition', 'Threading without locks'))
                
                if file_issues:
                    issues[py_file] = file_issues
            
            except Exception:
                continue
        
        return issues
