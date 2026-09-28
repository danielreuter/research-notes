---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: flock-ir-lowering · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T06:05Z

# #231 @ 15ab6a3d: three lint fixes and one test row, then I approve (it's G0 for the re-baseline)

1. **P10:** `integrations/vllm/verity_vllm/program/registry/topp_words.py` has 928 lines, over the 800 limit: split it (the builder,
   and the pieces). `check/match/program_compare.py` has 927, above its recorded 905: move the v2 comparison into its own module. Don't
   raise either cap.
2. **P11:** `program_compare.py:56` `_as_v1_selects` names a version: name the job.
3. **By-name:** `topp_words.py:265` `_folds`: `name in ("gate", "gatei")`. Decide it from the structure, or add an allowlist entry
   with the reason if it's a fixed IR field name.
4. **Test:** add #169's constructed divergent-halves row to `test_the_keep_word_as_word_gates_is_topp_keep`.

Then hand off the new head to `lanes/vllm-coordinator/`. I re-run the lints and the jdiff, then send the merge request. The re-baseline
is waiting on it.
