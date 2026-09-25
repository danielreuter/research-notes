---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T05:00Z
---

# agkr integration ready: a2edab4d

`lane/agkr-bound` at **a2edab4d** is the integration of `lane/agkr-fp8` a97576b5, merged first as 4a3aeb04, and `lane/agkr-nvf4`
c97d2ad2. Both came in by merge, not rebase, on base main baeefd21. Six files conflicted, and I resolved them as follows:

- `field.py`, `kernels.py`, `logup.py`, `prover.py`: take agkr-nvf4's additions (`lookup_mults`, the gate_eval wire CSRs).
- `ligero.open_w_qc_eval`: keeps agkr-fp8's row-chunked opening on parts under 40 GB, with agkr-nvf4's `row_code_dot split=64`.
- `bench_result.py`: agkr-nvf4's fp4-nvf4 branch wraps agkr-fp8's FP8-aware BF16/E4M3 branch.

Evidence is art:c347036b (gate-log/v1). It comes from run r20260925-042709-74f0 on my A100 pod vy-agkr-bound, using
`git archive a2edab4d` and the script `lanes/agkr-bound/evidence/pod-scripts/01_integration.sh`.

- The Rust verifier: `cargo test --release` passes 8/8.
- The `backends/gkr` Python tests:
  - gpu/v2/tests: 16 passed.
  - packed/tests: 38 passed, 9 skipped.
  - tensor/tests: 21 passed, 1 skipped.
  - tensor/fused/tests: 8 passed, 17 skipped.
- One bench_result cell per relation family at 4096 VUs, 1 rep. Every proof sha256 equals the verified cell's, and the Python
  and Rust verifiers accept each one:

| cell | verified cell | proof sha256 | t.total on A100 (1 rep) |
|---|---|---|---|
| bf16-ampere (default path) | art:300a526a | f2c05851… | 0.954 s |
| bf16-hopper | art:c09947fd | 4a05ada6… | 0.746 s |
| fp8-hopper | art:ad76c106 | 0021aa91… | 0.409 s |
| fp4-nvf4 | art:f277786d | ebe7c545… | 0.307 s |

The A100 times are not Table 2 cells. The rows' SKUs differ, except for bf16-ampere, and even that one is a single rep.

Nothing is merged into main. The lane continues on step 2, operands bound. Its first commits are 6b39234e and 082866ff, and a
separate handoff follows when its results are registered.
