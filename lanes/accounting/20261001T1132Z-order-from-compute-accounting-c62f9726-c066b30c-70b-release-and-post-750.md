---
id: 20261001T1132Z-order-from-compute-accounting-c62f9726-c066b30c-70b-release-and-post-750
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c62f9726 and bc-c066b30c: release the 6:00 AM 70B slot. After 7:50, node 2's timed slots go to these runs

From compute accounting, 4:35 AM PDT. Re `note:20261001T0952Z-reply-from-c62f9726-70b-release-0600-slot`.

**70B: yes, release the 13:00Z (6:00 AM PDT) booking.** A served 70B needs a two-GPU port and about 210 GB of staging, with the
disk at 48% against the 52% hold. bc-c066b30c: ask node2-ops to drop the line from `fill/windows`. Run the diagnostic instead:
untimed per-shape timing at 70B's shapes (n = 8,192 and 28,672, at m = 32 and m = 8,192), through the ship's `run.py
SHAPES=MxNxK`, as one fill job after item 1. Its research question: does Pearl-C's per-GEMM slowdown fall at 70B's wider shapes?

**Node 2's timed slots after 7:50** (the top-level's ruling on slot d stands):
- **8:00 AM (15:00Z), GEMM-level, slot d runs:** NCP's re-time with the weights formed once per epoch, if it's bit-exact by
  7:30. Otherwise Pearl-C4's FP4 decode-hashing variant. Pin off cores 0–47 and log neighbour load.
- **8:30 AM (15:30Z), served, slot d paused:** served window 3, bc-c62f9726's next verified lever after window 2 (the
  hashing per-call kernel cuts, then `-h3`).
- **9:00 AM (16:00Z), GEMM-level, slot d runs:** Pearl-C4 (bc-e8ffd7f2), re-timed with the widened β and the narrow k/v shapes.
  Pin and log as at 8:00.

Each owner posts READY or BLOCKED 20 min before its slot. An empty slot is released to fill.
