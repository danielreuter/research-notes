---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vLLM coordinator · cc: vllm-staging-bug · created: 2026-09-30T19:45Z

**#594's batch-8 proof: one pass, and one failure with a new cause. The 130 stay held.** The staging mismatch is gone in both proof
runs, but Gumbel at batch 8 now fails identity coverage.

- **g218, Llama-3.2-1B, top-p 0.95, b8, 256/32: PASS**, 460/460 on the uniform draw (`r20260930-192204-fd2b`, pre-merge tree
  `c6f1ec98`, with #594 merged from `6a7ff652`).
- **g211, TinyLlama-1.1B, Gumbel, b8, 256/32: FAIL, twice**: `r20260930-192928-96f5`, after the Commit retried the same run in
  `/workspace/jobs/cov/cov-g211-2/<row>/commit.log`. There's no bounded-staging error now. Instead:
  `identity coverage: 118 of 40108 required identities have no binding (first: step 0 runner.sampler/splits inv 0 req r0 rank 0)`
  and `boundary_linkage FAIL 118/118: prescribed splits of r0 at step 0 not committed`. The Gumbel sampler's splits tap is not
  committed at batch 8. TinyLlama Gumbel at batch 1 passes (g250, g228).
- **Rerun from main, as root asked:** the run branch is now main `b1c77be0` (#594 on main) + #483 #487 #501 #502 #503, at
  `d7b32933`. g218 and g211 are rerunning from it through the dispatcher (`vllm-epoch-run/cov-g218-3` and `cov-g211-3`). I
  release the 130 only if both pass 460/460. If g211 fails the same way again, it's yours and vllm-staging-bug's to route.
- **Submissions** now go to the dispatcher as plain Kueue Jobs (`dispatch.py submit config-run`), with 8 Builds kept pending in
  deployments-cpu. The feeder is running greedy deployments at every batch and the TP2 block meanwhile.
