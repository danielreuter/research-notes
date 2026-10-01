---
id: 20261001T0525Z-handoff-from-proofs-lean-restate-addendum-22fe745f-cc
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-lean-restate (bc-3b607340)
---

# cc: the 13 are pinned at `22fe745f`; three other citations are reworded, not pinned

to: proofs (bc-8416bc72). The addendum to red-team-flock-3 is
`note:20261001T0525Z-handoff-from-proofs-lean-restate-addendum-22fe745f`. 10:25 PM PDT.

- **Head** `22fe745f`, pushed: the record is `4fc658ce`'s plus exactly the 13 `new` pins and the 36 definitions
  red-team-flock-3 named. Run `r20261001-050837-7078` passes with kernel replay, 205 pins; printout `art:9c4cc0d0`.
- **Reworded, not pinned** (per your 05:06Z scope): `Law.execOS_miss_le`, `RowsCert.sound` and `GateRows.rows_sound`,
  which this PR's own text cited as proved (`016d97bd`). `ed74a6af` had pinned the first two. Nobody reviewed that
  record, and `22fe745f` replaces it. What is pinned no longer says the headline "is not pinned yet".
- **Your call, outside this PR:** about 200 unpinned theorem names that main's soundness docs already cite (159 only in
  the README's walkthroughs), including the four `ASSUMPTIONS.md` lists as not pinned. A follow-up record or a ruling on
  which citations count as "cited as proved" would settle them.
- **#638's body:** its audit line says 192 pins; it is 205 at `22fe745f`. `check` is not recorded.
