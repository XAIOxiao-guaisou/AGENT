"""
Mission Orchestrator - 任务编排器
===================================

State machine-driven task orchestration for autonomous execution.
状态机驱动的任务编排，用于自主执行。

Core Features:
- Idea → AtomicTasks decomposition
- 7-state lifecycle management
- Dependency graph construction
- Async task distribution
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import networkx as nx
import json


class TaskState(Enum):
    """Task lifecycle states / 任务生命周期状态"""
    PENDING = "pending"
    STRATEGY_REVIEW = "strategy_review"
    EXECUTING = "executing"
    SELF_CHECK = "self_check"
    REMOTE_AUDIT = "remote_audit"
    HEALING = "healing"
    DONE = "done"


@dataclass
class AtomicTask:
    """
    Atomic task unit / 原子任务单元
    
    Each task represents a single, independent unit of work.
    每个任务代表一个独立的工作单元。
    """
    task_id: str
    goal: str
    dependencies: List[str] = field(default_factory=list)
    files_affected: List[str] = field(default_factory=list)
    validation_script: Optional[str] = None
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary / 序列化为字典"""
        return {
            'task_id': self.task_id,
            'goal': self.goal,
            'dependencies': self.dependencies,
            'files_affected': self.files_affected,
            'validation_script': self.validation_script,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AtomicTask':
        """Deserialize from dictionary / 从字典反序列化"""
        data['state'] = TaskState(data['state'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class MissionOrchestrator:
    """
    Mission Orchestrator - 任务编排器
    
    Manages the complete lifecycle of autonomous task execution.
    管理自主任务执行的完整生命周期。
    """
    
    def __init__(self):
        self.tasks: List[AtomicTask] = []
        self.dependency_graph: Optional[nx.DiGraph] = None
        self.current_task: Optional[AtomicTask] = None
        self.execution_history: List[Dict] = []
        
    def decompose_idea(self, idea: str) -> List[AtomicTask]:
        """
        Decompose idea into atomic tasks / 将想法分解为原子任务
        
        Args:
            idea: User's idea description / 用户的想法描述
            
        Returns:
            List of atomic tasks / 原子任务列表
        """
        # Extract key components from idea
        components = self._extract_components(idea)
        
        # Generate atomic tasks
        tasks = []
        task_counter = 0
        
        for component in components:
            task = AtomicTask(
                task_id=f"task_{task_counter:03d}",
                goal=component['goal'],
                files_affected=component.get('files', []),
                dependencies=component.get('dependencies', []),
                metadata={'component_type': component.get('type', 'general')}
            )
            tasks.append(task)
            task_counter += 1
        
        self.tasks = tasks
        return tasks
    
    def _extract_components(self, idea: str) -> List[Dict]:
        """
        Extract components from idea / 从想法中提取组件
        
        This is a rule-based extraction. In future, can be enhanced with NLP.
        这是基于规则的提取。未来可以用 NLP 增强。
        """
        components = []
        
        # Keywords mapping / 关键词映射
        keywords_map = {
            'database': {
                'goal': 'Set up database models and connections',
                'files': ['models/__init__.py', 'models/base.py', 'config/database.py'],
                'type': 'database'
            },
            'api': {
                'goal': 'Implement API endpoints',
                'files': ['api/__init__.py', 'api/routes.py'],
                'type': 'api'
            },
            'auth': {
                'goal': 'Implement authentication system',
                'files': ['auth/__init__.py', 'auth/jwt_handler.py'],
                'type': 'auth',
                'dependencies': ['database']
            },
            'test': {
                'goal': 'Create test suite',
                'files': ['tests/__init__.py', 'tests/test_main.py'],
                'type': 'testing'
            }
        }
        
        idea_lower = idea.lower()
        
        # Extract matched components
        for keyword, component_spec in keywords_map.items():
            if keyword in idea_lower:
                components.append(component_spec.copy())
        
        # Always add main entry point if not a pure test project
        if 'test' not in idea_lower or len(components) > 1:
            components.insert(0, {
                'goal': 'Create main entry point',
                'files': ['main.py', 'config/settings.py'],
                'type': 'core'
            })
        
        return components if components else [{
            'goal': 'Implement core functionality',
            'files': ['main.py'],
            'type': 'general'
        }]
    
    def build_dependency_graph(self, tasks: Optional[List[AtomicTask]] = None) -> nx.DiGraph:
        """
        Build task dependency graph / 构建任务依赖图
        
        Args:
            tasks: List of tasks (uses self.tasks if None) / 任务列表
            
        Returns:
            Directed graph of task dependencies / 任务依赖有向图
        """
        if tasks is None:
            tasks = self.tasks
        
        graph = nx.DiGraph()
        
        # Add nodes
        for task in tasks:
            graph.add_node(task.task_id, task=task)
        
        # Add edges based on dependencies
        for task in tasks:
            for dep in task.dependencies:
                # Find dependency task
                dep_task = next((t for t in tasks if t.metadata.get('component_type') == dep), None)
                if dep_task:
                    graph.add_edge(dep_task.task_id, task.task_id)
        
        self.dependency_graph = graph
        return graph
    
    def get_next_task(self) -> Optional[AtomicTask]:
        """
        Get next executable task / 获取下一个可执行任务
        
        Returns task with no pending dependencies.
        返回没有待处理依赖的任务。
        """
        if not self.dependency_graph:
            self.build_dependency_graph()
        
        for task in self.tasks:
            if task.state == TaskState.DONE:
                continue
            
            # Check if all dependencies are done
            deps_done = all(
                self._get_task_by_id(dep).state == TaskState.DONE
                for dep in task.dependencies
                if self._get_task_by_id(dep)
            )
            
            if deps_done and task.state == TaskState.PENDING:
                return task
        
        return None
    
    def _get_task_by_id(self, task_id: str) -> Optional[AtomicTask]:
        """Get task by ID / 通过 ID 获取任务"""
        return next((t for t in self.tasks if t.task_id == task_id), None)
    
    def step(self, task: Optional[AtomicTask] = None) -> TaskState:
        """
        Execute one step of the state machine / 执行状态机的一步
        
        Args:
            task: Task to step (uses current_task if None) / 要执行的任务
            
        Returns:
            New state after step / 步骤后的新状态
        """
        if task is None:
            task = self.current_task
        
        if not task:
            return TaskState.PENDING
        
        # State machine transitions
        match task.state:
            case TaskState.PENDING:
                return self._transition_to_strategy_review(task)
            case TaskState.STRATEGY_REVIEW:
                return self._transition_to_executing(task)
            case TaskState.EXECUTING:
                return self._transition_to_self_check(task)
            case TaskState.SELF_CHECK:
                return self._transition_to_remote_audit(task)
            case TaskState.REMOTE_AUDIT:
                return self._transition_to_done(task)
            case TaskState.HEALING:
                return self._transition_to_executing(task)
            case TaskState.DONE:
                return TaskState.DONE
    
    def _transition_to_strategy_review(self, task: AtomicTask) -> TaskState:
        """Transition: PENDING → STRATEGY_REVIEW"""
        task.state = TaskState.STRATEGY_REVIEW
        self._log_transition(task, 'PENDING', 'STRATEGY_REVIEW')
        return task.state
    
    def _transition_to_executing(self, task: AtomicTask) -> TaskState:
        """Transition: STRATEGY_REVIEW/HEALING → EXECUTING"""
        old_state = task.state.value
        task.state = TaskState.EXECUTING
        self._log_transition(task, old_state, 'EXECUTING')
        return task.state
    
    def _transition_to_self_check(self, task: AtomicTask) -> TaskState:
        """Transition: EXECUTING → SELF_CHECK"""
        task.state = TaskState.SELF_CHECK
        self._log_transition(task, 'EXECUTING', 'SELF_CHECK')
        return task.state
    
    def _transition_to_remote_audit(self, task: AtomicTask) -> TaskState:
        """Transition: SELF_CHECK → REMOTE_AUDIT"""
        task.state = TaskState.REMOTE_AUDIT
        self._log_transition(task, 'SELF_CHECK', 'REMOTE_AUDIT')
        return task.state
    
    def _transition_to_done(self, task: AtomicTask) -> TaskState:
        """Transition: REMOTE_AUDIT → DONE"""
        task.state = TaskState.DONE
        self._log_transition(task, 'REMOTE_AUDIT', 'DONE')
        return task.state
    
    def trigger_healing(self, task: AtomicTask) -> TaskState:
        """Trigger healing state / 触发修复状态"""
        old_state = task.state.value
        task.state = TaskState.HEALING
        self._log_transition(task, old_state, 'HEALING')
        return task.state
    
    def _log_transition(self, task: AtomicTask, from_state: str, to_state: str):
        """Log state transition / 记录状态转换"""
        self.execution_history.append({
            'task_id': task.task_id,
            'from_state': from_state,
            'to_state': to_state,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_execution_summary(self) -> Dict:
        """
        Get execution summary / 获取执行摘要
        
        Returns:
            Summary of current execution state / 当前执行状态摘要
        """
        state_counts = {}
        for task in self.tasks:
            state_counts[task.state.value] = state_counts.get(task.state.value, 0) + 1
        
        return {
            'total_tasks': len(self.tasks),
            'state_distribution': state_counts,
            'completed': state_counts.get('done', 0),
            'in_progress': len(self.tasks) - state_counts.get('done', 0),
            'completion_rate': state_counts.get('done', 0) / len(self.tasks) if self.tasks else 0
        }
    
    def save_state(self, filepath: str):
        """Save orchestrator state to file / 保存编排器状态到文件"""
        state = {
            'tasks': [task.to_dict() for task in self.tasks],
            'execution_history': self.execution_history,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self, filepath: str):
        """Load orchestrator state from file / 从文件加载编排器状态"""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.tasks = [AtomicTask.from_dict(task_data) for task_data in state['tasks']]
        self.execution_history = state['execution_history']
        self.build_dependency_graph()
