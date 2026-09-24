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
- **10:32Z, re your 0905Z ask (#57 Commit-only on the merged tip):** `2c8aa2b3` itself can't run it, so it runs at `f16703a2` (`2c8aa2b3` + the import fix), same Build/Match inputs as the PASS run: `r20260924-103124-47d5` on vyv-sw-57, ETA about 11:25Z. Pod tests at `f16703a2` are green (79 passed; 77 passed, 4 skipped). I'll append the verdict here.
- **11:36Z: #57 Commit PASS on the merged tree `f16703a2`.** `r20260924-103124-47d5`: `commit PASS rc=0 wall=3509s runs 3 failed 0`, every check PASS (runtime_match, local_replay, boundary_linkage, checkpoint_binding, execution_extent, required_value_coverage, program_source_identity; manifest_verify True). C2 oracle 159,840/159,840 equal; sampled replay 5,883/5,883 equal ×3; linkage 432/432; weights 316/316. Verdict `art:bad7b21ccf3ad4e615b298387f1d65ab5068baf3ca8bef44710792411eb8a97e`, preserved (readback, rc 0), 6 labels durable (`arm=merged-staging-2c8aa2b3-plus-f16703a2`). That answers your 0905Z ask.
- **13:05Z: #67 Commit PASS at `f16703a2`.** `r20260924-102613-0196`: `commit PASS rc=0 wall=8787s runs 3 failed 0`, every check PASS, manifest_verify True. Sampled replay 38,748/38,748 equal ×3 (the MoeSum strata that failed at `2c5e038b` now evaluate), linkage 1308/1308, weights 212/212. Verdict `art:51826b816021d736b7a5d66ebb4b883c662b73fcbcc869f01a6a5bdd8cb8b607`, preserved, 6 labels durable. vyv-sw-67b is drained and terminated.
- **Open item (not fixed here, fail-safe, costs time):** on rows with the FA2 tap (OLMoE), Commit pairs 1 and 2 never reuse pair 0's sampled replay. `binding_map_p{pair}.json` embeds `collector.fa2_tap_bounded`, whose counters accumulate across pairs in the one process (`split_launches` 32 then 48), and the replay-cache key hashes the whole file (`commit_delta.py` around 2385; the counters are written around 589). Each pair re-runs the ~25–30 min replay, about +55 min on #67. A fix would key on the map without `collector.fa2_tap_bounded`, or reset the tap stats per pair. It touches replay-reuse semantics, so it's your call before int-final.
