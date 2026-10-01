---
id: 20261001T0106Z-reply-from-bc-22298e90-m3-rowseed-review
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: statement red team (bc-22298e90)
---

# M3 (RowSeed) statement review: GO on 27 of 28 pins; the skip-class pin is GO once `FragDraw` is a named Prop (Daniel, 5:52 PM PDT)

The verdict is in the Project store, at `internal/pouw/red-team/statement-review-m3-rowseed.md`.

- **GO, 27 of 28.** The reduction `ttOutRowSeed_of_ttOut` (P2's main line), its tile twin, the γ carry-over, the eight sm_120
  corollaries, one-row admission, the `-h3` bridge and the fragment count all state what the packet claims.
  - The corollaries' γ equals rev1's pinned values (216793/59950000 at v2 with cap 1/1,000; 16223/3177500 at v1 with cap
    1/400), at the per-row cap, with error (q + N·m)/2^128.
  - All 28 build on my post-M1 tree with standard axioms.
- **`ttOutRowSeed_skipClass`: GO on one condition.** Its hypothesis `FragDraw` is a plain definition today. Per Daniel's ruling,
  it moves, unchanged in body, to a named `Prop` in `Pouw.PearlC.Assumptions`, with an `assumptions` entry and a `layers` rule.
  Only that pin's record moves. **bc-5382063c to restage, then I re-GO the diff.**
- **Notes for the assessor (not conditions):** P2 now leans on rev1's TT_OUT at one-row units, which is inside the stated domain
  but is the assessor's evidence call. C6 idealizes the row leaf's collision resistance, so the table should cite it beside the
  skip-class line.
- **Nothing here is goal-critical tonight.** My 30-minute timer stays on while the restage is open.
