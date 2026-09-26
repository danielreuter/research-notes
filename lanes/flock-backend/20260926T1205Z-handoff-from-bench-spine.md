---
lane: flock-backend
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T12:05Z
---

# bench-spine: bench.cell's machine-identity check has landed on main (PR #74, merge 961d0667)

This is red-team-flock's 12:00Z item 2, and it applies to your five L40S re-runs.

- **Plan:** `bench.cell plan` reads both pods' RunPod machine id and public IP, or takes them from `--placement FILE`, and records them
  in `cell.placement`. It refuses the pair when:
  - the two pods share a machine id, public IP, DMI uuid or kernel boot id;
  - the prover reaches the verifier over a host-private address (the 172.24.0.x bridge), unless both machine ids are known to differ;
  - the identity recorded isn't enough to tell the two machines apart.
- **Probe:** every job now runs `backends/numerical/python/verity_numerical/bench/placement.py probe` before your pod script. The
  probe writes `placement.json` to the run (on the prover, including its route to the verifier). The script itself is unchanged.
- **Check and register:** `check` and `register` compare both runs' identities, not hostnames. They flag a run on a pod other than the
  planned one, and stamp both machines into the registered document.
- **For the re-runs:** put the verifier on a different machine and give it a public, routed address as `--verifier-addr`. Plan
  refuses the US-TX-4 pairing, so you'll know before any spend.
- **Your test:** one line in your `backends/flock/tests/test_ir_lowering.py::test_an_ir_cell_plans_through_the_spine` changed; it now
  passes a two-machine placement.
