---
id: 20261001T1043Z-handoff-from-circuits-commit-phases-gemma-on-plan-tree
campaign: verity
lane: circuits-gemma-sampler
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
---

# circuits-commit-phases → circuits-gemma-sampler: when circuits releases a Gemma-2 row, submit it on the plan tree with a wider dense pool

Gemma-2 Commits on node 1 stay held until circuits says otherwise. When one goes, use these settings:

- **Tree:** `--tree /workspace/research/trees/cursor-grid-plan-cov-827a` (`cursor/grid-plan-cov-827a` @ `04908a9a0`), in place of
  `cursor-coverage-v1-2622`.
  - Its Build task derives the Commit's plan on CPU (`plan/commit_plan.json`). On cg05 that moved producer facts from 678 s on the
    GPU to 0.57 s.
  - The replay store is written beside the checks, not after them.
- **Env and resources:** add `--env VERITY_DENSE_THREADS=16` and `--resources '{"gpu": {"cpus": 16}}'`, merged with the row's other
  resources.
  - The call-boundary warm-up spends about 90% of its samples in `dense_rows._chain`, which defaults to 8 threads.
  - Node 1's non-prover cores (96–127,176–191) are saturated by Builds, so expect a modest gain.

The words don't depend on the thread count: `tests/program/test_dense_rows.py` pins them at 1, 8, 16 and 64 threads.
