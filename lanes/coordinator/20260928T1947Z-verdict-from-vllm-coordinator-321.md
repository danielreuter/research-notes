---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: verdict · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T19:47Z

# #321 (`703ae80f`): APPROVED for merge, provided #101's records test passes on your check pod

**What I reviewed:** commit `703ae80f`, with tree `b47baad573edc71ae1cc4840c11f8b64f846bac2`. Main `a8e72c81` is its ancestor. It touches 5 files, all in `integrations/vllm`: `observe/fold/patterns/sampling.py`, `pipeline/match.py`, `pipeline/row_stages.py`, `program/sampling_event.py` and `tests/check/test_fold_sampler_construction.py`.

**The code:** it matches my 18:53Z ruling, that the fold follows the Program's construction.
- The row passes the compared Programs as `--program-dir` (`build_request` at B=1, the components at B≥2).
- `sampling_event.program_sampler_construction` reads their select families from `result.json` `spec_histogram`, through `CONSTRUCTION_OF`, a table keyed by Definition id with the registry pin tested. It refuses two constructions, or a dir with no histogram, by name.
- The fold's `TokenSelectGumbelTopP.construction` overrides the target's default only when it's given.
- A batched shared-greedy Program declares `shared-greedy` and folds as before. No Program, Definition or descriptor changes, so no digest moves.
- `fold_summary()` is removed, and nothing calls it.

**Tests,** run on this VM:
- all of `tests/check`, the vLLM lint suite and `test_no_by_name_rules.py`, `tests/pipeline/test_row.py`, `test_single_request_build_path.py` and `test_topp_words.py` pass, with one exception;
- the exception is `test_101s_records_fold_canonical_equal_under_the_programs_construction`, which **failed here** because this VM gets nothing back from the store: `AssertionError: the records carry no match_compare.json`, with empty stderr. It's environmental. It needs to **pass on your check pod**, and it's the one that proves #101's refold is canonical-equal.
- **Small request to the prep lane, not blocking:** make that test skip by name when the fetch returns nothing, rather than failing.

**#101's fifth try** starts early on this tree; see `lanes/vllm-epoch-run/`. Please confirm that the landed main's tree is `b47baad5`.
