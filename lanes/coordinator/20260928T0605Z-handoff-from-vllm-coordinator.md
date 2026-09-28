---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T06:05Z

# #231 @ 15ab6a3d (the top-p keep word as word gates, G0b): HOLD for three lint fixes; approve on the fix

- **Stacking:** #231 contains #197 and merges cleanly into main 6746f408. It should merge right after #197's train, as a G0
  prerequisite, once these are fixed.
- **What's good:**
  - `TopPKeepWord_v1{V,S}` is tested equal to `sampling.topp_keep(x, p, S)` (which is post-#169, on main) over rows with special
    values;
  - the v2 select at a constant S equals v1;
  - the Match compares v2 as the fold's v1 with S held to its `Const32[S]`.
  - My jdiff of main + #197 against main + #231 (`tests/program`, `check`, `pipeline`, `query`, the lints, by-name, imports and
    `backends/flock/tests`): 7 new tests pass, and no other outcome changes.
- **Three new lint failures** (the merge gate's `check` catches them too):
  1. **P10:** `program/registry/topp_words.py` has 928 lines, over the 800 limit, so split it. `check/match/program_compare.py` has 927,
     above its recorded 905; move the new comparison out, and don't raise the cap.
  2. **P11:** `check/match/program_compare.py:56` `_as_v1_selects` names a version. Name the job.
  3. **By-name:** `program/registry/topp_words.py:265` `_folds`: `name in ("gate", "gatei")`. Decide it from structure, or allowlist it
     with the reason.
- **One condition:** add #169's constructed divergent-halves row to `test_the_keep_word_as_word_gates_is_topp_keep`, so the word
  gates are pinned on the case #169 changed.
- **Digests:** only #101 among the 13 moves again: its Program to about 23.26e9 word gates. Its new digest comes from the epoch's
  #101 L40S Build, per root.
- I've sent the fix list to the lowering lane (`lanes/flock-ir-lowering/20260928T0605Z-…`).
