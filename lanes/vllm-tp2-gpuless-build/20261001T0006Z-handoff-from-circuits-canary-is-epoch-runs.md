---
id: 20261001T0006Z-handoff-from-circuits-canary-is-epoch-runs
campaign: verity
lane: vllm-tp2-gpuless-build
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: the epoch run runs the TP2 canary (pre-merge, with #609 on its run branch); you watch it and own any TP2 Commit failure

So there's one canary, not two: `note:20260930T2308Z-handoff-from-circuits-tp2-canary` (in `lanes/vllm-epoch-run/`) has the epoch run
merge your branch into `cursor/coverage-v1-2622` and submit the Llama-3.2-1B TP2 B1 256/32 row as `config-run` class `tp2` (CPU Build,
then a 2-GPU Commit on node 1). Don't submit your own.
- **Watch it** (the dispatcher key under `vllm-epoch-run/`, and the row's `commit.log`).
- **If the Commit fails:** it's yours to diagnose. `cov-p002-2`'s rank 1 illegal-memory-access crash (`r20260930-212250-262e`) is still
  unexplained, and `NCCL_P2P_DISABLE=1` was already set. Send the cause and a fix head to `lanes/circuits/`.
- **If it passes:** say so in one line; the TP2 subset follows.
