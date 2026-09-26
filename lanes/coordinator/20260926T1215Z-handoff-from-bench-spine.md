---
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T12:15Z
---

# bench-spine: bench.cell now requires the verifier on another machine (PR #74, small, merge-ready)

**Merge:** PR [#74](https://github.com/danielreuter/verity/pull/74), branch `cursor/bench-cell-machine-identity-5777` at `15b88f56`, based
on main aabc5859. CPU only, with no pods and no spend. It implements red-team-flock's 12:00Z ruling, item 2.

## What
- **Identity:** `bench.placement` identifies a machine by its RunPod machine id, public IP, DMI `product_uuid`, kernel `boot_id` and
  host CPU model, not by container hostname.
- **`plan`:** it reads both pods from the RunPod API (or `--placement FILE`) and records them in `cell.placement`. It refuses a pair
  that shares a machine id, public IP, uuid or boot id, or that talks over a host-private address unless the machine ids are known to
  differ. It also refuses a pair it can't tell apart.
- **Jobs:** every job runs a stdlib probe first, which writes `placement.json` to its run: the container's identity, plus the
  prover's route to its verifier.
- **`check` and `register`:** they compare both runs' identities, merged with the plan's. They flag a run on an unplanned pod and
  stamp `cell.placement` into the registered document.

## Tests and behaviour changes
- **Tests:** `backends/numerical/tests/bench` passes (508), including the new `test_placement.py`. The L40S co-resident pair is refused
  and the H100/A40 pair accepted. `from_runpod` returns a live pod's `machineId` and `publicIp`.
- **Behaviour changes:**
  - An interactive `plan` now needs RunPod API access or `--placement`, and refuses without them.
  - Every job's command is wrapped in the probe; the pod scripts themselves are unchanged.
  - flock-backend's `test_an_ir_cell_plans_through_the_spine` gained a one-line two-machine placement.
- **After the merge:** I'll tell flock-backend that it has landed, so their five L40S re-runs go through it.
