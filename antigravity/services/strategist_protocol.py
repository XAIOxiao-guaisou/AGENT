"""
Sheriff Strategist Protocol - 战略官协议
=====================================

Standardized protocol for Tier 3 remote semantic audit.
Tier 3 远程语义审计的标准化协议。

Phase 21 P2 Final Tuning (审查官 Enhancement):
- Sheriff-Audit-v1 protocol definition
- Structured JSON response format
- Logic score, architectural debt, race conditions, naming consistency
- No code patches, only expert advice
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class StrategistAuditRequest:
    """
    Request for strategist audit / 战略官审计请求
    
    Sheriff-Audit-v1 Protocol
    """
    project_name: str
    project_root: str
    code_snapshot: Dict[str, str]  # file_path -> code_content
    vibe_score: float
    test_coverage: float
    audit_timestamp: str
    request_id: str


@dataclass
class StrategistAuditResponse:
    """
    Response from strategist audit / 战略官审计响应
    
    Sheriff-Audit-v1 Protocol (审查官's 标准化报文)
    """
    logic_score: int  # 0-100
    approved: bool
    debt_found: List[str]  # Architectural debt items
    naming_vibe: str  # "consistent" | "inconsistent"
    expert_advice: str
    race_condition_report: Optional[List[Dict[str, str]]] = None
    architectural_concerns: Optional[List[str]] = None
    response_timestamp: str = ""
    request_id: str = ""
    
    def __post_init__(self):
        """Set timestamp if not provided / 设置时间戳"""
        if not self.response_timestamp:
            self.response_timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary / 转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON / 转换为 JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class StrategistProtocol:
    """
    Sheriff Strategist Protocol Handler / Sheriff 战略官协议处理器
    
    Phase 21 P2: 审查官's "远程战略官协议标准化"
    """
    
    PROTOCOL_VERSION = "Sheriff-Audit-v1"
    
    # Prompt template for remote strategist (审查官's 强制返回结构)
    REMOTE_AUDIT_PROMPT = """
作为 Sheriff Brain 的战略官 (Strategist)，你必须对以下代码进行"语义审查"。

**严禁返回代码补丁。**

你的职责是：
1. 评估代码的逻辑质量 (Logic Score: 0-100)
2. 识别架构债务 (Architectural Debt)
3. 检测潜在竞态条件 (Race Conditions)
4. 评估变量命名与项目语境的一致性 (Naming Consistency)

**你必须仅返回以下 JSON 结构，不得包含任何其他内容：**

```json
{{
  "logic_score": <int 0-100>,
  "approved": <bool>,
  "debt_found": [<list of architectural debt items>],
  "naming_vibe": "<consistent | inconsistent>",
  "expert_advice": "<string>",
  "race_condition_report": [
    {{
      "file": "<file_path>",
      "line": <line_number>,
      "description": "<description>"
    }}
  ],
  "architectural_concerns": [<list of concerns>]
}}
```

---

**项目信息：**
- 项目名称: {project_name}
- Vibe Score: {vibe_score:.1f}
- Test Coverage: {test_coverage:.1f}%

**代码快照：**
{code_snapshot}

---

**请严格按照上述 JSON 格式返回审计结果。**
"""
    
    def __init__(self):
        """Initialize protocol handler / 初始化协议处理器"""
        pass
    
    def create_audit_request(
        self,
        project_name: str,
        project_root: str,
        code_snapshot: Dict[str, str],
        vibe_score: float,
        test_coverage: float
    ) -> StrategistAuditRequest:
        """
        Create audit request / 创建审计请求
        
        Args:
            project_name: Project name / 项目名称
            project_root: Project root path / 项目根路径
            code_snapshot: Code snapshot / 代码快照
            vibe_score: Vibe score / Vibe 分数
            test_coverage: Test coverage / 测试覆盖率
            
        Returns:
            Audit request / 审计请求
        """
        request_id = f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return StrategistAuditRequest(
            project_name=project_name,
            project_root=project_root,
            code_snapshot=code_snapshot,
            vibe_score=vibe_score,
            test_coverage=test_coverage,
            audit_timestamp=datetime.now().isoformat(),
            request_id=request_id
        )
    
    def format_prompt(self, request: StrategistAuditRequest) -> str:
        """
        Format prompt for strategist / 格式化战略官提示词
        
        Args:
            request: Audit request / 审计请求
            
        Returns:
            Formatted prompt / 格式化提示词
        """
        # Format code snapshot
        code_snapshot_str = ""
        for file_path, code_content in request.code_snapshot.items():
            code_snapshot_str += f"\n### {file_path}\n```python\n{code_content}\n```\n"
        
        return self.REMOTE_AUDIT_PROMPT.format(
            project_name=request.project_name,
            vibe_score=request.vibe_score,
            test_coverage=request.test_coverage,
            code_snapshot=code_snapshot_str
        )
    
    def parse_response(self, response_text: str, request_id: str) -> Optional[StrategistAuditResponse]:
        """
        Parse strategist response / 解析战略官响应
        
        Args:
            response_text: Response text from LLM / LLM 响应文本
            request_id: Request ID / 请求 ID
            
        Returns:
            Parsed response or None if invalid / 解析后的响应或 None
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = response_text.strip()
            
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0].strip()
            elif '```' in json_str:
                json_str = json_str.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['logic_score', 'approved', 'debt_found', 'naming_vibe', 'expert_advice']
            for field in required_fields:
                if field not in data:
                    print(f"⚠️ Missing required field: {field}")
                    return None
            
            # Create response object
            response = StrategistAuditResponse(
                logic_score=int(data['logic_score']),
                approved=bool(data['approved']),
                debt_found=list(data['debt_found']),
                naming_vibe=str(data['naming_vibe']),
                expert_advice=str(data['expert_advice']),
                race_condition_report=data.get('race_condition_report'),
                architectural_concerns=data.get('architectural_concerns'),
                request_id=request_id
            )
            
            return response
        
        except Exception as e:
            print(f"❌ Failed to parse strategist response: {e}")
            print(f"   Response text: {response_text[:200]}...")
            return None
    
    def validate_response(self, response: StrategistAuditResponse) -> bool:
        """
        Validate strategist response / 验证战略官响应
        
        Args:
            response: Strategist response / 战略官响应
            
        Returns:
            True if valid / 如果有效则返回 True
        """
        # Check logic score range
        if not (0 <= response.logic_score <= 100):
            print(f"⚠️ Invalid logic_score: {response.logic_score}")
            return False
        
        # Check naming vibe
        if response.naming_vibe not in ['consistent', 'inconsistent']:
            print(f"⚠️ Invalid naming_vibe: {response.naming_vibe}")
            return False
        
        # Check expert advice is not empty
        if not response.expert_advice or len(response.expert_advice) < 10:
            print(f"⚠️ Expert advice too short or empty")
            return False
        
        return True
    
    def create_mock_response(self, request: StrategistAuditRequest) -> StrategistAuditResponse:
        """
        Create mock response for testing / 创建测试用的模拟响应
        
        Args:
            request: Audit request / 审计请求
            
        Returns:
            Mock response / 模拟响应
        """
        # Simple mock logic
        logic_score = int(request.vibe_score * 0.9)  # Slightly lower than vibe
        approved = logic_score >= 90
        
        return StrategistAuditResponse(
            logic_score=logic_score,
            approved=approved,
            debt_found=[] if approved else ["Mock architectural debt: Consider refactoring"],
            naming_vibe="consistent" if request.vibe_score >= 95 else "inconsistent",
            expert_advice=f"Mock expert advice: Project shows good quality (Vibe: {request.vibe_score:.1f})",
            race_condition_report=None,
            architectural_concerns=None if approved else ["Mock concern: Review async patterns"],
            request_id=request.request_id
        )


# Global protocol instance
strategist_protocol = StrategistProtocol()
