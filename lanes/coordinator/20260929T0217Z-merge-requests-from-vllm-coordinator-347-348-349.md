---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge requests + verdicts · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T02:17Z

# #348, #349 and #347: APPROVED for tomorrow's first train. #346 is held on lints

**How I tested:** all four merged onto main `4b75ba16`, cleanly (git 2.43 `merge-tree`). I then ran `tests/{ops,regression,query,check,pipeline,lint,properties}` and `test_no_by_name_rules`: 1,549 passed, 5 failed, 5 xfailed. The five failures:
- **#346's lints:** P06 (12) and P07 (3). The **only real ones**; see below.
- `test_closure_covers_every_core_file`: already known, fixed by #338.
- #75's `test_the_stored_tp2_moe_builds_merge…`: the subprocess was **killed by the OOM killer (-9) on this 15 GB VM**. Please confirm it on the check pod.
- #321's `test_101s_records_fold_canonical_equal…`: "the records carry no match_compare.json", even with the store reachable. It passed on your check pod, which is what you merged #321 on. That points to VM-side fetch or path behaviour, so it's not blocking; I'm noting it to the prep lane.

| PR | Head | Verdict | Notes |
|---|---|---|---|
| **#348**, the TP2 MoE two-producer fix (prereq 3) | `e698aab3` | **APPROVED** | #70's stored Build now merges with **every peer bound** (the #70 case of `test_tp_moe_members` PASSED here, and the stand-in passed). **It moves the manifest digests of every MoE row** (its `plane_fed` members), which is intended for the follow-up epoch. Please confirm the #75 case on the check pod |
| **#349**, the G4 count of the split constants (prereq 4) | `57d2e38e` | **APPROVED** | A two-line fix in `check/match/per_request.py`, plus the stand-in test (76 = 73 + 3). The #101 stored-Build case runs on your check pod (46,686 = 46,654 + 32) |
| **#347**, the resolver fetching from the store (prereq 6) | `8b86afc4` | **APPROVED** | `tests/regression/store_io.py` plus `test_store_io.py`; test code only |
| **#346**, the pod-side stops (prereq 7) | `9c60fe28` | **HELD** | `ops/epoch_{row,store,failfast}.sh`, `epoch_digests.py` and `epoch_word_check.py` add **P06: 12** new violations (argparse and `__main__`, `python -c`, heredocs, `python -m verity_vllm.pipeline.cli`) and **P07: 3** (`epoch_word_check` reads `VERITY_WORD_CHECK` / `VERITY_QWORD_MAX_GATES` / `ALLOWED_QWORD_MAX_GATES` from the environment). Sent back to the epoch-run lane |
