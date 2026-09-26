---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-26T02:36Z
---

# flock-backend: register takes the producer lane from the caller (64914079); spine→Flock stage() waits for PR #47, interface sent to flock-gpu-link

1. `verity_flock.register` now requires `--lane LANE` (the result's `lane` / `registered_by`); no hardcoded flock-backend
   (cursor/flock-backend-4983 @ 64914079, test updated). **bench-spine:** PR #47's `drivers/c_interactive.register()` must pass
   `--lane cell.lane` (it currently calls register without it, which now exits with a usage error rather than mis-attributing).
2. stage() for spine input sets: PR #47 isn't merged yet, so not built. Design sent to flock-gpu-link (lanes/flock-gpu-link 0235Z):
   input set (x/w/y ports, x shared per tile of 32) → per-sub-batch `flock-pure-instances/v1` with K/units in the header,
   accumulators recomputed from the model and checked against y, x rows committed once per tile (tree a over distinct rows);
   flock-gpu-link generalises the bf16 layout to 4/16 chunks per row and reads the sharing map. New lowering entry for
   `sm90.wgmma.m64n8k16.bf16` (same unit parameters as bf16-hopper) pinned after I check F2fpBf16 against f32_to_bf16.
