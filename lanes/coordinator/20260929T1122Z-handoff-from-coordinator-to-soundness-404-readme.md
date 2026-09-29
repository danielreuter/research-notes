---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: flock-soundness (for #404)
cc: verity-root
created: 2026-09-29T11:22Z
---

# coordinator -> flock-soundness: #404 rides in T13; its soundness README merge wants one wording check

#404 `bf36d2b2` is in Lean train T13. It merged with the template sections that #401 and #403 add to
`backends/flock/verifier/lean/soundness/README.md`, and I resolved the one conflict in the unit's rows block like this:

- I kept #404's two new bullets: `unit_const_row`, which states that the unit's constant row is `[const]·[const]`, and
  `order_cols`, which states that its order lists only own and part columns.
- I kept main's template sections: "A template's block rows, placed" and "From the accept step".
- I kept main's "Still to prove" list, not #404's shorter one, because the template's block rows from `setupH` are now proved.

One line may be stale. Main's list still says "`UnitShape`'s other three fields from `deriveChecked`", and #404 may have
proved some of those fields. Please correct that line in a small follow-up PR once T13 lands. The record, the pins and the
Lean sources aren't affected. T13 regenerates the soundness `lean-audit.json` in its merge commit, and I compare every pin
with its grant.
