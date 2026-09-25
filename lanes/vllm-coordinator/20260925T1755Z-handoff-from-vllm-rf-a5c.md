---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-a5c (bc-ac8c8a30)
created: 2026-09-25T17:55Z
---
# MERGE-READY vllm-rf-a5c: `lane/vllm-rf-a5c` @ 40b9e571 (base main f7de4620)

- Head `40b9e571` = a5b `da9e4847` rebased onto main (`ce6d69d4`), then `git merge origin/main` at `f7de4620` (main had moved past
  `38a8d35d`; b5patb landed). Pushed.
- Lints 45/45 head and base. Gate (b) same pod (t1), head `r20260925-170857-a861` vs base `r20260925-173534-b495`:
  4046 vs 4023, **0 new failures / skips / skip reasons**, 0 outcome changes, 40 only-in-base (deleted row_pod tests + CLI renames), 63
  only-in-head all pass.
- #101 at `40b9e571` on g1 `r20260925-170927-4a2d`: SAME-OF-RECORD (program ccc21347, manifest 90f81868, run root 7adcef49, commit PASS).
- #70 at `da9e4847` on tp2d `r20260925-144310-53e5`: commit FAIL of record, cmp70 32/32 equal vs f1's base.
- Gate (a) at `da9e4847` only (73P/85S, 0 changes); not re-run on the merged tree — say if you want it.
- Behaviour changes: none intended (one CLI; same flags/defaults/env). Found-not-fixed: TP Commit writes no `commit/verdict.json`;
  row_pod heredoc verdict is now `row_records.match_summary`, not folded into `check/verdict.py`.
- Details: `lanes/vllm-rf-a5c/READY.md`, evidence `lanes/vllm-rf-a5c/evidence/`.
- Pods: tp2d terminated 16:47Z; g1 handed to b5vc 17:40Z; t1 handed to b5vc 17:55Z. New spend about $5 of $10.
