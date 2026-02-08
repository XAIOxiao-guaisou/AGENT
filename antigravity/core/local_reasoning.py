"""
Local Reasoning Engine - 本地推理引擎
=====================================

Rule-based local decision making without LLM dependency.
基于规则的本地决策，不依赖 LLM。

Core Features:
- Intent mapping (意图映射)
- Constraint validation (约束验证)
- AST-based code scanning (基于 AST 的代码扫描)
- Project structure analysis (项目结构分析)
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import re


@dataclass
class Intent:
    """
    Parsed user intent / 解析的用户意图
    """
    primary_goal: str
    requires_database: bool = False
    requires_api: bool = False
    requires_auth: bool = False
    requires_testing: bool = False
    language: str = "python"
    framework: Optional[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class ProjectState:
    """
    Current project structure state / 当前项目结构状态
    """
    has_models: bool = False
    has_api: bool = False
    has_auth: bool = False
    has_tests: bool = False
    existing_files: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.existing_files is None:
            self.existing_files = []
        if self.dependencies is None:
            self.dependencies = []


class ConstraintSet:
    """
    Best practices constraint set / 最佳实践约束集
    
    Validates code against quality rules.
    根据质量规则验证代码。
    """
    
    def __init__(self):
        self.max_function_lines = 50
        self.max_file_lines = 500
        self.require_docstrings = True
        self.require_type_hints = True
        self.require_error_handling = True
    
    def validate_code(self, code: str, filename: str) -> List[str]:
        """
        Validate code against constraints / 根据约束验证代码
        
        Returns:
            List of violation messages / 违规消息列表
        """
        violations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [f"Syntax error: {e}"]
        
        # Check function length
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno + 1
                if func_lines > self.max_function_lines:
                    violations.append(
                        f"Function '{node.name}' has {func_lines} lines "
                        f"(max: {self.max_function_lines})"
                    )
                
                # Check docstring
                if self.require_docstrings:
                    if not ast.get_docstring(node):
                        violations.append(f"Function '{node.name}' missing docstring")
                
                # Check error handling
                if self.require_error_handling:
                    has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
                    if not has_try and 'main' not in node.name.lower():
                        violations.append(
                            f"Function '{node.name}' lacks error handling"
                        )
        
        # Check file length
        total_lines = len(code.split('\n'))
        if total_lines > self.max_file_lines:
            violations.append(
                f"File has {total_lines} lines (max: {self.max_file_lines})"
            )
        
        return violations
    
    def validate_plan(self, plan: Dict) -> List[str]:
        """
        Validate execution plan / 验证执行计划
        
        Returns:
            List of plan violations / 计划违规列表
        """
        violations = []
        
        # Check for circular dependencies
        if 'dependencies' in plan:
            # Simple cycle detection
            deps = plan['dependencies']
            if len(deps) != len(set(deps)):
                violations.append("Circular dependency detected")
        
        # Check file naming conventions
        if 'files_to_create' in plan:
            for file in plan['files_to_create']:
                if not file.endswith('.py'):
                    violations.append(f"Non-Python file: {file}")
                if not re.match(r'^[a-z_][a-z0-9_]*\.py$', os.path.basename(file)):
                    violations.append(f"Invalid Python filename: {file}")
        
        return violations


class IntentMapper:
    """
    Intent mapper - 意图映射器
    
    Maps natural language to structured intent.
    将自然语言映射到结构化意图。
    """
    
    def __init__(self):
        self.keyword_patterns = {
            'database': ['database', 'db', 'model', 'orm', 'sql', 'postgres', 'mysql'],
            'api': ['api', 'rest', 'endpoint', 'route', 'fastapi', 'flask'],
            'auth': ['auth', 'login', 'jwt', 'token', 'session', 'password'],
            'testing': ['test', 'pytest', 'unittest', 'coverage']
        }
    
    def map(self, idea: str) -> Intent:
        """
        Map idea to intent / 将想法映射到意图
        
        Args:
            idea: User's idea description / 用户想法描述
            
        Returns:
            Structured intent / 结构化意图
        """
        idea_lower = idea.lower()
        
        # Extract keywords
        keywords = []
        for word in idea.split():
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 3:
                keywords.append(clean_word)
        
        # Detect requirements
        requires_database = any(
            kw in idea_lower for kw in self.keyword_patterns['database']
        )
        requires_api = any(
            kw in idea_lower for kw in self.keyword_patterns['api']
        )
        requires_auth = any(
            kw in idea_lower for kw in self.keyword_patterns['auth']
        )
        requires_testing = any(
            kw in idea_lower for kw in self.keyword_patterns['testing']
        )
        
        # Detect framework
        framework = None
        if 'fastapi' in idea_lower:
            framework = 'fastapi'
        elif 'flask' in idea_lower:
            framework = 'flask'
        elif 'django' in idea_lower:
            framework = 'django'
        
        return Intent(
            primary_goal=idea,
            requires_database=requires_database,
            requires_api=requires_api,
            requires_auth=requires_auth,
            requires_testing=requires_testing,
            framework=framework,
            keywords=keywords
        )


class LocalReasoningEngine:
    """
    Local Reasoning Engine - 本地推理引擎
    
    Makes autonomous decisions without LLM calls.
    在不调用 LLM 的情况下做出自主决策。
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".")
        self.constraint_set = ConstraintSet()
        self.intent_mapper = IntentMapper()
    
    def draft_plan(self, idea: str) -> Dict:
        """
        Draft execution plan based on intent / 基于意图起草执行计划
        
        Args:
            idea: User's idea / 用户想法
            
        Returns:
            Execution plan / 执行计划
        """
        # 1. Map intent
        intent = self.intent_mapper.map(idea)
        
        # 2. Analyze current project
        project_state = self.analyze_project_structure()
        
        # 3. Generate plan
        plan = {
            'intent': intent.primary_goal,
            'files_to_create': [],
            'files_to_modify': [],
            'dependencies': [],
            'tasks': []
        }
        
        # 4. Add components based on intent
        if intent.requires_database and not project_state.has_models:
            plan['files_to_create'].extend([
                'models/__init__.py',
                'models/base.py'
            ])
            plan['dependencies'].append('sqlalchemy')
            plan['tasks'].append('Create database models')
        
        if intent.requires_api and not project_state.has_api:
            plan['files_to_create'].extend([
                'api/__init__.py',
                'api/routes.py'
            ])
            if intent.framework:
                plan['dependencies'].append(intent.framework)
            plan['tasks'].append('Implement API endpoints')
        
        if intent.requires_auth and not project_state.has_auth:
            plan['files_to_create'].extend([
                'auth/__init__.py',
                'auth/jwt_handler.py'
            ])
            plan['dependencies'].extend(['pyjwt', 'cryptography'])
            plan['tasks'].append('Implement authentication')
        
        if intent.requires_testing and not project_state.has_tests:
            plan['files_to_create'].extend([
                'tests/__init__.py',
                'tests/test_main.py'
            ])
            plan['dependencies'].append('pytest')
            plan['tasks'].append('Create test suite')
        
        # Always ensure main entry point
        if 'main.py' not in project_state.existing_files:
            plan['files_to_create'].append('main.py')
        
        # 5. Validate plan
                # 5. Validate plan
        violations = self.constraint_set.validate_plan(plan)
        if violations:
            plan['warnings'] = violations
        
        return plan
    
    @staticmethod
    def validate_shadow_prediction(task_id: str, prediction: Dict) -> bool:
        """
        Phase 16.4: Consensus Engine.
        Validates a Shadow Kernel prediction against physical reality.
        
        Checks:
        1. Syntax Validity (AST Parse)
        2. Non-Empty Content
        3. 'Hallucination' Heuristics (e.g. valid Python)
        """
        content = prediction.get('simulated_content', '')
        if not content:
            print(f"❌ CONSENSUS VETO: Prediction for {task_id} is empty.")
            return False
            
        try:
            import ast
            ast.parse(content)
            # Future: Check against architectural constraints?
            return True
        except SyntaxError as e:
            print(f"❌ CONSENSUS VETO: Prediction for {task_id} contains invalid syntax: {e}")
            return False
        except Exception as e:
            print(f"❌ CONSENSUS VETO: Prediction validation failed: {e}")
            return False
    
    def analyze_project_structure(self) -> ProjectState:
        """
        Analyze current project structure / 分析当前项目结构
        
        Returns:
            Project state / 项目状态
        """
        state = ProjectState()
        
        # Check for key directories
        state.has_models = (self.project_root / 'models').exists()
        state.has_api = (self.project_root / 'api').exists()
        state.has_auth = (self.project_root / 'auth').exists()
        state.has_tests = (self.project_root / 'tests').exists()
        
        # List existing Python files
        if self.project_root.exists():
            for file in self.project_root.rglob('*.py'):
                rel_path = file.relative_to(self.project_root)
                state.existing_files.append(str(rel_path))
        
        # Check requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                state.dependencies = [
                    line.split('==')[0].strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                ]
        
        return state
    
    def should_escalate_to_remote(self, error: Dict) -> bool:
        """
        Decide if error should be escalated to remote / 决定是否将错误升级到远程
        
        Args:
            error: Error information / 错误信息
            
        Returns:
            True if should escalate / 如果应该升级则返回 True
        """
        error_type = error.get('type', '')
        retry_count = error.get('retry_count', 0)
        
        # Simple errors handled locally
        if error_type in ['SyntaxError', 'ImportError', 'IndentationError']:
            return False
        
        # Repeated errors escalated
        if retry_count > 2:
            return True
        
        # Complex errors escalated
        if error_type in ['DesignError', 'LogicError', 'ArchitectureError']:
            return True
        
        return False
    
    def suggest_auto_fix(self, error: Dict) -> Optional[Dict]:
        """
        Suggest automatic fix for error / 为错误建议自动修复
        
        Args:
            error: Error information / 错误信息
            
        Returns:
            Fix suggestion or None / 修复建议或 None
        """
        error_type = error.get('type', '')
        message = error.get('message', '')
        
        if error_type == 'ImportError':
            # Extract missing module
            match = re.search(r"No module named '(\w+)'", message)
            if match:
                module = match.group(1)
                return {
                    'action': 'install_dependency',
                    'module': module,
                    'command': f'pip install {module}'
                }
        
        elif error_type == 'SyntaxError':
            if 'unexpected EOF' in message:
                return {
                    'action': 'check_brackets',
                    'suggestion': 'Check for unclosed brackets or quotes'
                }
        
        return None
