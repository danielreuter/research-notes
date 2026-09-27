---
cursor:
  subagentId: "bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777"
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-27T03:50Z
---

# bench-spine: flock-backend's placement-probe fix is PR #107 on main, head 4a9b0934, for the train after #100

Answers `lanes/bench-spine/20260927T0338Z-handoff-from-coordinator.md`.

- **The PR:** [#107](https://github.com/danielreuter/verity/pull/107), branch `cursor/placement-probe-pod-env-5777`, head **`4a9b0934`**, on main
  3040ac1f. CPU only, no spend.
- **The fix:** `852816d6` cherry-picked as `9445a732`, with identical content. `cursor/flock-backend-4983` carries 16 other
  commits past main, so I didn't take the branch. Cells registered from flock-backend's branch record `852816d6`. The
  placement code is the same.
- **Tests (`4a9b0934`):**
  - `probe()` with no `RUNPOD_*` recovers the pod id, public IP and datacenter from `/proc/1/environ`. It reads only those
    keys, so a `RUNPOD_API_KEY` in the file never reaches the record.
  - The job's environment wins, and an unreadable file records None.
  - A null pod id refuses at `register` under a shared IP, and the recovered one registers.
  - `backends/numerical/tests/bench` passes (573).
- **Not run:** `check` and `research merge` are yours. There is no `research check` subcommand on this side.
