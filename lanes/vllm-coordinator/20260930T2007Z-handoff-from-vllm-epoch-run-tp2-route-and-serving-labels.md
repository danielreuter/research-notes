---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vLLM coordinator · created: 2026-09-30T20:07Z · re: your 19:09Z GO, parts 2 and 3

Two parts of the grid need a decision from you:

1. **The TP2 block (73 deployments) can't run on `config-run`.** Its Build task has no GPU, and vLLM refuses a 2-rank engine there:
   `ParallelConfig: World size (2) is larger than the number of available GPUs (0) in this node` (rank 0, in `derive_step`,
   18 s in). The 18 that ran are labelled `unsupported` with that cause, not `fail`. The rest wait in `grid_deferred_tp2`.
   **Which route should TP2 take?** The TP2 lane's template (`cfgtp2-deferred` on the node), a GPU Build class, or a
   world-size override in the Build? I'll requeue them on whichever you name.
2. **Serving variants have no row-id label.** The execution vocabulary is `bi-eager`, `bi-eager-fa2`, `eager`, `bi-compiled` and
   `compiled` (`engine/build.py`), and `engine_kwargs` pins `enable_prefix_caching=False`. What label should chunked prefill take
   (e.g. `bi-eager-cp`), and how does it reach the engine? Prefix caching also needs a slug before I label it unsupported.

Being labelled `unsupported` now by a background job (about 330 labels still to write): top-k (16), TP4 (16), and every 4k deployment as `build timeout` (105). The
grid's workloads are committed to the run branch (`d7b32933`, on main `b1c77be0`). #594's proof reruns from main are in flight.
