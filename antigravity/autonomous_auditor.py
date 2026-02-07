"""
Autonomous Auditor - 自主审计器
=================================

Integrates all Sheriff Brain components for autonomous execution.
整合所有 Sheriff Brain 组件以实现自主执行。

Core Features:
- Async pipeline execution (异步流水线执行)
- Component integration (组件集成)
- Autonomous run loop (自主运行循环)
- State persistence (状态持久化)
"""

import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json

from .mission_orchestrator import (
    MissionOrchestrator, AtomicTask, TaskState
)
from .local_reasoning import LocalReasoningEngine
from .sheriff_strategist import SheriffStrategist, OptimizedPlan


class AsyncPipeline:
    """
    Async pipeline for concurrent task execution / 异步流水线用于并发任务执行
    
    Allows executing Task A while pre-reviewing Task B.
    允许在执行任务 A 的同时预审任务 B。
    """
    
    def __init__(self):
        self.futures: List[asyncio.Future] = []
        self.results: Dict[str, Any] = {}
    
    async def __aenter__(self):
        """Enter async context / 进入异步上下文"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context / 退出异步上下文"""
        # Wait for all pending futures
        if self.futures:
            await asyncio.gather(*self.futures, return_exceptions=True)
    
    def submit(self, func, *args, **kwargs) -> asyncio.Future:
        """
        Submit async task / 提交异步任务
        
        Args:
            func: Function to execute / 要执行的函数
            *args, **kwargs: Function arguments / 函数参数
            
        Returns:
            Future object / Future 对象
        """
        # Create task
        if asyncio.iscoroutinefunction(func):
            future = asyncio.create_task(func(*args, **kwargs))
        else:
            # Wrap sync function in async
            async def async_wrapper():
                return func(*args, **kwargs)
            future = asyncio.create_task(async_wrapper())
        
        self.futures.append(future)
        return future
    
    async def wait_for(self, future: asyncio.Future, timeout: Optional[float] = None):
        """
        Wait for specific future / 等待特定 future
        
        Args:
            future: Future to wait for / 要等待的 future
            timeout: Timeout in seconds / 超时时间（秒）
            
        Returns:
            Result of future / future 的结果
        """
        try:
            if timeout:
                return await asyncio.wait_for(future, timeout=timeout)
            else:
                return await future
        except asyncio.TimeoutError:
            return None


class AutonomousAuditor:
    """
    Autonomous Auditor - 自主审计器
    
    Orchestrates autonomous execution with all Sheriff Brain components.
    使用所有 Sheriff Brain 组件编排自主执行。
    
    Workflow:
    1. Decompose idea into tasks
    2. Generate local plan
    3. Request remote review (async)
    4. Execute tasks with self-check
    5. Remote audit
    6. Deliver or heal
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize autonomous auditor / 初始化自主审计器
        
        Args:
            project_root: Project root directory / 项目根目录
        """
        self.project_root = project_root or Path(".")
        
        # Initialize components
        self.orchestrator = MissionOrchestrator()
        self.local_reasoner = LocalReasoningEngine(self.project_root)
        self.remote_strategist = SheriffStrategist()
        
        # State
        self.current_idea: Optional[str] = None
        self.execution_log: List[Dict] = []
        self.is_running = False
    
    async def autonomous_run(self, idea: str) -> Dict:
        """
        Complete autonomous execution / 完全自主执行
        
        Args:
            idea: User's idea / 用户想法
            
        Returns:
            Execution result / 执行结果
        """
        self.current_idea = idea
        self.is_running = True
        
        try:
            # 1. Task decomposition
            self._log("Starting autonomous execution", {"idea": idea})
            tasks = self.orchestrator.decompose_idea(idea)
            self._log("Tasks decomposed", {"count": len(tasks)})
            
            # 2. Build dependency graph
            self.orchestrator.build_dependency_graph(tasks)
            
            # 3. Generate local plan
            plan = self.local_reasoner.draft_plan(idea)
            self._log("Local plan generated", {"files": len(plan['files_to_create'])})
            
            # 4. Async pipeline execution
            async with AsyncPipeline() as pipeline:
                # Request remote review of plan (async)
                review_future = pipeline.submit(
                    self.remote_strategist.tune_plan,
                    plan
                )
                
                # Execute tasks
                for i, task in enumerate(tasks):
                    # Pre-review next task while executing current
                    next_task = tasks[i + 1] if i + 1 < len(tasks) else None
                    
                    result = await self._execute_task_with_pipeline(
                        task, next_task, pipeline
                    )
                    
                    if not result['success']:
                        self._log("Task failed", {"task_id": task.task_id})
                        # Trigger healing (Phase 20 - to be implemented)
                        break
                
                # Wait for plan review
                optimized_plan = await pipeline.wait_for(review_future, timeout=30)
                if optimized_plan:
                    self._log("Plan optimized", {
                        "score": optimized_plan.quality_score,
                        "approved": optimized_plan.approved
                    })
            
            # 5. Final delivery check
            delivery_result = self._final_delivery_check()
            
            self.is_running = False
            return delivery_result
            
        except Exception as e:
            self._log("Execution failed", {"error": str(e)})
            self.is_running = False
            raise
    
    async def _execute_task_with_pipeline(
        self,
        task: AtomicTask,
        next_task: Optional[AtomicTask],
        pipeline: AsyncPipeline
    ) -> Dict:
        """
        Execute task with async pipeline / 使用异步流水线执行任务
        
        Args:
            task: Current task / 当前任务
            next_task: Next task for pre-review / 下一个任务用于预审
            pipeline: Async pipeline / 异步流水线
            
        Returns:
            Execution result / 执行结果
        """
        # Pre-review next task (async)
        next_review_future = None
        if next_task:
            next_plan = self._generate_task_plan(next_task)
            next_review_future = pipeline.submit(
                self.remote_strategist.tune_plan,
                next_plan
            )
        
        # Execute current task through state machine
        self.orchestrator.current_task = task
        
        # PENDING → STRATEGY_REVIEW
        self.orchestrator.step(task)
        
        # STRATEGY_REVIEW → EXECUTING
        self.orchestrator.step(task)
        
        # Simulate execution (actual code generation in Phase 20)
        execution_result = self._execute_task_logic(task)
        
        # EXECUTING → SELF_CHECK
        self.orchestrator.step(task)
        
        # Local verification
        if not self._local_verify(execution_result):
            self._log("Local verification failed", {"task_id": task.task_id})
            return {'success': False, 'reason': 'local_verification_failed'}
        
        # SELF_CHECK → REMOTE_AUDIT
        self.orchestrator.step(task)
        
        # Remote audit (simulated for now)
        audit_passed = True  # TODO: Implement actual remote audit
        
        if audit_passed:
            # REMOTE_AUDIT → DONE
            self.orchestrator.step(task)
            self._log("Task completed", {"task_id": task.task_id})
            return {'success': True}
        else:
            # Trigger healing
            self.orchestrator.trigger_healing(task)
            return {'success': False, 'reason': 'remote_audit_failed'}
    
    def _generate_task_plan(self, task: AtomicTask) -> Dict:
        """
        Generate plan for specific task / 为特定任务生成计划
        
        Args:
            task: Task to plan / 要规划的任务
            
        Returns:
            Task plan / 任务计划
        """
        return {
            'intent': task.goal,
            'files_to_create': task.files_affected,
            'dependencies': task.dependencies,
            'tasks': [task.goal]
        }
    
    def _execute_task_logic(self, task: AtomicTask) -> Dict:
        """
        Execute task logic / 执行任务逻辑
        
        This is a placeholder. Actual implementation in Phase 20.
        这是占位符。实际实现在 Phase 20。
        
        Args:
            task: Task to execute / 要执行的任务
            
        Returns:
            Execution result / 执行结果
        """
        self._log("Executing task", {"task_id": task.task_id, "goal": task.goal})
        
        # Simulate file creation
        created_files = []
        for file in task.files_affected:
            file_path = self.project_root / file
            created_files.append(str(file_path))
        
        return {
            'created_files': created_files,
            'success': True
        }
    
    def _local_verify(self, execution_result: Dict) -> bool:
        """
        Local verification / 本地验证
        
        Args:
            execution_result: Execution result / 执行结果
            
        Returns:
            True if verification passed / 验证通过返回 True
        """
        # Basic verification
        if not execution_result.get('success'):
            return False
        
        # Check created files (simulated)
        created_files = execution_result.get('created_files', [])
        if not created_files:
            return False
        
        # TODO: Add VibeCheck integration
        # TODO: Add constraint validation
        
        return True
    
    def _final_delivery_check(self) -> Dict:
        """
        Final delivery check / 最终交付检查
        
        Returns:
            Delivery result / 交付结果
        """
        summary = self.orchestrator.get_execution_summary()
        
        # Check completion
        if summary['completion_rate'] < 1.0:
            return {
                'delivered': False,
                'reason': 'incomplete_tasks',
                'summary': summary
            }
        
        # TODO: Add dual-signature check (Phase 21)
        
        return {
            'delivered': True,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _log(self, event: str, data: Optional[Dict] = None):
        """
        Log execution event / 记录执行事件
        
        Args:
            event: Event name / 事件名称
            data: Event data / 事件数据
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'data': data or {}
        }
        self.execution_log.append(log_entry)
        
        # Print for debugging
        print(f"[{log_entry['timestamp'][:19]}] {event}: {data}")
    
    def get_execution_log(self) -> List[Dict]:
        """
        Get execution log / 获取执行日志
        
        Returns:
            Execution log / 执行日志
        """
        return self.execution_log
    
    def save_state(self, filepath: str):
        """
        Save auditor state / 保存审计器状态
        
        Args:
            filepath: File path to save / 保存文件路径
        """
        state = {
            'idea': self.current_idea,
            'execution_log': self.execution_log,
            'orchestrator_state': self.orchestrator.get_execution_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self, filepath: str):
        """
        Load auditor state / 加载审计器状态
        
        Args:
            filepath: File path to load / 加载文件路径
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.current_idea = state.get('idea')
        self.execution_log = state.get('execution_log', [])


# Convenience function for quick usage
async def autonomous_execute(idea: str, project_root: Optional[Path] = None) -> Dict:
    """
    Convenience function for autonomous execution / 自主执行的便捷函数
    
    Args:
        idea: User's idea / 用户想法
        project_root: Project root directory / 项目根目录
        
    Returns:
        Execution result / 执行结果
    """
    auditor = AutonomousAuditor(project_root)
    return await auditor.autonomous_run(idea)


# Sync wrapper for non-async contexts
def autonomous_execute_sync(idea: str, project_root: Optional[Path] = None) -> Dict:
    """
    Synchronous wrapper for autonomous execution / 自主执行的同步包装器
    
    Args:
        idea: User's idea / 用户想法
        project_root: Project root directory / 项目根目录
        
    Returns:
        Execution result / 执行结果
    """
    return asyncio.run(autonomous_execute(idea, project_root))
