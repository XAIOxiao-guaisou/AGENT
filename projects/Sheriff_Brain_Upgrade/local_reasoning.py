"""
Local Reasoning Engine - 本地推理引擎
===================================

Defensive decision layer to reduce blind dependency on LLM code generation.
防御性决策层，减少对 LLM 生成代码的盲目依赖。

Phase 19: Core Architecture
- Intent mapping via regex + keyword weighting
- AST constraint validation (Sheriff Quality Rules)
- Pre-generation quality checks
"""

import ast
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Intent:
    """
    Recognized intent from idea / 从 Idea 识别的意图
    """
    category: str  # 'database', 'api', 'ui', 'test', etc.
    confidence: float  # 0.0 - 1.0
    keywords: List[str]
    suggested_actions: List[str]


class IntentMapper:
    """
    Intent Mapper - 意图识别器
    
    Phase 19: Local intent recognition via regex + keyword weighting
    Phase 19 Deep Optimization: Confidence threshold for remote escalation
    """
    
    # Confidence threshold for remote escalation (Deep Optimization)
    CONFIDENCE_THRESHOLD = 0.7  # If below this, escalate to REVIEWING state
    
    # Intent patterns with weighted keywords
    INTENT_PATTERNS = {
        'database': {
            'keywords': ['database', 'db', 'storage', 'persist', 'save', 'store', 'model', 'schema'],
            'weight': 1.0
        },
        'api': {
            'keywords': ['api', 'endpoint', 'route', 'backend', 'server', 'rest', 'graphql'],
            'weight': 1.0
        },
        'ui': {
            'keywords': ['ui', 'frontend', 'interface', 'page', 'dashboard', 'component', 'view'],
            'weight': 1.0
        },
        'authentication': {
            'keywords': ['auth', 'login', 'user', 'password', 'token', 'session', 'permission'],
            'weight': 1.2  # Higher weight for security-critical features
        },
        'test': {
            'keywords': ['test', 'testing', 'unittest', 'integration', 'coverage'],
            'weight': 0.8  # Always implied, lower weight
        },
        'deployment': {
            'keywords': ['deploy', 'deployment', 'production', 'docker', 'container'],
            'weight': 0.9
        }
    }
    
    def analyze(self, idea: str) -> List[Intent]:
        """
        Analyze idea and extract intents / 分析 Idea 并提取意图
        
        Phase 19 Deep Optimization: Returns confidence score for escalation decision
        
        Args:
            idea: High-level idea description
            
        Returns:
            List of recognized intents sorted by confidence
        """
        idea_lower = idea.lower()
        intents = []
        
        for category, config in self.INTENT_PATTERNS.items():
            # Count keyword matches
            matched_keywords = []
            for keyword in config['keywords']:
                if keyword in idea_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Calculate confidence
                confidence = (len(matched_keywords) / len(config['keywords'])) * config['weight']
                confidence = min(confidence, 1.0)  # Cap at 1.0
                
                # Suggest actions based on category
                actions = self._suggest_actions(category)
                
                intent = Intent(
                    category=category,
                    confidence=confidence,
                    keywords=matched_keywords,
                    suggested_actions=actions
                )
                intents.append(intent)
        
        # Sort by confidence (highest first)
        intents.sort(key=lambda x: x.confidence, reverse=True)
        
        return intents
    
    def should_escalate_to_remote(self, intents: List[Intent]) -> bool:
        """
        Determine if should escalate to remote strategist / 判断是否应升级到远程战略官
        
        Phase 19 Deep Optimization: Confidence threshold mechanism
        
        Args:
            intents: List of recognized intents
            
        Returns:
            True if should escalate to REVIEWING state
        """
        if not intents:
            # No intents recognized, escalate for safety
            return True
        
        # Check if highest confidence is below threshold
        max_confidence = intents[0].confidence
        
        if max_confidence < self.CONFIDENCE_THRESHOLD:
            print(f"   ⚠️ Low confidence ({max_confidence:.2f} < {self.CONFIDENCE_THRESHOLD})")
            print(f"   🚀 Escalating to REVIEWING state (remote strategist)")
            return True
        
        return False
    
    def _suggest_actions(self, category: str) -> List[str]:
        """
        Suggest actions for intent category / 为意图类别建议动作
        
        Args:
            category: Intent category
            
        Returns:
            List of suggested actions
        """
        action_map = {
            'database': [
                '创建数据库模型',
                '定义 Schema',
                '实现 CRUD 操作',
                '添加数据库迁移'
            ],
            'api': [
                '设计 API 端点',
                '实现路由处理',
                '添加请求验证',
                '实现错误处理'
            ],
            'ui': [
                '设计界面布局',
                '实现组件',
                '添加交互逻辑',
                '优化用户体验'
            ],
            'authentication': [
                '实现用户注册',
                '实现登录逻辑',
                '添加 Token 验证',
                '实现权限控制'
            ],
            'test': [
                '编写单元测试',
                '添加集成测试',
                '提高测试覆盖率',
                '实现端到端测试'
            ],
            'deployment': [
                '配置部署环境',
                '创建 Dockerfile',
                '设置 CI/CD',
                '配置生产环境'
            ]
        }
        
        return action_map.get(category, ['实现基础功能'])


class ASTConstraintValidator:
    """
    AST Constraint Validator - AST 约束校验器
    
    Phase 19: Sheriff Quality Rules enforcement
    Phase 19 Deep Optimization: Type Hints enforcement + defensive templates
    
    Quality Rules:
    - No functions > 50 lines
    - All functions must have try-except
    - All functions must have Type Hints (Deep Optimization)
    - No hardcoded secrets
    - No eval/exec usage
    """
    
    MAX_FUNCTION_LINES = 50
    
    def __init__(self):
        """Initialize validator"""
        self.violations = []
    
    def validate_code(self, code: str, filepath: str = "<string>") -> Tuple[bool, List[str]]:
        """
        Validate code against Sheriff Quality Rules / 根据 Sheriff 质量准则校验代码
        
        Args:
            code: Python code to validate
            filepath: File path for error reporting
            
        Returns:
            (is_valid, violations)
        """
        self.violations = []
        
        try:
            tree = ast.parse(code, filename=filepath)
        except SyntaxError as e:
            self.violations.append(f"Syntax Error: {e}")
            return False, self.violations
        
        # Visit all nodes
        for node in ast.walk(tree):
            # Check function length
            if isinstance(node, ast.FunctionDef):
                self._check_function_length(node, code)
                self._check_exception_handling(node)
                self._check_type_hints(node)  # Deep Optimization
            
            # Check for eval/exec
            if isinstance(node, ast.Call):
                self._check_unsafe_functions(node)
            
            # Check for hardcoded secrets
            if isinstance(node, ast.Assign):
                self._check_hardcoded_secrets(node, code)
        
        is_valid = len(self.violations) == 0
        return is_valid, self.violations
    
    def _check_function_length(self, node: ast.FunctionDef, code: str):
        """Check if function exceeds max line limit"""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            func_lines = node.end_lineno - node.lineno + 1
            
            if func_lines > self.MAX_FUNCTION_LINES:
                self.violations.append(
                    f"Function '{node.name}' is {func_lines} lines (max: {self.MAX_FUNCTION_LINES})"
                )
    
    def _check_exception_handling(self, node: ast.FunctionDef):
        """Check if function has try-except (simplified check)"""
        has_try = any(isinstance(child, ast.Try) for child in ast.walk(node))
        
        # Only enforce for non-trivial functions (> 5 lines)
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            func_lines = node.end_lineno - node.lineno + 1
            
            if func_lines > 5 and not has_try:
                self.violations.append(
                    f"Function '{node.name}' lacks try-except error handling"
                )
    
    def _check_unsafe_functions(self, node: ast.Call):
        """Check for eval/exec usage"""
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self.violations.append(
                    f"Unsafe function '{node.func.id}' detected (line {node.lineno})"
                )
    
    def _check_hardcoded_secrets(self, node: ast.Assign, code: str):
        """Check for hardcoded secrets (simplified)"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                
                # Check for suspicious variable names
                if any(secret in var_name for secret in ['password', 'api_key', 'secret', 'token']):
                    # Check if assigned a string literal
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if len(node.value.value) > 5:  # Non-trivial string
                            self.violations.append(
                                f"Potential hardcoded secret in '{target.id}' (line {node.lineno})"
                            )
    
    def _check_type_hints(self, node: ast.FunctionDef):
        """
        Check if function has type hints / 检查函数是否有类型注解
        
        Phase 19 Deep Optimization: Enforce Type Hints for all functions
        """
        # Check if function has return type annotation
        if node.returns is None:
            self.violations.append(
                f"Function '{node.name}' missing return type hint (line {node.lineno})"
            )
        
        # Check if arguments have type annotations
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != 'self':
                self.violations.append(
                    f"Argument '{arg.arg}' in function '{node.name}' missing type hint (line {node.lineno})"
                )


class LocalReasoningEngine:
    """
    Local Reasoning Engine - 本地推理引擎
    
    Phase 19: Defensive decision layer
    
    Responsibilities:
    - Intent recognition
    - Pre-generation quality checks
    - AST constraint validation
    """
    
    def __init__(self):
        """Initialize reasoning engine"""
        self.intent_mapper = IntentMapper()
        self.ast_validator = ASTConstraintValidator()
    
    def analyze_idea(self, idea: str) -> Dict:
        """
        Analyze idea and extract structured information / 分析 Idea 并提取结构化信息
        
        Args:
            idea: High-level idea description
            
        Returns:
            Analysis result with intents and recommendations
        """
        print("\n🧠 Local Reasoning Engine - Analyzing Idea")
        print(f"   Idea: {idea[:100]}...")
        
        # Extract intents
        intents = self.intent_mapper.analyze(idea)
        
        print(f"\n   📊 Recognized Intents:")
        for intent in intents:
            print(f"      - {intent.category}: {intent.confidence:.2f} confidence")
            print(f"        Keywords: {', '.join(intent.keywords)}")
        
        # Generate recommendations
        recommendations = []
        for intent in intents:
            if intent.confidence >= 0.5:  # Threshold
                recommendations.extend(intent.suggested_actions)
        
        return {
            'intents': intents,
            'recommendations': recommendations,
            'primary_intent': intents[0] if intents else None
        }
    
    def validate_generated_code(self, code: str, filepath: str = "<generated>") -> Dict:
        """
        Validate generated code against Sheriff Quality Rules / 根据 Sheriff 质量准则校验生成的代码
        
        Args:
            code: Generated Python code
            filepath: File path for error reporting
            
        Returns:
            Validation result
        """
        print(f"\n🔍 Validating generated code: {filepath}")
        
        is_valid, violations = self.ast_validator.validate_code(code, filepath)
        
        if is_valid:
            print("   ✅ Code passes all Sheriff Quality Rules")
        else:
            print(f"   ❌ Found {len(violations)} violations:")
            for violation in violations:
                print(f"      - {violation}")
        
        return {
            'is_valid': is_valid,
            'violations': violations,
            'can_proceed': is_valid
        }


# Example usage
if __name__ == "__main__":
    engine = LocalReasoningEngine()
    
    # Test 1: Intent analysis
    idea = "创建一个用户认证系统，包含登录、注册和权限管理功能，使用数据库存储用户信息"
    result = engine.analyze_idea(idea)
    
    print(f"\n📋 Recommendations:")
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"   {i}. {rec}")
    
    # Test 2: Code validation
    good_code = """
def process_data(data):
    try:
        result = data.strip().lower()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
"""
    
    bad_code = """
api_key = "sk-1234567890abcdef"  # Hardcoded secret!

def giant_function():
    # This function is way too long
    line1 = 1
    line2 = 2
    # ... imagine 50+ more lines
    return eval("1 + 1")  # Unsafe!
"""
    
    print("\n" + "=" * 60)
    print("Testing Good Code:")
    engine.validate_generated_code(good_code)
    
    print("\n" + "=" * 60)
    print("Testing Bad Code:")
    engine.validate_generated_code(bad_code)
