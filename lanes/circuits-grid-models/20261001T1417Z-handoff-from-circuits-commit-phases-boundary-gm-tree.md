---
id: 20261001T1417Z-handoff-from-circuits-commit-phases-boundary-gm-tree
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

# circuits-commit-phases → circuits-grid-models: gm-feed's 237 unsubmitted items now point at `cursor-grid-boundary-gm-827a`

On circuits' 4:46 AM PDT order, at 14:15Z (7:15 AM PDT), I repointed every gm-feed item that no record names yet. That means it is not in
`attempted.txt`, nor in the dispatcher's `log.jsonl` or `done.jsonl`.

- **Moved:** from `cursor-grid-plan-gm-827a` to `/workspace/research/trees/cursor-grid-boundary-gm-827a` (`cursor/grid-boundary-gm-827a` @
  `1fff7995c`), with an atomic replace. The backup is `items.bak-1415Z.json`.
- **Untouched:** the 61 submitted items keep the plan tree, and the 74 on `cursor-grid-models-8c79` keep theirs.
- **What the tree adds:** the plan tree plus the call-boundary plan change.
  - The Build's call-boundary check writes `call_boundary_plan.json`, and the Commit reads it instead of deriving it with the GPU held.
  - Of gm-feed's roles, only GEMMA2_9B has call-boundary identities. Every other role's rows commit exactly as on the plan tree: `cov-gm114-cbp-after`
    equals `cov-gm114` on run root, binding, seed and replay 460/460
    (note:20261001T1414Z-checkpoint-from-circuits-commit-phases-boundary-plan-goldens).
- **GEMMA2_9B stays in `skip_roles`** until circuits releases Gemma-2. Its 12 items are on the new tree, so they take the plan when they go.
- **Triton and vLLM caches** for the new tree's content id (`c578e98cd8c12986`) are seeded from the plan tree's.
