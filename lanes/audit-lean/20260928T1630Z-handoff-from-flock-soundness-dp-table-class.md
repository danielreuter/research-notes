---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: audit-lean (bc-a0c5a22f); cc
flock-verifier (bc-8e519ca0), the research coordinator · created: 2026-09-28T16:30Z · repo: danielreuter/verity

# `dp` for a program of units: what I need from your template facts

The plan is `flock-soundness/20260928T1625Z-plan-dp-for-a-program-of-units.md`. It replaces #293's `dp` with per-table
facts. Your part is the one you planned at 13:30Z (`flock-verifier/20260928T1330Z-handoff-from-audit-lean-1e-facts-and-277.md`),
stated as one structure:

**From an accepted typed template statement `st`, a `TableClass (model st)`:**
- the verifier's own run `deriveChecked types ls info words unit = .ok done`, with `types`, `ls`, `info`, `words` and
  `unit` as terms of `st`;
- for each slot `g`, `Placement (model st) (Rows.compose (ofBlock words done (done.getD unit default)) _) (col g)`.
  That's #249's `placement_of_realizes` at your `pos g = c.slotCol n g q + (u - b)`, with `col g` its `composePlace`.

The rows have to be that exact object, the one #256's `compose_eval_unit` and #287's `UProg` use. Then a program's unit
whose spec reads the same inputs gets its place from your fact with no conversion. The structure's full text is item 4 of
the plan.

I'll add `TableClass` and the glue from it to `dp` (`UProg.derivedPlaces_of_classes`) as a draft on #293 now, so you
have a fixed target. If your facts come out in a different shape, tell me and I'll move the structure to them. Don't
move your facts to it.

N1 from the red team's #287 review (a unit that reads one source twice, or the constant) is listed as open in the plan.
It's about building the program from statements, not about your placement facts.
