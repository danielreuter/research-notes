---
lane: coordinator
kind: handoff
from: x4-sha256-fill
created: 2026-09-25T19:36Z
---

# merge-ready lane/x4-sha256-fill @ 8edb8000: PINS row bf16-ampere-x4+sha256 (A100 gate passed); red-team class grant requested; A100 cell capped at 4096

## Merge
- Tip `lane/x4-sha256-fill` @ 8edb8000 (base origin/main cd963fd4), one commit: `backends/ligero-verify/src/leaf.rs` PINS row
  `("bf16-ampere-x4", "sha256", a862f7a0…94e5, 848a99cd…9326)`. Rust only, no Python or statement change.
- Evidence r20260925-175055-0792 (vy-x4-sha256-a100, A100-SXM4-80GB, tree cd963fd4): fixture m = 90,165 rows/col, L 2,964,
  Q 126,595, pins 35; gate 2048 VUs, **13 honest sub-batches + 86 negatives, 0 failures**; sha256 conformance on bf16-ampere-x4
  8 passed, 1 skipped (11.6 min). The pod's `system-digest` of the proved system gives the pinned pair.
- Tests: `cargo test --release` in backends/ligero-verify 34 + 8 + 27 pass (VM). On the pod, the rebuilt verifier from 8edb8000
  reports `system pinned (bf16-ampere-x4+sha256)` and 25/25 ACCEPT at 2^-128.05 on the 4096 cell's dump (r20260925-192613-398d).
- Behaviour change: bf16-ampere-x4+sha256 statements go from "no pinned hashed system" (reject) to pinned.

## Red team: class grant request for bf16-ampere-x4+sha256
Same `sha256/row/v1` gadget and `hashchain.compose` as the granted fp8-ada-x4+sha256 (da74b03e) and bf16-hopper-x4+sha256; the
new part is the BF16 Ampere x4 relation under it. Please route to a red-team lane for the COMPLETE_ZK_BACKEND class
(the relation's declared class); the cell stays provisional until then.

## A100 cell capped at 4096 (instance set)
The frozen `bench-instances/v1` `vu-k1536` set holds 4,096 instances and has no generator stream: the first sweep
(r..0792, l4096 p4) ran 8192 and 16384 by repeating instances (the harness warned; equiv refused at 16384). Those points are
out (rule I / admissibility 3). The A100 cell is the 4096 point, re-measured on 8edb8000 with its proof dump (r..398d); its
instances field IS the frozen ref (range [0, 4096), manifest 059103cf…). For reference only (repeats), the throughput was
flat anyway: 4096 1842, 8192 1737, 16384 1859 VU/s. If the A100 line should sweep past 4096 it needs a generated stream
for vu-k1536 (a user/spec decision, not mine).
