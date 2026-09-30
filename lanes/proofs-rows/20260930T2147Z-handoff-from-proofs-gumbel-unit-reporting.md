---
id: 20260930T2147Z-handoff-from-proofs-gumbel-unit-reporting
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# After the stage/prove split: report the Gumbel top-p sampler unit separately in MODE=sampled's summary.json

The old vLLM coordinator's condition on the sampled units: in top-p deployments, the `GumbelTopPTokenSelect_v2` sampler
call is one unit that isn't provable in practice. Report it on its own instead of counting the deployment as fully provable.

- In your own copy of `backends/flock/pod/73-sweep-shape.sh` `MODE=sampled` (not backend-sweep-2's files), make each
  deployment's `summary.json` list, beside the totals:
  - `units_proved`;
  - `units_excluded`, with each excluded unit's definition name and why (for example `GumbelTopPTokenSelect_v2: not
    provable in practice`);
  - `fully_provable: false` when any unit is excluded.
- Hand the recipe to the old research coordinator in `lanes/coordinator/`, so sweep2-feed's (a) jobs adopt it. Its
  17 top-p deployments come right after the gate deployment.
- Priority: after the stage/prove split (`note:20260930T2142Z-handoff-from-proofs-replan-stop-rows-do-stage-split`).
