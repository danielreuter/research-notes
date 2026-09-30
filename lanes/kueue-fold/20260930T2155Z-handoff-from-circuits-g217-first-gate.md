---
id: 20260930T2155Z-handoff-from-circuits-g217-first-gate
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); for kueue-fold and n2-commits (bc-698052e1)
---

# circuits → n2-commits: cov-g217 is approved and runs FIRST; other node-2 records count only if its run root is byte-identical to node 1's

This supersedes "start with the Qwen reruns" in `20260930T2155Z-handoff-from-circuits-node2-research-questions.md`. The research owner
said yes at 2:54 PM PDT (Slack 1790805213.401649).

- **Question:** does node 2 reproduce node 1's computation?
- **Pass condition:** the **run root and the committed record digest are byte-identical** to node 1's `cov-g217` run
  (`/workspace/jobs/cov/cov-g217/llama32-1b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager/commit/`). A matching verdict
  alone isn't enough.
- **Before it, record node 2 against node 1** (don't change node 2's clocks: that's a node change, and PoUW relies on the lock):
  - driver: node 1 is **580.173.02**;
  - SM clocks: node 1 is unlocked (max 2,430 MHz), node 2 is locked at 2,100 MHz;
  - the tree's vLLM pin `d9105ea80`, the same venv and torch as node 1's tree;
  - `VLLM_USE_DEEP_GEMM=0`.
- **If the roots differ:** hold every node-2 Commit record (they don't count), keep node 2 on Builds, and send the first differing
  member to `lanes/circuits/`.
- **If they match:** run the 8 Qwen2.5 #557 reruns, then the Commit-ready Phi-3 / TinyLlama / SmolLM2-360M / Llama rows, each naming
  its research question, as in the first-batch handoff.
