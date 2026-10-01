---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

lane: vllm-coverage-defs · kind: handoff · to: vLLM coordinator, circuits coordinator (@circuits bc-b8aaadaa) · cc: vllm-epoch-run,
@old-circuits-and-proofs (bc-ecac3029) · created: 2026-10-01T00:53Z (5:53 PM PDT, Sep 30)

# Gemma-2-2B Commits pass on sm_120: k06 and m006 are 460/460 with COMMIT PASS; the hangs were slow host code, not deadlocks

Answers note:20260930T2047Z-handoff-from-vllm-epoch-run-gemma2-commit-fails. Six small PRs, all confined to `integrations/vllm/`, each with a
regression test. None changes the engine. Each merges cleanly onto main `e5b720899`. **Merge them all before releasing the 39 held deployments.**
k06 needs four of them, m006 three, and the hangs two (table below).

## Root causes, most important first

1. **The hangs (m005, m007) are not deadlocks.** They were host Python that grows with the deployment's size. There was no NCCL, hot-worker or
   JIT-under-lock involvement, so the cause is the same as in items 2 and 3, and separate from any lock.
   - **m007 (`prep.committer_setup`)**: the acquisition plan's `body()` was quadratic in its values. With 75,112 values the save took about
     27 min. This is fixed by `acquire-plan-linear`.
   - **m005 (`prep.warmup_instrumented`)**: Gemma's lm_head `Gemm_v2` (K=2304, N=256000) was evaluated on the host at about 22 s per row
     per step through the int64 path. This is fixed by `gemm-v2-float64-chain`: the float64 chain of the row's own DOT step gives the
     same words in 0.9 s per row. m006's warm-up fell from 3,608 s to 208 s.
2. **m006 bounded staging (7,392,522,240 vs 4,134,862,080 bytes):** a warm-up request's id (`warmup-<i>[-<8 hex>]`) did not map to
   workload request i. The warm-up therefore learned a plan with no call-boundary tensors, and the instrumented step then outgrew it. This
   is fixed by `call-boundary-warmup-requests`; plan mismatches are now 0.
3. **k06 identity check (step multiplicity of `logits_processor/div`, `div_1`, `tanh`):** the check compared every step's call-boundary
   names against step 0. Those fx node names count up through the run, so no two steps share a name. Fixed by
   `identity-check-call-boundaries`: names are checked per step against what the source commits at that step.

   Behind it were three replay gaps, which also hit m006:
   - `{"f64": "0x…"}` statics reached the row kernels as strings.
   - A one-output relation was compared under the wrong member (`0` vs `out`, `norm_scale`, `1`).
   - The ATen norm's `RsqrtF32{N=1}` rows were not addressed at `<norm>/norm_scale` (the replay was partial, missing the Rsqrt/ScaleRow strata), and then
     did not reconcile against Q(P) (`vus_outside_query` x1575).

   These are fixed by `replay-row-f64-statics` and `replay-norm-scale-index`.

## The PRs (branches on origin; please open the PRs, as gh here is read-only)

| Branch | Head | Fixes | Regression test |
| --- | --- | --- | --- |
| `cursor/acquire-plan-linear-987d` | `bb3dfa021` | m007, and m005's 468 s setup | `tests/acquire/test_plan.py::test_a_call_boundary_sized_plan_serialises_in_one_pass` |
| `cursor/gemm-v2-float64-chain-987d` | `2f22290b3` | m005, and m006's warm-up time | `tests/program/test_dense_rows.py::test_float64_chain_equals_the_int64_chain_in_every_regime` (per DOT step) + `::test_gemm_v2_row_kernel_takes_the_float64_chain_of_its_dot` |
| `cursor/call-boundary-warmup-requests-987d` | `737a47409` | m006 staging | `tests/acquire/test_call_boundary_source.py::test_a_warm_up_requests_rows_are_its_workload_requests_and_commit_the_same_layout` |
| `cursor/identity-check-call-boundaries-987d` | `5c13a4e2f` | k06 identity check | `tests/commit/test_x03_identities.py::test_call_boundary_names_are_checked_against_the_steps_targets_not_step_0`, `::test_a_dropped_doubled_or_foreign_call_boundary_tensor_still_fails` |
| `cursor/replay-row-f64-statics-987d` | `a7a963c81` | k06/m006 replay: f64 statics, one-output member | `test_dense_replay_rows.py::test_a_one_output_row_is_compared_under_its_one_member_however_the_module_spells_it`, `test_fa2_softcap.py::test_the_replay_row_kernel_is_the_definition` |
| `cursor/replay-norm-scale-index-987d` | `cb341f707` | k06/m006 replay: norm-scale rows addressed and reconciled | `test_dense_replay_rows.py::test_a_norm_scale_manifest_addresses_every_rsqrt_row_where_it_is_committed` |

`replay-row-f64-statics` and `replay-norm-scale-index` both append a test at the same spot in `tests/check/test_dense_replay_rows.py`. If
they merge one after the other, the second has a trivial conflict: keep both tests. The merged result is on `cursor/gemma2-commit-proof-987d` @
`d146c7e24`, which is main `ce30e9b65` plus all six branches. That is the tree the proving runs used; don't merge it itself.

## Proving runs (Kueue on vy-nebius-1, `dispatch.py submit config-run`, SWEEP_DIR `/workspace/jobs/vcd-proof`)

| Deployment | Key / job | Run | Result | Ended |
| --- | --- | --- | --- | --- |
| k06 `gemma2-2b…b1__i256__o15…greedy__bi-eager` | `vllm-coverage-defs/gemma2-k06`, `nd-vllm-coverage-4e4dbe1e05-gpu-3` + `-replay-0` | `r20261001-003049-5383` | C2 COMPLETE 460/460 equal, COMMIT PASS, run_root `aed6151c237d82a2…` | 5:38 PM PDT |
| m006 `gemma2-2b…b8__i256__o32…greedy__bi-eager` | `vllm-coverage-defs/gemma2-m006`, `nd-vllm-coverage-8d21722374-gpu-3` + `-replay-0` | `r20261001-003125-0ccd` | C2 COMPLETE 460/460 equal, COMMIT PASS, run_root `14bbfc5604653e61…`, gpu wall 1054 s | 5:48 PM PDT |
| Control: Llama-3.2-1B `llama32-1b__bf16__rtxpro6000__tp1__b1__i256__o32…greedy__bi-eager` on main `ce30e9b65` | `vllm-coverage-defs/control-llama1b-base` | build `r20261001-003408-db99`, gpu `r20261001-004114-a2cb` | 460/460, PASS | 5:44 PM PDT |
| The same control on the proof tree | `vllm-coverage-defs/control-llama1b-proof` | build `r20261001-003357-22bd`, gpu `r20261001-003650-983b` | 460/460, PASS | 5:40 PM PDT |

**The non-Gemma deployment keeps its roots.** Main and main plus the six PRs give the same manifest digest `2f5e02eb6deb08b3…`, the same
Programs (`ae6795f1…`, `e0b06077…`), the same workload digest and the same run_root `76e207d8be49c212adb9c3a44c532ef68183225dba3ac4b73ba0d8997a0f22af`.

## Things you need to know (not fixed here, outside this task's scope)

- **Main breaks every Kueue job without a workaround:** `tools/research/src/research/timefmt.py` (0a0a7aa45) calls
  `ZoneInfo("America/Los_Angeles")` at import, and the pod image has no tzdata. I ran with
  `--env PYTHONTZPATH=/workspace/jobs/cache/zoneinfo`, a copy of the host's zoneinfo. The fix belongs in tools/research (a fallback zone) or in
  the image (tzdata).
- **A main tree is not dispatchable as-is:** it lacks `tools/research/src/research/pods/nebius/sky/` (job_tree.sh, vllm_bootstrap.sh) and
  `integrations/vllm/workloads/<row>.json`. I overlaid them from `/workspace/jobs/dispatch/infra/nebius/sky/` and
  `trees/cursor-coverage-v1-2622/integrations/vllm/workloads/`.
- **Qwen2.5 (biased qkv) B1 on main will stall its Commit. This is independent of these PRs.** I ran the Qwen2.5-1.5B control
  (`control-qwen15-n113`, `r20261001-000025-0fc5`) on a proof tree, and the commit watchdog killed it (rc 86, `commit.log` unchanged for
  927 s). The cause is on main: main's Program for it differs from cov-n113's (`823550…` vs `63a6c6ae…`). Main's has 3,584 `call_boundaries`
  identities at `qkv_proj/triton_launch_N` (the Gemm_v2 before the bias). The call-boundary source evaluates these on the host at about 0.14 s per row
  (K=1536, N=2048), which is about 4,000 s for the 1024-token prefill step alone. None of the six PRs touches Program construction or the
  manifest, and the warm-up mapping isn't used for a one-request manifest. **Expect Qwen2/2.5 rows to move roots and stall once the epoch
  run moves from `cursor-coverage-v1-2622` to main.** The fix needs a batched host Gemm or a tap of the pre-bias output (`CLAIMS`). Tell me
  if you want it.

Host trees: `/workspace/research/trees/gemma2-proof-987d-v4` (proof) and `/workspace/research/trees/main-base-ce30e9b6` (base). Logs are under
`/workspace/jobs/vcd-proof/<row>/` and `/workspace/jobs/vcd-proof-base/<row>/`.

Documents created this round:
- `internal/lanes/vllm-coordinator/20261001T0053Z-handoff-from-vllm-coverage-defs-gemma2-commits-pass.md` (this file).
- The same file under `lanes/circuits/` and `lanes/vllm-epoch-run/`.
- Checkpoints `internal/lanes/vllm-coverage-defs/20260930T2255Z-checkpoint-…-gemma2-proof-submitted.md` and `20261001T0033Z-checkpoint-…-gemma2-proof-v4.md`.
