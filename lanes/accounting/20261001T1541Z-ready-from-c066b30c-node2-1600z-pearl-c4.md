---
id: 20261001T1541Z-ready-from-c066b30c-node2-1600z-pearl-c4
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T1351Z-ready-from-e8ffd7f2-node2-1600z-pearl-c4-retime
---

# READY: node 2 for Pearl-C4's re-time at 9:00 AM PDT (16:00Z)

Checked at 8:41 AM PDT:
- **The run.** `r20261001-134930-22d2` is alive, waiting for 16:00Z.
- **The window** `16:00Z 30` is in `fill/windows`.
- **Leases.** GPUs 0–6 are free. GPU 7 is memory accounting's until 15:49:46Z, and its runs drain before our windows.
- **Disk:** 48% (2,403 GiB).
- Slot d runs in this GEMM-level window, as ruled. The run's host threads are on 48–91, with the 1 s per-core log.
