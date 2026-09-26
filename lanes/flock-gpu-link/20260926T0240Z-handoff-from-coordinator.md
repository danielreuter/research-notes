---
lane: flock-gpu-link
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T02:40Z
---

# Your tip goes to main through flock-backend's integration

`cursor/flock-gpu-link-797a` @ 758a8edf conflicts with main (c79005af) in `live/src/gpu.rs` and `cuda/prove_chunk.cuh`,
against PR #41's `ChunkParams`. I've asked flock-backend to merge main plus your 758a8edf into its branch with one
`ChunkParams`: main's `sha256` flag name, with your `sha_mid` / `sha_pad` kept
(`lanes/flock-backend/20260926T0240Z-handoff-from-coordinator.md`). Then I gate and merge.

If you commit more before that lands, merge `origin/main` into your branch first, so the two integrations don't diverge.
Build the NVFP4 layout on the merged `ChunkParams`.
