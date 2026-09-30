---
id: 20260930T1130Z-handoff-from-build-optimization-batch-8-1k-target
campaign: overnight-sep30
lane: build-v2-kv
kind: handoff
status: open
repo: danielreuter/verity
origin: build-optimization (bc-47d0a3ed)
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

# build-optimization -> build-v2-kv (bc-57ddc507): a build-v2 target, Llama-3.2-1B at batch 8 with 1k context (28-minute Build)

**Why it matters:** root's 11:18Z note. The sweep's `llama32-1b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__greedy__bi-eager`
(run `r20260930-102756-ce52`) took 28 minutes to Build and peaked at 17 GiB, against about 4 minutes at batch 1. Shared key/value
prefixes should hit exactly this case.

**Where the 28 minutes went**, from the second attempt's own timeline (1,695 s; the row dir is
`/workspace/jobs/cov/cov-k20/<row>` on vy-nebius-1):
- **Derives, serial, 1,352 s:**
  - the step derive, 26 s;
  - the envelope request derive at LP1024 T127, 596 s, 10.2 GB, 187K Calls;
  - the two extra shapes that attempt re-derived: LP913 T48 (348 s) and LP1024 T44 (382 s).

  The first attempt's other six extra shapes took 13–419 s each, the largest LP717 T127 at 419 s and 6.6 GB. Their sum is about
  2,400 s of derive time.
- **Composition, 278 s.**
- **Manifest, 65 s.**

So after #479 (parallel derives) the critical path is the single envelope derive at LP1024 T127, which is your tokens² term.

**In the benchmark now:**
- It's the config `llama32-1b-1k` (phase `decode`), row `llama32-1b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager`. Its
  workload declares the L40S target, so a CPU host builds it.
- The workload is on `cursor/build-bench-6942` at `33081b38`. `build_bench.py` in the Project store's `internal/build-benchmark/` takes
  `--rows llama32-1b-1k:decode`.
- On my cores 128–159, starting at 13:30Z after the quiet hour, `r20260930-112335-b150` runs the baseline (main, serial derives), and
  then `r20260930-112356-ac03` runs attempt 7 (every build-v1 change).

Your `ov.gate` can compare against the baseline run's `bench.json` once it lands, at about 14:00Z.
