# E2E Hell-Level Tests

E2E stress testing suite for Sheriff Brain Phase 21.

## Tests

1. **test_topology_collapse.py** - 50+ modules with 7-layer circular dependencies
2. **test_tamper_pulse.py** - 1000 files with 5 changes/sec tampering
3. **test_telemetry_flood.py** - 10 concurrent agents producing 1000 msg/s

## Usage

Run all tests:
```bash
python tests/e2e/run_all_tests.py
```

Run individual tests:
```bash
python tests/e2e/test_topology_collapse.py
python tests/e2e/test_tamper_pulse.py
python tests/e2e/test_telemetry_flood.py
```

## Requirements

- Python 3.8+
- psutil
- All antigravity modules

Install dependencies:
```bash
pip install psutil
```
