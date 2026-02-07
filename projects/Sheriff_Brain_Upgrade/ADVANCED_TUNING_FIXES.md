"""
Industrial-Grade Patches - Advanced Tuning Fixes
工业级补丁 - 高级调优修正

Based on reviewer's deep analysis, these fixes address:
1. DAG serialization risk (networkx.DiGraph → JSON)
2. Negative reinforcement precision (AST code snippets)
3. Double-circuit sandbox cleanup (sys.modules isolation)
4. Delta audit for HEALING state
"""

# ============================================================================
# Fix 1: DAG Serialization with networkx
# ============================================================================

# Add to imports in autonomous_auditor.py:
import networkx as nx
import json
import hashlib
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from .task import AtomicTask, TaskState
from .sandbox import SandboxMemoryExceeded

# Modified _save_paused_state method:
def _save_paused_state(self, task_id: str):
    """
    Save state when hitting token threshold
    
    Industrial-Grade Patch: PAUSED state persistence for 100% recovery
    Advanced Tuning: Fixed DAG serialization using networkx.node_link_data
    """
    state = {
        'paused': True,
        'paused_at_task': task_id,
        'total_tokens_used': self.total_tokens_used,
        'tasks_completed': self.tasks_completed,
        'tasks_failed': self.tasks_failed,
        'execution_order': self.execution_order,
        'completed_tasks': [
            t for t in self.execution_order 
            if self.orchestrator.tasks[t].state == TaskState.DONE
        ],
        # FIXED: Use networkx serialization instead of direct dict
        'dag_topology': nx.node_link_data(self.orchestrator.dependency_graph) if hasattr(self.orchestrator, 'dependency_graph') else {},
        'output_hashes': {
            t: hashlib.md5(self.orchestrator.tasks[t].code_generated.encode()).hexdigest()
            for t in self.execution_order 
            if self.orchestrator.tasks.get(t) and self.orchestrator.tasks[t].code_generated
        },
        'forbidden_zones': list(self.forbidden_zones),
        'timestamp': datetime.now().isoformat()
    }
    
    self.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print(f"\n⏸️ PAUSED STATE SAVED")
    print(f"   File: {self.state_file}")
    print(f"   Paused at: {task_id}")
    print(f"   Tokens used: {self.total_tokens_used}/{self.quota.token_threshold_pause}")
    print(f"   Completed: {self.tasks_completed} tasks")
    print(f"   DAG nodes: {len(state['dag_topology'].get('nodes', []))}")
    print(f"\n   💡 To resume: Run the same mission again")
    print(f"   💡 Dashboard will show: ⏸️ PAUSED (Token Limit)")

# Modified _load_state method:
def _load_state(self):
    """
    Load previous state for cold-start recovery
    
    Industrial-Grade Patch: 100% recovery capability
    Advanced Tuning: Restore DAG from networkx serialization
    """
    if not self.state_file.exists():
        return None
    
    try:
        state = json.loads(self.state_file.read_text(encoding='utf-8'))
        
        if state.get('paused'):
            print(f"\n🔄 RESUMING FROM PAUSED STATE")
            print(f"   Paused at: {state['paused_at_task']}")
            print(f"   Completed: {state['tasks_completed']} tasks")
            print(f"   Tokens used: {state['total_tokens_used']}")
            print(f"   Timestamp: {state['timestamp']}")
            
            # Restore state
            self.total_tokens_used = state['total_tokens_used']
            self.tasks_completed = state['tasks_completed']
            self.tasks_failed = state['tasks_failed']
            self.paused_at_task = state['paused_at_task']
            self.execution_order = state.get('execution_order', [])
            self.forbidden_zones = set(state.get('forbidden_zones', []))
            self.is_paused = True
            
            # FIXED: Restore DAG from networkx serialization
            if 'dag_topology' in state and state['dag_topology']:
                try:
                    self.orchestrator.dependency_graph = nx.node_link_graph(state['dag_topology'])
                    print(f"   ✅ DAG restored: {len(state['dag_topology'].get('nodes', []))} nodes")
                except Exception as e:
                    print(f"   ⚠️ Failed to restore DAG: {e}")
            
            return state
    except Exception as e:
        print(f"⚠️ Failed to load state: {e}")
    
    return None


# ============================================================================
# Fix 2: Negative Reinforcement with AST Code Snippets
# ============================================================================

def _classify_violations(self, violations: List[str], code: str) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Classify violations as structural vs. non-structural
    
    Industrial-Grade Patch: Negative reinforcement for structural errors
    Advanced Tuning: Extract code snippets for precise feedback
    
    Args:
        violations: List of violation messages
        code: Generated code to extract snippets from
    
    Returns:
        (structural_errors, non_structural_errors, code_snippets)
    """
    import re
    import ast
    
    structural_keywords = [
        'missing type hint',
        'missing return type',
        'lacks try-except',
        'unsafe function',
        'eval',
        'exec'
    ]
    
    structural_errors = []
    non_structural_errors = []
    code_snippets = {}  # {function_name: code_snippet}
    
    # Parse code to extract function definitions
    try:
        tree = ast.parse(code)
        function_map = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract function source code
                lines = code.split('\n')
                func_start = node.lineno - 1
                func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start + 10
                func_code = '\n'.join(lines[func_start:func_end])
                function_map[node.name] = func_code
    except:
        function_map = {}
    
    for violation in violations:
        is_structural = any(kw in violation.lower() for kw in structural_keywords)
        
        if is_structural:
            structural_errors.append(violation)
            
            # Extract function name and get code snippet
            match = re.search(r"[Ff]unction '(\w+)'", violation)
            if match:
                func_name = match.group(1)
                forbidden_path = f"{func_name}:structural_error"
                self.forbidden_zones.add(forbidden_path)
                
                # Get code snippet if available
                if func_name in function_map:
                    code_snippets[func_name] = function_map[func_name]
                    print(f"   🚫 Forbidden zone added: {forbidden_path}")
                    print(f"      Code snippet captured ({len(function_map[func_name])} chars)")
        else:
            non_structural_errors.append(violation)
    
    return structural_errors, non_structural_errors, code_snippets

def _generate_negative_reinforcement_prompt(
    self, 
    task: AtomicTask, 
    structural_errors: List[str],
    code_snippets: Dict[str, str]
) -> str:
    """
    Generate prompt with negative reinforcement
    
    Industrial-Grade Patch: Force LLM to change logic topology
    Advanced Tuning: Include failed code snippets as counter-examples
    """
    # Build forbidden constraints with code examples
    forbidden_examples = []
    for error in structural_errors:
        forbidden_examples.append(f"- {error}")
        
        # Add code snippet if available
        import re
        match = re.search(r"[Ff]unction '(\w+)'", error)
        if match and match.group(1) in code_snippets:
            func_name = match.group(1)
            snippet = code_snippets[func_name]
            forbidden_examples.append(f"\n  反面教材 (Failed Implementation):\n