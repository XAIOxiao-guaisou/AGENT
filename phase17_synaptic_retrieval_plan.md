# Phase 17: Synaptic Retrieval Plan

## Goal
Empower the Consensus Engine to actively search the Fleet Knowledge Graph (GKG) for existing capabilities matching the user's intent, and automatically inject them into the execution plan.

## User Review Required
-   **Auto-Injection**: If a high-confidence match (>0.85) is found in the GKG, the system will automatically add it to the task dependencies.
-   **Synapse Test**: Verification will require a multi-project setup simulation.

## Proposed Changes

### [antigravity/core/local_reasoning.py]
#### [MODIFY] `LocalReasoningEngine.draft_plan`
-   **Logic Injection**:
    1.  Extract `intent.primary_goal`.
    2.  Call `FleetKnowledgeGraph.find_fleet_capability(intent)`.
    3.  If match found (simulated for now or real if GKG ready):
        -   Add to `plan['dependencies']`.
        -   Log `🧠 SYNAPSE: Found capability '{match}' in fleet.`

### [antigravity/core/mission_orchestrator.py]
#### [MODIFY] `MissionOrchestrator.step` (PREDICTING state)
-   **Enhancement**:
    -   Before Shadow Simulation, check if `task.dependencies` can be satisfied by Fleet.
    -   This might be part of `draft_plan` usage effectively.

## Verification Plan

### Test Script: `synapse_demo.py`
-   **Scenario**: Task "Encrypt User Data".
-   **Expectation**:
    -   Intent: "encrypt data".
    -   GKG Search: Finds `vortex_core.crypto.encrypt`.
    -   Plan: Includes `import vortex_core.crypto`.
    -   Output: `🧠 SYNAPSE: Auto-linked [vortex_core] for 'encryption'`.

