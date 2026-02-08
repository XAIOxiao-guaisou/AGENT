
"""
Fleet Refactor Manager - The Healer of Antigravity 🏥
=====================================================

Responsible for propagating updates across the fleet.
When a Provider project updates, this manager alerts all Consumer projects.

"One update, Fleet sync."
"""

import logging
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from antigravity.core.fleet_manager import ProjectFleetManager

logger = logging.getLogger("antigravity.refactor")

class FleetRefactorManager:
    _instance = None
    
    def __init__(self):
        self.fleet_mgr = ProjectFleetManager.get_instance()
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def propagate_update(self, provider_id: str, change_summary: str = "Core Logic Update"):
        """
        Triggered when a Provider project (e.g., vortex) is updated.
        Finds all consumers and flags them for refactoring.
        """
        logger.info(f"🏥 Healer: Propagating update from '{provider_id}'...")
        
        consumers = self._find_consumers(provider_id)
        if not consumers:
            logger.info(f"   ✅ No consumers found for '{provider_id}'. Fleet is stable.")
            return

        print(f"\n⚠️  Fleet Refactor Alert: '{provider_id}' updated!")
        print(f"   Affected Consumers: {', '.join(consumers)}")
        
        for consumer_id in consumers:
            self._flag_consumer(consumer_id, provider_id, change_summary)
            
    def _find_consumers(self, provider_id: str) -> List[str]:
        """
        Identify projects that depend on the provider.
        """
        consumers = []
        # Naive scan of all projects (O(N*M)) - Acceptable for fleet size < 1000
        for pid, meta in self.fleet_mgr.projects.items():
            if pid == provider_id:
                continue
                
            # Use FleetManager's dependency scanner
            # Note: This scans file system, might be slow. 
            # Phase 14 Optimization: Should leverage GKG in future.
            deps = self.fleet_mgr.scan_cross_dependencies(pid)
            if provider_id in deps:
                consumers.append(pid)
                
        return consumers

    def _flag_consumer(self, consumer_id: str, provider_id: str, change_summary: str):
        """
        Mark consumer as NEEDS_REFACTOR and generate INTENTION.md.
        """
        meta = self.fleet_mgr.projects.get(consumer_id)
        if not meta:
            return
            
        project_root = Path(meta.path)
        intention_file = project_root / "INTENTION.md"
        
        # Check if already flagged?
        # For now, append or overwrite.
        
        intention_content = f"""# ⚠️ Refactoring Required

**Source:** Fleet Refactor Manager
**Trigger:** Upstream update in `{provider_id}`
**Timestamp:** {datetime.now().isoformat()}

## Summary
The upstream dependency `{provider_id}` has been updated:
> {change_summary}

## Action Items
1. [ ] Run `antigravity audit {consumer_id}` to check for broken imports.
2. [ ] Verify compatibility with new `{provider_id}` APIs.
3. [ ] Re-sign project after verification.

## Suggested Evolution
(DeepSeek could insert code migration suggestions here based on diffs)
"""
        try:
            with open(intention_file, 'w', encoding='utf-8') as f:
                f.write(intention_content)
                
            logger.info(f"   🚩 Flagged '{consumer_id}': Created INTENTION.md")
            # Update Fleet Manager Status?
            # self.fleet_mgr.update_status(consumer_id, "NEEDS_REFACTOR") 
            # FleetManager might not support this status yet.
        except Exception as e:
            logger.error(f"Failed to flag consumer '{consumer_id}': {e}")

