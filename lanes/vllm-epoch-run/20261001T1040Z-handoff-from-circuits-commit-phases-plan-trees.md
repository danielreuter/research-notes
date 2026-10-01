---
id: 20261001T1040Z-handoff-from-circuits-commit-phases-plan-trees
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
---

# circuits-commit-phases → vllm-epoch-run (feeder and labeller): new config-run items go on the plan trees

On the top-level's 3:05 AM PDT order, these are node 1's trees for every new Commit from 3:36 AM PDT (10:36Z):

| for | tree | branch @ commit |
| --- | --- | --- |
| cov / cg rows (was `cursor-coverage-v1-2622`) | `/workspace/research/trees/cursor-grid-plan-cov-827a` | `cursor/grid-plan-cov-827a` @ `04908a9a0` |
| gm rows (was `cursor-grid-models-8c79`) | `/workspace/research/trees/cursor-grid-plan-gm-827a` | `cursor/grid-plan-gm-827a` @ `05fa9d3ea` |

Each new tree is its old one plus three changes:

1. **The plan at the Build's end.** A config run's Build task derives the Commit's plan on CPU, and the Commit task reads its producer
   facts from it.
2. **The replay store beside the checks.** The replay bundle's store is written beside the binding and manifest coverage, not after them.
3. **`VERITY_DENSE_THREADS`.** This caps the float64 dense chain's threads (default 8).

The rule-cache inputs and Programs are unchanged.

- **gm-feed is already switched** (note:20261001T1038Z-handoff-from-circuits-commit-phases-plan-tree in `lanes/circuits-grid-models/`).
- **Anything else you submit** (`dispatch.py submit config-run vllm-epoch-run/...`) should use `--tree` with the matching new path.
- **Rows already in flight** keep their old trees, which I didn't touch.
- **For the labeller:** a Commit on the new trees records `verdict.plan` (`used`, or `plan_recomputed` with its reason) and a
  `prep.producer_facts` span whose `source` is `plan` or `derived`. A `plan FAIL` line in `stages.txt` after the Build does not fail
  the row.
