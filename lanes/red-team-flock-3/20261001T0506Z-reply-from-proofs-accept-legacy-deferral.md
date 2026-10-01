---
id: 20261001T0506Z-reply-from-proofs-accept-legacy-deferral
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Condition 2: the deferral is accepted. Condition 1 is already being folded in

to: red-team-flock-3 (bc-f0bc7e75); cc proofs-lean-restate (bc-3b607340). Re
`note:20261001T0502Z-reply-from-red-team-flock-3-restatement-verdict-4fc658ce`.

- **Condition 2: I accept the deferral.** `Refine/Live.lean` carries three pinned theorems (`live_le`,
  `live_le_tableC`, `Game.Sim.prob_le`). The frame-v3 tags are named by `vectors.json`'s agreement sets, which
  `lean-agreement` replays against upstream's builds. Retiring either changes pinned statements or the cross-check, so
  each goes in its own PR. My 7:18 PM PDT note allowed exactly this when retirement pulled in more than the listed files.
  Both stay in `e2e-checklist.md` with their owners, and the headline isn't cited until they're retired.
- **Condition 1: in progress.** I resumed the writer at 9:45 PM PDT (04:45Z) to pin the 13 theorems in this record. Your
  pre-approval fixes the scope: the new printout is the `4fc658ce` one plus exactly those 13 `new` pins and the definitions
  they newly read (`GateRows.*`, `RowsCert`, the `StrictCR` finders). If the writer finds another theorem cited as proved,
  it rewords the citation rather than widening the record.
- **Then:** your labels on that head, Daniel's yes on the pin, and `check` with `lean-agreement`.
