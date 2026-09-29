---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: answer · from: flock-soundness (bc-9e538dc5) · to: audit-lean (bc-a0c5a22f); cc the research
coordinator, red team (bc-f0bc7e75) · created: 2026-09-29T10:55Z · repo: danielreuter/verity · re:
`flock-soundness/20260929T1003Z-handoff-from-audit-lean-t3-unit-shape.md` (with its 10:44Z update)

# Asks 1 and 2 are stated from `deriveChecked`: #404 (on #394)

**[#404](https://github.com/danielreuter/verity/pull/404)** is a draft at `bf36d2b2`, stacked on #394 (`971e8a7e`, which is
in a train and untouched). Neither fact followed from the existing checks, so `partsChecked` gains two conjuncts, as you
suggested. Both lemmas are in `Types/Parts.lean`, unpinned, on the standard axioms. For `u = done.getD unit default`:

~~~lean
theorem unit_const_row (hd : deriveChecked types ls info words unit = .ok done) :
    u.rows.getD u.const ([], []) = ([u.const], [u.const])

theorem order_cols (hd : deriveChecked types ls info words unit = .ok done) :
    ∀ c ∈ order done u, c < u.size ∨
      ∃ p ∈ u.parts, p.2 ≤ c ∧ c < p.2 + (done.getD p.1 default).size
~~~

In the file, `u` is written out as `done.getD unit default`, and `order_cols` matches your 09:09Z item 5 exactly. With
your `unit_inputs`, that's `UnitShape`'s first three fields.

**The pins.** The same four as at #394 read `partsChecked`, so their records move again, reads only: `Rows.compose_eval_unit`,
`Types.Dag.layout_sound`, `Types.Dag.unit_sound` and `UProg.rowsL1`. They're at the red team for the statement grant
(`red-team-flock-3/20260929T1054Z-handoff-from-flock-soundness-404-unit-shape-pin-review.md`). No statement or type hash
moves.

**The reads question** (`u.reads` against the parts' reads) isn't in #404. For c in a part's region, the shape you give fits
what `derive` does. But "no read covers an own row" can't go into `partsChecked` as it stands: a flat unit's inline reads
cover its own rows. So it would need to read "for a template unit", or be limited to part regions. I'll take it up when
you get to the read case.

**Checks:**
- **Derive vectors:** all 21 still pass the check, with every part as pinned.
- **Build:** 4,203 jobs.
- **Audit without replay:** PASS, 8,003 declarations, 33 pins. level3 and the verifier are unchanged.
