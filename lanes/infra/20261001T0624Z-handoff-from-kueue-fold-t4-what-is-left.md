---
id: 20261001T0624Z-handoff-from-kueue-fold-t4-what-is-left
campaign: verity
lane: infra
kind: handoff
status: done
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), answering the infra coordinator's 10:53 PM PDT message
---

# kueue-fold at 11:24 PM PDT: T4 is two merges from done; every item from 2302Z is answered

## T4: node 1 on the central scheduler, with process-level leases (noon PDT)

**Live on node 1 now (no further node change needed):**
- `n1_lease.py` (`infra/nebius` `a98736cbd`) runs in tmux `n1-lease`, every 5 s.
- It lends GPUs held by Kueue holder pods in `provers`, through node 1's own gpu-lease on `/run/gpu-lease`.
- It grows only within `provers`' unborrowed nominal quota, so it never takes a GPU from `deployments-gpu`. It sends SIGTERM
  to a host-process lease that has expired or sits outside the pool.
- Host smoke test, 11:13 PM PDT: the holder grew, GPU 5 was unfenced, torch saw one device, the job exited with rc 0, and the
  pool shrank at 11:15 PM PDT.

**Left, and whose move:**

1. **Review `cursor/n1-gpu-executor-9bf0`** (`6a3c05f76`, `8654a3b97`; 116 tests pass). Move: cluster-build
   (`note:20261001T0622Z-handoff-from-kueue-fold-n1-executor-branch-review`).
   - `cluster submit` wraps a node-1 GPU job in node 1's gpu-lease.
   - The switch is a description key, `gpu_executor = "n1-lease"` on vy-nebius-1. Without it, a node-1 GPU job is refused,
     as today.
   - A timed job is never sent to node 1.
2. **Merge it.** Move: the research coordinator, through `research merge` with a passing `check`. This is the blocker.
3. **The cutover: a one-line PR adding the key to `tools/cluster/descriptions/nebius.toml`.** Move: mine, once item 2
   lands.
   - *Changes:* only the description, which each submitter's own `--source` tree reads. No live node config changes.
   - *Before:* the `n1-lease` loop is up with no errors in `/workspace/verity-guest/n1_lease.out`, and `provers` has free
     nominal quota.
   - *After:* one 1-GPU `research run --queue` to vy-nebius-1 runs and leaves `delivered`, and the pool shrinks after it.
   - *Rollback:* revert the PR. Trees already checked out with the key still submit until they update. A job already
     running keeps its lease until it ends.
4. **Optional, not needed for T4:** the cluster agent's grants of node-1 leases (`VY_LEASE_BRAIN`). The contract is still
   unanswered (`note:20260930T2233Z-handoff-from-kueue-fold-node1-lease-grant-contract`). Move: cluster-build.

## The items from 2302Z

- **backend-sweep-2's leases:** moot. The lane has been stopped since 3:51 PM PDT. Its chunks at 0% were the loopback
  verifier, not hangs.
- **n2-commits' rc 12 replays:** fixed in the template (`dfe17f6aa`, live 11:04 PM PDT). The replay exits 0 when the
  Commit's verdict has no `replay_deferred`. Reply: `note:20261001T0620Z-reply-from-kueue-fold-rc12-fixed`.
- **node2-ops' OOM:** g080's Builds are a mixture-of-experts model. `n2_build.sh` (`3dd19c6a1`) now gives such repos
  256 GiB. g080-r1 is requeued at that size, g084 is moved to `done/`, and cov-m004-2 is cancelled. A finished item now
  leaves a `.done` record, so a stale rerun exits 0 (`c332e1685`). Deployed on both nodes.
- **node2-ops' lending deployed off:** acknowledged; nothing for me to do.
- **vllm-epoch-run's 3 duplicate Gemma Builds:** answered. Their leftovers are vllm-epoch-run's or circuits' call.
- **circuits #572's manifest digests:** waiting on circuits. I'll add the mixed-pair refusal (a Build's tree commit must
  equal its Commit's) when #572 is close to merging.
- **The storage plan's `ephemeral-storage` quota: not applied, because it is the wrong resource.**
  - Node 1's `ephemeral-storage` allocatable is about 234 GiB, the root disk.
  - The bundles live on `/workspace`, a 4.9 TB hostPath (31% used) that kubelet doesn't count. The planned 2 TB of
    nominal quota would schedule against 234 GiB.
  - Proposal for the morning, with the steward: an extended resource the node advertises (for example
    `verity.dev/workspace-gb`, by a node status patch), which the queues cover and the templates request.
  - Nothing is pending in any queue, so "replays ahead of Builds" has nothing to reorder tonight.

## Seen in `lanes/infra/`, not mine, for routing

- **The drift reference:** node 1's dispatcher copies of `cluster_up.sh` and `quiet_hour.sh` are older than `infra/nebius`.
  Move: node1-dispatcher.
- **The live patch letting `provers` borrow 6 GPUs**
  (`note:20261001T0608Z-note-from-nebius-infra-provers-borrow-patched-live`): not mine. `n1_lease` reads only the nominal
  quota, so it isn't affected either way.
- **proofs-bf16-hill's CPU confinement** (`AllowedCPUs` on `user.slice` and `system.slice`): a live node change. It needs
  a cutover plan, and Daniel's word if he wants it. I can draft the plan if you assign it to me.
  - Until it lands, I'm not moving node 2's CPU backlog onto node 1
    (`note:20261001T0340Z-alert-from-nebius-infra-both-nodes-out-of-gpu-work`), since that would add foreign load to the
    prover slices.
- **console's overnight numbers** (`queue`, `quota-cutover`): infra's to fill in. For T4, the state as of now is "executor
  live, waiting on merge".

The 30-minute timer stays on until the cutover PR lands.

## Addendum, 12:25 AM PDT: T4 is one merge from done

- **cluster-build approved the executor** (`note:20261001T0701Z-reply-from-cluster-build-n1-executor-review`). The
  cutover is on the same branch as `fa9f02ab4`, so merging [#645](https://github.com/danielreuter/verity/pull/645)
  (`cursor/n1-gpu-executor-9bf0`) is T4. It merges cleanly onto `main` `4e2a7abcd`. Move: the research coordinator, a train
  with `check`.
- **Node 1 takes pinned GPU jobs only** (`--on vy-nebius-1`). The submit path can't see node 1's lease pool, so an unpinned
  job still goes to node 2, as today. Live routing is cluster-build's follow-up.
- **The capacity is small:** `provers`' unborrowed nominal quota, 2 GPUs less provers' own Workloads. bf16-hill's two
  benches held both at 12:20 AM PDT.
  - The lever is letting holders borrow for `--preemptible` jobs, which a Commit could then reclaim mid-lease. That changes
    agreed semantics (`a98736cbd` keeps holders unborrowed), so it is for you, or for Daniel.
- **After the merge:** I run the post-check from the plan, one pinned 1-GPU `research run --queue`, once `provers` has a free
  GPU.

## Addendum, 1:20 AM PDT: the 1:02 AM PDT ruling runs on node 1's lease pool

- **The ruling's literal path was blocked.** Plain `gpu-lease --on 0` or `--on 2` on node 1 waits on `n1_lease`'s fences. It
  would also risk Kubernetes putting a Commit pod on the same GPU.
- **Instead:** `n1_lease` `025260083` is live since 1:16 AM PDT, with `VY_POOL_BORROW=2` until 5:10 AM PDT
  (`note:20261001T0825Z-draft-from-kueue-fold-n1-borrowed-leases-cutover`).
  - Holders borrow up to 2 GPUs, only for `--preemptible` waiters, and a Commit's reclaim stops the lease: SIGTERM through
    its scope, then SIGKILL.
  - The post-check passed: a lease on GPU 1, rc 0.
  - The claimants were told how to use it (`note:20261001T0820Z-handoff-from-kueue-fold-node1-gpus-how`).
- **[#645](https://github.com/danielreuter/verity/pull/645)** is at `7714e0021`, with your merge of `infra/nebius` and #496's
  `provers` pool. It is ready, and its merge is still T4.

## Addendum, 7:19 AM PDT: T4 is done

- **[#645](https://github.com/danielreuter/verity/pull/645) merged** at 5:40 AM PDT in TS2 (main `da9a9cfef`), with
  `gpu_executor = "n1-lease"` and the pinned-only rule.
- **The post-merge test passed.** `r20261001-141528-63f3` is one pinned 1-GPU `research run --queue --on vy-nebius-1
  --preemptible`, launched from main's tree. Its custody record is
  `art:6687c3c5c1e80ccd80a7e76a5a3ec78a18a492f3cf82039b2d47b66a3036ef11`.
  - The queue placed it on node 1 ("starts now, owner's node").
  - The runner ran in its own systemd scope with `taskset -c 96-127` and `MemoryMax=2G`.
  - `n1_lease` grew a holder at 14:15:40Z and unfenced GPU 2 at 14:15:48Z.
  - `gpu-lease` granted GPU 2 (`CUDA_VISIBLE_DEVICES=2`), and the job exited rc 0, class SUCCESS.
  - The holder shrank at 14:17:53Z, after the 120 s idle window.
- **A run that didn't count:** `r20261001-134656-9fb7` was refused on the machine side. My launcher was this VM's stale
  snapshot, which didn't know `--question` and forwarded it without `--queue`. Main's own launcher doesn't do that.
- **What I held back:** I submitted only once 2 or more cohort GPUs were free. While `deployments-gpu` borrows `provers`'
  nominal GPUs, a lease holder reclaims one (`provers` is `reclaimWithinCohort: Any`) and evicts a running Commit. That's
  the same as a proofs Kueue job, and it's queue policy, not a bug, but it matters for who uses the pool.
- **Still open, all yours:**
  - `note:20261001T1215Z-ask-from-kueue-fold-node1-queue-switch-pool-cap`: the pool grants at most `provers`' unused
    nominal GPUs, so the dispatcher's GPU stages shouldn't move onto it.
  - `note:20261001T1050Z-finding-from-kueue-fold-provers-blocked-on-memory-quota`.
  - Node 1's `gpu-lease` records no busy samples ("busy 0m00s of 0m00s sampled").
  - Lease borrowing (`VY_POOL_BORROW`) is off since 5:10 AM PDT. Turning it back on is a restart of the `n1-lease` tmux
    session with new variables.
- My 30-minute timer is unsubscribed.
