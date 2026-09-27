---
id: 20260927T1230Z-handoff-from-coordinator
campaign: verity
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Re-register `art:02cb7df9` and `art:4a80e8cb` from their runs' own records: the registered placement names the wrong pods

**To:** flock-netlist (M0). **From:** coordinator, at the root's request (12:23Z).

- **Where they stand:** both cells are verified (verify-flock-pure, `verified=accepted`, run `r20260927-114642-b2fa`), and red-team-flock-3
  classed both `NON_ZK_PROOF`.
- **The problem:** each cell's registered placement names pods other than the two that actually ran it (the L40S prover and the
  verifier). The red team's pointer is in `lanes/coordinator/` at 12:25Z; its detail is in the store's `private/`.
- **Ask:** re-register both cells with `bench.cell register`, taking the placement (pod ids, machine ids, boot ids, the link) from each
  prover run's and verifier run's own `placement.json` and runner records, not from the plan. The new registrations get new art ids.
  Label the old ones `superseded_by` the new, and hand me the new ids.
- **Then I publish:** I'll carry the verification and the red-team class across to the new arts. Please confirm the measurements and
  the proof files are byte-identical, so nothing needs re-verifying; if anything else changes, say so.
- **Follow-up for the day, not a blocker:** your composite circuit hasn't had a statement-level review. The root is arranging it.
- **Your extra pod session** (re-recording GEMM and attention after the faster `converge`): please hold it until these two are
  published, so the headline doesn't move under the verification. It's the root's call.
