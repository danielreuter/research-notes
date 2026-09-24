---
lane: integrator
kind: handoff
from: vllm-57-fix
created: 2026-09-24T10:27Z
---

# staging 2c8aa2b3 crashes every v2 Commit (stale `verity_capture` imports from #57's fix after the relayout); fix is `f16703a2` on lane/vllm-57-fix, a fast-forward from staging

- **Symptom.** #67's Commit at `2c8aa2b3` (run `r20260924-101839-ef1b`) died after 29 s:
  - `commit_delta.py` line 1417 raised `ModuleNotFoundError: No module named 'verity_capture'`.
  - The stage then graded a leftover `commit/runs.jsonl` and reported FAIL.
  - Any v2 Commit with a required manifest takes this path, so the final harness would crash on every row.
- **Cause.** The relayout's move map predates #57's fix, and its import check executes module bodies only. The fix's function-local imports kept their old paths:
  - `commit_delta.oracle_producers_of_record` (lines 996–998) and `main` (line 1417) import `verity_capture.commit`.
  - `oracle_compare.producers_of_programs` imports `verity_vllm.query.correspondence`, now `verity_vllm.correspondence.reader_for_query`. That one is inside a try, so it would have silently dropped the producer facts.
  - Your `2c8aa2b3` fixed only the test file's imports.
- **Fix: `f16703a2`** (`origin/lane/vllm-57-fix`, parent `2c8aa2b3`, so it fast-forwards) repoints those imports.
  - It also adds `tests/test_imports_resolve.py`, which uses `ast` to resolve every absolute first-party import in `verity_vllm/` and `tests/`, function-local ones included.
  - A scan of the whole tree finds only these, plus `data/contract/ck-elem/argmax_rule/measure_archive.py:27` importing `verity_vllm.capture`. That data script isn't on any Commit path and I left it alone.
- **Evidence in flight.** #67's Commit at `f16703a2` is running as `r20260924-102613-0196` on vyv-sw-67b, ETA about 12:05Z. Pod tests at `f16703a2` are running on vyv-sw-57; results go in my state note.
- **For your final harness,** please take `f16703a2` before launching it.
