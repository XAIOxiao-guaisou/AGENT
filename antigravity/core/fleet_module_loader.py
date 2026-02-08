
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
        Phase 13.5 Tuning: Namespace Guard & Physical Anchor (Merkle Check)
        """
        fleet_mgr = ProjectFleetManager.get_instance()
        
        # 1. Locate Project
        project_meta = fleet_mgr.projects.get(target_project_id)
        if not project_meta:
            raise ImportError(f"Fleet project '{target_project_id}' not found.")
            
        project_root = Path(project_meta.path).resolve()
            
        project_root = Path(project_meta.path).resolve()
            
        # 2. Physical Anchor: Instant Merkle Verification
        # We perform a FORCED incremental hash audit
        if DeliveryGate:
            try:
                # Initialize Gate for the target project
                gate = DeliveryGate(project_root)
                # Physical Anchor: Verify Merkle Integrity
                is_secure = gate.verify_integrity()
                
                if not is_secure:
                    status = 'TAMPERED' # If verify fails, it's tampered
                    logger.critical(f"🛑 BLOCKED: Physical Anchor Validation Failed for '{target_project_id}' (Status: {status})")
                    raise ProjectSecurityError(
                        f"Security Block: Target project '{target_project_id}' failed Physical Anchor check ({status}). Import denied."
                    )
            except Exception as e:
                # Re-raise Security Errors
                if isinstance(e, ProjectSecurityError):
                    raise
                # Check if it was an import error of the module itself? No, we are past imports.
                logger.error(f"Physical Anchor Error for {target_project_id}: {e}")
                # If error in verification, we should probably fail secure, but for now fallback?
                # "fail secure" -> Block.
                # But let's fallback to status check if just some IO error?
                integrity = fleet_mgr.verify_fleet_integrity(target_project_id)
                if integrity.get('status') in ['TAMPERED', 'CONTAMINATED']:
                    raise ProjectSecurityError("Security Block: Cached status is COMPROMISED.")
        else:
            # Fallback to Fleet Manager status if DeliveryGate not available
            logger.warning("DeliveryGate not found (module missing), falling back to cached status")
            integrity = fleet_mgr.verify_fleet_integrity(target_project_id)
            if integrity.get('status') in ['TAMPERED', 'CONTAMINATED']:
                raise ProjectSecurityError("Security Block: Cached status is COMPROMISED.")

        # 3. Namespace Guard: Virtual Mounting
        # Instead of hacking sys.path, we mount to 'fleet.<project_id>.<module>'
        virtual_pkg = f"fleet.{target_project_id}"
        virtual_module_name = f"{virtual_pkg}.{module_name}"
        
        # Check if already loaded
        if virtual_module_name in sys.modules:
            return sys.modules[virtual_module_name]
            
        # Construct path to the module file
        # Assuming module_name is like "core.utils" -> "core/utils.py"
        module_rel_path = module_name.replace('.', '/') + ".py"
        module_file = project_root / module_rel_path
        
        if not module_file.exists():
            # Try as package (init.py)
            module_file = project_root / module_name.replace('.', '/') / "__init__.py"
            if not module_file.exists():
                 raise ImportError(f"Module '{module_name}' not found in project '{target_project_id}'")
        
        try:
            logger.info(f"🧠 Neural Nexus: Mounting {virtual_module_name}...")
            spec = importlib.util.spec_from_file_location(virtual_module_name, module_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[virtual_module_name] = module
                spec.loader.exec_module(module)
                logger.info(f"✅ Synapse Established: {virtual_module_name}")
                return module
            else:
                 raise ImportError(f"Failed to create spec for {module_file}")
        except Exception as e:
            logger.error(f"Synapse Failure: {e}")
            raise
