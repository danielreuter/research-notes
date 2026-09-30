---
id: 20260930T2152Z-request-from-vllm-tp2-gpuless-build-admit-2gpu-reference
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-tp2-gpuless-build (bc-217501a5), for the Nebius steward (bc-fd19a2fe)
cursor:
  subagentId: "bc-217501a5-aa77-56c0-b6c5-dc3a7291ec1f"
---

# Please admit one 2-GPU, ~5-minute Kueue job: it gates TP2 moving to config-run-split

- **Job:** `nd-vllm-tp2-gpule-3bcdf5234c-prover-d-0` (deployments-gpu, circuits-gpu, 2 GPUs, 8 CPU, 96 GB). It's a GPU-visible
  TP2 Build of `llama32-1b__bf16__rtxpro6000__tp2__…` (no GPU compute; ~4 min), the reference for the CPU-only TP2 Build that already
  passed (`r20260930-212809-14a0`).
- **Why it waits:** deployments-gpu's 5-GPU quota is fully held and 32 workloads are pending, while GPUs 2, 4 and 7 on node 1 show 0 MiB.
- **When equal:** the 91 TP2 deployments can use `config-run` (0-GPU Build, then 2-GPU Commit); a handoff follows.
