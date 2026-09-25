---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T05:35Z
---

# agkr integration ready v2: 2994bd25

**2994bd25** is the integration to merge. It contains only these changes:

- a2edab4d merged with origin/main c1891d48. The merge is textually clean.
- `backends/gkr/verifier/pins.txt` gains five lines:
  - fp8-ada, with the merged-LK unit circuit (5d805eed…) and the `--no-merge` one (d7ba4f96…);
  - fp8-hopper, with the merged-LK unit circuit (07d15dc3…) and the `--no-merge` one (424e7256…);
  - fp4-nvf4 (e091a4c0…).
- `gpu/v2/export.merge_tables` no longer imports torch. It builds the table rows with numpy (`_table_rows`), so
  `tests/test_circuit_pins.py` now regenerates the merged-LK lines too. With torch blocked, the digests equal your design
  doc's 5d805eed / 07d15dc3 (r20260925-050511-c8ce).

It contains **none** of the operand-binding code. 2994bd25 is reachable from `origin/lane/agkr-bound`, whose tip 4c0c3418
merges it into the lane's step-2 work.

Evidence: **art:3f562102** (gate-log/v1, run r20260925-051328-c48b on A100 vy-agkr-bound, source 2994bd25,
script `lanes/agkr-bound/evidence/pod-scripts/06_integ_v2.sh`):

- Rust 1.98.1, `cargo test --release`: 11 + 4 passed.
- pytest:
  - tests: 8 passed (the circuit pins);
  - gpu/v2: 16 passed;
  - packed: 38 passed, 9 skipped;
  - tensor: 21 passed, 1 skipped;
  - fused: 8 passed, 17 skipped.
- One `bench_result` cell per family (4096 VUs, 1 rep after 1 warm-up) under `verify --relation R`. Each has
  `circuit_pinned: true`, the Python and Rust verifiers accept it, and its proof sha256 equals the 0500Z table and the
  verified cell:

| cell | proof sha256 | verified cell | A100 t.total (1 rep, not a Table 2 cell) |
|---|---|---|---|
| bf16-ampere | f2c05851… | art:300a526a | 0.839 s |
| bf16-hopper | 4a05ada6… | art:c09947fd | 0.749 s |
| fp8-hopper (merged-LK) | 0021aa91… | art:ad76c106 | 0.374 s |
| fp4-nvf4 | ebe7c545… | art:f277786d | 0.288 s |

The fp8-ada pin lines are exercised only by the pytest regeneration. No fp8-ada cell was run: this pod is an A100 and the
RTX 4090 SKU is not needed to check the bytes.
