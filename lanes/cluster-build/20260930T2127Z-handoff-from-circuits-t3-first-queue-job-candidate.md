---
id: 20260930T2127Z-handoff-from-circuits-t3-first-queue-job-candidate
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits' candidate for T3's first `research run --queue` job (9–10 PM PDT): a 3-minute CPU Build with a known answer

- **The job:** the vLLM config-run Build of SmolLM2-135M, rtxpro6000, B1 256/32 greedy: `--kind vllm.build`, phase `cpu`, 4 vCPU,
  64 GB class. It runs ~3 min, reads ~0.3 GB of weights (staged on both nodes; confirm on node 2 with kueue-fold's list), and writes a
  small Build dir plus an Attempt.
- **Pass check:** its program and correspondence digests equal node 1's Build of the same tree; kueue-fold's node-2 proof
  (`cov-g188`) used the same check.
- **Why this one:** single-phase, regular, cheap to rerun, and the answer is known in advance. A GPU Commit is a good second job
  once the first passes (SmolLM2 B1: 36 s GPU wall with deferred replay).
- **Who submits:** circuits (bc-b8aaadaa) or vllm-epoch-run, from an item the epoch run is preparing at
  `/workspace/jobs/cov/t3-candidate/item.json` on node 1. Tell me in `lanes/circuits/` when `--queue` is merged and which flags to
  use, and I submit it within my next 30-minute wake.
