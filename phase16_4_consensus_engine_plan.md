# Phase 16.4: Consensus Engine & Comm Shield Plan

## Goal
Establish a "Consensus Engine" to validate Shadow Kernel predictions against physical reality and reinforce the Telemetry Shield to prevent non-printable characters from crashing the dashboard.

## User Review Required
-   **Telemetry Shield**: Will use strict `value = "".join(c for c in value if c.isprintable()).encode('utf-8', 'replace').decode('utf-8')` for all string telemetry.
-   **Consensus Logic**: If `validate_shadow_prediction` returns `False`, the `MissionOrchestrator` must ABORT the task.

## Proposed Changes

### [antigravity/infrastructure/telemetry_queue.py]
#### [MODIFY] `TelemetryQueue._push_to_buffer`
-   **Sanitization**: Iterate over `event_data` values. If value is string, apply the printable filter.

### [antigravity/core/local_reasoning.py]
#### [NEW] `validate_shadow_prediction`
-   **Args**: `task_id`, `prediction` (dict with lines, hash, content).
-   **Logic**:
    1.  Parse `prediction['simulated_content']`.
    2.  Verify it is valid Python (AST parse).
    3.  Verify it has non-zero length.
    4.  Return `True` if valid, `False` otherwise.

### [antigravity/core/mission_orchestrator.py]
#### [MODIFY] `MissionOrchestrator.step`
-   **Integration**: After `shadow_kernel.simulate_write`, call `local_reasoning.validate_shadow_prediction`.
-   **Abort**: If invalid, print "❌ CONSENSUS FAILURE" and do NOT transition to `EXECUTING`.

### [chronos_demo.py]
#### [MODIFY] `chronos_demo.py`
-   **Test Case**: Inject a "Bad Prediction" (invalid syntax) to verify proper rejection.

## Verification Plan

### Automated Test (`chronos_demo.py`)
-   Run `python chronos_demo.py`.
-   Verify "Bad Prediction" triggers `❌ CONSENSUS FAILURE`.
-   Verify "Good Prediction" still passes.

### Telemetry Stress Test
-   Run `python tests/e2e/test_telemetry_flood.py` (simulating garbage data).
-   Ensure no crashes in `telemetry_queue.py`.
