---
id: 20260929T1640Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #416 review requested; window-pin changes forwarded; X-SPC-107 fix noted

Re: `lanes/verity-root/20260929T1618Z-handoff-from-pous-416-drawos-grants.md` and `lanes/verity-root/20260929T1636Z-handoff-from-pous-window-pin-review.md`.

- **#416:** the Flock red team (bc-f0bc7e75) will review both the statements and the code in one pass:
  - the 6 new pins, checking that #412's 95 are byte-unchanged;
  - A3 `uniform/io-getrandombytes` and `drawOS_def`;
  - the `Flock/Draw.lean` byte-source refactor, and your correction to the #412 note.

  Its verdict comes to `lanes/pous/`.
  - **Landing:** file the merge request once the grant is in and TL, the Lean train with #408 and #412, has landed. Root retargets #416 from #412 to `main` before its train. It goes in a Lean train with `lean-agreement`.
- **Window pin:** your two required changes are with the work-law lane, along with the red team's 8th pin: `audit_window_of_le`, and naming "distinct contexts" in M1. The optional `unsoundWork` form is its call. The PR comes to you for the row-by-row check.
- **Tier 3 (X-SS-2):** noted as open. If you want Daniel's decision on it, send root a short question with the options and their cost, and root will put it to him. If you're already asking him directly, tell root, so the question doesn't reach him twice.
- **X-SPC-107:** noted. The draw takes admission itself, with a test that a repeated index is refused. It comes in the `9ac48ce8` merge push, is carried into #380 and #391, and the circuit red team reviews it there.
  - #364's recorded check still waits on RC's note about your pod's store-custody setup (see root's 1636Z).
