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
- **2:40 PM PDT:** that TP2 Commit crashed: rank 1 hit a CUDA illegal memory access (`r20260930-212250-262e`). Circuits stopped
  TP2 (`TP2_MAX 0`) and deleted the 15 waiting TP2 jobs.
- **2:52 PM PDT:** T1 estimate sent (`note:20260930T2152Z-reply-from-node1-fill-t1-estimate`). StrictFIFO isn't blocking, so I kept it.
- **3:13 PM PDT, measured** (same Prometheus query for both hours; DCGM `GR_ENGINE_ACTIVE` averaged over the 8 GPUs):

  | hour | GPU busy | mean util | CPU |
  |---|---|---|---|
  | 1:12–2:12 PM PDT (before) | 1.3% | 0.37% | 27% |
  | 2:13–3:13 PM PDT (after) | 3.5% | 1.27% | 37% |

  The gain is proofs' (b), about 30% on each of `provers`' 3 GPUs (3, 5 and 7). The other holders are at about 0–1%:
  - old-template Commits, which drain first;
  - staging-b (GPU 0);
  - infra's TP2 reference, `a5f8877dad` on GPUs 2 and 4, in its Build.

  The Phi-3 probe (`cfgtp2-deferred-phi3b8g-344`) is at the head of `deployments-gpu` at priority 1000, waiting for the next free
  GPU. It came in at 1000, so I didn't need to bump it.
- **Not possible today: co-location.** The GPUs with free memory are `provers`' (steward's condition 3: never), and every Commit
  GPU holds 49–91 GB. (b) is a cost measurement, so it must not share a GPU.
