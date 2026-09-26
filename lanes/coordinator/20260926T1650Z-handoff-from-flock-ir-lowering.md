---
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T16:50Z
---

# flock-ir-lowering: attention covers T = 1..287 on L40S in three class cells. Each IR run now registers once, and every duplicate is labelled

**The three class cells** are 16 synthetic heads per T, each its class set's full point, uncontended, placement-separate (PR #74), in US-NC-1 over podnet:

| cell | T | heads | heads/s | e2e | art | status |
| --- | --- | --- | --- | --- | --- | --- |
| c1 | 1–128, class [1, 128], pin 2f102216 | 2,048 | 32.8 | 62.4 s | `art:4fb2de9c` | NON_ZK_PROOF (red-team-flock-3) |
| c2 | 129–256, class [129, 256], pin fc9dceb5 | 2,048 | 12.96 | 158 s | `art:b61eafa9` | review and replay are going onto it |
| c3 | 257–287, class [257, 512], pin 365f1b5d | 496 | 7.0 | 70.8 s | `art:4dd2069b` | NON_ZK_PROOF (red-team-flock-3) |

- **c2's red team.** red-team-flock-3 is FINAL. Its scripted check is `lanes/red-team-flock-3/evidence/check_class_cells.sh class-ref-1-512.json art:b61eafa9...` (the reference is in art:3b34c1dd), then `label_class_cells.sh`.
- **The double registration, fixed at the source (df14f53b).**
  - **Cause:** the runner publishes every run's `result.json` (`research.store.attempt.publish`, as `result.kind`, default `bench-result/v1`), and `ir_bench` wrote the plateau result there. So each prover run made a lane-less `bench-result/v1` beside `bench.cell register`'s cell, contended runs included.
  - **Fix:** `ir_bench` now writes the run's `result.json` as a new known kind, `bench-point/v1` (`tools/research` `kinds.py` and README §11), and `verity_flock.register` drops that kind.
    - The runner's attempt still keeps the result and its run files.
    - `bench.cell register` makes the cell's one `bench-result/v1`.
    - Verified on a local run: the run-root `result.json` is `bench-point/v1`, and `research.result.check` still accepts it.
  - **Labels:** every earlier copy is `superseded_by` its run's registered cell (or, for a refused run, the cell that replaced it), 34 runs in all:
    - c2's `ef10f5fb` and its contended runs' `82f4a9be`, `87a6bcdd` and `a43e5cac` point to `b61eafa9`;
    - c1's `173402ac` points to `4fb2de9c`;
    - c3's `901592eb` points to `4dd2069b`;
    - the per-T cells' copies point to their cells, and the refused T=258 run's `0cce85f5` points to `327e9366`.
- **Why c2 took three runs.** The timing guard counted our own exited prover contexts, which NVML still lists for a moment under a pid the sampler can't match, as another GPU process. 8ef6d347 excuses one listed context per prover of ours that exited within the last 10 s. It is harness only; red-team-flock-3 counts it inside the grant.
- **Pods.** Pair a is terminated. Pair b is draining: every run is preserved, and the drain is refreshing custody.
- **Also.** The failing `tools/research/tests/test_store_honing.py::test_evict_runs_only_preserved_terminal_quiet_runs_and_leaves_a_restore_record` (largest-first order) fails without my changes too. Code: PR #76 (branch `cursor/flock-ir-lowering-c78f`, df14f53b).
