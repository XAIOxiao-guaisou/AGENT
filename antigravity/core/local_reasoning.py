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



class ComplexTaskSplitter:
    """
    Phase 19: Swarm Intelligence.
    Splits complex objectives into atomic sub-tasks.
    """
    def split(self, idea: str) -> List[str]:
        # Simple heuristic: split by 'and', 'with', ','
        # "Build a login system and a dashboard with metrics"
        # -> ["Build a login system", "a dashboard", "metrics"]
        # Refined regex to avoid splitting "user and password" or other common phrases?
        # For v1, keeps it simple.
        parts = re.split(r' and | with |,\s*', idea, flags=re.IGNORECASE)
        tasks = [p.strip() for p in parts if len(p.strip()) > 5] # Min length filter
        return tasks if len(tasks) > 1 else []

class ConsensusVoter:
    """
    Phase 20: Global Consensus.
    Democratizes logic by requiring multi-node alignment.
    """
    def __init__(self, threshold=0.66):
        self.threshold = threshold # 2/3 majority

    def cast_votes(self, task_id: str, shadow_prediction: Dict) -> Dict:
        """
        Simulates 3 heterogeneous audit nodes.
        Node A: Physical Integrity
        Node B: Intent Resonance
        Node C: Security Gate
        """
        votes = []
        
        # Node A: Physical Integrity
        votes.append(self.audit_physical_integrity(shadow_prediction))
        
        # Node B: Intent Resonance
        votes.append(self.audit_intent_resonance(shadow_prediction))
        
        # Node C: Security Gate
        votes.append(self.audit_security_gate(shadow_prediction))
        
        # Calculate Approval
        approval_count = sum(1 for v in votes if v['approved'])
        approval_rate = approval_count / len(votes)
        
        status = "CONSENSUS_REACHED" if approval_rate >= self.threshold else "CONSENSUS_FAILED"
        
        return {
            "status": status,
            "rate": approval_rate,
            "details": votes
        }

    def audit_physical_integrity(self, prediction: Dict) -> Dict:
        """Node A: Checks if AST hash is stable and valid."""
        phash = prediction.get('predicted_hash')
        if phash == "PREDICTION_PARSE_ERROR":
            return {"node": "Physical", "approved": False, "reason": "AST Parse Error"}
        return {"node": "Physical", "approved": True, "reason": "AST Valid"}

    def audit_intent_resonance(self, prediction: Dict) -> Dict:
        """Node B: Checks if code aligns with PLAN.md (Simulated)."""
        # In a real system, we'd compare vector embeddings of code vs plan.
        # For v1.7.0, we accept unless explicitly flagged as "POISON_PILL" in content
        content = prediction.get('simulated_content', "")
        if "POISON_PILL" in content:
             return {"node": "Intent", "approved": False, "reason": "Malicious Intent Detected"}
        return {"node": "Intent", "approved": True, "reason": "Aligned with Plan"}

    def audit_security_gate(self, prediction: Dict) -> Dict:
        """Node C: Scans for hardcoded secrets or unsafe patterns."""
        content = prediction.get('simulated_content', "")
        # Simple check for hardcoded secrets pattern
        if "SECRET_KEY =" in content or "password =" in content:
             # Allow if it's os.getenv, reject if literal string (simplified)
             if "os.getenv" not in content and "os.environ" not in content:
                 return {"node": "Security", "approved": False, "reason": "Hardcoded Secret"}
        return {"node": "Security", "approved": True, "reason": "Security Pass"}


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
        self.task_splitter = ComplexTaskSplitter()
        self.consensus_voter = ConsensusVoter() # Phase 20
    
    def draft_plan(self, idea: str) -> Dict:
        """
        Draft execution plan based on intent.
        Phase 22: Optimized for reduced complexity.
        """
        # 0. Swarm Decomposition
        swarm_plan = self._draft_swarm_plan(idea)
        if swarm_plan:
            return swarm_plan

        # 1. Map intent
        intent = self.intent_mapper.map(idea)
        
        # 2. Analyze current project
        project_state = self.analyze_project_structure()
        
        # 3. Initialize basic plan
        plan = {
            'intent': intent.primary_goal,
            'files_to_create': [],
            'files_to_modify': [],
            'dependencies': [],
            'tasks': []
        }
        
        # 4. Inject Components
        self._inject_components(intent, project_state, plan)
            
        # 5. Synaptic Retrieval (Smart Probe)
        self._run_synaptic_probe(intent, plan)
        
        # 6. Validate plan
        violations = self.constraint_set.validate_plan(plan)
        if violations:
            plan['warnings'] = violations
        
        return plan

    def _draft_swarm_plan(self, idea: str) -> Optional[Dict]:
        """Phase 19: Swarm Decomposition Logic"""
        subtasks = self.task_splitter.split(idea)
        if not subtasks:
            return None
            
        print(f"🐝 SWARM: Detected complex task. Splitting into {len(subtasks)} sub-tasks.")
        swarm_plan = {
            'type': 'swarm_composite',
            'intent': idea,
            'subtasks': [],
            'tasks': []
        }
        
        try:
            from antigravity.core.knowledge_graph import FleetKnowledgeGraph
            gkg = FleetKnowledgeGraph.get_instance()
            
            for sub in subtasks:
                matches = gkg.find_fleet_capability(sub, top_k=1)
                assigned_node = matches[0]['project_id'] if matches else "local"
                score = matches[0]['score'] if matches else 0.0
                
                print(f"   - Subtask: '{sub}' -> Assigned to [{assigned_node}] (Score: {score:.2f})")
                swarm_plan['subtasks'].append({
                    'intent': sub,
                    'assigned_node': assigned_node,
                    'confidence': score
                })
            return swarm_plan
        except Exception as e:
            print(f"⚠️ Swarm Assignment Failed: {e}")
            return None

    def _inject_components(self, intent, project_state, plan):
        """Phase 22: Component Injection Logic"""
        # Database
        if intent.requires_database and not project_state.has_models:
            plan['files_to_create'].extend(['models/__init__.py', 'models/base.py'])
            plan['dependencies'].append('sqlalchemy')
            plan['tasks'].append('Create database models')
        
        # API
        if intent.requires_api and not project_state.has_api:
            plan['files_to_create'].extend(['api/__init__.py', 'api/routes.py'])
            if intent.framework:
                plan['dependencies'].append(intent.framework)
            plan['tasks'].append('Implement API endpoints')
        
        # Auth
        if intent.requires_auth and not project_state.has_auth:
            plan['files_to_create'].extend(['auth/__init__.py', 'auth/jwt_handler.py'])
            plan['dependencies'].extend(['pyjwt', 'cryptography'])
            plan['tasks'].append('Implement authentication')
        
        # Testing
        if intent.requires_testing and not project_state.has_tests:
            plan['files_to_create'].extend(['tests/__init__.py', 'tests/test_main.py'])
            plan['dependencies'].append('pytest')
            plan['tasks'].append('Create test suite')
        
        # Entry Point
        if 'main.py' not in project_state.existing_files:
            plan['files_to_create'].append('main.py')

    def _run_synaptic_probe(self, intent, plan):
        """Phase 17: Synaptic Retrieval Logic"""
        try:
            from antigravity.core.knowledge_graph import FleetKnowledgeGraph
            from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
            
            gkg = FleetKnowledgeGraph.get_instance()
            matches = gkg.find_fleet_capability(intent.primary_goal, top_k=1)
            
            for match in matches:
                pid = match.get('project_id')
                score = match.get('score', 0)
                
                if pid and score > 0.95:
                    print(f"♻️ REDUNDANCY DETECTED: Local intent matches [{pid}] with score {score}")
                    TelemetryQueue.push_event(TelemetryEventType.STATE_CHANGE, {
                        'event': 'REDUNDANCY_DETECTED',
                        'intent': intent.primary_goal, 'match': pid, 'score': score
                    })
                    plan.setdefault('quarantine', []).append({
                        'reason': 'redundant_capability',
                        'replacement': f"fleet.{pid}",
                        'score': score
                    })
                
                if pid:
                    import_stmt = f"fleet.{pid}"
                    if import_stmt not in plan['dependencies']:
                        plan['dependencies'].append(import_stmt)
                        print(f"🧠 SYNAPSE: Auto-linked [{pid}] for '{intent.primary_goal}'")
        except Exception as e:
            print(f"⚠️ Synapse Probe Failed: {e}")
    
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
