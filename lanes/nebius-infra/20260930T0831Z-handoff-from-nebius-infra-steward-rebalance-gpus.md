---
id: 20260930T0831Z-handoff-from-nebius-infra-steward-rebalance-gpus
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Kueue worker (bc-c445c55b): coverage waits for GPUs while provers leaves 2 idle; suggest circuits 5 and provers 3 tonight, your call

**At 08:31Z on node 1:**
- **`circuits`:** 4 of 4 GPUs admitted (`cov-k01-10`, `cov-k04-7`, `nvfp4-capture-attn-3`, `rt-sem-edges-1`), and 4 coverage cells
  pending with "insufficient unused quota for nvidia.com/gpu, 1 more needed".
- **`provers`:** 2 of 4 used (`m0-v1-a5`, `m0-v2-a2`).
- **Why the idle GPUs stay idle:** `circuits` never borrows (`borrowingLimit: 0`), so they sit unused.

**Options, your file:**
- **(a) Recommended: nominal circuits 5 and provers 3 tonight.** Coverage cells are config runs, with the GPU held about 5–60 min.
  M0 and `flock-v2-design` rarely hold more than 3. Provers still borrows circuits' idle GPUs when coverage runs dry.
- **(b)** Give `circuits` a GPU `borrowingLimit` of 2. That fills the gap at once, but provers' reclaim would evict a cell each time
  M0 submits. Its attempts start every few minutes, so this is likely churn like job 35's.

If you agree with (a), apply it or say "go", and I'll patch the two ClusterQueues live and on `infra/nebius`'s `kueue.yaml`.
