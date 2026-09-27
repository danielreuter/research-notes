---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: ligero-hygiene (small cloud lane)

**Launch status:** READY (9:25 AM PT, Sep 25).

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `ligero-hygiene`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/ligero-hygiene.md`. Write your first checkpoint
> within 10 minutes.

## Why

Loose ends in B-Ligero's verifier and tests, left by ligero-steps-pin and reverify-tile-2 (both merged). None blocks a
current Table 2 cell, but each weakens the verifier's evidence. Read:
- `$RESEARCH_NOTES/lanes/coordinator/20260925T1505Z-handoff-from-reverify-tile-2.md` and reverify-tile-2's report;
- the red team's tile review, sent to reverify-tile-2 by red-team-standard-hash-2;
- `$RESEARCH_NOTES/lanes/coordinator/20260925T0935Z-handoff-from-ligero-steps-pin.md` ("Known failures and limits").

## Work, in order

1. **The combined tree on main.** Run `pytest backends/direct/ligero/{hashauth_test,reverify_test,steps_pin_test}.py` and
   `cargo test --release` in `backends/ligero-verify`, on main **239c0e28** or later. That's the first tree with both
   reverify-tile-2's tile recomputation and the cherry-picked 977ad27b/906255b2 (a run_files tree with manifest.json at the
   root), which were only tested apart. Report the counts. Fix anything the combination broke first.
2. **`live_test.py::test_shared_pair_every_coin_from_the_verifier[None]`** fails on main too (since at least 5631e667):
   "G: parameters give 2^-99.86 ... requested 2^-100". Find whether it's the test's parameters or the soundness calculator.
   Fix it. If the calculator is right and the parameters are too weak, fix the parameters, not the bound.
3. **Three committed-operand conformance negatives** timed out at 30 minutes on a pod at load about 500, so they're
   inconclusive. Re-run them on an unloaded pod (`--exclusive`) with a longer timeout, and report pass/fail. If one is
   really that slow, profile it and say why.
4. **The red team's three tile follow-ups:**
   - a float seed in the manifest fails cleanly (a FAIL with a reason, not an exception);
   - `set.sharing` is checked against `set.tile` (inconsistent sharing / tile fails);
   - a negative for a missing `.hproof` (fails, not accepted and not an exception).
   Each with a test.

## Limits

- Branch `lane/ligero-hygiene` from `origin/main`. Push after every commit. Merge-ready handoff to `lanes/coordinator/` when
  done (tip, test counts, what changed). A red-team spot-check follows only if you change what a verifier accepts.
- Pods: the cheapest CPU pod (`--exclusive` for item 3), `--custody-r2`, no laptop fetches, terminate at the end.
- FINAL: 20:00Z. Budget: $8 (pods).
