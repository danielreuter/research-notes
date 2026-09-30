---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

kind: handoff · from: vllm-coverage-defs · to: vllm-coordinator · cc: vllm-epoch-run · created: 2026-09-30T16:53Z

**The Gemma-2 gap list is built. All 15 dense Definitions pass the sm_120 capture: 450/450 cases, 0 mismatches.**

## PR heads (all pushed; none force-pushed; each confined to `integrations/vllm/`)

| branch | head | base | what |
|---|---|---|---|
| `cursor/fa2-softcap-sm120-987d` (#551) | d86e361d | main | AttentionSoftcap_v2 (granted) |
| `cursor/softcap-replay-row-987d` | 91947326 | main + #551 (merge) | AttentionSoftcap_v2 replay row evaluator; exact on GPU (job 217, 0 mismatches vs capture 7fa28706…) |
| `cursor/call-boundary-weight-only-987d` | 0ba8865b | main 2c4101bf0 | call-boundary plan evaluates a weight-only Call made once at step 0 into every step's body (Gemma-2 norm `AddScalarBf16{C=1.0}`); 8,805/8,805 boundaries on CPU |
| `cursor/dense-replay-rows-987d` | 3d18086e | main 2c4101bf0 | `ir_rows`: replay row kernels for 15 dense Definitions (RMSNorm chain, GeluTanhMul, soft-capped logits); 283,410/283,410 Gemma-2 rows are VUs on CPU |

Merge order to unlock the Gemma-2-2B rtxpro6000 deployment: #551, softcap-replay-row, call-boundary-weight-only, dense-replay-rows. There are no digest moves.

## The sm_120 capture (Kueue job 268, vy-nebius-1, RTX PRO 6000 Blackwell, torch 2.13.0+cu129)

- **Command:** `properties-admission produce --n 30 --seed 7`, then `check`, once for each of the 15 `dense/*_difftest` adapters. The adapters are restored from `528f9d21f^` and used only in the host tree `vcd-dense`; they are not in any PR.
- **Result:** every Definition is `status pass` with 30/30 passed.
- **Definitions:** SquareBf16, SquareF32, MeanTriton, AddScalarF32, AddScalarBf16, AddWidenedBf16, RsqrtF32, ScaleRowBf16, ScaleRowF32, MulVecF32, NarrowF32ToBf16, GeluTanhMul, Bf16DivScalar, Bf16Tanh, Bf16MulScalar.
- **Outputs:** `/workspace/jobs/vcd-dense/*.check.json` on the host; `cat *.check.json | sha256sum` = eac7c94e31f18977…

## Gap list status (from `20260930T1518Z-handoff-…-gemma2-gap-list`)

- **Softcap attention:** new Definition (#551) plus a row evaluator. Done.
- **The call-boundary refusal "Call c reads Call a of step 0":** a plan fix. Done.
- **The 15 dense families with "no registered evaluator":** binding only (`ir_rows`). Done, and exact on sm_120.
- **Match-side softcap fold:** left alone, as instructed.

Note: git and gh authentication on this VM started failing at 16:53Z. All heads were already on origin (the tracking refs match), so no bundle was needed.
