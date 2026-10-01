---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T10:41Z

**The widened pool for item 2 is live (3:35 AM PDT).** `VERITY_DENSE_THREADS` (`cursor/dense-threads-8c79` @ `5c8df15b4`) is on both
plan trees. gm-feed's 12 GEMMA2_9B items carry `VERITY_DENSE_THREADS=16` and `resources.gpu.cpus=16`, and they are still held.

**It can't widen much on node 1.** The dispatcher pins every non-prover task to 96–127,176–191. Those 48 cores measured 100% busy at
3:24 AM PDT (12 Builds). The idle cores are the RC's check slots (8–95: 55 of 88 idle) and the provers' (128–175: 43 of 48 idle).
Daniel's 01:35Z ruling keeps vLLM jobs off the provers' cores. So 16 threads buy only a larger CFS share for the Commit.

**My call: keep Gemma-2 held, apart from at most one B1 canary.** This is untested on a Gemma row. A real gain needs cores outside the
48 (infra's `VY_DISPATCH_CPUS`, or a ruling), which I haven't asked for.
