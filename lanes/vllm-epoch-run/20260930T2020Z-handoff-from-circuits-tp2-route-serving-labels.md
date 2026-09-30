---
id: 20260930T2020Z-handoff-from-circuits-tp2-route-serving-labels
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# @circuits answers your 1:07 PM PDT asks: TP2 through cfgtp2-deferred; chunked prefill runs as `-cp`; prefix caching `-pc`, unsupported

I coordinate the vLLM remit now (`lanes/circuits/`); send findings and asks there. @old-circuits-and-proofs' 1:15 PM PDT swap
(#483/#501 out, #557 in, re-run the affected Qwen2/2.5 deployments) stands.

1. **TP2 (73 deployments): the TP2 lane's `cfgtp2-deferred` template**, Build and Commit on two GPUs of one host (the sweep plan's
   "TP2 configs: 2 on one host"). It's the route #499 already merged. No GPU Build class and no world-size override: those are
   new code, and Daniel's priorities hold new work until infra settles. The 18 labelled `unsupported` for "World size (2) > 0
   GPUs" are a routing artifact, not a finding: requeue them with the other 55, and supersede those labels when they land.
   Queue them after the single-GPU grid, in engine-key order. I'm telling @infra the queue needs a 2-GPU-on-one-host class.
2. **Chunked prefill: slug `-cp` on the execution you run** (e.g. `bi-eager-cp`), reaching the engine as
   `engine_kwargs` `enable_chunked_prefill=True` with `max_num_batched_tokens` below one step's prefill tokens, so prefill
   really splits. Run the plan's 16 (all 16 models, B8 1k/128 greedy) if Build and Commit take it with no code change. If they
   need code, label them `unsupported` with the cause, and tell me; I log it as backlog.
3. **Prefix caching: slug `-pc`, label `unsupported` now** ("engine built with prefix caching off by design"), as the plan says.

Send me, in `lanes/circuits/`: whether both #594 proof reruns from main pass (g218, g211), whether the 130 are released, how
many Commit-ready deployments are queued, and when the Qwen2/2.5 re-runs on #557 go in.
