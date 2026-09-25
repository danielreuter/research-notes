---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b5vab
created: 2026-09-25T21:10Z
---
# MERGE REQUEST vllm-rf-b5vab: `lane/vllm-rf-b5vab` @ `3201c3f4` (engine/vllm_adapter.py split, B5)

- **Head `3201c3f4`**, base b4c `9689a1ef`; lane work = one commit `d0e04cf8` + two merges of b4c heads. Merges **cleanly**
  with main `fee32f05` (scratch check, not pushed; lint scan 0 problems, split proof holds there).
- **Gates at `3201c3f4`** (predates PR #29):
  - lints rc 0 (head `r20260925-181128-fbe5`, base `r20260925-181148-2918`, b4b-cpu).
  - gate (b) vs `9689a1ef` same pod: 4063/4063, 0 new failures/skips/skip reasons; 2 flaky gc-freeze tests failed->passed.
  - gate (a) T0+T1 on c4ir-reg (two halves `r20260925-181956-7c6e` + `r20260925-182011-fabf`): 158 = 73 passed / 85
    skipped, = a23b base test by test; only the known #70/#75 reworded skip reasons (a4's).
  - #101 on b4b-g1 `r20260925-185918-5fec`: program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`, commit PASS,
    non-interference 992/992 = record (and = b4c's 9689a1ef run on the same pod).
  - All runs PRESERVED on R2.
- **Behaviour:** none. Verbatim moves (56/56 statements, source + AST), `vllm_adapter` re-exports every moved name (no
  importer changed), allowlist entries moved 1:1, P10 entry (1,913) deleted, no allowlist grew. One test's monkeypatch target
  (`test_compiled_execution_header` -> `engine.build`).
- **Found, not fixed:** see READY.md (gc's `_adapter_fn` tests; capture.py at 795/800).
- READY: `lanes/vllm-rf-b5vab/READY.md`. Pods all terminated; spend ~$9 of $16.
