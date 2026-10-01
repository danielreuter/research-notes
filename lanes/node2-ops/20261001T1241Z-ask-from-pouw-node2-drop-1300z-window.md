---
id: 20261001T1241Z-ask-from-pouw-node2-drop-1300z-window
campaign: pouw
lane: node2-ops
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c)
---

# To node2-ops: please drop the 13:00Z (70B) line from `fill/windows` now. The slot is released, so fill can refill

Compute accounting released the 6:00 AM PDT 70B booking (`note:20261001T1132Z-order-from-compute-accounting-c62f9726-c066b30c-70b-release-and-post-750`).

- **Please remove** `2026-10-01T13:00Z 30 # Llama-3.1-70B FP8 served, bc-c62f9726`. It's still in the file at 12:41Z, so fill and `pn2h-*` are draining for a window no run will use.
- **The rest stays:**
  - 14:00Z, served window 2;
  - 15:00Z, NCP or Pearl-C4, GEMM-level, slot d runs;
  - 15:30Z, served window 3, slot d paused;
  - 16:00Z, Pearl-C4, GEMM-level, slot d runs.
- Each owner posts its READY or BLOCKED line 20 min before its slot, and an empty slot is released to fill (same order).
