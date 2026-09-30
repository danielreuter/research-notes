---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T21:22Z

**Checkpoint:** 411 labelled: 82 pass, 26 fail, 303 unsupported. Node 1: 10 Builds running and 8 waiting in deployments-cpu. **29 Commit-ready waiting** in deployments-gpu, with 4 running (TP2's 2-GPU jobs are among them). Node 2: 6 Builds in flight (your cap is 6).

**Done since 20:50Z:**
- **#557 swap, on a new run branch:** `cursor/coverage-v1-2622` @ `7db8c455` = main `73eee493` + #503 + #557 + PR B (#598, with PR A #599) + infra/nebius, with no #483/#501 (and no #487/#502: I run no FP8). #503's uniform replay draw is ported into PR A's `c2_replay` and the bundle's args. The grid's workloads are committed there. The feeder submits from v1 now. v0 (`cursor/coverage-v0-2622`) is left as it was, not force-pushed.
- **Qwen2/2.5:** 111 deployments of Qwen2.5-0.5B, 1.5B and 7B are runnable on v1 (87 single-GPU and 24 TP2), and k03 reruns. They replace the `pending #535` labels as results land. The 45 at 4k now carry the build-timeout cause. Gumbel at batch 8 and up joins the Gumbel hold.
- **Node 2:** Builds go through `n2_build.sh submit` (TP1 only, 256 GB or less), up to 6 in flight, and node 1's Build queue is kept at 8 pending.
- **Serving variants:** the 16 `-pc` deployments are labelled `unsupported` (prefix caching off by design). The 16 `-cp` deployments are `unsupported` too, because chunked prefill needs code: the Build's step model assumes unchunked prefill (`pipeline/launch_context.py`), and `bi-eager-cp` isn't in `engine/build.py`'s execution table, which fails closed. **That's backlog for you to log.**
- **Gemma-2 is held (39).** `20260930T2047Z-handoff-from-vllm-epoch-run-gemma2-commit-fails.md` in this folder has the details.

**Still open:** the Gumbel hold (g211's `runner.sampler/splits` cause) and the dispatcher's stale two-task template, which keeps replay on the GPU (`lanes/nebius-infra/20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale.md`).
