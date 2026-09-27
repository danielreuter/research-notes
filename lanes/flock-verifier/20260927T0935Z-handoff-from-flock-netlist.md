---
id: flock-verifier/20260927T0935Z-handoff-from-flock-netlist
campaign: verity
lane: flock-verifier
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 967b8d06
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Shared-row layout is final at 967b8d06 (as proposed at 09:07Z)

See `note:one-stage-e2e/20260927T0935Z-handoff-from-flock-netlist` §1 for the byte order and the load checks.

What your verifier needs to change:
- the row roots over the tables;
- the digest region value `b‖c[p][refs[i][p]]`;
- the public digest over the tables' `b‖c`, then the refs, then the outputs;
- for a drawn statement, the population's refs of the drawn units.

The circuit, Σ and the statement-digest formulas are unchanged.
