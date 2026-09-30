---
id: 20260930T1445Z-checkpoint-commit-hold-after
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: report
status: checkpoint
repo: danielreuter/verity
origin: vllm-config-run-tp2
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---
SmolLM2 B1 Commit GPU hold 436 s -> 83-88 s (Kueue jobs 196/203/208), all 35 roots equal to cov-k01-10 (run root a48fbe4eb4a31fcf, 460/460).
Causes: the hidden_gpu_tree + native collector JIT was rebuilt per Commit (torch puts the tree's source path in the shared build.ninja), and Triton's cache
is ephemeral in pods. Fix branch cursor/jit-tree-invariant-sources-3847 @ e0c56cb4; template lines in
note:20260930T1445Z-handoff-from-vllm-config-run-tp2-commit-gpu-hold. Replay-off-GPU scoped, not started (needs a decision).
