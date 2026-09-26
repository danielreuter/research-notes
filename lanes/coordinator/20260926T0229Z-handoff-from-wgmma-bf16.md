---
lane: coordinator
kind: handoff
from: wgmma-bf16
created: 2026-09-26T02:29Z
---

# wgmma-bf16: merge-ready, PR #49. `sm90.wgmma.m64n8k16.bf16` is PINNED on a fresh H100 capture; the census has `gemm-coordinate/k1536/sm90-wgmma-bf16`

**To:** research coordinator (bc-8ece7cde). **PR:** [#49](https://github.com/danielreuter/verity/pull/49), branch `cursor/wgmma-bf16-db07`
(an agent branch, not `lane/wgmma-bf16`), tip `c2d6c823`, six commits off `origin/main` `35560c88`.

## Result
- **The model already existed.** It is `HOPPER_BF16_WGMMA_K16`: one group of 16, a 26-bit adder, floor −133, veritor lane HP's.
  It had no registry id, and our harness had never measured it. Its parameters equal those of `HOPPER_BF16_M16N8K16`.
  No new derivation was needed. The measurement on the instruction vLLM issues found 0 mismatches.
- **New semantics value:** `sm90.wgmma.m64n8k16.bf16`, with PTX `wgmma.mma_async.sync.aligned.m64n8k16.f32.bf16.bf16`.
  - Its model is `HOPPER_BF16_WGMMA_K16`, now in `models.MODELS`.
  - Its status is `pinned`, citing dossier `art:50508ab77719ba3d93bd2985416eba0029116f313304a4632e67ad0dd28579d9`.
  - Trust computes PINNED. P1–P5 pass, and Ta passes on the veritor capture replayed on the device.
  - Still missing for TRUSTED: Tc, Td and Te. S1 needs a second H100 or driver.
- **Census:** `gemm-coordinate/k1536/sm90-wgmma-bf16` ("GemmCoordinate<1536> · sm90 wgmma · BF16") has no `legacy_target`.
  The census test now checks that every subcircuit binds a registry instruction, and no longer requires one subcircuit per target.
  The `sm90-mma-bf16` fidelity note is unchanged. It is still true of that subcircuit and of the frozen `BF16_HOPPER` target.

## Evidence (vy-wgmma-bf16-h100: H100 80GB HBM3, driver 580.126.09, nvcc 12.4.131, GPU-d5e245b4-…)
| run | artifact | what | mismatches |
|---|---|---|---|
| r20260926-020157-242a | `art:8f903385776fdb04bd3008120f44422b76fa4e2cbb5ad6533275a67548d7a6a0` | A from shared memory (SS): 26,361,344 swept (14 families, specials asserted against the total semantics), 2,876,928 chained elements (4 back-to-back wgmma), veritor's 44,046 records | 0 |
| r20260926-020210-aee8 | `art:f9508ae817053e57d93332518608430d7988a7bf2fdf0fc0d58bcf6695ec74d5` | A from registers (RS): the same | 0 |
| r20260926-021005-456c | `art:4ca1294d1cf34183e57d638873ea6cbee75ee42054e88c6b105ac61e0f49b513` | canary (26,624) | 0 |
| r20260926-015437-4839 | `art:34fe5a0cf98e7b3e95b3e1213f1af3d66dee83fb34540e5b20e9131261ad1f71` | compile check: 1× `HGMMA.64x8x16.F32.BF16` per tile kernel, 4× in the chained kernels | — |

- The Ampere control misses 3.15M of the swept elements.
- The first pair, r20260926-015601-b530 and -015605-bc89, used the same seeds. Its words are identical to the re-runs'.
  It is marked failed only because of a replay bookkeeping false alarm, fixed in `e3ddc7e0`. Both first-pair runs are preserved.
- All labels are `--by wgmma-bf16` and are on the remote. Every attempt is preserved.

## Tests, negatives, behaviour changes
- `pytest packages/verity/tests/ml packages/verity/tests/proofs backends/numerical/tests/bench`: 765 passed.
- The full-suite failures are the same set as on `origin/main` here: `test_repository` ×2, the evaluation kernel list, and 6 `tools/research` environment tests.
- `verity.ml.tc.total.HOPPER_BF16_WGMMA_K16` is the same object as before, now defined in `models.py` and re-exported. Its `validated` text is longer.
- In `trust.py`, a tc_probe `capture_replay` counts as a replay. Its model mismatches and unexpected tile words make it unclean.
- In `tc_probe.Model`, `total=True` asserts the specials family. Worker descriptors now carry that flag and resolve via `models.MODELS`. The FP8 and mma paths are unchanged.

## Pods and spend
One pod, vy-wgmma-bf16-h100 (0fybv7cytq3at4), was created about 01:50Z and drained and terminated at 02:12Z. Spend was about $1 of the $20 budget.

## Handed on
flock-gpu-link (`lanes/flock-gpu-link/20260926T0229Z-handoff-from-wgmma-bf16.md`) gets the lowering.
