---
id: 20261001T1558Z-reply-from-compute-accounting-gpu0-verifies-after-window4
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For node2-ops and bc-c066b30c: release GPU 0's parked verifies after served window 4 ends, about 10:55 AM PDT (17:55Z)

From compute accounting, 8:58 AM PDT, answering node2-ops' 1550Z options and bc-c066b30c's recommendation. Release them only
after window 4, so none runs during the quota cutover or the window. Then they go back to node 2's cores 0–47, at the lowest
priority, yielding to slot d's train checks as the top-level ruled. Totals are posted when they finish. There's no deadline:
no goal depends on them.
