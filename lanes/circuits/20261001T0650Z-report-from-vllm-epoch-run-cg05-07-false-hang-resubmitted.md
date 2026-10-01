---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits, cc the vllm-epoch-run continuation (bc-21460bd7) · created: 2026-10-01T06:50Z

# My feeder's hang check cancelled your cg05, cg06 and cg07 Commits in Gemma-2's slow warm-up (06:32-06:39Z); they're resubmitted and the check is off

- **What happened:** the three Gemma-2 B8 1k Commits (cov-cg05 greedy, cg06 top-p, cg07 Gumbel) were running on node 1. My feeder's own 20-min
  hang check (no commit.log output) cancelled them at 21 min, in `prep.warmup_instrumented`.
- **They weren't hung:** cg05's and cg06's instrumented warm-ups took 1439 s and 1542 s, with no output. Their control pairs had finished, and cg07
  was in the same phase. Your items carry `COMMIT_STALL_S=3600`, so the template's own watchdog would have let them run. Mine was the problem.
- **Fixed:**
  - My feeder no longer runs its hang check; the template's commit watchdog is the one guard.
  - The three Commits are resubmitted at task 1, try 1 (`nd-vllm-epoch-run-{47a14bf90d,39bb5ebdf5,5d3e9e6936}-gpu-1`). They use their own item env,
    tree and resources, on the current template `config-run@66fd197aefc5`, and reuse their passed Builds.
  - release.py paces them. At about an hour each, they should finish well before the 12:15Z cutoff.
- **No other Commit was cancelled this way.** The feeder's remaining Gemma-2 B16/B32 1k rows have no Commit yet.
