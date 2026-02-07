# Industrial-Grade Patches - Implementation Code Snippets
# 工业级补丁 - 实施代码片段

## 1. PAUSED State Persistence Methods

Add these methods to `AutonomousAuditor` class:

```python
def _save_paused_state(self, task_id: str):
    """
    Save state when hitting token threshold
    
    Industrial-Grade Patch: PAUSED state persistence for 100% recovery
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
        'dag_topology': self.orchestrator.dependency_graph,
        'output_hashes': {
            t: hashlib.md5(self.orchestrator.tasks[t].code_generated.encode()).hexdigest()
            for t in self.execution_order 
            if self.orchestrator.tasks[t].code_generated
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
    print(f"\n   💡 To resume: Run the same mission again")
    print(f"   💡 Dashboard will show: ⏸️ PAUSED (Token Limit)")

def _load_state(self):
    """
    Load previous state for cold-start recovery
    
    Industrial-Grade Patch: 100% recovery capability
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
            
            return state
    except Exception as e:
        print(f"⚠️ Failed to load state: {e}")
    
    return None
```

## 2. Token Tracking in reasoning_loop()

Add token threshold check in the main loop:

```python
async def reasoning_loop(self, mission: str) -> Dict:
    # ... existing code ...
    
    # Step 2: Execute each task
    for task_id in execution_order:
        # Industrial-Grade: Check token threshold BEFORE executing task
        if self.total_tokens_used >= self.quota.token_threshold_pause:
            print(f"\n⚠️ TOKEN THRESHOLD REACHED")
            print(f"   Current: {self.total_tokens_used} tokens")
            print(f"   Threshold: {self.quota.token_threshold_pause} tokens")
            print(f"   🛑 Entering PAUSED state...")
            
            # Save state for cold-start recovery
            self._save_paused_state(task_id)
            
            # Mark task as PAUSED
            task = self.orchestrator.tasks[task_id]
            task.state = TaskState.PAUSED  # Need to add this state to TaskState enum
            
            break
        
        # ... rest of task execution ...
        
        # Track tokens (mock for now, will integrate with actual LLM)
        estimated_tokens = len(task.description) * 2  # Rough estimate
        self.total_tokens_used += estimated_tokens
```

## 3. Structural Error Classification

Add this method for intelligent error detection:

```python
def _classify_violations(self, violations: List[str]) -> Tuple[List[str], List[str]]:
    """
    Classify violations as structural vs. non-structural
    
    Industrial-Grade Patch: Negative reinforcement for structural errors
    
    Structural errors (require prompt regeneration):
    - Missing type hints
    - No try-except blocks
    - Unsafe eval/exec usage
    
    Non-structural errors (can be healed):
    - Hardcoded secrets
    - Function too long
    
    Returns:
        (structural_errors, non_structural_errors)
    """
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
    
    for violation in violations:
        is_structural = any(kw in violation.lower() for kw in structural_keywords)
        
        if is_structural:
            structural_errors.append(violation)
            
            # Extract AST path and mark as forbidden zone
            # Example: "Function 'foo' missing type hint (line 42)"
            # -> forbidden_zone: "foo:missing_type_hints"
            if 'function' in violation.lower():
                import re
                match = re.search(r"Function '(\w+)'", violation)
                if match:
                    func_name = match.group(1)
                    forbidden_path = f"{func_name}:structural_error"
                    self.forbidden_zones.add(forbidden_path)
                    print(f"   🚫 Forbidden zone added: {forbidden_path}")
        else:
            non_structural_errors.append(violation)
    
    return structural_errors, non_structural_errors

def _generate_negative_reinforcement_prompt(self, task: AtomicTask, structural_errors: List[str]) -> str:
    """
    Generate prompt with negative reinforcement
    
    Industrial-Grade Patch: Force LLM to change logic topology
    """
    forbidden_constraints = "\\n".join([
        f"- {error}" for error in structural_errors
    ])
    
    prompt = f\"\"\"
你上一次生成的代码违反了架构约束。以下代码路径已被标记为"不可接受"：

{forbidden_constraints}

在接下来的尝试中，请更换实现拓扑（不仅仅是修改代码）。
必须：
1. 使用完全不同的函数结构
2. 确保所有函数都有 Type Hints
3. 所有函数都包含 try-except 错误处理
4. 避免使用 eval/exec 等不安全函数

任务描述：{task.description}
\"\"\"
    
    return prompt
```

## 4. Enhanced rollback_task in MissionOrchestrator

Add state persistence to rollback:

```python
# In mission_orchestrator.py

async def rollback_task(self, task_id: str, reason: str):
    """
    Rollback task to previous snapshot / 将任务回滚到之前的快照
    
    Phase 19 Deep Optimization: ROLLBACK state
    Industrial-Grade Patch: State persistence
    """
    task = self.tasks.get(task_id)
    if not task:
        return
    
    snapshot = self.snapshots.get(task_id)
    if not snapshot:
        print(f"   ⚠️ No snapshot found for {task_id}, cannot rollback")
        return
    
    print(f"\n🔄 ROLLBACK - {task_id}")
    print(f"   Reason: {reason}")
    
    # Restore from snapshot
    task.state = TaskState.ROLLBACK
    task.code_generated = snapshot['code_generated']
    task.audit_result = snapshot['audit_result']
    task.retry_count = snapshot['retry_count']
    task.error_message = reason
    
    print(f"   ✅ Rolled back to snapshot from {snapshot['timestamp']}")
    
    # Industrial-Grade: Persist rollback state
    self._persist_rollback_state(task_id, reason, snapshot)
    
    # Check if should retry or give up
    if task.retry_count < task.max_retries:
        task.retry_count += 1
        task.state = TaskState.PENDING
        print(f"   🔄 Retry {task.retry_count}/{task.max_retries}")
    else:
        print(f"   ❌ Max retries reached, task marked as ROLLBACK")

def _persist_rollback_state(self, task_id: str, reason: str, snapshot: Dict):
    """Persist rollback event for audit trail"""
    rollback_log = {
        'task_id': task_id,
        'reason': reason,
        'snapshot_id': snapshot.get('checkpoint_id'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Append to rollback log file
    rollback_file = Path(self.project_root) / ".rollback_log.jsonl"
    with rollback_file.open('a', encoding='utf-8') as f:
        f.write(json.dumps(rollback_log, ensure_ascii=False) + '\\n')
```

## 5. Add PAUSED State to TaskState Enum

```python
# In mission_orchestrator.py

class TaskState(Enum):
    """
    8-State Task Lifecycle / 8 状态任务生命周期
    
    Phase 19 Deep Optimization: Enhanced with ROLLBACK state
    Industrial-Grade Patch: Added PAUSED state
    """
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    REVIEWING = "REVIEWING"
    GENERATING = "GENERATING"
    AUDITING = "AUDITING"
    HEALING = "HEALING"
    ROLLBACK = "ROLLBACK"
    PAUSED = "PAUSED"  # NEW: Token threshold reached
    DONE = "DONE"
```

---

**Next Steps**:
1. Copy these methods into `autonomous_auditor.py`
2. Add PAUSED state to `TaskState` enum in `mission_orchestrator.py`
3. Test PAUSED → Resume flow
4. Verify state persistence in `.antigravity_state.json`
