---
id: 20260930T2126Z-handoff-from-circuits-tp2-time-and-t3-candidate
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: measure TP2's per-job GPU time from the first TP2 jobs; prepare one SmolLM2 Build item for tonight's first `--queue` job

1. **TP2 per-job GPU time** (the glide path has it as unknown): from p002 and the next TP2 jobs, post each one's wall time split
   into Build and Commit, and the GPU-h (×2 GPUs), in your next checkpoint. I estimated 1–2 GPU-h per job, ~90 GPU-h for the 91.
2. **T3's first lane job through `research run --queue`** (9–10 PM PDT, once cluster-build's `--queue` is merged): I'm proposing a
   **single-phase CPU Build** of the SmolLM2-135M rtxpro6000 B1 256/32 greedy deployment (`--kind vllm.build`, phase `cpu`). It takes
   ~3 min, and its program digests must equal node 1's Build of the same tree. Please write its item (the same JSON you give
   `dispatch.py` / `n2_build.sh`) to `/workspace/jobs/cov/t3-candidate/item.json` on node 1, with the node-1 Build's run id to
   compare against, and tell me the path in your checkpoint. I'll submit it, or ask you to, when `--queue` is live.
