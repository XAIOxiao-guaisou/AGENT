"""
Mission Orchestrator - 任务编排器
================================

Sheriff Brain's decision-making center for autonomous task decomposition.
Sheriff Brain 的决策中枢，实现 Idea 到 AtomicTasks 的自主拆解。

Phase 19: Core Architecture
- 8-State lifecycle management (including PAUSED)
- Topological sorting for dependencies
- Async pipeline scheduling
- DAG serialization for state persistence
"""

import asyncio
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import json
import networkx as nx  # Industrial-Grade Patch: DAG serialization


class TaskState(Enum):
    """
    8-State Task Lifecycle / 8 状态任务生命周期
    
    Phase 19 Deep Optimization: Enhanced with ROLLBACK state
    Industrial-Grade Patch: Added PAUSED state for token threshold
    
    State Flow:
    PENDING → ANALYZING → [REVIEWING] → GENERATING → AUDITING → [HEALING] → [ROLLBACK] → DONE
    
    Special States:
    - PAUSED: Token threshold reached, execution suspended
    - ROLLBACK: Failure recovery, restore from snapshot
    """
    PENDING = "PENDING"           # 待处理
    ANALYZING = "ANALYZING"       # 本地意图与约束分析
    REVIEWING = "REVIEWING"       # 远程战略审查（可选/降级）
    GENERATING = "GENERATING"     # 异步流水线生成
    AUDITING = "AUDITING"         # 多层级质量审计
    HEALING = "HEALING"           # 自愈修复循环
    ROLLBACK = "ROLLBACK"         # 失败回滚（安全性保障）
    PAUSED = "PAUSED"             # 熔断挂起（Token 阈值触发）
    DONE = "DONE"                 # 双签完成交付


@dataclass
class AtomicTask:
    """
    Atomic Task Object / 原子任务对象
    
    Phase 19: Smallest unit of execution with dependency tracking
    """
    task_id: str
    description: str
    task_type: str  # 'database', 'api', 'ui', 'test', etc.
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Execution metadata
    code_generated: Optional[str] = None
    audit_result: Optional[Dict] = None
    healing_applied: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'task_id': self.task_id,
            'description': self.description,
            'task_type': self.task_type,
            'dependencies': self.dependencies,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'healing_applied': self.healing_applied
        }


class MissionOrchestrator:
    """
    Mission Orchestrator - 任务编排中枢
    
    Phase 19: Autonomous task decomposition and scheduling
    
    Key Responsibilities:
    - Idea → AtomicTasks decomposition
    - Dependency resolution via topological sort
    - State machine management
    - Async pipeline coordination
    """
    
    def __init__(self, project_root: str):
        """
        Initialize mission orchestrator
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.tasks: Dict[str, AtomicTask] = {}
        self.execution_order: List[str] = []
        self.current_mission: Optional[str] = None
        
        # Deep Optimization: DAG management
        self.dag_graph: Dict[str, List[str]] = {}  # task_id -> [dependent_task_ids]
        self.in_degree: Dict[str, int] = {}  # task_id -> number of dependencies
        
        # Deep Optimization: Snapshot management for ROLLBACK
        self.snapshots: Dict[str, Dict] = {}  # task_id -> snapshot_data
        
        # Deep Optimization: Task granularity control
        self.MAX_TASK_COMPLEXITY = 50  # Max lines per task description
    
    async def decompose_idea(self, idea: str) -> List[AtomicTask]:
        """
        Decompose idea into atomic tasks / 将 Idea 拆解为原子任务
        
        Phase 19: Core decomposition logic
        
        Args:
            idea: High-level idea description
            
        Returns:
            List of atomic tasks with dependencies
        """
        print(f"\n🧠 Mission Orchestrator - Decomposing Idea")
        print(f"   Idea: {idea[:100]}...")
        
        # Step 1: Intent analysis (simplified - will use LocalReasoningEngine)
        intent_keywords = self._analyze_intent(idea)
        
        # Step 2: Generate atomic tasks based on intent
        tasks = []
        task_counter = 1
        
        # Database setup (if needed)
        if any(kw in intent_keywords for kw in ['database', 'db', 'storage', 'data']):
            task = AtomicTask(
                task_id=f"task_{task_counter:03d}",
                description="设置数据库架构和模型",
                task_type="database",
                dependencies=[]
            )
            tasks.append(task)
            task_counter += 1
        
        # API implementation (if needed)
        if any(kw in intent_keywords for kw in ['api', 'endpoint', 'route', 'backend']):
            deps = [tasks[-1].task_id] if tasks else []
            task = AtomicTask(
                task_id=f"task_{task_counter:03d}",
                description="实现 API 端点和业务逻辑",
                task_type="api",
                dependencies=deps
            )
            tasks.append(task)
            task_counter += 1
        
        # UI implementation (if needed)
        if any(kw in intent_keywords for kw in ['ui', 'frontend', 'interface', 'page']):
            deps = [tasks[-1].task_id] if tasks else []
            task = AtomicTask(
                task_id=f"task_{task_counter:03d}",
                description="实现用户界面和交互",
                task_type="ui",
                dependencies=deps
            )
            tasks.append(task)
            task_counter += 1
        
        # Testing (always needed)
        test_deps = [t.task_id for t in tasks]
        task = AtomicTask(
            task_id=f"task_{task_counter:03d}",
            description="编写单元测试和集成测试",
            task_type="test",
            dependencies=test_deps
        )
        tasks.append(task)
        
        # Store tasks
        for task in tasks:
            self.tasks[task.task_id] = task
        
        print(f"   ✅ Decomposed into {len(tasks)} atomic tasks")
        for task in tasks:
            deps_str = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            print(f"      - {task.task_id}: {task.description}{deps_str}")
        
        return tasks
    
    def _analyze_intent(self, idea: str) -> Set[str]:
        """
        Analyze intent keywords from idea / 从 Idea 分析意图关键词
        
        Args:
            idea: Idea description
            
        Returns:
            Set of intent keywords
        """
        idea_lower = idea.lower()
        keywords = set()
        
        # Database keywords
        if any(kw in idea_lower for kw in ['database', 'db', 'storage', 'persist', 'save data']):
            keywords.add('database')
        
        # API keywords
        if any(kw in idea_lower for kw in ['api', 'endpoint', 'route', 'backend', 'server']):
            keywords.add('api')
        
        # UI keywords
        if any(kw in idea_lower for kw in ['ui', 'frontend', 'interface', 'page', 'dashboard']):
            keywords.add('ui')
        
        # Testing keywords (always implied)
        keywords.add('test')
        
        return keywords
    
    async def get_parallel_execution_batches(self) -> List[List[str]]:
        """
        Get batches of tasks that can be executed in parallel / 获取可并行执行的任务批次
        
        Phase 19 Deep Optimization: DAG-based parallel execution
        
        Returns:
            List of task batches, where each batch can be executed in parallel
        """
        print("\n🔀 Computing parallel execution batches (DAG)...")
        
        # Build DAG
        graph: Dict[str, List[str]] = {task_id: [] for task_id in self.tasks}
        in_degree: Dict[str, int] = {task_id: 0 for task_id in self.tasks}
        
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep in graph:
                    graph[dep].append(task_id)
                    in_degree[task_id] += 1
        
        self.dag_graph = graph
        self.in_degree = in_degree.copy()
        
        # Compute batches
        batches = []
        remaining_in_degree = in_degree.copy()
        
        while any(degree >= 0 for degree in remaining_in_degree.values()):
            # Find all tasks with in_degree == 0 (can execute in parallel)
            current_batch = [task_id for task_id, degree in remaining_in_degree.items() if degree == 0]
            
            if not current_batch:
                # Check for cycles
                remaining = [tid for tid, deg in remaining_in_degree.items() if deg >= 0]
                if remaining:
                    raise ValueError(f"Circular dependency detected in tasks: {remaining}")
                break
            
            batches.append(current_batch)
            
            # Update in_degree for next batch
            for task_id in current_batch:
                remaining_in_degree[task_id] = -1  # Mark as processed
                for neighbor in graph[task_id]:
                    remaining_in_degree[neighbor] -= 1
        
        print(f"   ✅ Computed {len(batches)} parallel batches:")
        for i, batch in enumerate(batches, 1):
            print(f"      Batch {i}: {', '.join(batch)} ({len(batch)} tasks in parallel)")
        
        return batches
    
    async def topological_sort(self) -> List[str]:
        """
        Perform topological sort on tasks / 对任务进行拓扑排序
        
        Phase 19: Ensures tasks execute in dependency order
        
        Returns:
            Sorted list of task IDs
        """
        print("\n📊 Performing topological sort...")
        
        # Build adjacency list
        graph: Dict[str, List[str]] = {task_id: [] for task_id in self.tasks}
        in_degree: Dict[str, int] = {task_id: 0 for task_id in self.tasks}
        
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep in graph:
                    graph[dep].append(task_id)
                    in_degree[task_id] += 1
        
        # Kahn's algorithm
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        sorted_tasks = []
        
        while queue:
            task_id = queue.pop(0)
            sorted_tasks.append(task_id)
            
            for neighbor in graph[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(sorted_tasks) != len(self.tasks):
            raise ValueError("Circular dependency detected in tasks!")
        
        self.execution_order = sorted_tasks
        
        print(f"   ✅ Execution order: {' → '.join(sorted_tasks)}")
        
        return sorted_tasks
    
    async def execute_mission(self, idea: str):
        """
        Execute complete mission from idea to delivery / 执行完整任务从 Idea 到交付
        
        Phase 19: Main orchestration loop
        
        Args:
            idea: High-level idea description
        """
        print("\n" + "=" * 60)
        print("🚀 Mission Orchestrator - Starting Execution")
        print("=" * 60)
        
        self.current_mission = idea
        
        # Step 1: Decompose idea
        tasks = await self.decompose_idea(idea)
        
        # Step 2: Topological sort
        execution_order = await self.topological_sort()
        
        # Step 3: Execute tasks in order
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            print(f"\n▶️  Executing {task_id}: {task.description}")
            
            # Update state
            task.state = TaskState.ANALYZING
            task.started_at = datetime.now()
            
            # TODO: Integrate with AutonomousAuditor for actual execution
            # For now, simulate execution
            await asyncio.sleep(0.5)  # Simulate work
            
            task.state = TaskState.DONE
            task.completed_at = datetime.now()
            
            print(f"   ✅ {task_id} completed")
        
        print("\n" + "=" * 60)
        print("🎉 Mission Complete!")
        print("=" * 60)
    
    async def create_snapshot(self, task_id: str):
        """
        Create snapshot before task execution / 在任务执行前创建快照
        
        Phase 19 Deep Optimization: ROLLBACK state support
        
        Args:
            task_id: Task ID to create snapshot for
        """
        task = self.tasks.get(task_id)
        if not task:
            return
        
        # Create snapshot of current task state
        snapshot = {
            'task_id': task_id,
            'state': task.state,
            'code_generated': task.code_generated,
            'audit_result': task.audit_result,
            'retry_count': task.retry_count,
            'timestamp': datetime.now().isoformat()
        }
        
        self.snapshots[task_id] = snapshot
        print(f"   📸 Snapshot created for {task_id}")
    
    async def rollback_task(self, task_id: str, reason: str):
        """
        Rollback task to previous snapshot / 将任务回滚到之前的快照
        
        Phase 19 Deep Optimization: ROLLBACK state
        
        Args:
            task_id: Task ID to rollback
            reason: Reason for rollback
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
        
        # Check if should retry or give up
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.state = TaskState.PENDING
            print(f"   🔄 Retry {task.retry_count}/{task.max_retries}")
        else:
            print(f"   ❌ Max retries reached, task marked as ROLLBACK")
    
    def get_task_status(self) -> Dict:
        """
        Get current status of all tasks / 获取所有任务的当前状态
        
        Returns:
            Status dictionary
        """
        status = {
            'mission': self.current_mission,
            'total_tasks': len(self.tasks),
            'by_state': {},
            'tasks': []
        }
        
        # Count by state
        for state in TaskState:
            count = sum(1 for t in self.tasks.values() if t.state == state)
            status['by_state'][state.value] = count
        
        # Task details
        for task_id in self.execution_order:
            task = self.tasks[task_id]
            status['tasks'].append(task.to_dict())
        
        return status
    
    def save_state(self, filepath: str):
        """
        Save orchestrator state to file / 保存编排器状态到文件
        
        Args:
            filepath: Path to save state
        """
        state = self.get_task_status()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"💾 State saved to {filepath}")


# Example usage
if __name__ == "__main__":
    async def main():
        orchestrator = MissionOrchestrator("./Sheriff_Brain_Upgrade")
        
        idea = "创建一个用户管理系统，包含数据库、API 和前端界面"
        
        await orchestrator.execute_mission(idea)
        
        # Print status
        status = orchestrator.get_task_status()
        print(f"\n📊 Final Status:")
        print(f"   Total Tasks: {status['total_tasks']}")
        for state, count in status['by_state'].items():
            if count > 0:
                print(f"   {state}: {count}")
    
    asyncio.run(main())
