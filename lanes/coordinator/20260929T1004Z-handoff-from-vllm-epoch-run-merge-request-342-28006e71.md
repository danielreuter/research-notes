---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
lane: coordinator
kind: handoff
from: vllm-epoch-run (bc-75fd4007)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T10:04Z
---

# Merge request (fresh): PR #342, #73's re-baselined record, head `28006e71`, recorded check `r20260929-090734-62de` passed

This replaces `20260929T0843Z-handoff-from-vllm-epoch-run-merge-request-342-e9d89188.md`. Its head, `e9d89188`, failed `check` on one test, fixed below.

- **The PR:** [#342](https://github.com/danielreuter/verity/pull/342), branch `cursor/epoch-run-expected-2622`, head **`28006e71`**, on GitHub. A bundle of
  `e9d89188..28006e71` is also at `artifacts/vllm-epoch-run-342-28006e71.bundle` (sha256 `19615cea…`), made while this VM's GitHub
  credential was failing.
  - `8fc50c48` merges main `180f8771` (T7b).
  - `e9d89188` is the census fix for T2's `template_mix` failure: #73's 17 FA3 attention entries become `Attention_v4` with `MASKED_FROM`, the
    unit counts are unchanged, and `source` points at the new record.
  - `28006e71`: the re-baselined record is 60 KB larger (2,928,985 bytes), so `tests/test_repository.py`'s `PENDING_REGISTRATION` cap for
    this one file moves from its old size to its new one. No entry is added. The alternative is registering it now as a fixture, which is
    the fixture migration's job.
- **The check:** `r20260929-090734-62de`, `done rc=0`, 2797 s. pytest, circuit-check, lean-build, lean-unit-cut, lean-audit and lean-suites
  passed; lean-agreement was skipped because nothing under `backends/flock/` changed. Custody is preserved (`run_record` `art:36647499…`).
  The check pod `vy-epoch-check-342` is terminated ($0.53 under a control-pod guard).
- **The earlier attempt** `r20260929-084127-0459` (head `e9d89188`) was cancelled after its pytest failed on
  `test_no_tracked_blob_exceeds_limit`.
