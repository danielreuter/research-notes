---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T13:30Z
---
# PR #63 verdict: APPROVE for merge (head `898c32ef`, vllm-more-exports)

- **Change** (one commit on `e3a2d81d`): the exporter learns FP8 block GEMM and MoE expert GEMM coordinates.
  - `ScaledMmFp8Block_v1` becomes `ScaledMmFp8BlockCoordinate<K,G>` (x and w e4m3, the sx/sw block scales, y bf16, through
    `HopperE4m3QgmmaDot32`).
  - `MoeExpertGemm(W)_v1` becomes `GemmCoordinate<K>` / `RoutedGemmCoordinate<K>` over the routed expert's rows.
  - **The bug it fixes:** `vu_store.py` stored weight rows only for `GEMM = ("Gemm_v1", "Gemm_v2")`, as `u16`. Every FP8 GEMM and
    MoE expert unit was dropped silently. It now dispatches through `WEIGHT_ROWS_OF` per family, with the word type taken from
    the array.
- **Safety:** every recomputed coordinate is compared with the row's recorded output word and raises `DecompositionMismatch` on a
  difference, so a wrong decomposition rule can'"'"'t produce a silently wrong instance set.
- **Record effect:** none. It'"'"'s exporter-only (`pipeline/vu_export.py`, `vu_store.py`, the test). Nothing on the Build, Match or
  Commit record path changes.
- **Recheck against main `2775d2c8`:** clean. Every ratchet lint runnable without pytest passes on the merged tree (39/39).
  `vu_export.py` is 567 lines (under the P10 800 cap).
- **Tests:** `tests/pipeline/test_vu_export.py` +69 (FP8 block and MoE expert decompositions). I couldn'"'"'t run pytest here; rely on
  the lane'"'"'s pod run.
- **Context:** the lane captured no sets tonight (#74'"'"'s Commit doesn'"'"'t fit 251 GB; #67'"'"'s export ran out of time budget before
  its first draw). Those two fixes are with vllm-vu-export (the budget) and m32 (#74'"'"'s off-host Commit crash), and each comes here
  for review.
