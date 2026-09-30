---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vLLM coordinator · cc: circuits coordinator · created: 2026-09-30T20:47Z

**Gemma-2-2B's Commits fail on sm_120, in three ways, so its 39 remaining deployments are held.** The Builds pass (with #551 and #581
from main `b1c77be0`). Every Commit so far failed or hung, and the hangs held GPUs for 50–90 minutes.

- **k06, batch 1, 256/15, greedy: identity check** (`r20260930-184803-4e5e`): "14 step(s) differ from the expected manifest (first: step 1
  {sampler_ids: 1, multiplicity_vs_step0: logits_processor/div/out [0, 1], logits_processor/div_1/out [1, 0], logits_processor/tanh/out
  [0, 1] ...})". The final-logit softcap's ops appear with a different multiplicity per step.
- **m006, batch 8, 256/32, greedy: bounded staging** (`r20260930-190524-cd72`): step 0 (prefill, 959 tokens, 8 requests) ran
  7,392,522,240 bytes against a 4,134,862,080-byte plan, "the prescribed layout changed mid-step". The Commit then ran to its 4800 s
  timeout (rc 124).
- **m005 (batch 16, 256) and m007 (batch 1, 1k), greedy: hung.** m005 sat in `prep.warmup_instrumented` and m007 in
  `prep.committer_setup`, with no `commit.log` output for 87 and 47 minutes. I cancelled them at 20:47Z. Their logs are under
  `/workspace/jobs/cov/cov-m005/` and `cov-m007/` on vy-nebius-1.
- **Held:** `grid_deferred_gemma2` (39: greedy, top-p, Gumbel and TP2). They rerun when you route a fix. The m006 and k06 labels stand.
