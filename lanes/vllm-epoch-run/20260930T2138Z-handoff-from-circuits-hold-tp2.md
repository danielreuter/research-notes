---
id: 20260930T2138Z-handoff-from-circuits-hold-tp2
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: stop submitting TP2 now; hold it until the GPU-less 2-rank Build lands; backfill with single-GPU deployments

Decision at 2:40 PM PDT (Slack, @proofs' thread 1790803906.392869): a TP2 `config-run-row` holds 2 GPUs idle through its Build, and
under StrictFIFO a waiting TP2 head also stalls the 1-GPU Commits behind it. Node 1's T1 (≥60% busy by 3:30 PM PDT) is at risk.

- **Stop submitting TP2.** Leave the 15 queued TP2 jobs to node1-fill, which deactivates them (not deletes): cov-p004-2 … p016-2.
  Don't resubmit them. `cov-p002-2` (running since 2:22 PM) may finish, but node1-fill cancels it if it's still in its Build at
  2:55 PM PDT.
- **TP2 comes back** as a CPU Build (node 2 eligible) plus a 2-GPU Commit once lane vllm-tp2-gpuless-build (bc-217501a5) lands; I'll
  tell you. Meanwhile, record `cov-p002-2`'s Build and Commit wall times if it finishes (the glide path wants TP2's GPU time).
- **Backfill:** keep ≥12 GPU-h of single-GPU work ready in `deployments-gpu`: the 29 Commit-ready, the 87 single-GPU Qwen2.5
  deployments on v1, Pythia, and the rest of the runnable grid, in engine-key order.
