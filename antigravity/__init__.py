"""
Antigravity v1.0.0 - The Awakened Sheriff Brain

4-Layer Architecture with Transparent Forwarding
"""

# CORE LAYER - Task orchestration and execution
from .core.mission_orchestrator import MissionOrchestrator
from .core.autonomous_auditor import AutonomousAuditor
from .core.local_reasoning import LocalReasoningEngine

# SERVICES LAYER - Quality assurance and semantic processing
from .services.sheriff_strategist import SheriffStrategist
from .core.context_compressor import ContextCompressor
from .services.rca_immune_system import RCAImmuneSystem
from .services.precision_healer import PrecisionHealer
# from .services.quality_tower import QualityTower  # Removed: Functional module, not a class
from .services.healing_executor import HealingExecutor
from .services.shadow_validator import ShadowValidator
from .services.dependency_analyzer import DependencyAnalyzer
from .services.context_manager import ContextManager

# INFRASTRUCTURE LAYER - Security, persistence, and telemetry
from .infrastructure.delivery_gate import DeliveryGate
from .infrastructure.telemetry_queue import TelemetryBuffer
from .infrastructure.p3_state_manager import P3StateManager
from .infrastructure.file_lock_manager import FileLockManager
from .infrastructure.audit_history import AuditHistoryManager
from .infrastructure.state_manager import StateManager
from .infrastructure.monitor import AntigravityMonitor as Monitor
from .infrastructure.performance_monitor import PerformanceMonitor

# INTERFACE LAYER - User interaction and visualization
# Note: Dashboard and UI components are imported directly when needed

# UTILS LAYER - Configuration and utilities
from .utils.config import CONFIG as Config
from .utils.vibe_check import VibeChecker as VibeCheck
# from .utils.env_checker import EnvChecker
# from .utils.p3_root_detector import P3RootDetector

# Version info
__version__ = "1.0.0"
__status__ = "Production"

# Transparent forwarding ensures backward compatibility
# External code can still use: from antigravity import AutonomousAuditor
# This maintains API stability despite internal reorganization

__all__ = [
    # Core
    "MissionOrchestrator",
    "AutonomousAuditor",
    "LocalReasoningEngine",
    # Services
    "SheriffStrategist",
    "ContextCompressor",
    "RCAImmuneSystem",
    "PrecisionHealer",
    # "QualityTower",  # Removed
    "HealingExecutor",
    "ShadowValidator",
    "DependencyAnalyzer",
    "ContextManager",
    # Infrastructure
    "DeliveryGate",
    "TelemetryBuffer",
    "P3StateManager",
    "FileLockManager",
    "AuditHistoryManager",
    "StateManager",
    "Monitor",
    "PerformanceMonitor",
    # Utils
    "Config",
    "VibeCheck",
    # "EnvChecker",
    # "P3RootDetector",
]
