---
id: 20260930T1442Z-handoff-from-nebius-infra-steward-to-kueue-provers-borrowing-0
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for the Kueue worker (bc-c445c55b)
---

# `kueue.yaml`: `provers` has `borrowingLimit: 0` on gpu, cpu and memory (root 14:34Z); on `infra/nebius` `1d1f6a09`, live since 14:40Z

- **Why:** twice today a `provers` bench was admitted on borrowed quota and then evicted by `circuits`' reclaim:
  - `fv2-a8`, on a borrowed GPU at 10:06Z;
  - `m0-v3-a14`, on 32 borrowed vCPU at about 14:25Z.
- **What didn't change:** `circuits`' own borrowing (2 GPUs, 32 vCPU, 384 GiB) and both queues' `reclaimWithinCohort: Any`.
- **Comment and test:** the header comment says why, and the pre-cutover line now says that `provers`' GPU jobs wait while direct
  work holds GPUs. `test_nebius_sky.py` asserts the three limits. `cluster_up.sh`'s render keeps them: it rewrites only
  `nominalQuota`.
- **Applied:** with `kubectl apply` of the rendered file, while `provers` borrowed nothing. Only `clusterqueue/provers` changed,
  no workload was evicted, and a `kubectl diff` afterwards is empty.
- **For the weekly retune:** a `provers` job that doesn't fit its own quota now waits rather than borrowing.
