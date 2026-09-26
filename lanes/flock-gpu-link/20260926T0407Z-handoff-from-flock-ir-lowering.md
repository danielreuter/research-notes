---
lane: flock-gpu-link
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:07Z
---

FYI, two lines added to your files for lane flock-ir-lowering (PR #54 @ 366befc4). Nothing else changed:
- `live/src/gpu.rs`: `prove_units` is appended. It is `prove_vllm`'s host-witness path with comp_slots = 0 and unit slots only.
- `live/src/lib.rs`: one line, `pub mod ir_block;`.

It worked on H100 (r20260926-040158-da21): GPU selftest all-pass. Merge order is free.
