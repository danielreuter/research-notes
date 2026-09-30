---
lane: vllm-sm120-tc-gemm
kind: report
created: 2026-09-30T02:48Z
status: open
---

CHECKPOINT fb3a7fde (05:44Z) [open] #483 acceptance PASS: 720/720 M>=2 bias cases exact (29.7M coords), circuit-check 0 failures; FP8 e4m3 25.0M-element fresh-seed capture 0 mismatches incl specials (r20260930-052000-e32d), PR #487 (5a/5b core models); ack vllm-sm120-kernels 0503Z (#481 moe_expert_dot kept; #483 doesn't touch the TARGETS record). Next: custody check, terminate pod.
CHECKPOINT 60549d3b (04:52Z) [open] WAIT vy-sm120-tc-gemm-1 r20260930-044225-355c (bias acceptance) + r20260930-041757-0bde (FP8 pin sweeps) check-back 05:20Z agent bc-049fc756-e63b-5b43-af14-0e5a94a2422d; gemvx closed (handoff 20260930T0452Z), PR #483 up.
CHECKPOINT 60549d3b (04:45Z) [open] coord decisions 0359Z acted on: #476 merge-ready @e213ccc3 (suite = base); bias Def GemmBiasF32Epilogue_v1 @60549d3b (cursor/vllm-sm120-bias-epilogue-422d) tests pass, circuit-check+724-case acceptance r20260930-044225-355c; 5b scale order sa*(sb*acc) (r20260930-041842-76a2); gemvx tree recovered (strided T threads + halving, 0/11M triplets), T(K,N) table r20260930-044507-fe26.
CHECKPOINT 9755dc08 (03:56Z) [open] step2 DONE (PR #476 @9755dc08): plain linears exact Gemm_v2 Hopper; bias M>=2 fp32-epilogue; bias M=1 cuBLAS gemvx not chain (handoff 0354Z). 5b first look: CUTLASS sm120 FP8 per-tensor+blockwise exact with new step. WAIT r20260930-035619-48cb + r20260930-035629-f454 (quick suites head/base) check-back 04:15Z agent bc-049fc756-e63b-5b43-af14-0e5a94a2422d
CHECKPOINT 9886a2e3 (03:22Z) [open] WAIT vy-sm120-tc-gemm-1 r20260930-031354-3b6d check-back 03:45Z agent bc-049fc756-e63b-5b43-af14-0e5a94a2422d: step2 cuBLASLt check tp1+tp2 (so far: only M=1 bias cases inexact, cuBLAS gemvx); WAIT r20260930-031907-a678: vLLM suite on step2 tree.
CHECKPOINT 9886a2e3 (03:15Z) [open] 5a: sm_120 e4m3 mma.sync (QMMA.16832) = GroupSum groups(32) width 26 (floor unobservable -126..-145), 0/6.4M mismatches (probe r20260930-030915-23f3, fit r20260930-031244-ecbc); Ada/Hopper/2xHMMA refuted. e5m2 r20260930-031447-a5ad running; step2 capture r20260930-031354-3b6d running.
CHECKPOINT 193a0d4b (03:09Z) [open] pod vy-sm120-tc-gemm-1 (2xqwly4jt3weya) up 03:07Z, checks PASS (drv 595.91.07, cc 12.0, 188 SMs); running bootstrap r20260930-030854-5819 + 5a e4m3 probe r20260930-030915-23f3; driver @193a0d4b.
CHECKPOINT 7fd9a186 (03:05Z) [open] POD ESTIMATE vy-sm120-tc-gemm-1: 1x RTX PRO 6000 secure $2.09/h, max 4h, ~3.5 GPU-h (~$7.3). branches: step2 cursor/vllm-sm120-gemm-corr-422d@d4f0dcd7, 5a cursor/vllm-sm120-fp8-probe-422d@7fd9a186.
CHECKPOINT f740c1d5 (02:55Z) [open] FINDING: pinned vLLM keeps sm_120 bf16 linear on cuBLASLt (Triton override cc 8.x only); step 2 = cuBLASLt correspondence; handoff 20260930T0255Z to vllm-coordinator; #465 @f740c1d5 wording fixed. next: driver + first pod.
CHECKPOINT d993873f (02:48Z) [open] step1 head cursor/vllm-sm120-target-422d@d993873f (PR #465) handed to vllm-coordinator (20260930T0248Z handoff); key blackwell_consumer, DOT=Hopper (sm_120 mma.sync = HOPPER_BF16_M16N8K16). next: plan step2/5a pod scripts; no pods until vy-sm120- line confirmed.
