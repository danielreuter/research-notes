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
- **2:14 PM PDT, change:** `deployments-gpu` → StrictFIFO, live (`kubectl patch`, `queueingStrategy` only) and on `infra/nebius`
  `e7bc39f38`; `test_nebius_sky` passes (20). The steward was told:
  `note:20260930T2116Z-handoff-from-node1-fill-deployments-gpu-strictfifo`.
- **2:18 PM PDT, asked proofs** to have backend-sweep-2 write its shape sweep to `backfill`, so `provers`' third GPU goes to (b) or (a)
  (`note:20260930T2118Z-handoff-from-node1-fill-sweep-to-backfill-frees-a-gpu-for-b`).
- **2:22 PM PDT, result:** the first TP2 job was admitted (`9c1e281bb3`, 67 min in the queue), on GPUs 2 and 4. Circuits was told
  (`note:20260930T2127Z-handoff-from-node1-fill-tp2-admits-now`).
- **Not possible today: co-location.** The GPUs with free memory are `provers`' (steward's condition 3: never), and every Commit
  GPU holds 49–91 GB. (b) is a cost measurement, so it must not share a GPU.
