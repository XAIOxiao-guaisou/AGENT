"""
Autonomous Auditor - Final Polishing Methods
工业级补丁 - 最终打磨方法

Add these methods to the AutonomousAuditor class for final polishing
"""

# Add to AutonomousAuditor class:

    def _filter_relevant_forbidden_zones(self, task: 'AtomicTask') -> Dict[str, float]:
        """
        Filter forbidden zones by relevance to current task
        
        Final Polishing: Decay weights for relevance scoring
        
        Returns:
            Dict[zone_name, confidence_weight]
            - 1.0: High relevance (keyword match)
            - 0.5: Medium relevance (recent fallback)
        """
        relevant_zones = {}  # {zone: weight}
        
        # Extract keywords from task description
        task_keywords = set(task.description.lower().split())
        task_keywords.add(task.task_type.lower())
        
        for zone in self.forbidden_zones:
            # Zone format: "function_name:structural_error"
            func_name = zone.split(':')[0].lower()
            
            # Check if function name appears in task keywords
            if any(keyword in func_name or func_name in keyword for keyword in task_keywords):
                relevant_zones[zone] = 1.0  # High relevance
        
        # If no relevant zones found, return most recent 3 zones with lower weight
        if not relevant_zones and self.forbidden_zones:
            recent_zones = list(self.forbidden_zones)[-3:]
            for zone in recent_zones:
                relevant_zones[zone] = 0.5  # Medium relevance (fallback)
        
        print(f"   🎯 Filtered forbidden zones: {len(relevant_zones)}/{len(self.forbidden_zones)} relevant")
        
        # Print weight distribution
        high_conf = sum(1 for w in relevant_zones.values() if w == 1.0)
        med_conf = sum(1 for w in relevant_zones.values() if w == 0.5)
        print(f"      High confidence: {high_conf}, Medium confidence: {med_conf}")
        
        return relevant_zones
    
    def _extract_function_name(self, error_message: str) -> Optional[str]:
        """Extract function name from error message"""
        import re
        match = re.search(r"[Ff]unction '(\w+)'", error_message)
        return match.group(1) if match else None
    
    def _generate_negative_reinforcement_prompt(
        self, 
        task: 'AtomicTask', 
        structural_errors: List[str],
        code_snippets: Dict[str, str]
    ) -> str:
        """
        Generate prompt with negative reinforcement
        
        Industrial-Grade Patch: Force LLM to change logic topology
        Final Polishing: Include confidence weights in prompt
        """
        relevant_zones = self._filter_relevant_forbidden_zones(task)
        
        # Build forbidden constraints with confidence indicators
        forbidden_examples = []
        for error in structural_errors:
            func_name = self._extract_function_name(error)
            if func_name:
                zone_key = f"{func_name}:structural_error"
                confidence = relevant_zones.get(zone_key, 0.0)
                
                if confidence > 0:
                    # Add confidence indicator
                    conf_label = "🔴 高度相关" if confidence == 1.0 else "🟡 参考案例"
                    forbidden_examples.append(f"- [{conf_label}] {error}")
                    
                    # Add code snippet if available
                    if func_name in code_snippets:
                        snippet = code_snippets[func_name]
                        forbidden_examples.append(
                            f"\n  反面教材 (Failed Implementation):\n```python\n{snippet}\n```\n"
                        )
        
        forbidden_constraints = "\n".join(forbidden_examples) if forbidden_examples else \
                               "\n".join([f"- {err}" for err in structural_errors])
        
        prompt = f"""
🚫 结构性失败警告 (Structural Failure Warning)

Sheriff 过滤系统已为你精选了与当前上下文最匹配的 {len(relevant_zones)} 条防御性约束：

{forbidden_constraints}

⚠️ 要求 (Requirements):
1. **更换实现拓扑** - 彻底废弃上述实现思路，使用完全不同的函数结构
2. **强制 Type Hints** - 所有函数必须有返回类型和参数类型注解
3. **强制错误处理** - 所有函数都必须包含 try-except 块
4. **禁用不安全函数** - 严禁使用 eval/exec 等不安全函数

📋 任务描述: {task.description}

💡 提示: 🔴 标记的案例与当前任务高度相关，🟡 标记的案例为近期失败参考。
"""
        
        return prompt
    
    def _send_introspection_signal(self, signal_type: str, **kwargs):
        """
        Send introspection signal to trigger self-optimization
        
        Final Polishing: Enable LLM self-reflection on resource usage
        """
        signal = {
            'type': signal_type,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        # Store signal for next HEALING cycle
        if not hasattr(self, 'introspection_signals'):
            self.introspection_signals = []
        
        self.introspection_signals.append(signal)
        
        print(f"   📡 Introspection signal sent: {signal_type}")
        print(f"      Suggestion: {kwargs.get('suggestion', 'N/A')}")


# Update _memory_guardian method in SandboxExecutor class:

    def _memory_guardian(self, process, max_memory_mb: int):
        """
        Memory guardian thread - monitors and kills process if memory exceeds limit
        
        Industrial-Grade Patch: Soft-hard approach for Windows compatibility
        Final Polishing: Two-level circuit breaker (warning → termination)
        """
        try:
            import psutil
            
            ps_process = psutil.Process(process.pid)
            warning_sent = False
            
            # FINAL POLISHING: Two-level thresholds
            warning_threshold = max_memory_mb * 0.8  # 80% = yellow warning
            critical_threshold = max_memory_mb       # 100% = red termination
            
            while self.memory_guardian_active and process.poll() is None:
                try:
                    # Get memory usage in MB
                    memory_mb = ps_process.memory_info().rss / (1024 * 1024)
                    
                    # Level 1: Warning + Introspection (80%)
                    if memory_mb > warning_threshold and not warning_sent:
                        print(f"\n⚠️ MEMORY WARNING (Level 1)")
                        print(f"   Current: {memory_mb:.1f}MB")
                        print(f"   Warning threshold: {warning_threshold:.1f}MB")
                        print(f"   Critical threshold: {critical_threshold:.1f}MB")
                        print(f"   💡 Consider code optimization")
                        
                        # FINAL POLISHING: Send introspection signal
                        # Note: This requires access to parent AutonomousAuditor
                        # In production, use a shared queue or callback
                        if hasattr(self, 'auditor') and hasattr(self.auditor, '_send_introspection_signal'):
                            self.auditor._send_introspection_signal(
                                signal_type='memory_warning',
                                memory_mb=memory_mb,
                                threshold=warning_threshold,
                                suggestion='Optimize algorithm complexity or reduce temporary variables'
                            )
                        
                        warning_sent = True
                    
                    # Level 2: Termination (100%)
                    if memory_mb > critical_threshold:
                        print(f"\n🔴 MEMORY CRITICAL (Level 2)")
                        print(f"   Current: {memory_mb:.1f}MB")
                        print(f"   Limit: {critical_threshold:.1f}MB")
                        print(f"   🔪 Terminating sandbox process...")
                        
                        # Kill process
                        process.terminate()
                        process.wait(timeout=2)
                        
                        # Raise custom exception
                        raise SandboxMemoryExceeded(
                            f"Sandbox memory exceeded: {memory_mb:.1f}MB > {critical_threshold:.1f}MB"
                        )
                    
                    time.sleep(0.1)  # Check every 100ms
                    
                except psutil.NoSuchProcess:
                    break
                    
        except ImportError:
            print(f"⚠️ psutil not available, memory monitoring disabled")
        except Exception as e:
            print(f"⚠️ Memory guardian error: {e}")


# Add to AutonomousAuditor.__init__:
    def __init__(self, project_root: str):
        # ... existing init code ...
        
        # Final Polishing: Introspection signals storage
        self.introspection_signals = []
        
        # Pass auditor reference to sandbox for introspection
        self.sandbox.auditor = self
