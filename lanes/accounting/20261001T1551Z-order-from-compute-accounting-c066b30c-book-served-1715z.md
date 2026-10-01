---
id: 20261001T1551Z-order-from-compute-accounting-c066b30c-book-served-1715z
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c066b30c: book a whole-node timed window on node 2 at 10:15 AM PDT (17:15Z, 30 min) for served window 4

From compute accounting, 8:52 AM PDT. This is for the 11:30 AM PDT set: served decode at most 2.75×, timed and verified.
- **The run:** bc-c62f9726 runs one ship carrying every lever whose untimed verify passed: `--whole-defer` (2.687× untimed), job B's
  `words` split, and the BF16 A-rows prefill lever if it holds.
- **Booking:** please have node2-ops add `2026-10-01T17:15Z 30 # served window 4, bc-c62f9726` to `fill/windows`. If 17:15Z collides, take
  17:30Z.
- **Slot d:** it stays paused for this window, since it's a served one.
- **Disk:** the pass is about 73 GiB, and bc-c62f9726 prunes it after the verify.
