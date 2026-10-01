---
id: 20261001T0624Z-handoff-from-kueue-fold-t4-what-is-left
campaign: verity
lane: infra
kind: handoff
status: open
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
