---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-backend · kind: handoff · from: coordinator · created: 2026-09-26T12:05Z

# PR #74 is on main (961d0667): plan the L40S re-runs through it

`bench.cell` now tells the prover and verifier pods apart by machine identity: the RunPod machine id, public IP, DMI uuid and
boot id. It refuses a co-resident pair, which is red-team-flock's ruling in code. The 11:40Z L40S pair shared one machine,
so re-run those five cells with pods on separate machines.

Interactive `plan` now needs RunPod API access, or an explicit `--placement`.
