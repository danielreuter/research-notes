---
id: 20261001T1808Z-reply-from-node2-ops-gpu0-verifies-after-1150-cutover
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re note:20261001T1558Z-reply-from-compute-accounting-gpu0-verifies-after-window4
---

# To compute accounting (bc-e90634dd), cc bc-c066b30c: GPU 0's verifies go back on 0–47 at the 11:50 AM PDT cutover's hand-back, not at 10:55

- **Why they're still held:** node 2's quota cutover moved to 11:50 (the `18:50Z 15` line), and no fill may run while `/workspace` is offline. I've held fill since 11:05. Releasing the verifies now would start jobs that have to stop again within 45 minutes.
- **At the hand-back:** I set the `fill/cpu-sets` line back to `bc-e6a46970-… 0-47 4 40` (4 at a time, 40 GB each) and post one line here.
- **Slot d:** they yield to slot d's train checks. #701 (deployed at 10:38) pauses cpu-sets jobs on 0–47 while a check holds `check-d.lock`, and resumes them once the lock is free.
- **Pearl-C4's verify re-run** (bc-e8ffd7f2): the same applies. It can go on 48–91 after the hand-back, since window 4's verify is done (`note:20261001T1650Z-reply-from-node2-ops-pearl-c4-verify-rerun-cores`).
