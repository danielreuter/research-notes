---
id: one-stage-e2e/20260927T0845Z-handoff-from-flock-netlist
campaign: verity
lane: one-stage-e2e
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 68ae79f2
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Bindings unchanged at 68ae79f2; only the statement digest's value moves

The four bindings of `e51e2b86` (partition digest, `program_sha512`, unit indices, each instance's circuit digest) are unchanged.
`68ae79f2` corrects the backend identity's `hashes` text (`sha512` for the round digest, statement digest and Σ, as they already
were), so a statement staged and proved from this commit has a different `statement_digest` value than one from `e51e2b86`. Records
you already have still verify as recorded.
