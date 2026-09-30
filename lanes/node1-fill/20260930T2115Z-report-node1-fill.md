---
id: 20260930T2115Z-report-node1-fill
campaign: one-pool
lane: node1-fill
kind: report
status: open
repo: danielreuter/verity
origin: node1-fill (bc-4992e18a), worker of infra (bc-17cc41f1)
---

# node1-fill: get node 1's GPUs doing approved work today, through its existing Kueue

## Log

- **2:13 PM PDT (21:13Z), baseline:** node 1 was 1.1% GPU busy over the last hour (DCGM `GR_ENGINE_ACTIVE`, 8 GPUs), with 0.3%
  mean utilization and 31% CPU. All 8 GPUs are reserved: `deployments-gpu` 5/5 and `provers` 3/3. Diagnosis:
  `note:20260930T2115Z-handoff-from-node1-fill-why-29-wait`.
