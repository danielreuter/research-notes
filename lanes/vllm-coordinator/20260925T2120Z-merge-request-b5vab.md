---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: b5vab, split `engine/vllm_adapter.py` (B5, pure structure), from vLLM coordinator bc-ecac3029, 21:20Z

- **Merge:** `lane/vllm-rf-b5vab` @ **`3201c3f4`**, `--no-ff`: one commit `d0e04cf8` plus two merges of b4c heads.
- **Sequencing:** it depends on b4, which **is already in main** (`d7eb3173`, merging `9689a1ef`). Nothing to wait for.
- **Recheck against main `fee32f05`:** clean, and every ratchet lint runnable without pytest passes on the merged tree
  (39/39). Since its base `9689a1ef`, main (c4ir, gc, PR #29, the bootstrap fix, non-vLLM work) shares only `README.md`
  and the p07/p08/p10/p11 allowlists with it. No one else touched `engine/vllm_adapter.py`.
- **Change:** `engine/vllm_adapter.py` (1,913 lines) is split into `engine/{build,capture,pinned,run_facts,code_identity}.py`.
  56/56 statements are verbatim (source and AST). `vllm_adapter` re-exports every moved name, so no importer changed, and
  `load_workload` and its callees stay in place for gc's path-extracting tests. The allowlist entries moved 1:1, the P10
  entry (1,913) is deleted, and none grew. One test's monkeypatch target changed
  (`test_compiled_execution_header` → `engine.build`).
- **Gates at `3201c3f4`** (all preserved on R2):
  - lints rc 0 at head and base;
  - gate (b) against `9689a1ef` on the same pod: 4063/4063, 0 new failures, skips or skip reasons; 2 flaky gc-freeze
    tests go from failed to passed;
  - gate (a) T0+T1 (two halves `r20260925-181956-7c6e` + `r20260925-182011-fabf` on c4ir-reg): 158 = 73 passed / 85
    skipped, the same as a23b's base test by test.
- **Acceptance:** #101 (`r20260925-185918-5fec`): program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`, commit
  PASS, non-interference 992/992, equal to the record and to b4c's run on the same pod.
- **PR #29:** the head predates PR #29, but b5vab shares no file with it, and the merged tree passes the lints.
- **Found, not fixed:** gc's `_adapter_fn` tests; `engine/capture.py` is at 795 of 800 lines. Details:
  `lanes/vllm-rf-b5vab/READY.md`. Pods terminated; about $9 of $16.

