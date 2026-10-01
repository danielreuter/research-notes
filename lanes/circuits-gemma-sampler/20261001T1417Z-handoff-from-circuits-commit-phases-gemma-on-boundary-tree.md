---
id: 20261001T1417Z-handoff-from-circuits-commit-phases-gemma-on-boundary-tree
campaign: verity
lane: circuits-gemma-sampler
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

# circuits-commit-phases → circuits-gemma-sampler: when circuits releases a Gemma-2 row, submit it on `cursor-grid-boundary-cov-827a`

This replaces the tree in note:20261001T1043Z-handoff-from-circuits-commit-phases-gemma-on-plan-tree. Use
`--tree /workspace/research/trees/cursor-grid-boundary-cov-827a` (`cursor/grid-boundary-cov-827a` @ `805ca614e`). Keep that note's
`--env VERITY_DENSE_THREADS=16` and `--resources '{"gpu": {"cpus": 16}}'`.

- **What changes for Gemma-2:** the Build's call-boundary check writes the call-boundary plan (`call_boundary_plan.json`). The Commit reads it in
  about 1 s, where it used to derive the plan after `warmup_control0` with its GPU held.
  - On node 1 that derivation took 22–28 s at B1, 73–100 s at B8, 150–185 s at B16, 250–260 s at B32 and 3,085 s at B64 i1024.
  - On the golden, `cov-cg04-cbp-after` (cg04-2's config) has the same run root `c22469530fd2f335`, binding, seed and replay 460/460 as cg04-2
    (note:20261001T1414Z-checkpoint-from-circuits-commit-phases-boundary-plan-goldens).
- **What to check on a row:** `call_boundary_plan.json` in the row dir after the Build, and `verdict.call_boundary_plan.used: true` with a
  `prep.call_boundary_plan` span of source `plan` in the Commit. A `plan_recomputed` with its `why` means the Commit derived the plan itself, as
  before. That is still correct, just slower.
- **Gemma-2 Commits on node 1 still go only when circuits releases them.**
