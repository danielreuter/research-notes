---
id: 20261007T1115Z-ask-from-nebius-infra-shadow-queues-trip-idle-alert
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# The shadow queues set off "GPU idle while work is waiting" on node 1 (4:15 AM PDT)

**Ask:** exclude the `shadow-*` queues from that alert's waiting count.

The 10:44Z Oct 7 alert (`20261007T1044Z-alert-gpu-idle-while-work-is-waiting-4f02baf9`, all 8 GPUs firing) is a false
positive.

- The rule `nebius-gpu-idle-work-waiting` counts waiting work as `sum(vy_queue_pending) + sum(vy_ready_jobs)`
  (`tools/research/src/research/pods/nebius/monitoring/alerting.yaml`).
- `vy-exporter` now also exports `vy_queue_pending` for the seven `shadow-*` ClusterQueues created at 08:28Z (cohort
  `vy-shadow`, namespace `vy-shadow`). Those queues hold bare Workload objects with no pods.
- In the hour to 11:10Z, the only non-zero `vy_queue_pending` was `queue="shadow-lean"` (1). Every `vy_ready_jobs` was 0,
  and the real queues had nothing pending. So no real work was waiting.

A fix would be `sum(vy_queue_pending{queue!~"shadow-.*"})` in refId W, or not exporting the shadow queues. Until then the
alert fires whenever a shadow workload is pending, and the "root checks after 30 minutes" step costs root a check for
nothing.

The 06:01Z alert of the same name was real: circuits' 8-GPU job was waiting then, before the shadow queues existed.

Both nodes stop at their 15:00Z deadline today, so this matters only if the rule or the shadow queues carry over. I haven't
changed anything.
