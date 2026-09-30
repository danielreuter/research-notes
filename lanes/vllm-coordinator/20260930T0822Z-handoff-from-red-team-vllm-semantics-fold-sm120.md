---
id: 20260930T0822Z-handoff-from-red-team-vllm-semantics-fold-sm120
campaign: overnight-sep30
lane: red-team-vllm-semantics
kind: handoff
status: open
repo: danielreuter/verity
origin: red-team-vllm-semantics
cursor:
  subagentId: "bc-05c0bb3e-507d-57b1-ae79-cac14d00af0d"
---

# `fold-sm120-linears` rated broken: confirms your known gap, no new action

The red-team label is on `r20260930-080757-a114`. It agrees with your status: this is the known, low-priority gap, so nothing is new.

- **Reproducer (code):** `observe/fold/patterns/gemm.py` `GemmLaunch.match` only accepts a Triton `matmul_kernel_persistent` launch.
- An sm_120 linear is `aten.mm` over cuBLASLt. In `r20260930-080344-10e2` it ran `cutlass_80_tensorop_bf16_s16816gemm_*` or `cutlass_80_wmma_tensorop_bf16_s161616gemm_*`.
- So the wrapper branch returns Unsupported with "aten.mm without exactly one batch-invariant matmul_kernel_persistent launch".
- **When fixing it:** the cuBLASLt pattern also has to refuse GEMMs with N % 8 != 0. For those shapes cuBLASLt runs `gemmSN_TN_kernel` (FP32 SIMT) or `cutlass_75 s1688` (k8 mma) instead of the chain, and they disagree with the Hopper chain. Same run.
