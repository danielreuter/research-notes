---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: handoff · from: audit-lean (bc-a0c5a22f) · created: 2026-09-28T05:28Z · repo: danielreuter/verity ·
re: `lanes/audit-lean/20260928T0505Z-handoff-from-coordinator.md` (run `r20260928-043118-707b`)

# audit-lean → coordinator: the replay failure is fixed on #154 and #177; the train passes the full local audit

**New heads, for the re-audit:**
- **#147:** `a09a04d3`, unchanged;
- **#156:** `a084ae06`, unchanged;
- **#154:** `ef8bede5` (was `e0dd3323`);
- **#177:** `8e9b0176` (was `81552896`).

Merge in the same order. #202 and #204 stay after the train.

## The cause

- **Realized lemmas, declared twice.** Lean generates equation and congruence lemmas on demand, in whichever module
  first needs them. Two of my soundness modules realized lemmas that level3's `LookupRows` (#185, on `main`) also
  realizes, without importing it:
  - `ExecLookup` (#177): `Flock.Lookup.row.eq_1`, `Flock.Lookup.decode.eq_def` and two of `decode`'s case-split lemmas;
  - `ExecRows` (#154): `Std.Legacy.Range.mk.congr_simp`.
- **Why the build didn't notice.** Importing both is fine for the build, but the replay refuses a constant declared both
  inside the soundness set and outside it.
- **#154 alone would have failed too.** The pair in `ExecRows` has nothing to do with #177.

## The fix

**Mine; #147 needs nothing.**
- Both files import `FlockLevel3.LookupRows`, so they reuse those lemmas instead of declaring them.
- `ExecLookup`'s own `build_spec` is renamed `build_facts`, since `FlockLevel3.build_spec` is now in scope.
- No statement, pin or proof step changes.
- Over `FlockSoundness`'s whole import closure, no constant is now declared both by a soundness module and by a module
  outside the set. I checked this by reading every module's constants from the `.olean` files.

## Checked locally on the merged train

The tree: `main` `6746f408` + #147 `a09a04d3` + #156 `a084ae06` + #154 `ef8bede5` + #177 `8e9b0176`, in that order. Tree
`4008e809`, no conflicts.

`tools/lean/audit.py --all --build`, kernel replay included, **PASS:**
- controls: PASS;
- executable: 2,556 declarations, 11 pins;
- level3: 1,011 declarations, 50 pins;
- soundness: 5,308 declarations in 93 modules, 9 pins, replay 20 s. This was 5,319 before; the difference is the
  lemmas now reused from level3.

Also on that tree:
- `backends/flock/tests`, `tests/test_repository.py` and `tools/lean/tests`: 77 passed, 5 skipped;
- `test_topp_word.py` deselected, since it fails the same way on `main` here (no `verity_vllm` on the path);
- `Check.lean` on #177 `8e9b0176`: 277 of 277 on standard axioms.

Both PR descriptions are updated. CPU only, $0.
