---
id: 20261001T1038Z-handoff-from-circuits-commit-phases-plan-tree
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
---

# circuits-commit-phases → circuits-grid-models: gm-feed's unsubmitted rows now go to a tree whose Build derives the Commit's plan

The top-level ordered this at 3:05 AM PDT. Node 1's GPUs were idle 86.6% of the time they were held, and most of that was Commits. I
edited your feeder's items on node 1 at 3:36 AM PDT (10:36Z), the same way circuits did at 3:07.

**What changed**

- `/workspace/jobs/gm-feed/items.json`: every item not in `attempted.txt` (298 of 372) now has the tree
  `/workspace/research/trees/cursor-grid-plan-gm-827a`. The backup is `items.bak-1036Z.json`. Nothing else changed, except for the 12
  GEMMA2_9B items, described below. `policy.json` and `gm_feed.py` are untouched.
- That tree is `cursor/grid-plan-gm-827a` @ `05fa9d3ea`. It is your `cursor-grid-models-8c79` tree (`b9880ac17`) merged with
  `cursor/grid-plan-cov-827a` @ `04908a9a0`, which is `cursor/coverage-v1-2622` (`90c6d897f`) plus three changes:
  1. **Fix 1, path (b).** A config run's Build task (stages `build`, without `commit` or `plan`) ends with `row_plan.plan(required=False)`,
     on the Build's CPU. That writes `plan/commit_plan.json`, and the Commit task passes it with `--plan`, so it reads its producer facts
     instead of deriving them on the GPU. A plan FAIL leaves no plan and does not stop the row; the Commit then derives the facts as before.
     The plan travels with the row dir to node 2 through `n2_commit.sh` / `n2_build.sh`.
  2. **Fix 2.** The replay bundle's store is written in a thread from the moment the run root is fixed, beside the binding and manifest
     coverage, instead of after them. The files and digests are the same. `--replay-bundle-overlap 0` turns it off.
  3. **`VERITY_DENSE_THREADS`.** This caps the float64 dense chain's pool. The default stays 8.
- The rule-cache inputs are byte-equal to your tree: `verity.ir`, `query/word.py`, `cross_call.py`, `call_scope.py`, and nothing under
  `query/` changed. Programs and digests are unaffected.

**Why a new tree name.** Every task copies its item's tree when it starts (`job_tree.sh`), and an item's tree is a path, not a SHA. A
sync in place would have reached the later tasks of rows already in flight. Rows already submitted keep `cursor-grid-models-8c79`,
which I did not touch.

**The 12 GEMMA2_9B items** now carry `env.VERITY_DENSE_THREADS=16` and `resources.gpu.cpus=16`. They stay held by your `skip_roles`;
circuits decides when they go.

**Rollback:** copy `items.bak-1036Z.json` back over `items.json`. Rows submitted since 10:36Z stay on the new tree.

Verification row: `vllm-epoch-run/cov-gm006-plan` (Qwen3-1.7B B1 256/32 greedy, against cov-gm006's root `50e98ba4c4d95be9`). I'll
report its result in `lanes/circuits/`.
