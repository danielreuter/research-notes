---
cursor:
  subagentId: "bc-1cdd7aa4-8d99-53e6-96d6-c05199ad69c6"
---

lane: vllm-coordinator · kind: handoff (merge-ready) · from: vllm-sm120-kernels (bc-1cdd7aa4) · created: 2026-09-30T05:03Z

# Merge-ready: #480 (188-SM constants + kernel difftests) and #481 (fused-MoE expert GEMMs on the target's k16 step)

**Order:** #466 (approved), then #465 (lane A), then #480, then #481. #481 contains #465 (merged at `43f91d1b`) and #480's commits under their original shas.

| PR | Branch @ head | Base | What |
|---|---|---|---|
| [#480](https://github.com/danielreuter/verity/pull/480) | `cursor/vllm-sm120-constants-difftests-69c6` @ `d6ab05fe` | `origin/main` `0ce2a4e0` | `stoch_negative_n3.sh` reads the Builds' num_SMs (the one literal 142); top-p drain crosses every split boundary of the device's SM count; 188-SM tests; difftest adapters `rope_difftest`, `moe_difftest`, `collectives_difftest` |
| [#481](https://github.com/danielreuter/verity/pull/481) | `cursor/vllm-sm120-kernels-69c6` @ `6f1924cc` | main + #465 + #480 | `MoeExpertGemm_v2` / `MoeExpertGemmW_v2{E,K,N,DOT}`, bound only on a family whose `TARGETS` record says `moe_expert_dot` (blackwell_consumer); Build, fold, replay rows, VU export, GP-01 and the acquisition source read it |

## Evidence (RTX PRO 6000 Server, driver 595.91.07, cc 12.0, 188 SMs; vLLM d9105ea80 cu129; every run --custody-r2, all preserved)
- **Exact on sm_120:**
  - fused/Triton RMSNorm with the norm-scale tap, MoE `topk_softmax`, and Gumbel top-p 40/40 (`r20260930-030603-3ddf`);
  - top-p split 162/162 plus the drain at the 188-SM boundaries (`r20260930-032412-1313`);
  - `moe_sum` (`r20260930-034154-d9d0`);
  - TP2 AllReduce2/AllGather2, NCCL 2.29.7, P2P off: op-level 30/30 (`r20260930-041759-859d`); live vLLM TP2 engine 25/25 on both ranks, plus the vocab range (`r20260930-040148-c83f`).
- **Fused-MoE expert GEMMs:** v1 is wrong on sm_120. Bulk capture (2 x 1,048,576 words): the Ampere step differs in 428 + 286 words, the Hopper-shaped step in 0 (`r20260930-032412-1313`). The admission check with v2 (`r20260930-041412-7981`): every failing case's first difference is in the SiLU section.
- **Partition gate:** `circuit-check --as-call` 4/4 ok on the v2 Definitions at DOT=Hopper and DOT=Ampere. `Q_word_v1{X=16,W=32,R=no-recompute}`: 16 units per Call, 0 committed interior words, 16-bit outputs, **0 recomputed/redundant gates**, 0 dead gates, 0 correspondence mismatches. Report `art:9f51a5f48614da39c73b3c8946010929c1e33a6e82f2abdeeef189ab17ce32c9`.
- **Tests:**
  - CPU on the VM: lints, `test_no_by_name_rules`, the dead-module check, kernel self-check, and the MoE/GP-01/VU-export/fold/replay/target tests all pass on both heads.
  - vLLM suite with torch on the pod at `098b9163` (`r20260930-042256-27a2`): of 53 failing ids, 52 also fail on the base `05305a3e` in the same environment (`r20260930-044854-ceaa`: missing fetched fixtures, `pous` not on the path, real-HF construction, B0's digest built on a GPU-visible 188-SM host).
  - The one head-only failure (`test_no_by_name_rules`) is fixed in `6f1924cc`.
  - Two `test_tp_moe_members` stored-build cases (L40S v1) ran over 20 minutes; I stopped them, so they are unverified. The train's `check` runs everything.

## Behaviour changes
- **sm_120 MoE configs** bind `_v2{DOT=HopperBF16WgmmaDot16_v1}`.
- **An unregistered target** (e.g. cc 10.0) now refuses the MoE block by name. Before, it silently bound v1.
- **The padded MoE construction** refuses on sm_120.
- **The drain list at 142 SMs** gains batches 35 and 36. This is a probe only; no record.

## Deliberately unchanged
- No digest of an existing record: cc 8.x and 9.0 keep `MoeExpertGemm_v1` ids, and the vocabulary's new roles sit only in annotations.
- cc 9.0 MoE still binds the Ampere step (no H100 MoE record, no fused_moe correspondence on sm_90): **decision for you**.

## Found, not fixed
- **`SiluMul_v1` edge gaps**, from the same source on every architecture:
  - NaN is written as 0x7FFF, not 0x7FC0;
  - for gates below -88.7, `expf` overflows and the GPU gives -0 where the stand-in keeps a subnormal;
  - signed zeros with subnormal gates.

  A `SiluMul_v2` would be `bf16(bf16(g / (1 + NvExpf(-g))) * u)` with the NaN word 0x7FFF; that still leaves 23 signed-zero words unexplained.
- **Rotary `RoPE_v1`:** 34/48 cases exact. Every failing case needs a bf16 +-max operand whose product overflows f32, which a |cos|,|sin| <= 1 cache can't produce.
- **Platform:** on the 2x PRO 6000 SYS host, a torch cuda:0 -> cuda:1 copy returns zeros (the P2P defect behind `NCCL_P2P_DISABLE`). vLLM's TP path is unaffected.
- **The quarantine `allreduce_difftest`** hangs under the `verity-vllm` launcher (spawn re-imports `__main__`).

## Pods and spend
vy-sm120-kernels-1 (03:00Z-05:02Z, $2.09/h) and vy-sm120-kernels-2 (2 GPUs, 03:33Z-04:21Z, $4.18/h): both terminated. About $7.6 of this lane's $15.
