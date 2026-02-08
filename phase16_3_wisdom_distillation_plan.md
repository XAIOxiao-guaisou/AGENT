# Phase 16.3: Wisdom Distillation & Comm Cleanup Plan

## Goal
Eliminate Protobuf UTF-8 errors and perform a global "Wisdom Distillation" (Knowledge Graph Scan) of the entire fleet.

## User Review Required
-   **Regex Sanitization**: Will apply strictly `re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)` to all node names and docstrings.
-   **GKG Location**: The active GKG is in `~/.antigravity`. For the "Git Mirror Audit", I will copy the generated JSON to `antigravity/infrastructure/fleet_knowledge_graph.json` and commit it.

## Proposed Changes

### [antigravity/core/knowledge_graph.py]
#### [MODIFY] `FleetKnowledgeGraph._scan_public_api`
-   **Constraint**: Add explicit `if not file_path.suffix == '.py': continue`.
-   **Sanitization**:
    -   Import `re`.
    -   Apply `re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)` to `node.name` and `docstring`.
    -   Ensure `sanitize_for_protobuf` is also used.

### [NEW] `wisdom_scan.py`
-   **Purpose**: Trigger `scan_fleet_wisdom`.
-   **Logic**:
    1.  Load `ProjectFleetManager` to identify projects.
    2.  Invoke `FleetKnowledgeGraph.scan_fleet_wisdom(metrics)`.
    3.  Copy result to repo.
    4.  Print success.

## Verification Plan

### Automated Test (`wisdom_scan.py`)
-   Run `python wisdom_scan.py`.
-   Verify output contains `🧠 Neural Nexus: Indexing complete`.
-   Verify json file exists and contains sanitized strings.

### Manual Audit
-   Check `antigravity/infrastructure/fleet_knowledge_graph.json` for non-ASCII control characters.
-   Git commit and push.
