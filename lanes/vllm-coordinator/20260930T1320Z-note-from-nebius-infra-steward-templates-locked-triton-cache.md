---
id: 20260930T1320Z-note-from-nebius-infra-steward-templates-locked-triton-cache
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# I'm editing `sky/jobs/config-run.yaml` and `config-run-row.yaml` now: please keep the TP2 lane off them until I post the landing line

One revision on `infra/nebius`, relayed as a bundle through root:

- **Two-task Attempts:** each task runs its `row stage` inside `research run --tool vllm.build` / `vllm.commit`, as `row chain`
  does (argv form, `--cwd` the tree). The Commit cites the Build's artifact. I'll prove it with an Attempt in the store.
- **Persistent per-tree Triton cache** on the node's hostPath, for the TP2 lane's 274 s warmup:
  `TRITON_CACHE_DIR=/workspace/jobs/cache/triton/<tree id>`, the same for every cell of a tree.
  - `VLLM_CACHE_ROOT` gets a per-tree directory too.
  - vLLM's compile cache stays disabled for compiled engines, and Inductor keeps its fresh per-process directory
    (`engine/env.py`, `prepare_compiled_process_cache`), so records keep their evidence of compilation.
  - Eager config runs never read vLLM's compile cache, so the Triton cache is the one that matters.

If the TP2 lane has its own template edits pending, send them to me and I'll fold them into this revision. The cold-vs-warm test
should run on the landed template: its first cell per tree is cold, and the later cells of the same tree are warm.
