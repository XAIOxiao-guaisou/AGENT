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
        Phase 26: Predictive Mirroring.
        Trend analysis + Proactive Suggestions.
        """
        metric = event.get('metric')
        if metric != 'SYNAPTIC_LATENCY':
            return
            
        project = event.get('project')
        latency = event.get('latency_ms', 0)
        
        # 1. Update Trend (Simple Moving Average simulation)
        # In real DB we'd query history. Here we use current weight as proxy for history?
        # No, let's keep a transient history in memory?
        # For simplicity in this file-based system, we just trust the spot latency 
        # but apply the formula: W_new = (1 - beta) * W_old + beta * (T_thresh / T_obs)
        
        current_weight = self.weights.get(project, 1.0)
        
        # Predictive Threshold
        if latency > 250:
            logger.warning(f"🔮 PREDICTION: {project} latency ({latency}ms) approaching critical mass.")
            TelemetryQueue.push_event(TelemetryEventType.PERFORMANCE_KNOB, {
                'event': 'PREDICTIVE_MIRROR_SUGGESTION',
                'project': project,
                'reason': f'Latency Trend > 250ms (Current: {latency})'
            })

        # Beta for smoothing (0.2 means we trust new data 20%)
        beta = 0.2
        t_threshold = 300.0
        
        # Avoid division by zero
        t_observed = max(latency, 1.0)
        
        # Formula: Inverse relationship. Higher latency -> Lower weight.
        # If latency is 600ms (2x threshold), ratio is 0.5.
        # If latency is 50ms (1/6 threshold), ratio is 6.0.
        
        performance_ratio = t_threshold / t_observed
        
        # Clamp ratio to avoid explosion? 
        # If latency 1ms -> ratio 300. That's too high. Cap at 2.0.
        performance_ratio = min(2.0, performance_ratio)
        # Cap low end to 0.1
        performance_ratio = max(0.1, performance_ratio)
        
        new_weight = (1 - beta) * current_weight + beta * performance_ratio
        
        logger.info(f"⚖️ SYNAPSE TUNE: {project} | Latency {latency}ms | Weight {current_weight:.2f} -> {new_weight:.2f}")
            
        self.weights[project] = new_weight
        self._save_weights()
