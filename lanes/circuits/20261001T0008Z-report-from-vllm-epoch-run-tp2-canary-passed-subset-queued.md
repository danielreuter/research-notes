---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits, cc vllm-tp2-gpuless-build · created: 2026-10-01T00:08Z · on your 23:08Z TP2 canary handoff

- **The TP2 canary passed.** cov-p000 (Llama-3.2-1B TP2 B1 256/32 greedy) is `r20260930-234646-6dab`.
  - The Build ran GPU-less in 121 s, and its digests equal the lane's references: step `d29ee587…` and `c3765e95…`, workload `f6383f05…` and
    `6ceecbaf…`, manifest `bb87df12…`.
  - The 2-GPU Commit passed in 191 s. Its replay was 460/460, summed over both ranks (family strata). Run root `068eb04fcd5baad0`.
  - No rank-1 crash: p002-2's illegal memory access didn't recur.
  - The TP Commit replays inline, so it seals no bundle.
- **The TP2 subset is queued**, in the canary's form, 2 at a time (`TP2_MAX` 2): greedy B1 and B8 at 256/32 for 9 models, OLMoE and Qwen3-30B-A3B
  included. That is 17 deployments beyond p000, B1 first. Each carries the research question.
  - p012 (TinyLlama) and p047 (Qwen3-4B) are building.
  - The TP2 top-p cells stay deferred. Say if you want them too.
- **A false hang, fixed:** at 00:02Z my hang check cancelled n145 (Qwen2.5-7B B8 greedy). It had gone 20 min without commit.log output, but it was
  sealing its replay bundle (about 25 MB/s), not hung.
  - The check now counts a growing bundle as progress (tested on node 1).
  - n145 is requeued as cov-n145-3.
  - The two TP2 Qwen2.5-7B cells it had held are restored.
  - No other deployment was cancelled this way.
