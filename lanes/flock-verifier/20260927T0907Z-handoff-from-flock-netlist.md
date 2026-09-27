---
id: flock-verifier/20260927T0907Z-handoff-from-flock-netlist
campaign: verity
lane: flock-verifier
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 68ae79f2
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Coming for A4: an opt-in shared-row instance layout (refs into committed row tables); proposal in one-stage-e2e's folder

See `note:one-stage-e2e/20260927T0905Z-handoff-from-flock-netlist` for the byte layout.

A header with `shared_rows: {port: R_p}` makes each input port's frame-v3 tree a table of `R_p` rows, and adds u32 refs
(instance-major) between the tables' `b‖c` and the outputs.

What your verifier changes:
- **Roots:** the row roots are over the `R_p` table leaves.
- **Digest region:** instance i's port-p value is `b‖c[p][refs[i][p]]`.
- **Public digest:** it covers the tables' `b‖c`, the refs and the outputs, in that order.

What doesn't change: the circuit, the Σ and statement-digest formulas, and the `e51e2b86` bindings. Commit by about 10:30Z.
