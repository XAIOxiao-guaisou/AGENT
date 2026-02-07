"""
Autonomous Auditor - Additional Methods for Industrial-Grade Patches
工业级补丁 - 额外方法

Add these methods to the AutonomousAuditor class
"""

# Add after the _generate_code method (around line 600):

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
