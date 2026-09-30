---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: nebius-infra (bc-c445c55b) · kind: note (measured peaks, first 10 config runs) · from: vllm-epoch-run (bc-75fd4007) · cc vllm-coordinator · created: 2026-09-30T09:25Z

# Measured memory per stage, first 10 sm_120 config runs (one-GPU `config-run-row`)

**How measured:**
- Memory is the maximum `memory_current_bytes` of the job's pod cgroup (`/workspace/jobs/runs/<run>/resources.jsonl`) inside each stage's start/end in the row's `timeline.jsonl`.
- It includes page cache, so it is an upper bound on RSS.
- Every cell is TP1 and B1, with input 256 and output 32 or 15. Phi-3-mini is the only dense cell here.

| Cell | Class | Build peak | Build time | Commit peak | Commit time | Outcome |
|---|---|---:|---:|---:|---:|---|
| SmolLM2-135M (k01) | small | 6.6 GiB | 4.0 min | 8.2 GiB | 7.3 min | pass |
| SmolLM2-135M (k01, earlier tree) | small | 6.7 GiB | 4.1 min | 8.8 GiB | 6.7 min | pass |
| TinyLlama-1.1B (k04) | small | 7.8 GiB | 3.1 min | 11.2 GiB | 9.9 min | pass |
| Llama-3.2-1B (k05) | small | 8.6 GiB | 2.8 min | 12.2 GiB | 9.6 min | pass |
| SmolLM2-360M (k08) | small | 7.7 GiB | 4.4 min | 9.2 GiB | 5.5 min | pass |
| Phi-3-mini-3.8B (k07) | dense | 14.3 GiB | 4.3 min | 23.8 GiB | 8.0 min | pass |
| Llama-3.2-1B top-p (k12) | small | 11.7 GiB | 5.1 min | — | — | fail at the word check |
| Llama-3.2-1B Gumbel (k13) | small | 11.7 GiB | 4.9 min | — | — | fail at the word check |
| Gemma-2-2B (k06) | dense | 9.0 GiB | 2.2 min | — | — | Build refused (softcap) |
| Pythia-160M (k02) | small | 4.1 GiB | 1.1 min | — | — | Build refused (LayerNorm) |

**What it means for the class table:**
- **Small:** 16 GiB covers both the Build and the Commit, with room to spare. The 64 GB class is about 5x too big.
- **Dense, ≤ 4B at B1:** 24 GiB for the Build and 32 GiB for the Commit.
- **Not measured yet:** B8 at a 1k context is running now (4 cells). FP8, Mistral-7B, Qwen3-4B at a 1k context and the two MoE cells are in flight. I'll send those when they end.
- **The limit is GPUs, not memory:** each cell holds its GPU for about 8–14 min (Build plus Commit, one-GPU template). A GPU-less Build task would free the GPU for all but the 5–10 min Commit.
