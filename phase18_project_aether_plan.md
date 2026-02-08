# Phase 18: Project Aether - Auto-Refactor Plan

## Goal
Achieve "Symbiotic Evolution" by automating redundancy detection and cleanup, and enforcing real-time synaptic telemetry.

## User Review Required
-   **Auto-Deletion**: The system will attempt to DELETE code in the Shadow Kernel if a fleet capability matches > 0.95. This is a high-risk operation guarded by the Consensus Engine.
-   **Synaptic Latency**: New metric `SYNAPTIC_LATENCY` will appear in telemetry.

## Proposed Changes

### [antigravity/core/local_reasoning.py]
#### [MODIFY] `LocalReasoningEngine.draft_plan`
-   **Validation**: When `find_fleet_capability` score > 0.95:
    1.  Trigger `REDUNDANCY_DETECTED` event.
    2.  Suggest `files_to_modify` to REMOVE the local redundant code.
    3.  Inject `fleet` dependency.

### [antigravity/core/fleet_module_loader.py]
#### [MODIFY] `FleetModuleLoader.load_module`
-   **Telemetry**: Measure start/end time of import.
-   **Push**: `TelemetryQueue.push_metric('SYNAPTIC_LATENCY', duration)`.

### [antigravity/core/mission_orchestrator.py]
#### [MODIFY] `MissionOrchestrator._transition_to_done`
-   **Iron Sync**:
    1.  Update `task.md` line for task_id.
    2.  Execute `git push --tags`.

## Verification Plan

### Test Script: `aether_demo.py`
-   **Scenario**:
    -   Create a local file `my_crypto.py` with identical logic to `vortex_core.crypto`.
    -   Task: "Refactor my_crypto.py to use fleet".
    -   Expectation:
        -   Shadow Kernel DELETES `my_crypto.py`.
        -   Shadow Kernel creates `main.py` importing `fleet.vortex_core`.
        -   Consensus Engine APPROVES.
