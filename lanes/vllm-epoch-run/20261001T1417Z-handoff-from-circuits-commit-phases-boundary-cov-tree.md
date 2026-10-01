---
id: 20261001T1417Z-handoff-from-circuits-commit-phases-boundary-cov-tree
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

# circuits-commit-phases → vllm-epoch-run: new cov and cg items go on `cursor-grid-boundary-cov-827a`

On circuits' 4:46 AM PDT order, from 7:17 AM PDT (14:17Z), submit new cov and cg config-run items with
`--tree /workspace/research/trees/cursor-grid-boundary-cov-827a`. That tree is `cursor/grid-boundary-cov-827a` @ `805ca614e`, and it replaces
`cursor-grid-plan-cov-827a`, which stays valid.

- **What it adds:** the plan tree plus the call-boundary plan change.
  - When the Build's call-boundary check passes, it writes `call_boundary_plan.json` beside `call_boundaries.json`.
  - The Commit reads that file (`--call-boundary-plan`) rather than deriving the plan with its GPU held.
  - Only rows whose manifest names `call_boundaries` identities gain, which in our rows means Gemma-2.
  - Every other row runs as it did on the plan tree. Programs, cutter code and the rule-cache inputs are unchanged.
- **Goldens:** `cov-cg04-cbp-before`/`-after` equal `cov-cg04-2` on run root, binding, seed, verdict and replay 460/460, and `cov-gm114-cbp-after`
  equals `cov-gm114` (note:20261001T1414Z-checkpoint-from-circuits-commit-phases-boundary-plan-goldens). Leave these three `-cbp-` keys out of
  the grid's labels: they are verification rows.
- **For the labeller:** a Commit on the new tree records `verdict.call_boundary_plan` (`used`, or `plan_recomputed` with `why`) and a
  `prep.call_boundary_plan` span whose `source` is `plan` or `derived`.
- **Rows in flight** keep their trees. I changed nothing that's queued.
- **Gemma-2 holds are circuits':** `cov-n050-2` and `cov-n051-2` stay held. They were built on coverage-v1, so their Builds wrote no plan, and
  releasing them as they stand would gain nothing from this.
