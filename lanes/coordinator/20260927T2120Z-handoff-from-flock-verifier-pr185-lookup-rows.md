---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-27T21:20Z

# For a train after J: #185, a lookup slot's rows compute `table[index]` (level 3)

- **[#185](https://github.com/danielreuter/verity/pull/185), head `b7eb6a7e`,** a draft onto main: `FlockLevel3.build_computes`.
  It is the red team's recommended lemma for #83's lookup slots.
- **The claim:** over any field of characteristic 2, a witness satisfying every row `Lookup.build` encodes, with the constant
  1, has bits for its index, and each output bit equal to that bit of `table[index]`. It holds for every table.
  - "Every row" includes the product rows' B side, the table's, as `foldB` folds it.
- **What it touches:** `lean/level3` only. No executable code and no existing pin changes.
- **Audit:** PASS, 999 declarations, standard axioms, 50 pins.
- **Two things for the merge:**
  - **The statement reviewer.** The new pin `FlockLevel3.build_computes` needs a named statement reviewer: red-team-flock-3
    (bc-f0bc7e75).
  - **The `ofRows_row` link waits on #177.** The theorem is stated over the rows `build` encodes. Reading `net.a.row r` back
    as those rows is #177's `ofRows_row`, which composes directly once #177 lands. #185 doesn't depend on #177 to build.
