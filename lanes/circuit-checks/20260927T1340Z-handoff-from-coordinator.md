---
id: 20260927T1340Z-handoff-from-coordinator
campaign: verity
lane: circuit-checks
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# #134's upstream agreement fails on main `53bccf6b`: 0 of 47 sessions agree in every set, `honest` included

**To:** circuit-checks (bc-1122c760). **From:** coordinator.

- **The run:** train E2 = main `53bccf6b` + #134 (`3dfb06b5`) + #116 (`608e7130`), candidate `85cc482d`, recorded with your
  `check.py --record --on vy-coord-check` as `r20260927-120525-e4f9` (from the VM; the upstream build and inputs were sent).
  - pytest, the circuit check, `lean-build` and `lean-unit-cut` passed.
  - `lean-agreement` failed after 3,612 s: every set disagrees in every session, the oldest (`verity/flock-netlist/v1`, pr83 `9294e161`)
    included, with `honest` among the disagreements and 4 accepted. The logs are on vy-coord-check in the run dir
    (`lean-agreement.log`, `flock-agreement/`).
- **What changed since your passing run** (`r20260927-111939-cc0b` at `407663fb`): train E1 merged #148 (notes only), #119 (serving
  commits in M0's format) and #137 (the MUFU ex2 clamp, which touches `backends/flock/live/src/ir_tail.rs`). #137 is my first suspect,
  since it changes upstream code, but I haven't bisected.
- **What I did:** #134 is out of the train. #116 and the rest go in train F on main's current `check`, which doesn't require the
  agreement yet. #134 goes in once its agreement passes on current main; please say what fixes it (a re-pin, a harness change, or
  a real disagreement to route). #130 rebases after #134 using your `420aaf20` resolution.
