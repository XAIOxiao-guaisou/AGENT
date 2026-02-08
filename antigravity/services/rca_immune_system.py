"""
RCA Immune System - 根因分析免疫系统
=====================================

Self-healing error recovery system with root cause analysis.
具有根因分析的自愈错误恢复系统。

Core Features:
- Error snapshot extraction (错误快照提取)
- Severity analysis (严重性分析)
- Auto-fix attempts (自动修复尝试)
- Escalation to remote expert (升级到远程专家)
- Fix history tracking (修复历史追踪)

Think of it as the "immune system" - it fights off infections (errors) automatically!
把它想象成"免疫系统" - 自动对抗感染（错误）！
"""

import sys
import traceback
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class ErrorSnapshot:
    """
    Error snapshot - 错误快照
    
    Captures complete error context for analysis.
    捕获完整的错误上下文以供分析。
    """
    error_type: str
    message: str
    traceback: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    local_vars: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary / 序列化为字典"""
        return {
            'error_type': self.error_type,
            'message': self.message,
            'traceback': self.traceback,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'function_name': self.function_name,
            'local_vars': self.local_vars,
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count
        }


@dataclass
class FixResult:
    """
    Fix result - 修复结果
    
    Records the outcome of a fix attempt.
    记录修复尝试的结果。
    """
    success: bool
    action: str
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary / 序列化为字典"""
        return {
            'success': self.success,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class RCAImmuneSystem:
    """
    RCA Immune System - 根因分析免疫系统
    
    The "immune system" of Sheriff Brain - automatically fights errors!
    Sheriff Brain 的"免疫系统" - 自动对抗错误！
    
    Workflow:
    1. Capture error snapshot (捕获错误快照)
    2. Analyze severity (分析严重性)
    3. Attempt auto-fix (尝试自动修复)
    4. Escalate if needed (必要时升级)
    
    Phase 21 P0 Enhancements:
    - Fuzzy error signature matching (模糊错误指纹匹配)
    - Cooldown period for locked projects (项目锁定冷却期)
    """
    
    # Phase 21: Immune Fatigue Protection
    MAX_HEALING_DEPTH = 3  # 免疫疲劳阈值 - Maximum healing attempts
    COOLDOWN_PERIOD = 300  # 冷却期 (5 minutes in seconds)
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize immune system / 初始化免疫系统
        
        Args:
            project_root: Project root directory / 项目根目录
        """
        self.project_root = project_root or Path(".")
        self.fix_history: List[Dict] = []
        self.error_patterns: Dict[str, int] = {}  # Track recurring errors
        
        # Phase 21: Healing stack for fatigue protection
        self.healing_stack: List[str] = []  # Track healing chain
        
        # Phase 21 P0: Cooldown management
        self.locked_projects: Dict[str, datetime] = {}  # project_id → lock_time
        
        # Auto-fix strategies
        self.auto_fix_strategies = {
            'ImportError': self._fix_import_error,
            'ModuleNotFoundError': self._fix_import_error,
            'SyntaxError': self._fix_syntax_error,
            'IndentationError': self._fix_indentation_error,
            'NameError': self._fix_name_error,
        }
    
    def _generate_error_signature(self, snapshot: ErrorSnapshot) -> str:
        """
        Generate fuzzy error signature / 生成模糊错误指纹
        
        Phase 21 P0: Focus on error type and location, ignore dynamic content.
        专注于错误类型和位置，忽略动态内容。
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Fuzzy error signature / 模糊错误指纹
        """
        # Use error type + file + line (ignore message)
        signature = f"{snapshot.error_type}:{snapshot.file_path}:{snapshot.line_number}"
        
        # For import errors, include module name
        if snapshot.error_type in ['ImportError', 'ModuleNotFoundError']:
            match = re.search(r"No module named '(\w+)'", snapshot.message)
            if match:
                module = match.group(1)
                signature = f"{snapshot.error_type}:module={module}"
        
        return signature
    
    def _lock_project(self, project_id: str):
        """
        Lock project with cooldown period / 锁定项目并设置冷却期
        
        Args:
            project_id: Project identifier / 项目标识符
        """
        self.locked_projects[project_id] = datetime.now()
        print(f"🔒 Project locked: {project_id}")
        print(f"   Cooldown period: {self.COOLDOWN_PERIOD}s ({self.COOLDOWN_PERIOD/60:.1f} minutes)")
    
    def _is_in_cooldown(self, project_id: str) -> bool:
        """
        Check if project is in cooldown / 检查项目是否在冷却期
        
        Args:
            project_id: Project identifier / 项目标识符
            
        Returns:
            True if in cooldown / 如果在冷却期则返回 True
        """
        if project_id not in self.locked_projects:
            return False
        
        lock_time = self.locked_projects[project_id]
        elapsed = (datetime.now() - lock_time).total_seconds()
        
        if elapsed >= self.COOLDOWN_PERIOD:
            # Cooldown expired, remove lock
            del self.locked_projects[project_id]
            print(f"🧊 Cooldown expired for project: {project_id}")
            return False
        
        return True
    
    def _get_cooldown_remaining(self, project_id: str) -> float:
        """
        Get remaining cooldown time in seconds / 获取剩余冷却时间（秒）
        
        Args:
            project_id: Project identifier / 项目标识符
            
        Returns:
            Remaining cooldown time / 剩余冷却时间
        """
        if project_id not in self.locked_projects:
            return 0.0
        
        lock_time = self.locked_projects[project_id]
        elapsed = (datetime.now() - lock_time).total_seconds()
        return max(0, self.COOLDOWN_PERIOD - elapsed)
    
    def on_error_captured(self, error: Exception, context: Optional[Dict] = None) -> FixResult:
        """
        Main entry point when error is captured / 捕获错误时的主入口
        
        This is the "immune response" - triggered when infection (error) detected!
        这是"免疫响应" - 检测到感染（错误）时触发！
        
        Phase 21: Added immune fatigue protection to prevent infinite loops.
        Phase 21 P0: Added fuzzy signature matching and cooldown period.
        
        Args:
            error: Exception object / 异常对象
            context: Additional context / 附加上下文
            
        Returns:
            Fix result / 修复结果
        """
        print(f"\n🦠 Immune System Activated! Error detected: {type(error).__name__}")
        
        # 0. Check cooldown period
        project_id = context.get('project_id', 'default') if context else 'default'
        
        if self._is_in_cooldown(project_id):
            cooldown_remaining = self._get_cooldown_remaining(project_id)
            print(f"🧊 Project in cooldown: {cooldown_remaining:.0f}s remaining ({cooldown_remaining/60:.1f} min)")
            
            return FixResult(
                success=False,
                action='cooldown_active',
                details=f"Project locked for {cooldown_remaining:.0f}s. Please wait for cooldown to expire."
            )
        
        # 1. Extract snapshot (提取快照)
        snapshot = self._extract_snapshot(error, context)
        print(f"📸 Snapshot captured: {snapshot.error_type} at {snapshot.file_path}:{snapshot.line_number}")
        
        # 2. Generate fuzzy error signature (生成模糊错误指纹)
        error_signature = self._generate_error_signature(snapshot)
        print(f"🔍 Error signature: {error_signature}")
        
        # 3. Check for immune fatigue (检查免疫疲劳)
        if error_signature in self.healing_stack:
            # Detected recursive healing attempt
            depth = self.healing_stack.count(error_signature)
            print(f"⚠️ Recursive healing detected! Depth: {depth}/{self.MAX_HEALING_DEPTH}")
            
            if depth >= self.MAX_HEALING_DEPTH:
                print(f"🛑 IMMUNE FATIGUE! Maximum healing depth reached.")
                print(f"   Locking project and escalating to expert...")
                
                # Clear healing stack to prevent further attempts
                self.healing_stack.clear()
                
                # Lock project with cooldown
                self._lock_project(project_id)
                
                # Force escalation to remote expert
                fix_result = self._force_expert_escalation(snapshot, context or {}, depth)
                self._log_fix(snapshot, fix_result)
                return fix_result
        
        # 4. Add to healing stack
        self.healing_stack.append(error_signature)
        
        try:
            # 5. Analyze severity (分析严重性)
            severity = self._analyze_severity(snapshot)
            print(f"🔍 Severity analysis: {severity}")
            
            # 6. Check if we can auto-fix (检查是否可以自动修复)
            if severity in ['LOW', 'MEDIUM'] and self._can_auto_fix(snapshot):
                print(f"💊 Attempting auto-fix...")
                fix_result = self._auto_fix(snapshot)
                
                # Always log the fix attempt (成功或失败都记录)
                self._log_fix(snapshot, fix_result)
                
                if fix_result.success:
                    print(f"✅ Auto-fix successful: {fix_result.action}")
                    # Remove from healing stack on success
                    self.healing_stack.remove(error_signature)
                    return fix_result
                else:
                    print(f"⚠️ Auto-fix failed: {fix_result.details}")
                    # Also remove from stack on failure to allow retry
                    if error_signature in self.healing_stack:
                        self.healing_stack.remove(error_signature)
            
            # 7. Escalate to remote expert (升级到远程专家)
            if snapshot.retry_count > 2 or severity == 'HIGH':
                print(f"🚨 Escalating to remote expert (retry: {snapshot.retry_count}, severity: {severity})")
                fix_result = self._escalate_to_expert(snapshot, context or {})
                self._log_fix(snapshot, fix_result)
                # Remove from healing stack after escalation
                if error_signature in self.healing_stack:
                    self.healing_stack.remove(error_signature)
                return fix_result
            
            # 8. No fix available
            print(f"❌ No auto-fix available, manual intervention required")
            fix_result = FixResult(
                success=False,
                action='no_fix_available',
                details=f"Error type {snapshot.error_type} requires manual intervention"
            )
            self._log_fix(snapshot, fix_result)
            # Remove from healing stack
            if error_signature in self.healing_stack:
                self.healing_stack.remove(error_signature)
            return fix_result
            
        except Exception as e:
            # Cleanup healing stack on exception
            if error_signature in self.healing_stack:
                self.healing_stack.remove(error_signature)
            raise
    
    def _force_expert_escalation(self, snapshot: ErrorSnapshot, context: Dict, depth: int) -> FixResult:
        """
        Force escalation to expert due to immune fatigue / 因免疫疲劳强制升级到专家
        
        Args:
            snapshot: Error snapshot / 错误快照
            context: Execution context / 执行上下文
            depth: Healing depth / 修复深度
            
        Returns:
            Fix result / 修复结果
        """
        print(f"   🏥 CRITICAL: Immune system exhausted after {depth} attempts")
        print(f"   📋 Project locked - requires expert intervention")
        
        # Enhance context with fatigue information
        context['immune_fatigue'] = True
        context['healing_depth'] = depth
        context['requires_root_cause_analysis'] = True
        context['priority'] = 'CRITICAL'
        
        # Import here to avoid circular dependency
        from .sheriff_strategist import SheriffStrategist
        
        strategist = SheriffStrategist()
        consultation = strategist.expert_consultation(
            snapshot.to_dict(),
            context
        )
        
        print(f"   💡 Expert diagnosis: {consultation.get('root_cause', 'Unknown')}")
        print(f"   🔧 Recommended fix: {consultation.get('fix_approach', 'Manual intervention')}")
        print(f"   🚨 Prevention: {consultation.get('prevention', 'Review architecture')}")
        
        return FixResult(
            success=False,
            action='immune_fatigue_escalation',
            details=json.dumps({
                'reason': 'Maximum healing depth exceeded',
                'depth': depth,
                'consultation': consultation
            }, ensure_ascii=False)
        )
    
    def _extract_snapshot(self, error: Exception, context: Optional[Dict] = None) -> ErrorSnapshot:
        """
        Extract error snapshot / 提取错误快照
        
        Like taking a "病历照片" (medical photo) of the error!
        就像给错误拍"病历照片"！
        
        Args:
            error: Exception object / 异常对象
            context: Additional context / 附加上下文
            
        Returns:
            Error snapshot / 错误快照
        """
        # Get traceback
        tb_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        
        # Parse file and line info
        file_path, line_number, function_name = self._parse_traceback(tb_str)
        
        # Get local variables (if available)
        local_vars = {}
        if error.__traceback__:
            frame = error.__traceback__.tb_frame
            local_vars = {k: str(v)[:100] for k, v in frame.f_locals.items()}  # Limit size
        
        # Check retry count
        error_key = f"{type(error).__name__}:{file_path}:{line_number}"
        retry_count = self.error_patterns.get(error_key, 0)
        self.error_patterns[error_key] = retry_count + 1
        
        return ErrorSnapshot(
            error_type=type(error).__name__,
            message=str(error),
            traceback=tb_str,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            local_vars=local_vars,
            retry_count=retry_count
        )
    
    def _parse_traceback(self, tb_str: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        Parse traceback to extract file, line, function / 解析回溯以提取文件、行、函数
        
        Args:
            tb_str: Traceback string / 回溯字符串
            
        Returns:
            (file_path, line_number, function_name) / (文件路径, 行号, 函数名)
        """
        # Look for pattern: File "path", line N, in function
        pattern = r'File "([^"]+)", line (\d+), in (\w+)'
        matches = re.findall(pattern, tb_str)
        
        if matches:
            # Get last match (most recent call)
            file_path, line_num, func_name = matches[-1]
            return file_path, int(line_num), func_name
        
        return None, None, None
    
    def _analyze_severity(self, snapshot: ErrorSnapshot) -> str:
        """
        Analyze error severity / 分析错误严重性
        
        Like a doctor diagnosing: 轻症 (LOW), 中症 (MEDIUM), 重症 (HIGH)
        就像医生诊断：轻症、中症、重症
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Severity level: LOW, MEDIUM, HIGH / 严重性级别
        """
        error_type = snapshot.error_type
        
        # Low severity - easy to fix
        if error_type in ['SyntaxError', 'IndentationError', 'ImportError', 'ModuleNotFoundError']:
            return 'LOW'
        
        # Medium severity - might need some work
        if error_type in ['NameError', 'AttributeError', 'KeyError', 'IndexError']:
            return 'MEDIUM'
        
        # High severity - complex issues
        if error_type in ['DesignError', 'LogicError', 'RuntimeError', 'ValueError']:
            return 'HIGH'
        
        # Unknown - treat as medium
        return 'MEDIUM'
    
    def _can_auto_fix(self, snapshot: ErrorSnapshot) -> bool:
        """
        Check if error can be auto-fixed / 检查错误是否可以自动修复
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            True if auto-fix available / 如果有自动修复则返回 True
        """
        return snapshot.error_type in self.auto_fix_strategies
    
    def _auto_fix(self, snapshot: ErrorSnapshot) -> FixResult:
        """
        Attempt automatic fix / 尝试自动修复
        
        The "immune system" fights back! 免疫系统反击！
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Fix result / 修复结果
        """
        strategy = self.auto_fix_strategies.get(snapshot.error_type)
        
        if not strategy:
            return FixResult(
                success=False,
                action='no_strategy',
                details=f"No auto-fix strategy for {snapshot.error_type}"
            )
        
        try:
            return strategy(snapshot)
        except Exception as e:
            return FixResult(
                success=False,
                action='strategy_failed',
                details=f"Auto-fix strategy failed: {str(e)}"
            )
    
    def _fix_import_error(self, snapshot: ErrorSnapshot) -> FixResult:
        """
        Fix ImportError / 修复导入错误
        
        Strategy: Install missing module
        策略：安装缺失的模块
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Fix result / 修复结果
        """
        # Extract module name
        match = re.search(r"No module named '(\w+)'", snapshot.message)
        if not match:
            return FixResult(
                success=False,
                action='parse_failed',
                details="Could not extract module name"
            )
        
        module_name = match.group(1)
        
        print(f"   📦 Installing missing module: {module_name}")
        
        # Try to install
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', module_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Also update requirements.txt
                self._update_requirements(module_name)
                
                return FixResult(
                    success=True,
                    action='module_installed',
                    details=f"Installed {module_name} and updated requirements.txt"
                )
            else:
                return FixResult(
                    success=False,
                    action='install_failed',
                    details=result.stderr
                )
        
        except subprocess.TimeoutExpired:
            return FixResult(
                success=False,
                action='install_timeout',
                details=f"Installation of {module_name} timed out"
            )
    
    def _fix_syntax_error(self, snapshot: ErrorSnapshot) -> FixResult:
        """
        Fix SyntaxError / 修复语法错误
        
        Strategy: Check for common issues (unclosed brackets, quotes)
        策略：检查常见问题（未闭合的括号、引号）
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Fix result / 修复结果
        """
        # For now, just provide suggestions
        # Actual code fixing would require AST manipulation
        
        suggestions = []
        
        if 'unexpected EOF' in snapshot.message:
            suggestions.append("Check for unclosed brackets (), [], {}")
            suggestions.append("Check for unclosed quotes '', \"\"")
        
        if 'invalid syntax' in snapshot.message:
            suggestions.append("Check for missing colons : after if/for/def/class")
            suggestions.append("Check for incorrect indentation")
        
        return FixResult(
            success=False,
            action='suggestions_provided',
            details="Suggestions: " + "; ".join(suggestions)
        )
    
    def _fix_indentation_error(self, snapshot: ErrorSnapshot) -> FixResult:
        """
        Fix IndentationError / 修复缩进错误
        
        Strategy: Suggest checking indentation
        策略：建议检查缩进
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Fix result / 修复结果
        """
        return FixResult(
            success=False,
            action='suggestions_provided',
            details="Check indentation: use 4 spaces consistently, avoid mixing tabs and spaces"
        )
    
    def _fix_name_error(self, snapshot: ErrorSnapshot) -> FixResult:
        """
        Fix NameError / 修复名称错误
        
        Strategy: Suggest checking variable names and imports
        策略：建议检查变量名和导入
        
        Args:
            snapshot: Error snapshot / 错误快照
            
        Returns:
            Fix result / 修复结果
        """
        # Extract undefined name
        match = re.search(r"name '(\w+)' is not defined", snapshot.message)
        if match:
            name = match.group(1)
            return FixResult(
                success=False,
                action='suggestions_provided',
                details=f"Variable '{name}' not defined. Check: 1) Is it imported? 2) Is it spelled correctly? 3) Is it in scope?"
            )
        
        return FixResult(
            success=False,
            action='suggestions_provided',
            details="Check variable names and imports"
        )
    
    def _update_requirements(self, module_name: str):
        """
        Update requirements.txt / 更新 requirements.txt
        
        Args:
            module_name: Module to add / 要添加的模块
        """
        req_file = self.project_root / 'requirements.txt'
        
        # Read existing requirements
        existing = set()
        if req_file.exists():
            with open(req_file, 'r') as f:
                existing = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        
        # Add new module if not exists
        if module_name not in existing:
            with open(req_file, 'a') as f:
                f.write(f"\n{module_name}\n")
            print(f"   📝 Added {module_name} to requirements.txt")
    
    def _escalate_to_expert(self, snapshot: ErrorSnapshot, context: Dict) -> FixResult:
        """
        Escalate to remote expert / 升级到远程专家
        
        When the immune system can't handle it, call the specialist!
        当免疫系统无法处理时，呼叫专家！
        
        Args:
            snapshot: Error snapshot / 错误快照
            context: Execution context / 执行上下文
            
        Returns:
            Fix result / 修复结果
        """
        print(f"   🏥 Requesting expert consultation...")
        
        # Import here to avoid circular dependency
        from .sheriff_strategist import SheriffStrategist
        
        strategist = SheriffStrategist()
        consultation = strategist.expert_consultation(
            snapshot.to_dict(),
            context
        )
        
        print(f"   💡 Expert diagnosis: {consultation.get('root_cause', 'Unknown')}")
        print(f"   🔧 Recommended fix: {consultation.get('fix_approach', 'Manual intervention')}")
        
        return FixResult(
            success=False,
            action='expert_consultation',
            details=json.dumps(consultation, ensure_ascii=False)
        )
    
    def _log_fix(self, snapshot: ErrorSnapshot, fix_result: FixResult):
        """
        Log fix attempt / 记录修复尝试
        
        Args:
            snapshot: Error snapshot / 错误快照
            fix_result: Fix result / 修复结果
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': snapshot.to_dict(),
            'fix': fix_result.to_dict()
        }
        self.fix_history.append(log_entry)
    
    def get_fix_history(self) -> List[Dict]:
        """
        Get fix history / 获取修复历史
        
        Returns:
            Fix history / 修复历史
        """
        return self.fix_history
    
    def get_statistics(self) -> Dict:
        """
        Get immune system statistics / 获取免疫系统统计
        
        Returns:
            Statistics / 统计信息
        """
        total_fixes = len(self.fix_history)
        successful_fixes = sum(1 for entry in self.fix_history if entry['fix']['success'])
        
        error_types = {}
        for entry in self.fix_history:
            error_type = entry['error']['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': total_fixes,
            'successful_fixes': successful_fixes,
            'success_rate': successful_fixes / total_fixes if total_fixes > 0 else 0,
            'error_types': error_types,
            'recurring_errors': len(self.error_patterns)
        }
