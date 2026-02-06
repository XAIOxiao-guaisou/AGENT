# Antigravity Phase 2: Agent Takeover (Optimized)

## 1. Core Architecture Refactor
- [ ] **Auditor -> Executor Transformation (`auditor.py`)**:
    - [ ] **Sheriff-1 Prompt Upgrade**: Switch to "Full Coverage" mode. Require entire file rewrite with robust logic.
    - [ ] **Robust Code Extractor**: Implement `_extract_code()` to handle markdown blocks and disable explanations.
    - [ ] **Self-Reflection**: Add "Self-Check" step in `audit_and_fix()` to verify against `PLAN.md` before writing.
- [ ] **Monitor Active Intervention (`monitor.py`)**:
    - [ ] **Event Filter**: Trigger takeover on "Empty File" or "Placeholder".
    - [ ] **Execution Lock**: Implement `execution_lock` to prevent recursive loops during Agent writes.
    - [ ] **Smart Retry Loop**: Feed test logs/tracebacks back to DeepSeek for targeted fixing.
- [ ] **Test Runner Loop (`test_runner.py`)**:
    - [ ] **Boolean Feedback**: Return `True/False` status codes.
    - [ ] **Test Isolation**: Ensure clean environment before tests.

## 2. Configuration & Safety
- [ ] **Config Center (`config/settings.json`)**:
    - [ ] Manage `DEEPSEEK_API_KEY`, `TEMPERATURE`, `MAX_TOKENS`.
    - [ ] Add `PROTECTED_PATHS` (White-list) to prevent Agent from modifying core system files.
- [ ] **Environment Pre-check (`env_checker.py`)**:
    - [ ] Auto-detect dependencies (e.g., `playwright`) demanded by `PLAN.md`.

## 3. State & Observability
- [ ] **Execution History**:
    - [ ] Log full "Think-Write-Test-Fail-Fix" chain in `vibe_audit.log`.
- [ ] **Dashboard Update (`dashboard.py`)**:
    - [ ] **Diff Viewer**: Show "Before" vs "Agent Generated".
    - [ ] **Retry Progress**: Show current retry attempt count.

## 4. Generic Takeover Workflow (Real-world Test)
- [ ] **Trigger**: User creates `PLAN.md` + empty `src/target.py`.
- [ ] **Loop**:
    - Agent detects empty file -> Gens Code -> Runs Test -> Fails -> Refines -> Passes.
