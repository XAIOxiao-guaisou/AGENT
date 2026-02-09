
import sys
import importlib
import logging
from pathlib import Path
from typing import Any
from antigravity.core.fleet_manager import ProjectFleetManager
try:
    from antigravity.infrastructure.delivery_gate import DeliveryGate
except ImportError:
    DeliveryGate = None

logger = logging.getLogger("antigravity.loader")

class ProjectSecurityError(ImportError):
    pass

class FleetModuleLoader:
    """
    The Synapse of Antigravity.
    Enables authorized, integrity-verified cross-project imports.
    """
    
    @staticmethod
    def load_fleet_module(target_project_id: str, module_name: str) -> Any:
        """
        Dynamically load a module from another project in the fleet.
        Phase 22: Optimized Synapse.
        """
        fleet_mgr = ProjectFleetManager.get_instance()
        
        # 1. Locate Project
        project_meta = fleet_mgr.projects.get(target_project_id)
        if not project_meta:
            raise ImportError(f"Fleet project '{target_project_id}' not found.")
            
        project_root = Path(project_meta.path).resolve()
            
        # 2. Physical Anchor
        FleetModuleLoader._verify_physical_anchor(target_project_id, project_root, fleet_mgr)

        # 3. Mount Synapse
        return FleetModuleLoader._mount_synapse(target_project_id, module_name, project_root)

    @staticmethod
    def _verify_physical_anchor(project_id: str, project_root: Path, fleet_mgr: ProjectFleetManager):
        """Phase 13.5: Merkle Verification Logic"""
        if DeliveryGate:
            try:
                gate = DeliveryGate(project_root)
                if not gate.verify_integrity():
                    logger.critical(f"🛑 BLOCKED: Physical Anchor Validation Failed for '{project_id}'")
                    raise ProjectSecurityError(f"Security Block: {project_id} TAMPERED.")
            except Exception as e:
                # Fail Secure Catch-all
                if isinstance(e, ProjectSecurityError): raise
                logger.error(f"Physical Anchor Error for {project_id}: {e}")
                integrity = fleet_mgr.verify_fleet_integrity(project_id)
                if integrity.get('status') in ['TAMPERED', 'CONTAMINATED']:
                    raise ProjectSecurityError("Security Block: Cached status is COMPROMISED.")
        else:
             # Fallback
             integrity = fleet_mgr.verify_fleet_integrity(project_id)
             if integrity.get('status') in ['TAMPERED', 'CONTAMINATED']:
                 raise ProjectSecurityError("Security Block: Cached status is COMPROMISED.")

    @staticmethod
    def _mount_synapse(project_id: str, module_name: str, project_root: Path) -> Any:
        """Phase 22: Module Mounting Logic"""
        virtual_pkg = f"fleet.{project_id}"
        virtual_module_name = f"{virtual_pkg}.{module_name}"
        
        if virtual_module_name in sys.modules:
            return sys.modules[virtual_module_name]
            
        import time
        from antigravity.infrastructure.telemetry_queue import TelemetryQueue, TelemetryEventType
        
        start_t = time.perf_counter()
        
        try:
            module_rel_path = module_name.replace('.', '/') + ".py"
            module_file = project_root / module_rel_path
            
            if not module_file.exists():
                module_file = project_root / module_name.replace('.', '/') / "__init__.py"
                if not module_file.exists():
                     raise ImportError(f"Module '{module_name}' not found in '{project_id}'")
            
            logger.info(f"🧠 Neural Nexus: Mounting {virtual_module_name}...")
            spec = importlib.util.spec_from_file_location(virtual_module_name, module_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[virtual_module_name] = module
                spec.loader.exec_module(module)
                
                # Telemetry
                elapsed = (time.perf_counter() - start_t) * 1000
                if elapsed > 300:
                    TelemetryQueue.push_event(TelemetryEventType.PERFORMANCE_KNOB, {
                        'event': 'SYNAPTIC_DRAG', 'project': project_id,
                        'latency_ms': elapsed, 'suggestion': 'LOCAL_MIRRORING'
                    })
                
                logger.info(f"✅ Synapse Established: {virtual_module_name}")
                return module
            else:
                 raise ImportError(f"Failed to create spec for {module_file}")
        except Exception as e:
            logger.error(f"Synapse Failure: {e}")
            raise
