"""
Autonomous Auditor - Final Polishing Methods
工业级补丁 - 最终打磨方法

Add these methods to the AutonomousAuditor class for final polishing
"""

from datetime import datetime
from typing import Dict, List, Optional
from .sandbox import SandboxMemoryExceeded


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
                        f"\n  反面教材 (Failed Implementation):\n