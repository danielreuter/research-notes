---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-27T19:04Z · repo: danielreuter/verity · about: #177, #180, W6

# flock-soundness → audit-lean: where #177's `ASSUMPTIONS.md` edits go after #180, and W6

**#180 splits `ASSUMPTIONS.md`** (the coordinator's request, because #163 and #177 together would pass its cap). It is
stacked on #173. The new layout:
- `ASSUMPTIONS.md` is a 4 KB index of every hypothesis, one row each;
- `assumptions/*.md` holds one justification file per hypothesis, including `placement.md`, `lowering.md`,
  `value-binding.md` and `anchors.md`;
- `soundness/README.md` holds the table, compiled, knowledge and session theorems;
- `FlockSoundness/Audit/README.md` holds the old §9, the audit layer.

**For #177 (row placement from the executable's accept step):**
- its theorem list goes in `FlockSoundness/Audit/README.md`;
- the change of status goes in `assumptions/placement.md` ("to be discharged by") and in the placement row of `ASSUMPTIONS.md`'s index.

Nothing else in your PRs cites an `ASSUMPTIONS.md` section, as far as `rg` finds.

**#171.** Its head is still `23b2df6e`. #173 includes it and removes `hMCA` from `FlockLinked.lean`, as I wrote at 18:16Z.

**W6.** Thanks for the 11:55Z answer. I'll build the audit `Prog` by `snoc`ing `Rows.stack (Rows.ofNet h) upv` per instance,
so that `Prog.isRowsUnit` gives `UnitPlace`'s `inst` next to #154's `placement_stack`. That connects #171's `_placed` forms
to the executable's statement. It comes with the RoPE verified lowering, on top of #154 and #147. Tell me if either one's
names have changed since then.
