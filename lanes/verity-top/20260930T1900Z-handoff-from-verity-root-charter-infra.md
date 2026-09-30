---
id: 20260930T1900Z-handoff-from-verity-root-charter-infra
campaign: verity
lane: verity-top
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Charter: infra, Verity side (completes `note:20260930T1740Z-handoff-from-pous-charter-infra`)

State as of 19:00Z Sep 30.

- **Owner:** a **fresh** infra coordinator, started from pous's charter plus this one. It takes over the workers below from the research coordinator.
- **Remit:** utilization of vy-nebius-1 and -2, the scheduler (Kueue queues `circuits`, `provers`, backfill), on-demand compute (RunPod), the GitHub broker, merge-train speed, and folding agents' task infra into one API.

## Workers (they report to RC today)
| lane | id | owns |
|---|---|---|
| nebius-infra steward | `bc-fd19a2fe-4dd1-5d17-b138-509b5268e910` | `infra/nebius` (#496), Grafana, the queues, the three-task config runs |
| Kueue worker / server bring-up | `bc-c445c55b-453a-5b6a-b6a1-f6fe3d1eda07` | node setup |
| node1-dispatcher | `bc-70706bc3-bf17-5315-9276-4811c214ffee` | node-1 dispatch; receives the alert sink's findings |
| merge-train time | `bc-8e199f0d-8659-5bbc-8056-197f69ba9ff8` | #531 (clean-host guard) |
| GPU-busy watcher | `bc-2edafd03-dd2d-5694-9c55-034c443cc2ca` | hourly GPU-busy checks |
| fail-closed guards and pod leases | `bc-529bea7d-5d34-50d2-91ce-57b592d72bfb` | guards |
| PoUW contact (server 2) | `bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d` | vy-nebius-2 handover |

## Open items (**D** = needs Daniel)
- **D:** rotate the Nebius operator key (`verity-setup`), which was exposed in POUS transcripts.
- **D:** the spend ceiling and on-demand policy (RunPod; no check pods left).
- One task API: the job-service design vs the SkyPilot migration.
- Land #496 and #531; roll the GitHub broker out to every lane (verified 17:16Z).
- Server-1 GPU busy was about 1% overnight: finish the CPU Build / GPU Commit / CPU replay split (circuit's PR B).

## Receives from the others
Circuit's three-task layout and caches; proof's merge-train machinery and Job queue stage 1; console's metrics feeds; and verity-root's Grafana alerts after the handover.

## Where state lives
- Lanes `nebius-infra`, `node1-dispatcher`; alert rules `pods/nebius/monitoring/alerting.yaml`; Grafana on vy-nebius-1 (`ssh -N -L 3000:127.0.0.1:3000`).
- The verity-root store's `docs/`: `infra-overview.md`, `shared-infra-plan.md`, `job-service-design.md`, `skypilot-migration-plan.md`, `gpu-utilization-postmortem.md`, `github-broker-rollout.md`, `nebius-server-runbook.md`, `merge-workflow-review.md`.
