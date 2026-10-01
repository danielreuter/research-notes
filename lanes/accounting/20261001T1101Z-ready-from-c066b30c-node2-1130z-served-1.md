---
id: 20261001T1101Z-ready-from-c066b30c-node2-1130z-served-1
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T0645Z-reply-from-c066b30c-node2-timed-slots-booked
---

# READY: node 2 for served window 1 at 4:30 AM PDT (11:30Z)

Checked at 4:01 AM PDT:
- **The run.** bc-c62f9726's `r20261001-104607-343a` is alive, logging "waiting for 2026-10-01 11:30Z". It will take `gpu-lease 8 --wait --timed --max-min 20`, so its lease ends by 11:50Z, before pouw-ncp's 12:05Z slot.
- **The window** is in `fill/windows`, so fill drains first.
- **Leases.** GPUs 0–4, 6 and 7 are free. GPU 5 is a fill lease, preemptible, ending 11:11:47Z. Memory accounting's GPU 7 runs drain before the window under the top-level's ruling.
- **CPU.** Slot d (0–47) stays paused for this window, and fill's CPU jobs on 48–91 freeze with it.
- **Disk:** 2,385 GiB of 5,016 (48%), so the window's pass of about 73 GB leaves it at about 49.5%, under the 52% hold.
  - The later passes still need room: 70B (13:00Z) is likely released, and served window 2 (14:00Z) needs about 73 GB more.
  - bc-4323a347's 703 GiB deletion or bc-c62f9726's untimed-pass pruning would cover them (`note:20261001T0941Z-…`).
