---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-26T22:19Z
---
# Merge-ready: norm-scale taps, PR #90 (`cursor/vllm-rf-normtap-57d5` @ `14ea93c6`)

**Merge request.** Branch `cursor/vllm-rf-normtap-57d5`, head `14ea93c6`, base `baa800c6` (origin/main at the start). It merges
cleanly into origin/main `56c62af2` (the two new main commits share no file with it) and into `cursor/no-recompute-partition-289b`
(`fd9f81e8`; see "Partition checker"). [PR #90](https://github.com/danielreuter/verity/pull/90) is still a draft. Pod terminated.
Spend is about $2.00 of the $10.

## What it adds (opt-in: `NORM_TAP=1`, `CommitConfig.norm_tap`, default 0)
- One committed f32 scale per norm Call per token row, family `norm_scales`, member `<norm module>/norm_scale`, in the same step stream
  and run root as the other committed values. The name `norm_scale` was already taken as by-name vocabulary in `FAMILIES`.
- **Fused CUDA norm** (`RMSNormFusedCuda_v2`): `verity-vllm norm-tap-build` (`ops/pod_norm_tap.sh`) builds a separate op from the
  sha-pinned generic `fused_add_rms_norm_kernel` of vLLM `d9105ea80` plus one `Tap` template parameter: thread 0 stores `s_variance`
  after the `__syncthreads()`. It is swapped in through `engine/hooks.py`, inside the manifest's norm modules and committed steps only.
- **Triton norm** (`RMSNormTriton_v1`): the pinned `_rms_norm_kernel` plus two lines (`scale_ptr`, `tl.store(... inv_rms)`).
  Qwen3's q/k norms use the same two kernels (scales shaped `[tokens, heads]`).
- **Gemma** (policy only, no kernel tap): the `RsqrtF32_v1{N=1}` output is protocol-required and captured at `torch.rsqrt`.
- With the flag on: `manifest build --norm-scales` adds one identity per (step, norm module), `Q_word_v1` counts the tapped scales as
  acquired interior words (`check_calls(acquired=...)`), the acquisition plan routes the family to the source, replay coverage names
  its mechanism, and form (B) skips the member (the Match record holds no value for it).

## Exactness (run `r20260926-204311-f524`, record `abcd33208a41…d439`, verifies with `--verify`)
L40S sm_89, torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80, Triton 3.7.1, `VLLM_BATCH_INVARIANT=1`; tap build sha256 `e4a4924f…`.
**OK: 62 of 62 kernel cases plus the source check.**
- **CUDA, 32 cases** (N = 64 to 4,096; 1, 7 and 257 rows; special rows: zeros, subnormals, huge values, ±inf, NaN, with and without
  a special residual; no weight). Outputs and residual are bit-identical to the installed `_C.fused_add_rms_norm` and to the tap-off
  instantiation. Every row's scale is written (NaN sentinels, 0 unwritten). Every scale equals the IR model's `RsqrtApprox` gate:
  all rows by the vectorized twin, sampled rows by the IR transcript.
- **Triton, 30 cases**: the same checks against vLLM's own launch. The installed source's sha equals the pinned one, the copy equals the
  pinned source plus the two tap lines, and the PTX arithmetic sequence is identical (73 ops, 57 without weight) with exactly one extra
  global store.
- **Source on vLLM's own modules** (`RMSNorm` with and without a residual, the q-norm shape, `GemmaRMSNorm`, all `forward_cuda`):
  outputs unchanged, nothing acquired outside a step, every patched site restored.

## #101 (`llama32-1b…bi-eager`, L40S, run `r20260926-204311-f524`)
- **Tap off:** Build, Match and Commit PASS. Program `ccc213475e7c…00c6b`, manifest `90f8186879d5…eaac` (7,043 identities) and run root
  `7adcef491845…1dec5` all equal the record.
- **Tap on:** Commit PASS. Manifest `cfc7e16b947b…f572`, 8,099 identities (+1,056 `norm_scales`: 33 norm modules × 32 steps).
  **9,471 norm-scale words = the plan's 9,471** (fused 9,184 = 32 modules × 287 rows; Triton 287, layer 0's input norm). Run root
  `9c89049cbfee…3b26`: new, never the record. `Q_word_v1{16,32}` strict passes with the 9,471 words acquired by the tap.

## Partition checker (the 20:48Z rule; run `r20260926-220038-b8d6`)
The checker is on `cursor/no-recompute-partition-289b`, not main, so I ran it on a **local trial merge** `23067146` of that branch
(`fd9f81e8`) and this one (`14ea93c6`), never pushed. Its tree is `c900e83d`, which `git merge-tree --write-tree fd9f81e8 14ea93c6`
reproduces. The merge is clean: this branch changes only `check_calls` / `check_query` in `query/word.py`. The query is `Q_word_v1{X=16,W=32,R=no-recompute}` with `verity.ir.partition.validate_unit_cut`.
- **19 norm specializations, all OK**: both kernels at N = 64, 128, 256, 576, 1,536, 2,048, 2,304, 2,560, 4,096, plus
  `RsqrtF32_v1{N=1}`. Each has a strict partition (every computed gate certified once, gate count exact), committed boundaries only
  (no uncommitted cross-unit read or output), every unit within the width rule (outputs 16 b, the scale one 32-bit value) and
  **0 recomputed gates**. Each norm commits **exactly 1 interior word per row, the value the tap stores**: `RsqrtApprox_v1` (fused)
  and `F32Mul_v1` = `inv_rms` (Triton).

| Definition (#101) | Calls | units | gates | committed interior words | acquired by the tap | recomputed | violations |
|---|---|---|---|---|---|---|---|
| `RMSNormFusedCuda_v2{N=2048}` | 9,184 | 37,626,848 | 141,102,976 | 9,184 | 9,184 | 0 | 0 |
| `RMSNormTriton_v1{N=2048}` | 287 | 588,063 | 3,899,182 | 287 | 287 | 0 | 0 |

- Per Call at N = 2,048: fused has 4,097 units (4,096 outputs, 1 committed), 21,508 gates (6,144 input, 11,266 computed, 4,098
  structure) and 12,288 cross-unit reads, all through committed values. Triton has 2,049 units, 17,682 gates (4,096 input, 9,485
  computed, 4,101 structure) and 8,192 cross-unit reads.
- **Whole #101 under the policy:** 46,558 Calls, 273,995,039 units, 18,805,632,462 gates, 64,169,215 committed interior words, of
  which the tap acquires 9,471. There is **one violation, not in a norm**: `GumbelTopPTokenSelect_v1{V=128256}`, `cut` /
  `gate-recomputed` on its 32 Calls. It is the same with the policy off, so it comes with the no-recompute branch's rule, not with
  this change (found, not fixed, below).
- The merged tree's tests: 177 passed (`query/test_word.py`, `test_norm_scales.py`, `test_partition_structural.py`,
  `test_partition_stubs.py`, the norm-tap source, source and property tests, `program/test_moe_router_ordered.py`,
  `packages/verity/tests/ir/test_ir_partition.py`). Lints, including dead modules: rc 0.

## Gate (b) (same pod, git clones of the shipped commits, `protocols/sampled_proofs` importable, script `gate_b2.sh`)
| side | run | lints | gate (b) |
|---|---|---|---|
| base `baa800c6` | `r20260926-205346-78c0` | rc 0 | 37 F / 3,908 P / 263 S / 6 xf (4,214) |
| head `75a10410` | `r20260926-205426-3f50` | rc 0 | 38 F / 3,952 P / 264 S / 6 xf (4,260) |
| head `14ea93c6` | `r20260926-214754-14b1` | rc 0 | 37 F / 3,954 P / 263 S / 6 xf (4,260) |

- `14ea93c6` vs base, **jdiff rc 0**: 46 new tests, all pass; 0 outcome changes, 0 new failures, 0 new skips. The 37 failures are
  base's.
- At `75a10410` the one new failure was `test_no_new_dead_modules` on `properties.norm_tap_exactness`. `14ea93c6` declares it and
  `ops/pod_norm_tap.sh` in `tests/census_roots.txt`, as for the FA2 tap. The one new skip there was the listed order-dependent
  `test_weakref_death…`.
- Commands:
  ~~~text
  research run --on vyv-rf-normtap-g1 --project verity --source <clean worktree @ sha> --cwd source --custody-r2 \
    --send gate_b2.sh [--env BOOTSTRAP=1] [--env WAIT_RUN=<run dir>] -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/gate_b2.sh" <label>'
  python3 baseline-jdiff.py gate_b-base.xml gate_b-head2.xml
  ~~~

## Behaviour changes (flag on only)
- A new committed family and a new run root. `row_stages` rebuilds the manifest with `--norm-scales`, moving a policy-less manifest
  aside as `manifest.no-norm-scales-<stamp>.json`. `commit_delta` gets `--norm-tap-so`, and the Commit stops (code 12) when the
  `.so` is missing. `manifest-verify` rebuilds under the same policy.
- The source refuses fused norms without a tap build or with a build of another tap version, an engine without
  `VLLM_BATCH_INVARIANT`, and an installed Triton kernel whose source sha differs from the pinned one. `build_ext` refuses any
  pinned file whose sha256 differs.

## What deliberately did not change
- With the flag off: no Program, manifest, commitment root, leaf id or verdict. #101 equals the record, and a CPU test pins
  byte-identity.
- No allowlist grows. `pipeline/commit.py` and `query/required.py` stay at their P10 caps (line-neutral edits).
- No leaf format or scheme change, no epoch work, nothing built on the retired recompute thresholds.
- The Definitions are not restated: the checker runs on the registered ones.

## Found, not fixed
- **The sampler under the no-recompute rule:** `GumbelTopPTokenSelect_v1{V=128256}` recomputes a gate (`gate-recomputed`, 32 Calls
  in #101). Once the no-recompute branch merges, a strict `manifest build --word-check 16/32` on #101 fails on it, tap on or off.
  Its owner (the no-recompute or sampler lane) should look.
- **Gemma (#57):** `Q_word` checks committed boundaries per Call, so the chain's interior Calls (square, mean, + eps) stay
  `output-not-committed` with or without the scale. #57 has no passing Commit.
- **TP and H100:** TP rows (rank workers) and H100 (FA3 rows) are not covered. The tap attaches in `commit_delta` only, and
  exactness is on sm_89 only.
- There was no RunPod CPU stock at 20:52Z (cpu3g/3c/3m/5c/5g/5m at 8/16/32 vCPU), so gate (b) ran on the L40S pod.

## Evidence
- Runs, all PRESERVED on R2: `r20260926-203003-9768` (bootstrap, tap build), `r20260926-204005-d287` (first exactness run),
  `r20260926-204311-f524` (exactness record plus #101 off, on and Q_word; run files `art:4d62bc3b212f…`), `r20260926-205346-78c0`
  and `r20260926-205426-3f50` (gate (b) base and first head), `r20260926-214754-14b1` (gate (b) at `14ea93c6`; run record
  `art:67518f1983e5…`), `r20260926-220038-b8d6` (partition checker; run record `art:e1f21e09f0ed…`).
- Notes: `lanes/vllm-rf-normtap/evidence/`, holding `pod-scripts/` (setup, exactness, #101, `gate_b2.sh`, `nt_partition.sh`,
  `baseline-jdiff.py`), `partition/` (`partition_norms.json`, `word_101.json`, logs) and `gate-b/` (both jdiffs).
- Pod `vyv-rf-normtap-g1` (`yqvagba5ef4ckg`, 1× L40S, $1.09/h) ran 20:28Z–22:17:54Z, about 1.83 h, **about $2.00**. No CPU pod.
