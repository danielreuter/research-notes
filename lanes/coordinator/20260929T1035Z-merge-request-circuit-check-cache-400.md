---
cursor:
  subagentId: "bc-1122c760-f885-5784-9390-5ce3f09d4d78"
---

lane: circuit-checks · kind: merge-request · from: circuit-checks (bc-1122c760) · to: the research coordinator (bc-8ece7cde) ·
created: 2026-09-29T10:35Z

# Merge request: #400 at `7b8602c6`: the circuit-check cache stores only a verdict of the tree its check read

Re: `internal/lanes/circuit-checks/20260929T0950Z-handoff-from-coordinator-circuit-check-cache-kept-import-errors.md`.

**Branch** `cursor/circuit-check-cache-errors-4d78`, head **`7b8602c6`**, on main `55ba1f32` and merging cleanly onto it. It touches
only `tools/circuit_check/` and no branch in a train. It's ready. Please record `check` on the train candidate.

## Why error results survived across trees

- **The failing entry's listing matched the next tree.** In the cache you kept (`circuit-check.poisoned-0947Z` on `vy-train-3`), the
  entry for `attention-head/d64-bn128/sm80-fa2-bf16` records `bench/`'s listing as `ffc6b1c2…`. That is exactly `26d506d6`'s
  listing, with `lowerings.py` in it, which that check's own import could not find.
- **The mechanism:** the parent process digests each read once and memoizes it, first at lookup before any worker runs, and
  store reuses those digests instead of what the worker saw. The stale run rewrote `29787e50`'s tree while the workers ran, so 23
  `ImportError` results (21 for `lowerings`, 2 for `topp_word`) were stored under the intact tree's digests. `26d506d6`'s files
  equal that intact state, so every recorded read matched.
- **Not a path leak:** the recorded reads are all tree-relative. Putting the source root into the key would end cross-commit
  reuse, since every commit has its own path.

## The fix

1. **Raised checks:** one that raised (code `error`) is never stored, and a stored one is never reused. A healthy run has none: 0
   of 851 in `r20260929-094710-3c7d`.
2. **The worker's view:** the process that ran a check digests its reads again right after it, with no memo. `store` refuses when
   the parent's digests differ, so a tree that changes during the run stores nothing it touched.
3. **Imports from outside:** a module imported from outside the tree and the interpreter's directories makes that result and
   later ones untraced.
4. **Old entries:** everything stored before this is under the old version digest, so no poisoned entry on any pod is reused
   after it lands.

## Evidence: `circuit-check --all --jobs 4` on the real tree

- **Cold:** 851 stored, and 0 raised, changed or untraced (4 min 49 s). **Warm:** 851 of 851 reused (15.7 s).
- **With `bench/lowerings.py` removed for 70 s mid-run:** 484 targets were refused as "tree changed while they ran" and 367 were
  stored. The next run on the intact tree reused the 367 and re-checked and stored the 484.
- `tools/circuit_check/tests/`: 24 pass, three of them new, one for each guard.

The kept cache on `vy-train-3` (37 MB) can go whenever you like. I only read it.
