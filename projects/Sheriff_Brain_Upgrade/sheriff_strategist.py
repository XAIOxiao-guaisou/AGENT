"""
Sheriff Strategist - 远程战略官
================================

Phase 19: Remote semantic audit and architectural review
阶段 19: 远程语义审计与架构审查

Deep Optimization Features:
- Architectural anchor & intent consistency (架构锚点与意图一致性)
- Semantic skeleton compression (语义骨架压缩)
- Decision reasoning (决策逻辑回传)
- Protocol version anchoring (协议版本锚点)
"""

import asyncio
import json
import hashlib
import ast
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class ArchitecturalAnchor:
    """
    Architectural Anchor - 架构锚点
    
    Phase 19 Deep Optimization: Intent consistency validation
    """
    mission_intent: str  # Original mission intent
    requirement_hash: str  # Hash of requirements
    architectural_constraints: List[str]  # Architectural rules
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Serialize anchor"""
        return {
            'mission_intent': self.mission_intent,
            'requirement_hash': self.requirement_hash,
            'architectural_constraints': self.architectural_constraints,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class SemanticSkeleton:
    """
    Semantic Skeleton - 语义骨架
    
    Phase 19 Deep Optimization: Compressed context for remote strategist
    """
    file_path: str
    functions: List[Dict]  # Function signatures + docstrings
    classes: List[Dict]  # Class structures
    imports: List[str]  # Import statements
    dependencies: List[str]  # Module dependencies
    
    def to_dict(self) -> Dict:
        """Serialize skeleton"""
        return {
            'file_path': self.file_path,
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports,
            'dependencies': self.dependencies
        }


class ContextCompressor:
    """
    Context Compressor - 上下文压缩器
    
    Phase 19 Deep Optimization: Semantic skeleton compression
    
    Extracts function signatures, docstrings, and class structures
    while removing implementation details to save tokens.
    """
    
    def compress_code(self, code: str, filepath: str) -> SemanticSkeleton:
        """
        Compress code to semantic skeleton / 将代码压缩为语义骨架
        
        Phase 19 Deep Optimization: AST-based skeleton extraction
        
        Args:
            code: Source code to compress
            filepath: File path for reference
            
        Returns:
            Semantic skeleton with signatures only
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return SemanticSkeleton(
                file_path=filepath,
                functions=[],
                classes=[],
                imports=[],
                dependencies=[]
            )
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            # Extract function signatures
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': ast.unparse(node.returns) if node.returns else None,
                    'docstring': ast.get_docstring(node),
                    'lineno': node.lineno
                }
                functions.append(func_info)
            
            # Extract class structures
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    'docstring': ast.get_docstring(node),
                    'lineno': node.lineno
                }
                classes.append(class_info)
            
            # Extract imports
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        
        skeleton = SemanticSkeleton(
            file_path=filepath,
            functions=functions,
            classes=classes,
            imports=imports,
            dependencies=[]  # TODO: Analyze dependencies
        )
        
        return skeleton
    
    def estimate_token_savings(self, original_code: str, skeleton: SemanticSkeleton) -> Dict:
        """
        Estimate token savings from compression / 估算压缩节省的 Token 数量
        
        Args:
            original_code: Original code
            skeleton: Compressed skeleton
            
        Returns:
            Savings metrics
        """
        original_chars = len(original_code)
        skeleton_chars = len(json.dumps(skeleton.to_dict()))
        
        # Rough token estimation (1 token ≈ 4 chars)
        original_tokens = original_chars // 4
        skeleton_tokens = skeleton_chars // 4
        
        savings = {
            'original_tokens': original_tokens,
            'skeleton_tokens': skeleton_tokens,
            'tokens_saved': original_tokens - skeleton_tokens,
            'compression_ratio': skeleton_tokens / original_tokens if original_tokens > 0 else 0
        }
        
        return savings


class SheriffStrategist:
    """
    Sheriff Strategist - 远程战略官
    
    Phase 19: Remote semantic audit and architectural review
    Phase 19 Deep Optimization: Context compression + decision reasoning
    
    Key Responsibilities:
    - Semantic audit via remote LLM
    - Architectural consistency validation
    - Context compression for token efficiency
    - Decision reasoning for knowledge transfer
    """
    
    def __init__(self, protocol_config_path: str):
        """
        Initialize sheriff strategist
        
        Args:
            protocol_config_path: Path to exchange protocol config
        """
        self.protocol_config = self._load_protocol_config(protocol_config_path)
        self.compressor = ContextCompressor()
        self.audit_history: List[Dict] = []
    
    def _load_protocol_config(self, config_path: str) -> Dict:
        """Load Sheriff-Exchange-v1 protocol configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return {
                'protocol_version': 'Sheriff-Exchange-v1',
                'response_format': {
                    'required_fields': ['approved', 'logic_score', 'expert_advice']
                }
            }
    
    async def request_semantic_audit(
        self,
        code_snapshot: Dict[str, str],
        project_context: Dict,
        architectural_anchor: ArchitecturalAnchor
    ) -> Dict:
        """
        Request semantic audit from remote strategist / 请求远程语义审计
        
        Phase 19 Deep Optimization: Full protocol implementation
        
        Args:
            code_snapshot: Dict of filepath -> code
            project_context: Project metadata
            architectural_anchor: Mission intent and constraints
            
        Returns:
            Audit response with decision reasoning
        """
        print("\n🌐 Sheriff Strategist - Requesting Semantic Audit")
        
        # Step 1: Compress context (semantic skeleton)
        compressed_context = await self._compress_context(code_snapshot)
        
        # Step 2: Build request per Sheriff-Exchange-v1 protocol
        request = self._build_audit_request(
            compressed_context,
            project_context,
            architectural_anchor
        )
        
        # Step 3: Send to remote LLM (mock for now)
        response = await self._send_to_remote_llm(request)
        
        # Step 4: Parse and validate response
        audit_result = self._parse_audit_response(response)
        
        # Step 5: Store audit history
        self.audit_history.append({
            'request': request,
            'response': audit_result,
            'timestamp': datetime.now().isoformat()
        })
        
        return audit_result
    
    async def _compress_context(self, code_snapshot: Dict[str, str]) -> Dict:
        """
        Compress code snapshot to semantic skeletons / 压缩代码快照为语义骨架
        
        Phase 19 Deep Optimization: Semantic skeleton compression
        
        Args:
            code_snapshot: Dict of filepath -> code
            
        Returns:
            Compressed context with skeletons
        """
        print(f"   🗜️ Compressing context ({len(code_snapshot)} files)")
        
        skeletons = {}
        total_original_tokens = 0
        total_skeleton_tokens = 0
        
        for filepath, code in code_snapshot.items():
            skeleton = self.compressor.compress_code(code, filepath)
            savings = self.compressor.estimate_token_savings(code, skeleton)
            
            skeletons[filepath] = skeleton.to_dict()
            total_original_tokens += savings['original_tokens']
            total_skeleton_tokens += savings['skeleton_tokens']
        
        tokens_saved = total_original_tokens - total_skeleton_tokens
        compression_ratio = total_skeleton_tokens / total_original_tokens if total_original_tokens > 0 else 0
        
        print(f"   ✅ Compression complete:")
        print(f"      Original: {total_original_tokens} tokens")
        print(f"      Compressed: {total_skeleton_tokens} tokens")
        print(f"      Saved: {tokens_saved} tokens ({(1-compression_ratio)*100:.1f}%)")
        
        return {
            'skeletons': skeletons,
            'compression_metrics': {
                'original_tokens': total_original_tokens,
                'compressed_tokens': total_skeleton_tokens,
                'tokens_saved': tokens_saved,
                'compression_ratio': compression_ratio
            }
        }
    
    def _build_audit_request(
        self,
        compressed_context: Dict,
        project_context: Dict,
        architectural_anchor: ArchitecturalAnchor
    ) -> Dict:
        """
        Build audit request per Sheriff-Exchange-v1 protocol / 构建审计请求
        
        Phase 19 Deep Optimization: Protocol version anchoring
        
        Args:
            compressed_context: Compressed code context
            project_context: Project metadata
            architectural_anchor: Architectural constraints
            
        Returns:
            Formatted request
        """
        request_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{architectural_anchor.requirement_hash}".encode()
        ).hexdigest()[:16]
        
        request = {
            'protocol_version': self.protocol_config.get('protocol_version', 'Sheriff-Exchange-v1'),
            'request_id': request_id,
            'request_type': 'semantic_audit',
            'project_context': {
                **project_context,
                'vibe_score': project_context.get('vibe_score', 0),
                'test_coverage': project_context.get('test_coverage', 0)
            },
            'local_analysis': {
                'compressed_context': compressed_context,
                'architectural_anchor': architectural_anchor.to_dict(),
                'requirement_hash': architectural_anchor.requirement_hash
            },
            'specific_questions': [
                "Is the implementation architecturally sound?",
                "Does the code align with the original mission intent?",
                "Are there any race conditions or logic flaws?",
                "Are naming conventions consistent?"
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"   📋 Request built: {request_id}")
        print(f"      Protocol: {request['protocol_version']}")
        print(f"      Requirement Hash: {architectural_anchor.requirement_hash[:8]}...")
        
        return request
    
    async def _send_to_remote_llm(self, request: Dict) -> Dict:
        """
        Send request to remote LLM / 发送请求到远程 LLM
        
        Phase 19: Mock implementation (will integrate with DeepSeek API)
        
        Args:
            request: Audit request
            
        Returns:
            LLM response
        """
        print(f"   🚀 Sending to remote strategist...")
        
        # TODO: Integrate with DeepSeek API
        # For now, return mock response
        await asyncio.sleep(0.5)  # Simulate network delay
        
        mock_response = {
            'request_id': request['request_id'],
            'logic_score': 88,
            'approved': True,
            'expert_advice': "Implementation is architecturally sound. Consider adding rate limiting for API endpoints.",
            'architectural_debt': [
                "Session management lacks proper cleanup mechanism"
            ],
            'race_condition_report': [],
            'naming_consistency': "consistent",
            'thought_chain': [
                "Analyzed function signatures and class structures",
                "Verified alignment with mission intent",
                "Checked for common anti-patterns",
                "Recommendation: Add rate limiting for production readiness"
            ],
            'recommended_actions': [
                "Add rate limiting middleware",
                "Implement session cleanup cron job"
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"   ✅ Response received (logic_score: {mock_response['logic_score']})")
        
        return mock_response
    
    def _parse_audit_response(self, response: Dict) -> Dict:
        """
        Parse and validate audit response / 解析并验证审计响应
        
        Args:
            response: Raw response from remote LLM
            
        Returns:
            Validated audit result
        """
        # Validate required fields per protocol
        required_fields = self.protocol_config.get('response_format', {}).get('required_fields', ['approved', 'logic_score', 'expert_advice'])
        
        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field in response: {field}")
        
        # Extract decision reasoning (Deep Optimization)
        thought_chain = response.get('thought_chain', [])
        
        print(f"\n   💭 Decision Reasoning:")
        for i, thought in enumerate(thought_chain, 1):
            print(f"      {i}. {thought}")
        
        return {
            'approved': response['approved'],
            'logic_score': response['logic_score'],
            'expert_advice': response['expert_advice'],
            'architectural_debt': response.get('architectural_debt', []),
            'race_conditions': response.get('race_condition_report', []),
            'naming_consistency': response.get('naming_consistency', 'unknown'),
            'recommended_actions': response.get('recommended_actions', []),
            'thought_chain': thought_chain,
            'timestamp': response['timestamp']
        }
    
    def validate_architectural_consistency(
        self,
        code: str,
        architectural_anchor: ArchitecturalAnchor
    ) -> Tuple[bool, List[str]]:
        """
        Validate code against architectural anchor / 验证代码与架构锚点的一致性
        
        Phase 19 Deep Optimization: Intent consistency check
        
        Args:
            code: Generated code
            architectural_anchor: Original mission intent
            
        Returns:
            (is_consistent, violations)
        """
        print(f"\n   🔍 Validating architectural consistency...")
        print(f"      Mission Intent: {architectural_anchor.mission_intent[:50]}...")
        
        violations = []
        
        # Check against architectural constraints
        for constraint in architectural_anchor.architectural_constraints:
            if constraint.lower() in ["no global variables", "no globals"]:
                if "global " in code:
                    violations.append(f"Violates constraint: {constraint}")
            
            elif constraint.lower() in ["must use async", "async required"]:
                if "async def" not in code:
                    violations.append(f"Violates constraint: {constraint}")
            
            elif constraint.lower() in ["type hints required", "must have type hints"]:
                # Check if functions have type hints
                try:
                    tree = ast.parse(code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if node.returns is None:
                                violations.append(f"Function '{node.name}' missing type hints (constraint: {constraint})")
                except:
                    pass
        
        is_consistent = len(violations) == 0
        
        if is_consistent:
            print(f"      ✅ Code is architecturally consistent")
        else:
            print(f"      ❌ Found {len(violations)} architectural violations")
            for v in violations:
                print(f"         - {v}")
        
        return is_consistent, violations


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize strategist
        config_path = Path(__file__).parent / "config" / "exchange_protocol.json"
        strategist = SheriffStrategist(
            protocol_config_path=str(config_path)
        )
        
        # Create architectural anchor
        anchor = ArchitecturalAnchor(
            mission_intent="创建用户管理 API with CRUD operations",
            requirement_hash=hashlib.md5(b"user_management_api_v1").hexdigest(),
            architectural_constraints=[
                "Must use async",
                "Type hints required",
                "No global variables"
            ]
        )
        
        # Mock code snapshot
        code_snapshot = {
            "api.py": '''
async def create_user(username: str, email: str) -> dict:
    """Create a new user"""
    try:
        user = {"username": username, "email": email}
        return {"status": "success", "user": user}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def get_user(user_id: int) -> dict:
    """Get user by ID"""
    try:
        # Mock user retrieval
        user = {"id": user_id, "username": "test"}
        return {"status": "success", "user": user}
    except Exception as e:
        return {"status": "error", "message": str(e)}
'''
        }
        
        project_context = {
            'project_name': 'user_management_api',
            'vibe_score': 92.5,
            'test_coverage': 85.0
        }
        
        # Request semantic audit
        result = await strategist.request_semantic_audit(
            code_snapshot,
            project_context,
            anchor
        )
        
        print(f"\n📊 Audit Result:")
        print(f"   Approved: {result['approved']}")
        print(f"   Logic Score: {result['logic_score']}")
        print(f"   Expert Advice: {result['expert_advice']}")
        
        # Validate architectural consistency
        strategist.validate_architectural_consistency(
            code_snapshot["api.py"],
            anchor
        )
    
    asyncio.run(main())