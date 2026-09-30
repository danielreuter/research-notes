---
lane: vllm-sm120-kernels
kind: report
created: 2026-09-30T02:44Z
status: open
---

CHECKPOINT 098b9163 (04:23Z) [open] PR #480 up; TP2 op-level 30/30 (host staging; P2P copies zero on SYS host); vy-sm120-kernels-2 terminated 04:21Z; MoE v2 admission: all fails in SiLU section. WAIT vy-sm120-kernels-1 r20260930-042256-27a2 (suite) check-back 04:50Z agent bc-1cdd7aa4
CHECKPOINT 4b96d529 (04:14Z) [open] MoE v2 DOT @ 7604eb59 (circuit-check 4/4); rope 34/48 (overflow edges), SiluMul_v1 edge gaps (generic); TP2 live engine 25/25 + vocab PASS. WAIT vy-sm120-kernels-2 r20260930-041347-704a, vy-sm120-kernels-1 r20260930-041412-7981 check-back 04:25Z agent bc-1cdd7aa4
CHECKPOINT 53f199ee (03:42Z) [open] FINDING: fused-MoE v1 (Ampere k16) fails on sm_120; bulk 1M words Ampere 428+286 diffs, Hopper-shaped 0 -> MoE v2 with DOT. WAIT vy-sm120-kernels-1 r20260930-034154-d9d0 check-back 04:00Z; WAIT vy-sm120-kernels-2 r20260930-034057-29e4 (TP2) check-back 04:15Z; agent bc-1cdd7aa4
CHECKPOINT 735c8027 (03:26Z) [open] job A r20260930-030603-3ddf ALL PASS on sm_120: norm tap, router tap, topp probe 162/162, Gumbel 40/40. WAIT vy-sm120-kernels-1 r20260930-032412-1313 check-back 04:10Z agent bc-1cdd7aa4: job B (drain@188, rope+MoE difftests, twins, MoE step)
CHECKPOINT 05305a3e (03:06Z) [open] WAIT vy-sm120-kernels-1 r20260930-030603-3ddf check-back 03:50Z agent bc-1cdd7aa4: job A (gate, bootstrap, norm/router tap, topp probe, Gumbel); branch cursor/vllm-sm120-kernels-69c6; meanwhile CPU: 188-SM constants, adapters
CHECKPOINT 5d9a6b99 (03:00Z) [open] JIT build-dir fix: PR #466 @ 5d9a6b99 (handoffs 0259Z to vllm-coordinator + RC); next: create vy-sm120-kernels-1, job A (gate, bootstrap, norm/router tap, topp probe, Gumbel)
CHECKPOINT d090c814 (02:44Z) [open] survey: SM count flows from TargetProfile.num_sms; hard 142 only in ops/stoch_negative_n3.sh + topp probe drain list; GPU tools = norm/router tap exactness, topp-split-probe, gumbel difftest; next: rotary/MoE/TP2 checks, pod plan
