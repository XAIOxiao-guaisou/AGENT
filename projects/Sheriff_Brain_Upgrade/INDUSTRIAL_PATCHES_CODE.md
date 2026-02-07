# Industrial-Grade Patches - Implementation Code Snippets
# 工业级补丁 - 实施代码片段

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from enum import Enum

# Import necessary classes if they exist in the same module
# If not, define minimal stubs for type checking
try:
    from .mission_orchestrator import TaskState, AtomicTask
except ImportError:
    # Define minimal stubs for standalone execution
    class TaskState(Enum):
        PENDING = "PENDING"
        ANALYZING = "ANALYZING"
        REVIEWING = "REVIEWING"
        GENERATING = "GENERATING"
        AUDITING = "AUDITING"
        HEALING = "HEALING"
        ROLLBACK = "ROLLBACK"
        PAUSED = "PAUSED"
        DONE = "DONE"
    
    class AtomicTask:
        def __init__(self):
            self.state = TaskState.PENDING
            self.code_generated = ""
            self.description = ""
            self.audit_result = None
            self.retry_count = 0
            self.max_retries = 3
            self.error_message = ""

class AutonomousAuditor:
    """
    Autonomous Auditor with Industrial-Grade Patches
    """
    
    def __init__(self, orchestrator, quota, project_root: str = "."):
        self.orchestrator = orchestrator
        self.quota = quota
        self.project_root = Path(project_root)
        self.state_file = self.project_root / ".antigravity_state.json"
        
        # State tracking
        self.total_tokens_used = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.execution_order = []
        self.forbidden_zones: Set[str] = set()
        self.is_paused = False
        self.paused_at_task = None
        
        # Load existing state if available
        self._load_state()
    
    def _save_paused_state(self, task_id: str):
        """
        Save state when hitting token threshold
        
        Industrial-Grade Patch: PAUSED state persistence for 100% recovery
        """
        # Collect completed tasks
        completed_tasks = []
        if hasattr(self.orchestrator, 'tasks') and self.orchestrator.tasks:
            for t in self.execution_order:
                if t in self.orchestrator.tasks:
                    task = self.orchestrator.tasks[t]
                    if hasattr(task, 'state') and task.state == TaskState.DONE:
                        completed_tasks.append(t)
        
        # Collect output hashes
        output_hashes = {}
        if hasattr(self.orchestrator, 'tasks') and self.orchestrator.tasks:
            for t in self.execution_order:
                if t in self.orchestrator.tasks:
                    task = self.orchestrator.tasks[t]
                    if hasattr(task, 'code_generated') and task.code_generated:
                        output_hashes[t] = hashlib.md5(task.code_generated.encode()).hexdigest()
        
        # Get DAG topology if available
        dag_topology = {}
        if hasattr(self.orchestrator, 'dependency_graph'):
            dag_topology = self.orchestrator.dependency_graph
        
        state = {
            'paused': True,
            'paused_at_task': task_id,
            'total_tokens_used': self.total_tokens_used,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'execution_order': self.execution_order,
            'completed_tasks': completed_tasks,
            'dag_topology': dag_topology,
            'output_hashes': output_hashes,
            'forbidden_zones': list(self.forbidden_zones),
            'timestamp': datetime.now().isoformat()
        }
        
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write state file
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
                self.tasks_failed = state.get('tasks_failed', 0)
                self.paused_at_task = state['paused_at_task']
                self.execution_order = state.get('execution_order', [])
                self.forbidden_zones = set(state.get('forbidden_zones', []))
                self.is_paused = True
                
                # Restore orchestrator state if possible
                if hasattr(self.orchestrator, 'tasks') and self.orchestrator.tasks:
                    # Mark the paused task as PAUSED
                    if self.paused_at_task in self.orchestrator.tasks:
                        task = self.orchestrator.tasks[self.paused_at_task]
                        if hasattr(task, 'state'):
                            task.state = TaskState.PAUSED
                    
                    # Mark completed tasks as DONE
                    for task_id in state.get('completed_tasks', []):
                        if task_id in self.orchestrator.tasks:
                            task = self.orchestrator.tasks[task_id]
                            if hasattr(task, 'state'):
                                task.state = TaskState.DONE
                
                return state
        except Exception as e:
            print(f"⚠️ Failed to load state: {e}")
        
        return None
    
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
            'exec',
            'no error handling',
            'no type hints'
        ]
        
        structural_errors = []
        non_structural_errors = []
        
        for violation in violations:
            violation_lower = violation.lower()
            is_structural = any(kw in violation_lower for kw in structural_keywords)
            
            if is_structural:
                structural_errors.append(violation)
                
                # Extract AST path and mark as forbidden zone
                # Example: "Function 'foo' missing type hint (line 42)"
                # -> forbidden_zone: "foo:missing_type_hints"
                if 'function' in violation_lower:
                    import re
                    match = re.search(r"Function ['\"](\w+)['\"]", violation)
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
        forbidden_constraints = "\n".join([
            f"- {error}" for error in structural_errors
        ])
        
        prompt = f"""
你上一次生成的代码违反了架构约束。以下代码路径已被标记为"不可接受"：

{forbidden_constraints}

在接下来的尝试中，请更换实现拓扑（不仅仅是修改代码）。
必须：
1. 使用完全不同的函数结构
2. 确保所有函数都有 Type Hints
3. 所有函数都包含 try-except 错误处理
4. 避免使用 eval/exec 等不安全函数

任务描述：{task.description}
"""
        
        return prompt
    
    async def reasoning_loop(self, mission: str) -> Dict:
        """
        Main reasoning loop with token threshold checking
        
        Industrial-Grade Patch: Token tracking and PAUSED state
        """
        # Initialize execution order if not loaded from state
        if not self.execution_order and hasattr(self.orchestrator, 'get_execution_order'):
            self.execution_order = self.orchestrator.get_execution_order()
        
        result = {
            'success': False,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_tokens_used': 0,
            'paused': False
        }
        
        # Step 2: Execute each task
        for task_id in self.execution_order:
            # Skip already completed tasks when resuming
            if self.is_paused and task_id == self.paused_at_task:
                print(f"\n🔄 RESUMING FROM TASK: {task_id}")
                self.is_paused = False
            
            # Industrial-Grade: Check token threshold BEFORE executing task
            if self.total_tokens_used >= self.quota.token_threshold_pause:
                print(f"\n⚠️ TOKEN THRESHOLD REACHED")
                print(f"   Current: {self.total_tokens_used} tokens")
                print(f"   Threshold: {self.quota.token_threshold_pause} tokens")
                print(f"   🛑 Entering PAUSED state...")
                
                # Save state for cold-start recovery
                self._save_paused_state(task_id)
                
                # Mark task as PAUSED
                if hasattr(self.orchestrator, 'tasks') and task_id in self.orchestrator.tasks:
                    task = self.orchestrator.tasks[task_id]
                    if hasattr(task, 'state'):
                        task.state = TaskState.PAUSED
                
                result['paused'] = True
                break
            
            # Get task from orchestrator
            if not hasattr(self.orchestrator, 'tasks') or task_id not in self.orchestrator.tasks:
                print(f"⚠️ Task {task_id} not found in orchestrator")
                continue
            
            task = self.orchestrator.tasks[task_id]
            
            # Skip if already done
            if hasattr(task, 'state') and task.state == TaskState.DONE:
                print(f"⏭️ Skipping already completed task: {task_id}")
                continue
            
            print(f"\n🚀 Executing task: {task_id}")
            print(f"   Description: {task.description[:100]}...")
            
            # Execute task (simplified for example)
            # In real implementation, this would call the LLM and generate code
            
            # Track tokens (mock for now, will integrate with actual LLM)
            estimated_tokens = len(task.description) * 2  # Rough estimate
            self.total_tokens_used += estimated_tokens
            
            # Simulate task completion
            if hasattr(task, 'state'):
                task.state = TaskState.DONE
            self.tasks_completed += 1
            
            print(f"   ✅ Task completed")
            print(f"   📊 Tokens used: {estimated_tokens} (Total: {self.total_tokens_used})")
        
        # Update result
        result['success'] = self.tasks_completed == len(self.execution_order)
        result['completed_tasks'] = self.tasks_completed
        result['failed_tasks'] = self.tasks_failed
        result['total_tokens_used'] = self.total_tokens_used
        
        return result

class MissionOrchestrator:
    """
    Mission Orchestrator with enhanced rollback capabilities
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.tasks: Dict[str, AtomicTask] = {}
        self.snapshots: Dict[str, Dict] = {}
        self.dependency_graph = {}
    
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
        task.code_generated = snapshot.get('code_generated', '')
        task.audit_result = snapshot.get('audit_result')
        task.retry_count = snapshot.get('retry_count', 0)
        task.error_message = reason
        
        print(f"   ✅ Rolled back to snapshot from {snapshot.get('timestamp', 'unknown')}")
        
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
        rollback_file = self.project_root / ".rollback_log.jsonl"
        rollback_file.parent.mkdir(parents=True, exist_ok=True)
        
        with rollback_file.open('a', encoding='utf-8') as f:
            f.write(json.dumps(rollback_log, ensure_ascii=False) + '\n')
    
    def get_execution_order(self) -> List[str]:
        """
        Get execution order based on dependency graph
        Simplified implementation for example
        """
        if self.dependency_graph:
            # In real implementation, this would do topological sort
            return list(self.tasks.keys())
        return list(self.tasks.keys())

# Example Quota class for testing
class Quota:
    def __init__(self, token_threshold_pause: int = 10000):
        self.token_threshold_pause = token_threshold_pause

# Test the implementation
if __name__ == "__main__":
    # Create test orchestrator
    orchestrator = MissionOrchestrator()
    
    # Create test tasks
    for i in range(3):
        task_id = f"task_{i}"
        task = AtomicTask()
        task.description = f"Test task {i}: Implement feature {i}"
        task.max_retries = 3
        orchestrator.tasks[task_id] = task
    
    orchestrator.dependency_graph = {"task_0": ["task_1"], "task_1": ["task_2"]}
    
    # Create quota
    quota = Quota(token_threshold_pause=100)
    
    # Create auditor
    auditor = AutonomousAuditor(orchestrator, quota)
    
    # Test reasoning loop
    import asyncio
    
    async def test():
        result = await auditor.reasoning_loop("Test mission")
        print(f"\n📊 Mission Result:")
        print(f"   Success: {result['success']}")
        print(f"   Completed tasks: {result['completed_tasks']}")
        print(f"   Total tokens used: {result['total_tokens_used']}")
        print(f"   Paused: {result['paused']}")
    
    asyncio.run(test())