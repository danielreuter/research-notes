---
id: integrator/20260924T0215Z-from-v2-residue
lane: vllm-v2-residue
kind: status
status: open
repo: verity
---
# v2-residue → integrator: `lane/vllm-v2-residue` = `8e0cbf27`, ready to merge

Three commits on staging `270db8f7`. The lane merges into staging `da63c97` cleanly (trial tree `7c3654b2`). Gates are below. The lane touches nothing in `sampled_replay.py`, `tp/*` or the by-name allowlist (still 312).

## Commits
- `004724a8`: **VERITY_SKIP is applied or refused.**
  - `NativeHostCommitter.apply_skip` drops the skipped classes' modules from the selection of record: the class tables at construction under v1, and the plan's selection inside `apply_plan_to_committer` under v2.
  - The v2 record gains `skip`: the classes, the dropped modules and the Values left unacquired.
  - `SkipRefused` is raised by name in these cases: a class that drops no selected module; the runner's sampler; and at `install()`, a skip that was never applied or whose class was selected again.
  - `plan_selection()` is factored out of `apply_plan_to_committer`.
- `b13f1a15`: **compiled rows select from the plan under v2.**
  - `commit_delta` hands the manifest to `CompiledGraphSource.use_plan` before the engine build. `wrap_model` derives the plan the same way the committer does and wraps `install.plan_selection`, applying VERITY_SKIP too.
  - Under v2, `wrap_model` refuses by name when there is no plan or manifest.
  - At install, the source's selection is held equal to the committer's, and any difference is refused.
  - The class-table path remains for `ACQUIRE_ENGINE=v1` only.
- `8e0cbf27`: **the IR registry leak** (below).

## One reading to confirm (defect 1)
"Unsound" skips are read narrowly: the refusals above. A skip that removes the only acquisition of a required boundary Value is **applied and recorded** (`skip.values_unacquired`), not refused. Every VERITY_SKIP does that by design, because it is a marginal-cost ablation and not a commitment. If you meant a stricter rule, it is one check in `apply_plan_to_committer` on `values_unacquired`.

## The leak: cause, reproduction, fix
- **Cause:** `test_required_manifest.py::test_registry_unavailable_is_a_named_fault_not_a_manifest_result`.
  - It "repaired" the environment with `monkeypatch.delitem(sys.modules, "verity.ir.defs")`. The next import then re-executed `verity.ir.defs` as a second module with its own empty `REGISTRY`.
  - Every `verity_vllm.registry.*` module first imported in that window (`b1`, `fp8`, `sampling`, `prims`, …) registered into the orphan for the rest of the process.
  - It only bites on a worker that had not yet imported the registry, which is why the full-suite collection order and `--dist loadfile` gates never showed it.
- **Original errors (p2p4 merged run, `/workspace/p2p4/logs/merged.log`):**
  - stoch ×7: `TypeError: DivFullRcp() missing 1 required positional argument: 'b'`.
  - promotion ×2: `Fp8GroupQuant_v1 is not a registered Definition`.
- **Deterministic reproduction** (one process, `-p no:randomly -n 0`): that one test, then `test_required_values_promotion.py`, then `test_sampled_replay_stoch.py`.
  - On `270db8f7`: **9 failed** (8 promotion, 1 stoch). The split differs from p2p4's because it depends on what the worker had already imported.
  - With the fix: **17 passed**. Also 17 passed on the `da63c97` trial merge.
- **Fix:**
  - The test loads `verity.ir.defs` first and puts **that same module object** back.
  - New `integrations/vllm/conftest.py`: an autouse guard fails any test that leaves a loaded `verity.*` module swapped, either in `sys.modules` or on its parent package attribute. It names the module and restores the originals.
  - On staging with only the guard added, it fails the culprit test naming `verity.ir.defs`.
  - The guard snapshots parent attributes, because `verity.ir.query` is legitimately a function.
  - Outside the census scope; the dead-code lint passes.

## Gates (cpu2, the same commands and env as `p6_logs/gates.sh`)
| run | result |
|---|---|
| lane `8e0cbf27`, main `-n 10 loadfile` ×2 | run 1: `t1` + `fa2_commit/test_roundtrip::test_transient_storage_is_released`. Run 2: `t1` − `test_twins` (known flake). Nothing else new. |
| staging `270db8f7`, main repeat | = `t1` exactly |
| lane extra / real-HF | 0 F, 81 pass (`t1` 73; +8 new tests) / the same 7 F |
| targeted `-n 4 loadfile` (p2p4's leak config), lane vs staging | the same 2 F (`test_admit_r19_host_working_set` ×2); +8 pass |
| trial merge `7c3654b2`: lints / leak repro / targeted | 7 pass / 17 pass / = lane |
| trial merge `7c3654b2`: main / extra / real-HF vs `d1` | MERGE_GATES |
| harness T0+T1, `VERITY_REGRESSION_ENGINE=v2`, rows not #11/#39, oracle expected (lane tree) | HARNESS |

- **The fa2 failure is a flake, not the lane.** It is a `tracemalloc` bound: 38,493 B against 37,984 B, over by 509 B, and it depends on what the worker has already warmed.
  - It passes alone on staging, on the lane and on the lane with `--noconftest`, and it passed in the lane's second main run.
  - The guard never runs inside a test body.
- **Harness scope:** it exercises none of the committer, plan-selection or compiled-source code. It was run because the new conftest applies to every harness check (`rebaseline` runs pytest).

## Merge notes
- dead-code-2 is clean: it deletes none of the 9 files. The merge onto `da63c97` is clean (`git merge-tree`).
- tp-v2 `3cd4de3`: the only conflict is `v1_bridge.py`, identical to staging's own conflict with tp-v2.

## Pod state
- cpu2 `/workspace/v2residue/` holds the trees `ref`, `src`, `guard`, `d3` and `mrg`, plus `logs/`, `rec/hsrc`, `jdiff.py`, `gates.sh` and `hrun.sh`. Reservations are removed.
