---
id: 20260929T0420Z-handoff-from-pous-draw-law-design-pointer
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: where the draw-law drafting worker should read (re: your 0403Z note)

## What to read

**The design** (a snapshot of the POUS store copy, taken 04:20Z) is at
`campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/sampled-proofs-circuit.md`.

- **§12.3:** closure draws and work-proportional tile sizing, with the integrity floor.
- **§12.2:** the theorem and the closure-law statement, which covers undrawn node units, plus the assumptions list,
  including the three the red team added.
- **§10.1:** the sizing ruling, and what it requires of `Flock/Draw.lean`, #167 and U2.

**The Lean** is at `campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/pouw-accountable-compute/`. §12.2 is proved against `main`'s `Stratified`, `harm_bound` and
`stratified_escape`: 21 pins, no `sorry`, standard axioms only.

- `PouwAccountable/Closure.lean` has the closure law, and `NOTES.md` lists each statement.
- **Its statement review is still pending**, so treat the pins as proposed.

## The red team's verdict

The verdict and the rule are in our 0406Z note. In short: §12.2 holds with conditions, and the closure law needs its
own pinned statement.

## Other notes

- **Still open:** the width rule is still with Daniel, and it doesn't affect the draw law. The one open question is
  whether narrow Z units get their own stratum. If Daniel adopts them, they are one more work-free class under the
  integrity floor, with about 22,000 draws.
- **#359:** out of draft now, ready for the research coordinator's next train.
