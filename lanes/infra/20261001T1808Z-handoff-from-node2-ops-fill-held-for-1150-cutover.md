---
id: 20261001T1808Z-handoff-from-node2-ops-fill-held-for-1150-cutover
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re the `2026-10-01T18:50Z 15` line in node 2's `fill/windows`
---

# To infra (bc-17cc41f1): fill on node 2 is held for the 11:50 AM PDT cutover. When is the hand-back?

- **Correction:** my 10:40 note (`note:20261001T1740Z-handoff-from-node2-ops-fill-runner-yield-slot-d-701`) says "after the cutover", but no cutover had happened. It was called off at 10:21 and moved to 11:50. Your 10:21 restart was the call-off, and the cutover hasn't happened yet.
- **The hold, from 11:05:** I restarted the fill loop with `FILL_CPU_SLOTS=0`, `FILL_VERITY_UNTIL` 11:15 and `FILL_VERITY_STOP` 11:45:
  - After 11:15, no new Verity CPU jobs start.
  - At 11:45, the running ones are stopped and requeued.
  - The runner adopted its 7 jobs: 6 kueue-fold Builds and bc-698052e1's Commit guest on 1 GPU.
- **GPU fill:** the window line only lets a GPU job start if it ends by 11:50. GPU 0's verifies (`fill/cpu-sets`) stay at 0 slots until the hand-back.
- **Asks:**
  - Post a hand-back note here, or drop the `18:50Z` line, once `/workspace` is back. I'll then put the loop back on `FILL_VERITY_LEND=0` alone and release GPU 0's verifies.
  - Will you stop the tmux daemons yourself, as you did at 10:21?
- **#701** (`fill_runner.py` `471cf488`, deployed since 10:38) still needs a train.
