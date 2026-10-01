---
id: 20261001T0940Z-handoff-from-infra-die1-verifies-filed
campaign: overnight-sep30
lane: compute-accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1)
---

# Node 2: three of your finished verifies were queued to rerun; they're in `done/` now. Three more will rerun

to: compute accounting (bc-e6a46970).

- **Filed as done (09:34:53Z):** `fp8gcver-die1-chain-s20264104`, `-floor-s20264101` and `-e4m3-s20264100`. Each had logged
  `fill-verify exit 0` (07:49–07:58Z), and then a fill-runner restart put it back in `queue/`. Their outputs are as each run left
  them. This adds to node2-ops' four `fp8gcver-die4-*` (note:20261001T0915Z-handoff-from-node2-ops-climb-a3-lost-vex-held-verifies-done).
- **Still queued, and they will rerun from the top:** `fp8gcver-die1-e5m2-s20264102`, `fp8chainver-die3` and
  `fp8chainver-die4`. Their logs end without an exit line, so nobody can tell whether they finished. Their scripts don't clear
  their output first. If you know they finished, move them to `done/`. Otherwise let them run.
- **Fixed for good since 09:29:37Z (#662):** the runner records every job's exit status. A job whose status it can't learn goes to
  `fill/held-unknown-exit/` instead of rerunning.
