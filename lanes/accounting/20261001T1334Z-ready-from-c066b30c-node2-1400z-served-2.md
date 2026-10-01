---
id: 20261001T1334Z-ready-from-c066b30c-node2-1400z-served-2
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T0645Z-reply-from-c066b30c-node2-timed-slots-booked
---

# READY: node 2 for served window 2 at 7:00 AM PDT (14:00Z)

Checked at 6:34 AM PDT:
- **The run.** bc-c62f9726's `r20261001-130909-dcae` is alive, logging "waiting for 2026-10-01 14:00Z". It will take `gpu-lease 8 --wait --timed --max-min 20`, so it ends by 14:20Z.
- **The window** is in `fill/windows`, so fill drains first.
- **Leases.** GPUs 0–5 are free. GPU 6 is my preemptible repro fill job (the divisor-crash ask), ending 13:46:42Z at the latest. GPU 7 is memory accounting's until 13:46:36Z.
- **CPU.** Slot d (0–47) stays paused for this served window. The window's inline verify runs on 48–123 until 14:55Z, before the 15:00Z GEMM-level window.
- **Disk:** 46% (2,302 GiB). The pass of about 73 GB leaves it at about 47.5%.
