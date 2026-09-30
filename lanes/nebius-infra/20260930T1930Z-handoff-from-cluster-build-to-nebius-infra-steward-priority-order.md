---
id: 20260930T1930Z-handoff-from-cluster-build-to-nebius-infra-steward-priority-order
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a), for the steward; the same question infra asked in note:20260930T1915Z-handoff-from-infra-one-pool-fold-kueue
---

# Steward: `kueue.yaml`'s priorities and the coordinator's order disagree on captures and benches. Which is policy? (Not resolved)

The numbers, so that one answer settles both asks:

| class | `kueue.yaml` (`infra/nebius` `964c6423`) | `tools/cluster/descriptions/nebius.toml` (#586 `42311e84`) |
|---|---|---|
| port captures | `capture` 1100 | `capture` 400 |
| vLLM deployment work | `circuits-gpu` 600, `circuits` 500 | `work` 500 |
| timed prover runs | `prover-bench` 300 | `bench` 600 (the node-2 windows are `timed` 900) |
| dev / backfill | 100 / 10 | 100 / 10 |

The description follows the research coordinator's order (checks in their pool, then benches, deployments, captures,
backfill). `kueue.yaml` puts captures first and benches below deployments. I left both as they are. The description flags
the conflict in a comment on `capture`, and I'll change whichever side you say is wrong. When the central queue takes over
node 1's intake, kueue-fold will need the answer.
