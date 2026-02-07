"""
Mission Orchestrator - DAG Serialization Methods
工业级补丁 - DAG 序列化方法

Add these methods to the MissionOrchestrator class for state persistence
"""

# Add to MissionOrchestrator class (after rollback_task method):

    def save_state(self, filepath: str):
        """
        Save orchestrator state with DAG serialization
        
        Industrial-Grade Patch: Uses networkx.node_link_data for JSON serialization
        
        Args:
            filepath: Path to save state file (.antigravity_state.json)
        """
        from pathlib import Path
        
        # Serialize tasks
        tasks_data = []
        for task_id, task in self.tasks.items():
            task_dict = {
                'task_id': task.task_id,
                'description': task.description,
                'task_type': task.task_type,
                'state': task.state.value,
                'dependencies': list(task.dependencies),
                'code_generated': task.code_generated,
                'audit_result': task.audit_result,
                'retry_count': task.retry_count,
                'max_retries': task.max_retries,
                'error_message': task.error_message,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
            tasks_data.append(task_dict)
        
        # Industrial-Grade: Serialize DAG using networkx
        dag_data = nx.node_link_data(self.dependency_graph) if self.dependency_graph else {}
        
        state = {
            'tasks': tasks_data,
            'execution_history': self.execution_history,
            'dag_topology': dag_data,
            'snapshots': {
                task_id: {
                    'checkpoint_id': snap['checkpoint_id'],
                    'timestamp': snap['timestamp'],
                    'state': snap['state'].value if hasattr(snap['state'], 'value') else snap['state']
                }
                for task_id, snap in self.snapshots.items()
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to file
        filepath_obj = Path(filepath)
        filepath_obj.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print(f"\n💾 State saved to: {filepath}")
        print(f"   Tasks: {len(tasks_data)}")
        print(f"   DAG nodes: {len(dag_data.get('nodes', []))}")
        print(f"   DAG edges: {len(dag_data.get('links', []))}")
    
    def load_state(self, filepath: str):
        """
        Load orchestrator state from file
        
        Industrial-Grade Patch: Restores DAG using networkx.node_link_graph
        
        Args:
            filepath: Path to state file
        """
        from pathlib import Path
        
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            print(f"⚠️ State file not found: {filepath}")
            return False
        
        try:
            state = json.loads(filepath_obj.read_text(encoding='utf-8'))
            
            print(f"\n🔄 Loading state from: {filepath}")
            print(f"   Timestamp: {state.get('timestamp')}")
            
            # Restore tasks
            for task_data in state.get('tasks', []):
                task = AtomicTask(
                    task_id=task_data['task_id'],
                    description=task_data['description'],
                    task_type=task_data['task_type']
                )
                task.state = TaskState(task_data['state'])
                task.dependencies = set(task_data.get('dependencies', []))
                task.code_generated = task_data.get('code_generated')
                task.audit_result = task_data.get('audit_result')
                task.retry_count = task_data.get('retry_count', 0)
                task.max_retries = task_data.get('max_retries', 3)
                task.error_message = task_data.get('error_message')
                
                self.tasks[task.task_id] = task
            
            # Industrial-Grade: Restore DAG from networkx serialization
            if 'dag_topology' in state and state['dag_topology']:
                self.dependency_graph = nx.node_link_graph(state['dag_topology'])
                print(f"   ✅ DAG restored: {len(state['dag_topology'].get('nodes', []))} nodes")
            
            # Restore execution history
            self.execution_history = state.get('execution_history', [])
            
            print(f"   ✅ Loaded {len(self.tasks)} tasks")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load state: {e}")
            return False
    
    def _persist_rollback_state(self, task_id: str, reason: str, snapshot: Dict):
        """
        Persist rollback event for audit trail
        
        Industrial-Grade Patch: Append-only rollback log
        """
        from pathlib import Path
        
        rollback_log = {
            'task_id': task_id,
            'reason': reason,
            'snapshot_id': snapshot.get('checkpoint_id'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Append to rollback log file
        rollback_file = Path(self.project_root) / ".rollback_log.jsonl"
        with rollback_file.open('a', encoding='utf-8') as f:
            f.write(json.dumps(rollback_log, ensure_ascii=False) + '\n')
        
        print(f"   📝 Rollback logged to: {rollback_file}")
