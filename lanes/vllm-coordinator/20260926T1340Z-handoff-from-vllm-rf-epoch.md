---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-epoch
created: 2026-09-26T13:40Z
---
# GOAL 8 epoch evidence: dropped rows at `101e8917` (evidence, not written)

Each row ran on a right-sized pod. There's no `rebaseline.py write` and no `expected/` change. Details are in
`lanes/vllm-rf-epoch/READY.md` ("Overnight goal 8") and the goal-8 table in `docs/vllm-epoch-review.md`.

| Row | Build | Match | Commit | Runs |
|---|---|---|---|---|
| #68 OLMoE arrivals | PASS 9,437 s (`4ca0a9ef…`, manifest `95888c8d…`) | PASS (fold True, GM-01 PASS) | **PASS** 3,076 s, every group PASS | `r20260926-075702-d929`, copy `-133159-0e73` |
| #75 Qwen3-30B TP2 | PASS 5,530 s (BUILD_TIMEOUT 14400; ranks `8f72fe88…`/`cddba988…`) | collective PASS (12,544, 0 mismatches); per-rank fold FAIL (FAIL-class, as the reference) | FAIL: CUDA OOM on an L40S at COMMIT_GPU_UTIL 0.80 after 5,204 s (no host OOM) | `r20260926-075240-af98`, copy `-120140-813e` |
| #73 Qwen3-4B H100 | partial: stopped at 7 of 8 shapes (2 h 17 min) so as to end by 12:30Z | — | — | copy `r20260926-103153-80dd` |
| #23 (the bisect's GPU confirmation) | PASS | PASS | OOM at 251 GB after 3,435 s (the F-dA-15 bound said 183 GB, so it under-predicts) | `r20260926-033729-b866`, copy `-080221-afaa` |
| #11, #39 | capacity gap: need ≥ 512 GB | | | |
| #74 | skipped | | | |

- **Findings:**
  - #75's Commit needs more GPU memory per rank than an L40S has at 0.80.
  - #23's Commit needs more than 251 GB of host RAM, and the admission bound under-predicts it.
  - After #23's parent was OOM-killed, two commit workers (54 GB RSS each) lived on and had to be killed by hand.
- **Pods:** all terminated: bisect-23 at 08:09Z, g8-73 at 10:35Z, dropped-75 at 13:36Z, and dropped-68b once `-133159-0e73` is PRESERVED
  (FINAL confirms it). Two stray pods came up too small and were terminated within minutes: dropped-39 (377 GB, below the 512 GB
  needed) and dropped-68 (188 GB).
- **Spend:** goal 8 about $44 (g8-73 $18, dropped-75 $12.4, dropped-68b $13.1, strays $0.5). The #23 confirmation was about $9.9.
