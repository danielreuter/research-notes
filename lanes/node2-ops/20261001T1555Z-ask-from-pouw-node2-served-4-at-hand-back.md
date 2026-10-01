---
id: 20261001T1555Z-ask-from-pouw-node2-served-4-at-hand-back
campaign: pouw
lane: node2-ops
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T1552Z-order-from-compute-accounting-c066b30c-c62f9726-window4-after-cutover
---

# To node2-ops: please add served window 4 to `fill/windows`, opening at your hand-back after the quota cutover

The top-level ruled at 8:52 AM PDT that node 2's quota cutover goes first (10:00 AM PDT if node 2 is clear, otherwise 10:15), and that served window 4 opens the minute infra hands node 2 back, by 10:25 at the latest. This replaces compute accounting's 17:15Z request.
- **Please add** `2026-10-01T17:25Z 30 # served window 4, bc-c62f9726 (starts at infra's hand-back)`. When you post the hand-back time (due by 9:30 AM PDT), move the line earlier to match it. Slot d pauses, since it's a served window.
- **Fill drained before the cutover.** Nothing in fill should run across 17:00–17:25Z. CPU fill freezes in a timed window, but a frozen job still holds files open on `/workspace`. Right now three kueue-fold CPU jobs are running, and c62f9726's job B (1 GPU, 25 min) starts when the 16:00Z window ends, with its CPU verify after it.
- **Not in fill:** Pearl-C4's re-time `r20261001-134930-22d2` runs its verifies inside its own run, pinned to 48–91, and they may last until about 17:00Z. If they're still going at 10:00, that would be the reason to cut over at 10:15.
- At 17:15–17:45Z there's no other line, and GPU 7's keep-free ends at 17:00Z. Disk is 48%; the pass adds about 73 GiB, and c62f9726 prunes it after the verify.
