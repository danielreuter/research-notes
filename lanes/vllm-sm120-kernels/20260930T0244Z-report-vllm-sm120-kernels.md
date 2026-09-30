---
lane: vllm-sm120-kernels
kind: report
created: 2026-09-30T02:44Z
status: final
---

CHECKPOINT 6f1924cc (05:04Z) [final] PRs #466 #480 #481 merge-ready (handoff 0503Z); sm_120 kernels exact except fused-MoE GEMMs (fixed: MoeExpertGemm_v2 DOT) and SiluMul/RoPE edge gaps (found); pods terminated 04:21Z/05:02Z, ~$7.6
CHECKPOINT 098b9163 (04:31Z) [open] WAIT vy-sm120-kernels-1 r20260930-042256-27a2 check-back 04:42Z agent bc-1cdd7aa4: vLLM suite on #481 head 098b9163; then base attribution, merge-ready handoff, terminate pod 1, FINAL. PRs #466 #480 #481
CHECKPOINT 098b9163 (04:23Z) [open] PR #480 up; TP2 op-level 30/30 (host staging; P2P copies zero on SYS host); vy-sm120-kernels-2 terminated 04:21Z; MoE v2 admission: all fails in SiLU section. WAIT vy-sm120-kernels-1 r20260930-042256-27a2 (suite) check-back 04:50Z agent bc-1cdd7aa4
CHECKPOINT 4b96d529 (04:14Z) [open] MoE v2 DOT @ 7604eb59 (circuit-check 4/4); rope 34/48 (overflow edges), SiluMul_v1 edge gaps (generic); TP2 live engine 25/25 + vocab PASS. WAIT vy-sm120-kernels-2 r20260930-041347-704a, vy-sm120-kernels-1 r20260930-041412-7981 check-back 04:25Z agent bc-1cdd7aa4
CHECKPOINT 53f199ee (03:42Z) [open] FINDING: fused-MoE v1 (Ampere k16) fails on sm_120; bulk 1M words Ampere 428+286 diffs, Hopper-shaped 0 -> MoE v2 with DOT. WAIT vy-sm120-kernels-1 r20260930-034154-d9d0 check-back 04:00Z; WAIT vy-sm120-kernels-2 r20260930-034057-29e4 (TP2) check-back 04:15Z; agent bc-1cdd7aa4
CHECKPOINT 735c8027 (03:26Z) [open] job A r20260930-030603-3ddf ALL PASS on sm_120: norm tap, router tap, topp probe 162/162, Gumbel 40/40. WAIT vy-sm120-kernels-1 r20260930-032412-1313 check-back 04:10Z agent bc-1cdd7aa4: job B (drain@188, rope+MoE difftests, twins, MoE step)
CHECKPOINT 05305a3e (03:06Z) [open] WAIT vy-sm120-kernels-1 r20260930-030603-3ddf check-back 03:50Z agent bc-1cdd7aa4: job A (gate, bootstrap, norm/router tap, topp probe, Gumbel); branch cursor/vllm-sm120-kernels-69c6; meanwhile CPU: 188-SM constants, adapters
CHECKPOINT 5d9a6b99 (03:00Z) [open] JIT build-dir fix: PR #466 @ 5d9a6b99 (handoffs 0259Z to vllm-coordinator + RC); next: create vy-sm120-kernels-1, job A (gate, bootstrap, norm/router tap, topp probe, Gumbel)
CHECKPOINT d090c814 (02:44Z) [open] survey: SM count flows from TargetProfile.num_sms; hard 142 only in ops/stoch_negative_n3.sh + topp probe drain list; GPU tools = norm/router tap exactness, topp-split-probe, gumbel difftest; next: rotary/MoE/TP2 checks, pod plan

## Results (sm_120: RTX PRO 6000 Blackwell Server Edition, driver 595.91.07, cc 12.0, 188 SMs; vLLM d9105ea80 cu129, torch 2.13.0+cu129)

| Kernel / constant | Evidence | Verdict |
|---|---|---|
| SplitsFor_v1 / GEMM NUM_SMS | code: both read TargetProfile.num_sms; the one literal 142 (ops/stoch_negative_n3.sh) now reads the Builds' num_SMs | fixed, PR #480 |
| top-p split probe (every S, ties, drain at 188-SM boundaries) | r20260930-030603-3ddf, r20260930-032412-1313 | 162/162 + drain |
| Gumbel top-p token select | r20260930-030603-3ddf | 40/40 |
| fused RMSNorm CUDA + Triton + norm-scale tap | r20260930-030603-3ddf | exact |
| MoE topk_softmax (router tap, op + live) | r20260930-030603-3ddf | exact |
| fused-MoE expert GEMMs | bulk r20260930-032412-1313 (2 x 1,048,576 words): Ampere step 428+286 diffs, Hopper-shaped 0; admission v2 r20260930-041412-7981 | v1 wrong on sm_120 -> MoeExpertGemm_v2{DOT}, PR #481 |
| moe_sum | r20260930-034154-d9d0 diag | exact |
| SiluMul_v1 (silu_and_mul) | r20260930-034154-d9d0 diag + pod probes | edge gaps (NaN 0x7FFF; g < -88.7 expf overflow -> -0; signed zero at subnormal gates), same source on every arch: found, not fixed |
| RoPE_v1 (rotary_embedding) | r20260930-034154-d9d0 | 34/48: every failing case has a bf16 +-max operand whose product overflows f32 (unreachable with |cos|,|sin| <= 1): found, not fixed |
| TP2 AllReduce2 / AllGather2, NCCL 2.29.7, P2P off, SYS topology | op-level r20260930-041759-859d 30/30; live vLLM TP2 engine r20260930-040148-c83f 25/25 both ranks; vocab range PASS | exact |

Artifacts: circuit-check of the MoE v2 Definitions art:9f51a5f48614da39c73b3c8946010929c1e33a6e82f2abdeeef189ab17ce32c9.
Platform finding: on the 2x RTX PRO 6000 SYS host a torch cuda:0 -> cuda:1 copy returns zeros (P2P broken, as for NCCL); stage through the host.
Found, not fixed: quarantine allreduce_difftest hangs under the verity-vllm launcher (spawn re-imports __main__); cc 9.0 MoE still binds the Ampere step (no H100 MoE record, unmeasured).

Handoffs received and acted on: 20260930T0240Z-note-from-vllm-coordinator-budget-line-live.md (pods created after it), 20260930T0246Z-handoff-from-vllm-coordinator-jit-build-dir.md (PR #466, handoffs 0259Z), 20260930T0253Z-note-from-vllm-coordinator-sweep-target.md (scope unchanged; "config run" wording), 20260930T0416Z-note-from-vllm-coordinator-466-467-overlap.md (answered 0431Z: no overlap).

## FINAL
~~~text
tip: cursor/vllm-sm120-kernels-69c6 @ 6f1924cc (base main@05305a3e + #465 f740c1d5)   merge-with: #466 cursor/twins-build-outside-checkout-69c6@5d9a6b99, #465, #480 cursor/vllm-sm120-constants-difftests-69c6@d6ab05fe
known-failures: 52 environment failures of the vLLM suite on the pod, identical on base 05305a3e (r20260930-044854-ceaa)   pod: vy-sm120-kernels-1 terminated 05:02Z, vy-sm120-kernels-2 terminated 04:21Z; ~$7.6
artifacts: art:9f51a5f48614da39c73b3c8946010929c1e33a6e82f2abdeeef189ab17ce32c9
~~~
PRs: #466 (twins build outside the checkout), #480 (188-SM constants + kernel difftests), #481 (MoeExpertGemm_v2 on the target's k16 step). Merge-ready handoff: lanes/vllm-coordinator/20260930T0503Z-handoff-from-vllm-sm120-kernels-merge-ready.md. Open decision for the coordinator: cc 9.0 MoE binding; SiluMul_v2.
