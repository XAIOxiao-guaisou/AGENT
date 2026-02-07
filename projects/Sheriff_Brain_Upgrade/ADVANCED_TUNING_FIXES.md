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
            forbidden_examples.append(f"\n  反面教材 (Failed Implementation):\n```python\n{snippet}\n```\n")
    
    forbidden_constraints = "\n".join(forbidden_examples)
    
    prompt = f"""
🚫 结构性失败警告 (Structural Failure Warning)

你上一次生成的代码违反了架构约束。以下代码路径已被标记为"不可接受"，必须彻底废弃该实现思路：

{forbidden_constraints}

⚠️ 要求 (Requirements):
1. **更换实现拓扑** - 不仅仅是修改代码，而是使用完全不同的函数结构
2. **强制 Type Hints** - 所有函数必须有返回类型和参数类型注解
3. **强制错误处理** - 所有函数都必须包含 try-except 块
4. **禁用不安全函数** - 严禁使用 eval/exec 等不安全函数

📋 任务描述: {task.description}

💡 提示: 参考上面的"反面教材"，避免重复相同的设计模式。
"""
    
    return prompt


# ============================================================================
# Fix 3: Double-Circuit Sandbox with sys.modules Cleanup
# ============================================================================

async def execute_in_sandbox(
    self,
    code: str,
    test_code: Optional[str] = None
) -> Tuple[bool, str, Dict]:
    """
    Execute code in sandbox with resource limits
    
    Phase 19 Deep Optimization: Shadow run with validation
    Industrial-Grade Patch: Memory guardian thread
    Advanced Tuning: Double-circuit with sys.modules cleanup
    """
    if not self.sandbox_dir:
        await self.create_sandbox()
    
    print(f"\n🔒 Executing in sandbox (timeout: {self.quota.max_execution_time_seconds}s, memory: {self.quota.max_memory_mb}MB)")
    
    # ADVANCED TUNING: Context reset - clear project modules from cache
    self._cleanup_module_cache()
    
    # Write code to sandbox
    code_file = self.sandbox_dir / "generated_code.py"
    
    # ADVANCED TUNING: Add I/O isolation wrapper
    isolated_code = self._wrap_with_io_isolation(code)
    code_file.write_text(isolated_code, encoding='utf-8')
    
    # ... rest of execution code ...
    
    try:
        # ... existing execution code ...
        
        # ADVANCED TUNING: Cleanup after execution
        self._cleanup_module_cache()
        
        return success, output, metrics
        
    except SandboxMemoryExceeded as e:
        print(f"   💥 Sandbox memory limit exceeded")
        self._cleanup_module_cache()
        return False, str(e), {'error': 'memory_exceeded', 'limit_mb': self.quota.max_memory_mb}
    
    except Exception as e:
        self.memory_guardian_active = False
        self._cleanup_module_cache()
        print(f"   ❌ Sandbox execution error: {e}")
        return False, str(e), {'error': str(e)}

def _cleanup_module_cache(self):
    """
    Cleanup sys.modules to ensure task isolation
    
    Advanced Tuning: Double-circuit sandbox cleanup
    """
    import sys
    
    # Get project root name
    project_name = self.project_root.name
    
    # Remove all modules that belong to current project
    modules_to_remove = [
        mod_name for mod_name in sys.modules.keys()
        if project_name in mod_name or mod_name.startswith('generated_')
    ]
    
    for mod_name in modules_to_remove:
        del sys.modules[mod_name]
    
    if modules_to_remove:
        print(f"   🧹 Cleaned {len(modules_to_remove)} modules from cache")

def _wrap_with_io_isolation(self, code: str) -> str:
    """
    Wrap code with I/O isolation
    
    Advanced Tuning: Redirect stdout/stderr to memory buffer
    """
    wrapper = f"""
import sys
from io import StringIO

# Redirect stdout/stderr to memory buffer
_original_stdout = sys.stdout
_original_stderr = sys.stderr
sys.stdout = StringIO()
sys.stderr = StringIO()

try:
    # User code
{chr(10).join('    ' + line for line in code.split(chr(10)))}
    
    # Get output
    _output = sys.stdout.getvalue()
    _errors = sys.stderr.getvalue()
    
finally:
    # Restore original streams
    sys.stdout = _original_stdout
    sys.stderr = _original_stderr
    
    # Print captured output
    if _output:
        print(_output, end='')
    if _errors:
        print(_errors, end='', file=sys.stderr)
"""
    return wrapper


# ============================================================================
# Fix 4: Delta Audit for HEALING State
# ============================================================================

# In sheriff_strategist.py, modify request_semantic_audit:

async def request_semantic_audit(
    self,
    task: AtomicTask,
    code_snapshot: Dict[str, str],
    project_context: Dict
) -> Dict:
    """
    Request semantic audit from remote strategist
    
    Advanced Tuning: Delta audit with fix-attempt tracking
    """
    # Build request
    request = self._build_audit_request(
        compressed_context,
        project_context,
        architectural_anchor
    )
    
    # ADVANCED TUNING: Add delta audit metadata for HEALING state
    if task.state == TaskState.HEALING:
        request['delta_audit'] = {
            'is_healing': True,
            'fix_attempt_count': task.retry_count,
            'previous_errors': task.error_message,
            'healing_priority': 'HIGH' if task.retry_count >= 3 else 'NORMAL'
        }
        
        print(f"   🔧 Delta Audit: Fix attempt #{task.retry_count}")
        print(f"   🎯 Priority: {request['delta_audit']['healing_priority']}")
    
    # Send to remote LLM
    response = await self._send_to_remote_llm(request)
    
    return response


# ============================================================================
# Verification Tests
# ============================================================================

"""
Verification Checklist:

1. Cold-Start Test:
   - Set token_threshold_pause = 100 (low value)
   - Run mission with 3+ tasks
   - Verify PAUSED state at task 2
   - Kill process
   - Restart and verify continuation from task 3
   - Check .antigravity_state.json for dag_topology field

2. Structural Circuit Breaker Test:
   - Generate code without try-except
   - Verify forbidden_zones contains function name
   - Verify second prompt includes "反面教材"
   - Verify code snippet is captured

3. Compression Ratio Test:
   - Print original size vs compressed size
   - Verify >= 92% compression ratio
   - Check dependency-aware layering (1-hop full, 2-hop skeleton)

4. Sandbox Isolation Test:
   - Run 2 tasks that modify global variables
   - Verify task 2 doesn't see task 1's modifications
   - Check sys.modules cleanup logs
"""
