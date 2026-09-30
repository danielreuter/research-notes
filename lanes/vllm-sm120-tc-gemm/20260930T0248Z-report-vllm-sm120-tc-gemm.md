---
lane: vllm-sm120-tc-gemm
kind: report
created: 2026-09-30T02:48Z
status: open
---

CHECKPOINT f740c1d5 (02:55Z) [open] FINDING: pinned vLLM keeps sm_120 bf16 linear on cuBLASLt (Triton override cc 8.x only); step 2 = cuBLASLt correspondence; handoff 20260930T0255Z to vllm-coordinator; #465 @f740c1d5 wording fixed. next: driver + first pod.
CHECKPOINT d993873f (02:48Z) [open] step1 head cursor/vllm-sm120-target-422d@d993873f (PR #465) handed to vllm-coordinator (20260930T0248Z handoff); key blackwell_consumer, DOT=Hopper (sm_120 mma.sync = HOPPER_BF16_M16N8K16). next: plan step2/5a pod scripts; no pods until vy-sm120- line confirmed.
