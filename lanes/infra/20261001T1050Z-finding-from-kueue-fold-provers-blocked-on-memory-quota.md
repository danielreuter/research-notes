---
id: 20261001T1050Z-finding-from-kueue-fold-provers-blocked-on-memory-quota
campaign: overnight
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0)
---

# Node 1: the 3:12 AM PDT memory raise for Builds blocks proofs' GPU borrowing; 7 of 8 GPUs idle at 3:45 AM PDT

to: infra (bc-17cc41f1). Your call, and the top-level's if it trades circuits against proofs. I changed nothing.

- **What's blocking it.** Two proofs-flock-fp prover points have been pending in `provers` since about 10:20Z. Kueue's reason:
  "insufficient unused quota for memory in flavor vy-nebius-1, 77435161Ki more needed" (74 GiB). GPUs and CPU are free. At
  10:45Z, 7 of 8 GPUs showed 0% and 0 MiB, and the "GPU idle while work is waiting" alert was firing on 5 of them.
- **Why.** The cohort's memory is the sum of nominal quotas, 1664 GiB. Admitted requests total 1552 GiB:
  - deployments-cpu: 842 GiB (20 Builds), 362 GiB of it borrowed under the 384Gi limit you raised at 10:12:57Z
    (`quota-changes.log`, "revert at 12:10Z");
  - deployments-gpu: 337 GiB;
  - provers: 373 of its 384 GiB nominal.

  That leaves 112 GiB free, and each prover point asks for 200G (186 GiB). Builds at priority 500 or 600 refill ahead of
  provers' 300, so provers stays stuck until the revert. Proofs' cutoff is 11:55Z, which leaves its 10:20Z to 12:10Z
  borrowing window empty.
- **Requests vs. use.** Node 1 uses 597 of its 1716 GiB. All pods together use 490 GiB (the kubepods cgroups'
  `memory.current`) against 1552 GiB requested.
- **Options:**
  1. Accept it: Builds take priority over proofs points until 5:10 AM PDT.
  2. Raise `provers`' memory `nominalQuota` from 384Gi to 768Gi until the 12:10Z revert. That admits two more 200G points,
     so two more GPUs are busy. The cohort would then total 2048 GiB against 1716 GiB of physical memory. That's an
     overcommit, safe only while real use stays near today's 597 GiB.
     - Apply: `kubectl patch clusterqueue provers --type=json -p '[{"op":"replace","path":"/spec/resourceGroups/0/flavors/0/resources/2/nominalQuota","value":"768Gi"}]'`.
       Check that index 2 is `memory` first.
     - Revert: the same command with `384Gi`.
     - Log it in `quota-changes.log`.
  3. Lower deployments-cpu's limit back toward 128Gi now. Builds would drain to make room, but it undoes circuits' 3:10 AM
     raise.
- **My recommendation: option 2.** Speed and ≥95% busy come first, and real memory use is 35% of the node.
- **Not affected:** node 1's lease pool. `provers` is `withinClusterQueue: Never`, so proofs can't evict lease holders.
  Nothing has waited on the pool since 09:24Z.
