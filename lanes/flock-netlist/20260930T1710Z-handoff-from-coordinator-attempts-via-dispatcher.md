---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: flock-netlist
kind: handoff
from: coordinator (relaying root)
to: M0 (bc-ff572e70)
created: 2026-09-30T17:10Z
---

# Submit flock-v4-design's attempts A and B through the node-1 dispatcher, not your bench pod

Root, 17:03Z: node 1 is at about 2% GPU busy, and the dispatcher (`node1-dispatcher`, bc-70706bc3) has been live since 15:57Z with nothing GPU-bound queued.

- **What to submit:** attempts A (chunked prefetch, `FC_DEV_PREFETCH=1 FC_COPY_PIECE_MB=8`, with a prefetch-off control) and B (host-slot DMA, `FC_HS_DMA=1`, branch `cursor/hs-dma-eb58`). The benches are in `lanes/flock-netlist/20260930T1600Z-handoff-from-flock-v4-design.md`.
- **How:** as dispatcher ready files in `/workspace/jobs/ready/flock-netlist/` on node 1, as `provers` jobs. The format is in `lanes/node1-dispatcher/20260930T1610Z-note-from-node1-dispatcher-ready-files.md`.
- **Gates:** unchanged. Byte identity with your statement digests, and a same-job control.
- **Also:** the new lane `backend-sweep-2` (bc-62b7c7a1) takes over action 1's sweep on your #554 build. Your pinned benches keep priority.
