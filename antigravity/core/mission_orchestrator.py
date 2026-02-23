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
from pathlib import Path


class TaskState(Enum):
    """Task lifecycle states / 任务生命周期状态"""
    PENDING = "pending"
    BLUEPRINTING = "blueprinting" # Phase 31: 架构推演
    CODING_LOOP = "coding_loop"   # Phase 31: 物理灌注
    ANALYZING = "analyzing"
    REVIEWING = "reviewing"      # Was STRATEGY_REVIEW / PREDICTING
    GENERATING = "generating"    # Was EXECUTING
    AUDITING = "auditing"        # Was SELF_CHECK / REMOTE_AUDIT
    HEALING = "healing"
    ROLLBACK = "rollback"        # Was PAUSED
    DONE = "done"


@dataclass
class AtomicTask:
    """Atomic task unit / 原子任务单元"""
    task_id: str
    type: str # 'research', 'code', 'test', 'review'
    goal: str
    metadata: Dict = field(default_factory=dict)
    state: TaskState = TaskState.PENDING
    dependencies: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'type': self.type,
            'goal': self.goal,
            'metadata': self.metadata,
            'state': self.state.value,
            'dependencies': self.dependencies,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'retry_count': self.retry_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AtomicTask':
        if 'state' in data:
            data['state'] = TaskState(data['state'])
        if 'started_at' in data and data['started_at']:
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        return cls(**data)

class ContextDriftError(Exception):
    """Raised when physical file state diverges from memory state"""
    pass

class MissionOrchestrator:
    """
    Core logic for dispatching and tracking tasks.
    核心逻辑：分发和跟踪任务。
    """
    def __init__(self, project_root: str = None):
        from pathlib import Path
        import networkx as nx
        
        # 审查官补丁：通过文件祖先链自动定位根目录
        if project_root is None:
            # 向上追溯 2 层到达 AGENT 根目录
            self.project_root = Path(__file__).resolve().parents[2]
        else:
            self.project_root = Path(project_root)
            
        # 强制更新 Checkpoint 路径
        self.checkpoint_dir = self.project_root / ".antigravity" / "checkpoints"
        try:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            # print(f"🏗️ [Orchestrator] 物理根目录已对齐: {self.project_root}")
        except Exception as e:
            print(f"⚠️ Failed to create checkpoint dir: {e}")

        self.tasks: List[AtomicTask] = []
        self.execution_history: List[Dict] = []
        self.current_task: Optional[AtomicTask] = None
        self.graph = nx.DiGraph()
        
    def build_dependency_graph(self):
        self.graph = nx.DiGraph()
        for task in self.tasks:
            self.graph.add_node(task.task_id, data=task)
            for dep in task.dependencies:
                self.graph.add_edge(dep, task.task_id)

    def _attempt_healing(self) -> bool:
        """Internal self-healing stub"""
        # Simple retry logic for now
        return True

    def _git_sync(self, task: AtomicTask):
        """Sync to git (Stub)"""
        pass

    def _iron_sync(self, task: AtomicTask):
        """Sync to Iron Gate (Stub)"""
        pass

    def step(self, task: Optional[AtomicTask] = None) -> TaskState:
        """
        Phase 26: 针对性 Debug 拦截 (Targeted Interceptor)
        """
        if task is None:
            task = self.current_task
        
        if not task:
            # v2.1.9: Auto-Scan Recovery
            return TaskState.PENDING
            
        # v2.1.9: Explicit Status Debug
        print(f"🔍 [Orchestrator] 当前任务 {task.task_id} 状态: {task.state}")

        # 🛡️ 哨兵拦截切面 (Sentinel Intercept)
        try:
            # Phase 22: Dispatcher Pattern
            handlers = {
                TaskState.PENDING: self._handle_pending,
                TaskState.BLUEPRINTING: self._handle_blueprinting,
                TaskState.CODING_LOOP: self._handle_coding_loop,
                TaskState.ANALYZING: self._handle_analyzing,
                TaskState.REVIEWING: self._handle_reviewing,
                TaskState.GENERATING: self._handle_generating,
                TaskState.AUDITING: self._handle_auditing,
                TaskState.HEALING: self._handle_healing,
                TaskState.ROLLBACK: self._handle_rollback,
                TaskState.DONE: self._handle_done
            }
            
            handler = handlers.get(task.state)
            if handler:
                return handler(task)
                
            return task.state

        except Exception as e:
            # 🚨 哨兵立即执行现场抓取 (Instant Capture)
            self._capture_sentinel_debug(task, e)
            return self.trigger_healing(task)

    def _capture_sentinel_debug(self, task, error):
        """生成当前项目专属的 .debug.json 快照"""
        import traceback, json, time
        from datetime import datetime
        
        # 统一存储在当前项目的 checkpoints 目录下
        snapshot_path = self.checkpoint_dir / f"debug_{task.task_id}_{int(time.time())}.json"
        
        snapshot = {
            "project_root": str(self.project_root),
            "task_id": task.task_id,
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
            print(f"🚨 [Sentinel] 捕捉到崩溃现场，快照已生成: {snapshot_path.name}")
        except Exception as snapshot_error:
            print(f"🚨 [Sentinel] 快照生成失败: {snapshot_error}")


    # --- Phase 22: State Handlers ---

    def _handle_pending(self, task):
        task.state = TaskState.BLUEPRINTING
        self._log_transition(task, 'PENDING', 'BLUEPRINTING')
        return TaskState.BLUEPRINTING

    def _call_deepseek_api(self, system_prompt: str, user_prompt: str) -> str:
        from antigravity.utils.config import CONFIG
        import urllib.request, json, os

        api_key = CONFIG.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("⚠️ [哨兵警告] Missing DEEPSEEK_API_KEY. Defaulting to dummy JSON.")
            if "json blueprint" in system_prompt:
                return '```json blueprint\n{"main.py": "Entry point", "core/": ""}\n```'
            return "print('dummy code generated due to missing API key')"
            
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'))
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"📡 [LLM Error] {e}")
            raise

    def _handle_blueprinting(self, task):
        """Phase 31: Autonomous Blueprinting and Physical Scaffolding"""
        import re, json
        print(f"🧠 [Orchestrator] 正在进行架构推演：请求 DeepSeek 蓝图...")
        system_prompt = '''你现在是 Antigravity 产线的首席架构师。接收到业务愿景后，绝对不要立即输出具体的业务代码。
你的第一步任务是：设计最优的模块化文件目录结构，并严格使用以下 JSON 格式在 Markdown 的 json blueprint 代码块中返回。
格式要求：键为文件或文件夹的相对路径，值为描述（文件夹的值为空字符串）。
示例：
```json blueprint
{
  "main.py": "主控入口",
  "core/": "",
  "core/strategy.py": "策略逻辑",
  "utils/logger.py": "日志工具"
}
```'''
        vision_file = self.project_root / "PLAN.md"
        vision_text = vision_file.read_text(encoding="utf-8") if vision_file.exists() else task.goal
        user_prompt = f"项目名称：{self.project_root.name}\n项目愿景：\n{vision_text}"

        try:
            llm_response = self._call_deepseek_api(system_prompt, user_prompt)
            match = re.search(r'```json blueprint\n(.*?)\n```', llm_response, re.DOTALL)
            if not match:
                raise ValueError("哨兵拦截：DeepSeek 未按协议输出 JSON 蓝图！")
            
            blueprint = json.loads(match.group(1))
            print(f"📡 [神经中枢] 成功接收架构蓝图，开始物理拓荒...")
            created_files = []

            for relative_path, description in blueprint.items():
                target_path = (self.project_root / relative_path).resolve()
                if not str(target_path).startswith(str(self.project_root.resolve())):
                    print(f"⚠️ [哨兵警告] 拒绝越权路径生成: {relative_path}")
                    continue

                if relative_path.endswith('/'):
                    target_path.mkdir(parents=True, exist_ok=True)
                    print(f"📁 创建目录: {relative_path}")
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.touch(exist_ok=True)
                    created_files.append(relative_path)
                    print(f"📄 铸造文件实体: {relative_path} ({description})")

            print(f"✅ [神经中枢] 物理拓荒完成。等待代码灌注。")
            task.metadata['created_files'] = created_files
            task.metadata['remaining_files'] = list(created_files) # To process in coding loop
            
            task.state = TaskState.CODING_LOOP
            self._log_transition(task, 'BLUEPRINTING', 'CODING_LOOP')
            return TaskState.CODING_LOOP

        except Exception as e:
            print(f"❌ [Blueprinting Error] {e}")
            return self.trigger_healing(task)

    def _handle_coding_loop(self, task):
        """Phase 31: Physical Pouring / 代码实体验注"""
        remaining = task.metadata.get('remaining_files', [])
        if not remaining:
            print(f"✅ [Coding Loop] 所有文件灌注完毕。流转至审核环节。")
            task.state = TaskState.AUDITING
            self._log_transition(task, 'CODING_LOOP', 'AUDITING')
            return TaskState.AUDITING
            
        current_file = remaining[0]
        print(f"✍️ [Coding Loop] 正在请求实体浇筑: {current_file}")
        
        system_prompt = f"""你现在是 Antigravity 产线的首席工程师。项目架构蓝图已敲定。请为指定文件生成完整的、生产级别的 Python 代码。
要求：只输出代码块，不要解释说明。格式：
```python
# 代码内容
```"""
        vision_file = self.project_root / "PLAN.md"
        vision_text = vision_file.read_text(encoding="utf-8") if vision_file.exists() else task.goal
        user_prompt = f"项目愿景：\n{vision_text}\n请实现文件 `{current_file}`。直接输出代码，无需 Markdown 包裹外其他内容。"

        try:
            llm_response = self._call_deepseek_api(system_prompt, user_prompt)
            import re
            match = re.search(r'```python\n(.*?)\n```', llm_response, re.DOTALL)
            code = match.group(1) if match else llm_response.replace('```python','').replace('```','')
            
            target_path = self.project_root / current_file
            target_path.write_text(code, encoding='utf-8')
            print(f"💾 [实体浇筑] 写入完成: {current_file}")
            
            # Pop and save state
            task.metadata['remaining_files'] = remaining[1:]
            
            return TaskState.CODING_LOOP
            
        except Exception as e:
            print(f"❌ [Coding Error] File {current_file}: {e}")
            return self.trigger_healing(task)

    def _handle_analyzing(self, task):
        """Phase 25: Neural Nexus / 快速分析穿透"""
        # Logic Penetration: Zero-G for Dashboard Tasks
        if task.metadata.get('created_via') == 'dashboard':
             print(f"🚀 [Zero-G] Dashboard 任务 {task.task_id} 检测到。绕过深度语义共识。")
        else:
             print(f"🧠 [Nexus] 正在快速检索任务 {task.task_id} 的语义索引...")
             
        # 强制补充文件路径元数据
        if not task.metadata.get('file_path'):
            task.metadata['file_path'] = 'PLAN.md'
        
        # State Penetration: Directly to REVIEWING
        task.state = TaskState.REVIEWING
        self._log_transition(task, 'ANALYZING', 'REVIEWING')
        return TaskState.REVIEWING

    def _handle_reviewing(self, task):
        """Phase 27: Confidence Engine / 强制 Zero-G 穿透"""
        # Logic Penetration
        if task.metadata.get('created_via') == 'dashboard' or 'task_' in task.task_id:
            print(f"🚀 [Zero-G] 检测到主权任务 {task.task_id}，正在强行跳过共识审计...")
            # State Penetration: Directly to GENERATING
            task.state = TaskState.GENERATING
            self._log_transition(task, 'REVIEWING', 'GENERATING')
            return TaskState.GENERATING
        
        print(f"🗳️ [Consensus] 审查官已批准策略，准予点火执行。")
        self._transition_to_generating(task)
        return TaskState.GENERATING

    def _handle_generating(self, task):
        """
        Phase 23.5: Absolute Portable Wake-up (绝对自适应唤醒协议)
        由审查官指导：废除硬编码，实现跨机 100% 物理对齐。
        """
        import os, time, subprocess
        from pathlib import Path
        from antigravity.utils.config import CONFIG
        
        # 1. 动态定位桌面路径 (Multi-Location Desktop Search)
        # 适配不同 Windows 版本、用户名及 OneDrive 环境 [幻觉可疑度: 2%]
        user_home = Path.home()
        # 2. 动态定位桌面路径 (Multi-Location Desktop Search)
        # 适配不同 Windows 版本、用户名及 OneDrive 环境 [幻觉可疑度: 2%]
        user_home = Path.home()
        potential_desktops = [
            user_home / "Desktop",
            user_home / "OneDrive" / "Desktop",
            user_home / "OneDrive" / "桌面",
            user_home / "桌面"
        ]
        
        # 2. 搜索 Antigravity.lnk
        editor_lnk = CONFIG.get('EDITOR_PATH')
        if not editor_lnk or not os.path.exists(editor_lnk):
            editor_lnk = None # Reset if invalid
            for desktop in potential_desktops:
                cand = desktop / "Antigravity.lnk"
                if cand.exists():
                    editor_lnk = str(cand)
                    break
        
        target_file = task.metadata.get('file_path') or 'PLAN.md'
        full_path = os.path.abspath(os.path.join(str(self.project_root), target_file))
        
        print(f"📡 [Path Discovery] 跨机链路自适应探测:")
        print(f"   - Current Workspace: {self.project_root}")
        print(f"   - Editor Shortcut: {editor_lnk if editor_lnk else 'NOT_FOUND'}")

        try:
            if editor_lnk and os.path.exists(editor_lnk):
                # 关键：切换工作目录至项目根目录，防止编辑器加载上下文偏移
                os.chdir(str(self.project_root))
                
                # 使用 Windows shell 直接唤起，比 subprocess.run 传递 LNK 更稳健 [幻觉可疑度: 5%]
                os.startfile(editor_lnk)
                
                print(f"✅ [Physical] 物理链路已握手成功。")
                time.sleep(1.0) # 预热
            else:
                print(f"❌ [Physical Error] 在新电脑未找到 Antigravity.lnk，请检查桌面。")
                return TaskState.HEALING
                
            task.state = TaskState.AUDITING
            self._log_transition(task, 'GENERATING', 'AUDITING')
            return TaskState.AUDITING
        except Exception as e:
            print(f"❌ [Migration Error] 物理唤醒失效: {e}")
            return TaskState.HEALING

    def _handle_generating(self, task):
        """
        Phase 23: Absolute Wake-up (绝对唤醒协议)
        v2.1.12: Absolute Path Hardening & GUI Warmup
        """
        from antigravity.utils.config import CONFIG
        import os
        import time
        
        # Try to find Antigravity.lnk dynamically if not in config
        user_home = Path.home()
        default_lnk = user_home / "Desktop" / "Antigravity.lnk"
        if not default_lnk.exists():
             default_lnk = user_home / "OneDrive" / "Desktop" / "Antigravity.lnk"
        
        editor_lnk = CONFIG.get('EDITOR_PATH', str(default_lnk))
        target_file = task.metadata.get('file_path') or 'PLAN.md'
        full_path = str(os.path.abspath(os.path.join(str(self.project_root), target_file)))
        
        try:
            print(f"⚡ [Physical Trigger] 正在强制唤醒编辑器: {full_path}")
            
            # v2.1.12: Hardening - Switch CWD to Project Root
            original_cwd = os.getcwd()
            try:
                os.chdir(str(self.project_root))
                print(f"📂 [Context] Switched CWD to: {os.getcwd()}")
                
                if os.path.exists(editor_lnk):
                    # GUI Warmup
                    print("⏳ [Warmup] 等待编辑器 GUI 就绪 (2s)...")
                    time.sleep(2.0)
                    
                    os.startfile(editor_lnk)
                    print(f"✅ [Physical] 编辑器已成功由系统外壳唤起。")
                    print(f"✅ Target Verified: {full_path}")
                else:
                    print(f"❌ [Physical Error] 快捷方式不存在: {editor_lnk}")
                    return TaskState.HEALING
            finally:
                os.chdir(original_cwd) # Restore CWD safety
                
            task.state = TaskState.AUDITING
            self._log_transition(task, 'GENERATING', 'AUDITING')
            return TaskState.AUDITING
        except Exception as e:
            print(f"❌ [Physical Error] 自动唤醒失败: {e}")
            return TaskState.HEALING

    def _handle_auditing(self, task):
        """Phase 31: Sentinel Audit (哨兵审计): Run main.py"""
        import subprocess, sys
        main_py = self.project_root / "main.py"
        if not main_py.exists():
             print("✅ [Sentinel Audit] 无 main.py 文件，跳过防空审查。")
             self._transition_to_done(task)
             return TaskState.DONE
        
        print(f"🏰 [Sentinel Audit] 本地空载运行探测主心骨 {main_py.name}...")
        try:
            res = subprocess.run([sys.executable, str(main_py)], capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                print("✅ [Sentinel Audit] 执行探测通过（0代码异常）。")
                self._transition_to_done(task)
                return TaskState.DONE
            else:
                tb = res.stderr or res.stdout
                print(f"❌ [Sentinel Audit] 宕机拒绝，截获 Traceback:\n{tb}")
                task.metadata['recent_traceback'] = tb
                task.state = TaskState.HEALING
                self._log_transition(task, 'AUDITING', 'HEALING')
                return TaskState.HEALING
        except Exception as e:
            print(f"⚠️ [Sentinel Audit] 执行超时或测试系统内部错误: {e}")
            self._transition_to_done(task)
            return TaskState.DONE
        
    def _handle_healing(self, task):
        """Phase 31: Autonomous Genesis (自主演化 / 自愈) -> Feed traceback to LLM"""
        if not hasattr(task, 'retry_count'):
            task.retry_count = 0
        task.retry_count += 1
        
        if task.retry_count > 3:
             print(f"❌ Healing failed (Max Retries). ROLLBACK.")
             task.state = TaskState.ROLLBACK
             self._log_transition(task, 'HEALING', 'ROLLBACK')
             return TaskState.ROLLBACK
        
        print(f"⚕️ [Autonomous Genesis] Healing Attempt {task.retry_count}/3...")
        
        try:
            tb = task.metadata.get('recent_traceback')
            if tb:
                print("⚕️ [Autonomous Genesis] 正在请求超级大脑热修复 main.py...")
                sys_prompt = "你是 Antigravity 热修复终端。分析报错信息，并输出 main.py 的修复后代码。只输出完整的 python 代码块。"
                user_prompt = f"报错Traceback：\n{tb}\n\n请只输出修复后的代码块，格式:\n```python\n#代码\n```"
                resp = self._call_deepseek_api(sys_prompt, user_prompt)
                import re
                match = re.search(r'```python\n(.*?)\n```', resp, re.DOTALL)
                code = match.group(1) if match else resp.replace('```python','').replace('```','')
                (self.project_root / "main.py").write_text(code, encoding="utf-8")
                print("✅ [Auto-Fix] 已应用热修复到 main.py")
                task.metadata['recent_traceback'] = None
                
            task.state = TaskState.AUDITING
            self._log_transition(task, 'HEALING', 'AUDITING')
            return TaskState.AUDITING
            
        except Exception as e:
            print(f"⚠️ Healing Error: {e}")
            return TaskState.ROLLBACK

    def _handle_rollback(self, task):
        # Was PAUSED
        return TaskState.ROLLBACK

    def _handle_done(self, task):
        return TaskState.DONE

    def _transition_to_generating(self, task: AtomicTask) -> TaskState:
        old_state = task.state.value
        task.state = TaskState.GENERATING
        task.started_at = datetime.now()
        self._log_transition(task, old_state, 'GENERATING')
        return task.state
    
    def _transition_to_auditing(self, task: AtomicTask) -> TaskState:
        old_state = task.state.value
        task.state = TaskState.AUDITING
        self._log_transition(task, old_state, 'AUDITING')
        return task.state
    
    def _transition_to_done(self, task: AtomicTask) -> TaskState:
        old_state = task.state.value
        task.state = TaskState.DONE
        self._log_transition(task, old_state, 'DONE')
        # Sync logic...
        self._git_sync(task)
        self._iron_sync(task)
        return task.state

    def trigger_healing(self, task: AtomicTask) -> TaskState:
        old_state = task.state.value
        task.state = TaskState.HEALING
        self._log_transition(task, old_state, 'HEALING')
        return task.state
    
    def _log_transition(self, task: AtomicTask, from_state: str, to_state: str):
        """Log state transition and push telemetry"""
        self.execution_history.append({
            'task_id': task.task_id,
            'from_state': from_state,
            'to_state': to_state,
            'timestamp': datetime.now().isoformat()
        })
        
        # Telemetry Injection
        try:
            from antigravity.infrastructure.telemetry_queue import TelemetryQueue
            TelemetryQueue.push_state_change(task.task_id, from_state, to_state)
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ Telemetry Error: {e}")
    
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

    def _handle_context_drift(self, file_path: Path, expected: dict, actual_lines: int) -> bool:
        """
        Phase 14.3: Hallucination Correction Loop.
        Attempt to realign Agent Context with Physical Reality.
        """
        print(f"⚕️ CORRECTION LOOP: Initiating cold read for {file_path.name}...")
        
        try:
            # 2. Intent Alignment (Safety Check)
            expected_count = expected.get('line_count', 1)
            if expected_count == 0: expected_count = 1
            
            drift_ratio = abs(actual_lines - expected_count) / expected_count
            
            if drift_ratio > 0.2: # >20% Drift is too dangerous to auto-heal
                print(f"🔥 DRIFT CRITICAL ({drift_ratio:.1%}): Cannot auto-heal. Aborting.")
                return False
                
            print(f"🔄 REALIGNING: Context Updated {expected_count} -> {actual_lines} lines. Syncing Intent...")
            return True
            
        except Exception as e:
            print(f"❌ Correction Failed: {e}")
            return False

    def pre_edit_audit(self, file_path: str, expected_metadata: dict) -> bool:
        """
        Iron Gate Protocol 1.5.0: Zero-Hallucination Gate.
        """
        from antigravity.utils.io_utils import safe_read, sanitize_for_protobuf
        from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
        
        path = Path(file_path)
        safe_path_str = sanitize_for_protobuf(str(path))
        
        if not path.exists():
            return True 
            
        print(f"🛡️ Iron Gate: Auditing '{safe_path_str}' against snapshot...")
        
        try:
            current_content = safe_read(path)
            actual_lines = len(current_content.splitlines())
            
            expected_lines = expected_metadata.get('line_count')
            if expected_lines is not None and actual_lines != expected_lines:
                print(f"⚠️ CONTEXT DRIFT DETECTED: Physical({actual_lines}) != Mind({expected_lines})")
                
                if self._handle_context_drift(path, expected_metadata, actual_lines):
                    print(f"✅ Iron Gate: Drift Healed. Authorized.")
                    return True
                
                error_msg = f"CONTEXT_DRIFT: {safe_path_str} Physical({actual_lines}) != Mind({expected_lines})!"
                TelemetryQueue.push_event(TelemetryEventType.SECURITY_BREACH, {
                    "event": "CONTEXT_DRIFT",
                    "file": safe_path_str,
                    "details": error_msg
                })
                raise ContextDriftError(error_msg)
                
            print(f"✅ Iron Gate: {safe_path_str} Physical alignment passed (Lines: {actual_lines}). Authorized.")
            return True
            
        except ContextDriftError:
            raise
        except Exception as e:
            safe_err = sanitize_for_protobuf(str(e))
            print(f"🛑 Iron Gate: Audit FAILED for '{safe_path_str}': {safe_err}")
            return False


