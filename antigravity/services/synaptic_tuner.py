"""
Synaptic Tuner
--------------
Phase 25: Adaptive Synapse
Autonomously adjusts fleet interaction weights based on telemetry.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

from antigravity.utils.config import CONFIG
from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType

logger = logging.getLogger("antigravity.synapse")

class SynapticTuner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.weights_file = self.project_root / "config" / "synapse_weights.json"
        self.weights: Dict[str, float] = self._load_weights()
        
    def _load_weights(self) -> Dict[str, float]:
        if not self.weights_file.exists():
            return {}
        try:
            with open(self.weights_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
            
    def _save_weights(self):
        self.weights_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.weights_file, 'w') as f:
            json.dump(self.weights, f, indent=2)

    def process_telemetry(self, event: Dict[str, Any]):
        """
        Adjust weights based on latency.
        Logic:
        - Latency > 300ms: Decay weight (punish slow nodes)
        - Latency < 50ms: Boost weight (reward fast nodes)
        """
        metric = event.get('metric')
        if metric != 'SYNAPTIC_LATENCY':
            return
            
        project = event.get('project')
        latency = event.get('latency_ms', 0)
        
        current_weight = self.weights.get(project, 1.0)
        
        if latency > 300:
            # Decay
            new_weight = max(0.1, current_weight * 0.9)
            logger.warning(f"📉 SYNAPSE DECAY: {project} (Latency {latency:.1f}ms) -> Weight {new_weight:.2f}")
            if new_weight < 0.3:
                 TelemetryQueue.push_event(TelemetryEventType.PERFORMANCE_KNOB, {
                    'event': 'SYNAPTIC_DROPOUT',
                    'project': project,
                    'suggestion': 'LOCAL_MIRRORING'
                })
        elif latency < 50:
            # Boost
            new_weight = min(2.0, current_weight * 1.1)
            # Only log significant boosts
            if new_weight > 1.5 and current_weight <= 1.5:
                logger.info(f"🚀 SYNAPSE BOOST: {project} is fast ({latency:.1f}ms)")
        else:
            return # Stable
            
        self.weights[project] = new_weight
        self._save_weights()
