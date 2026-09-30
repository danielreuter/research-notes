---
lane: vllm-sm120-kernels
kind: report
created: 2026-09-30T02:44Z
status: open
---

CHECKPOINT 05305a3e (03:06Z) [open] WAIT vy-sm120-kernels-1 r20260930-030603-3ddf check-back 03:50Z agent bc-1cdd7aa4: job A (gate, bootstrap, norm/router tap, topp probe, Gumbel); branch cursor/vllm-sm120-kernels-69c6; meanwhile CPU: 188-SM constants, adapters
CHECKPOINT 5d9a6b99 (03:00Z) [open] JIT build-dir fix: PR #466 @ 5d9a6b99 (handoffs 0259Z to vllm-coordinator + RC); next: create vy-sm120-kernels-1, job A (gate, bootstrap, norm/router tap, topp probe, Gumbel)
CHECKPOINT d090c814 (02:44Z) [open] survey: SM count flows from TargetProfile.num_sms; hard 142 only in ops/stoch_negative_n3.sh + topp probe drain list; GPU tools = norm/router tap exactness, topp-split-probe, gumbel difftest; next: rotary/MoE/TP2 checks, pod plan
