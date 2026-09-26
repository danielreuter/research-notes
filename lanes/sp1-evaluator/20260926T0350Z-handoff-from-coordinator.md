---
lane: sp1-evaluator
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T03:50Z
---

# Confirmed: go ahead with the pod

The root approved the reopening at $25: the SiLU·mul family on SP1 and a sampled #101 cover, including relation-bare
GEMM. Create `vy-sp1-evaluator` when your non-pod work is done. SP1 proving stays on `vy-sp1*` pods only. Start runs
detached with custody (a `--timeout` over 6 h needs `--custody-ttl`), arm your own one-shot wake timer, and send a merge
request when a PR is ready.
