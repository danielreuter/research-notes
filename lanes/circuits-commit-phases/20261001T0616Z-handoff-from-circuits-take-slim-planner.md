---
id: 20261001T0616Z-handoff-from-circuits-take-slim-planner
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: take the TP2 lane's slim planner (`cbfbf9384`) into your branch. It cuts the slim plan's GPU hold from 476 s to 26 s

- **Where it is:** `cursor/replay-on-cpu-3847` @ `cbfbf9384` (main `c1e920090` merged in; against main it's the planner only, 11 files,
  +294/−48). The commits are `0be326994` (`driver.populate` memo) and `feb6f4827` (`pipeline/replay_plan.py`, `verity-vllm replay-plan`,
  `store_dump.touch`, `c2_replay.plan(planner)`).
- **The findings:** `note:20261001T0600Z-handoff-from-vllm-config-run-tp2-slim-planner-gpu-hold`.
  - The 415 s in-process plan was 244 s indexing, 61 s loading, 57 s population and 34 s pick walk.
  - The planner process does the first three while the GPU works. Phi-3 B8's Commit fell from 894 s to 626 s, and the touched set is
    byte-identical.
- **What to do:** cherry-pick those two commits onto `cursor/commit-gpu-phases-8c79` with `-x`, and keep them as their own commits in
  your one PR. Check them against the advisor's constraint: the planner may load, index and enumerate before the root is fixed, but the
  sample draw and the pick walk happen only after the Commit sends the seed. Confirm that in the code and in your gate rows.
- The TP2 lane has stopped pushing to that branch.
