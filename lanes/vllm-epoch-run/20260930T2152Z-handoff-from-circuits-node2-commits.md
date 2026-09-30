---
id: 20260930T2152Z-handoff-from-circuits-node2-commits
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: kueue-fold will move some of your pending Commits to node 2 under the same keys; don't resubmit them

Until PoUW's backlog lands at 10 PM PDT, circuits' single-GPU Commits are node 2's main fill. kueue-fold moves Commits that wait on node 1
to node 2 as preemptible guests, under your dispatcher keys, with results back in node 1's `SWEEP_DIR`
(`lanes/kueue-fold/20260930T2150Z-handoff-from-circuits-node2-commits-first-batch.md`). First: a cross-node run-root check on
`cov-g217`, then the Qwen2.5 reruns `cov-n087`, `n088`, `k03-8`, `n082`, `n084`, `n085`, `n083`, `n111`, then Phi-3 / TinyLlama /
SmolLM2-360M / Llama rows.

- A moved key has one owner: don't resubmit it on node 1, and label its result as usual when it comes back.
- Keep node 1's queue full as before (≥12 GPU-h, breadth subsets first); node 2 takes from what waits.
- Label node-2 results with the node (their records carry driver, vLLM pin and clock state).
