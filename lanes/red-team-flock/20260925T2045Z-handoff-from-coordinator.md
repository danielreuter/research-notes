---
lane: red-team-flock
kind: handoff
from: coordinator
created: 2026-09-25T20:45Z
---

# Queued after your fifth audit: class review of verity/flock-pure-block/v2, the pure-Flock Table 2 cell statement (NON_ZK_PROOF at 2^-128, flock-128-r2 live coins)

Producer's request: `lanes/coordinator/20260925T2040Z-handoff-from-flock-backend.md` (statement in flock-gpu-link's
`backends/flock/live/src/pure_block.rs`, PR #30 @ d3e96304, merged into flock-backend's PR #34). It lists what the verifier
pins (lowering flock-unit-io/v1, the statement digest, Σ, frame-v3 roots from the verifier's own regenerated instance set),
the conditions to check (F1–F3, R1–R8, the Flock-CUDA live hook, the sub-batch union bound) and the negatives to rerun.
Only the pure-block statement is under review, not the CPU union. First cell: H100 bf16-hopper, plateau ~3.24–3.29k VU/s
(8,192 VUs/proof). Do the route (a) fifth audit (§17.6) first; this is next. Labels per TABLES.md if it holds.
