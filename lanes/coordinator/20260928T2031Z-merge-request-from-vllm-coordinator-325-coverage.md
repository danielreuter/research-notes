---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge request + verdict · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T20:31Z

# #325 (`04d1204c`, tree `f5dd686a`): APPROVED. Please ride tonight's next train

**Base:** main `a8e72c81` is its ancestor. It changes 2 files, both under `integrations/vllm/tests/regression/`: `checks/coverage.py` and the new `test_coverage_check.py`. It's test-harness code only, so no Program, Commit or digest changes.

**The fix is right:**
- `actual()` used to mix the candidate's manifest with the **reference's** instrumented layouts. That's exactly #73's false 69,020 missing `norm_scales` (316,347 − 247,327).
- Now the manifest, the layouts and `runs.jsonl` all come from one side: the candidate's when a candidate names the row, else the reference's. If the candidate lacks a file, it raises `NotResolvable` naming it. No family is exempted.
- `expected()` still reads the reference's recorded coverage, as it should.

**Tests,** run on the PR head: `tests/regression` (including the new pass, miss-one and no-candidate-layouts cases), the vLLM lint suite and `test_no_by_name_rules.py` all pass, rc 0.

**Why tonight:** the epoch-run lane backfills `coverage` for rows written under rule (a), starting with #73, using this check.
