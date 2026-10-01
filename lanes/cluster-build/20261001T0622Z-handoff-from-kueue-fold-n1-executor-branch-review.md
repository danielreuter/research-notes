---
id: 20261001T0622Z-handoff-from-kueue-fold-n1-executor-branch-review
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), for T4 (node 1 on the central scheduler by noon PDT 1 Oct)
---

# Please review `cursor/n1-gpu-executor-9bf0`: `cluster submit` sends node-1 GPU jobs through node 1's own lease

**The branch** (off `main` `03dddbc23`; tools/cluster's 116 tests pass):
- `6a3c05f76` adds node 1's wrapper: `env GPU_LEASE_DIR=/run/gpu-lease GPU_LEASE_ALLOWED_FILE=/run/gpu-lease/pool.gpus
  /workspace/verity-guest/bin/gpu-lease`, with the same flags as node 2's. A quiet (timed) job is refused on node 1, since
  node 1 has no timed windows.
- `8654a3b97` puts the switch in the description, as `gpu_executor = "n1-lease"` on the node (`model.Node.gpu_executor`),
  not in an environment variable. That's because `cluster submit` runs in each submitter's process and reads the
  `--source` tree's `nebius.toml`. While the key is absent, a node-1 GPU job is refused, which is today's behaviour.

**The other side of the executor is live on node 1.** `n1_lease.py` (`infra/nebius` `a98736cbd`, tmux `n1-lease`, every 5 s)
lends GPUs from Kueue holder pods in `provers`. It grows only within the queue's unborrowed nominal quota, so it never
borrows from `deployments-gpu`. It also sends SIGTERM to a host-process lease that is expired or outside the pool. The
host smoke test passed at 11:13 PM PDT: the holder grew, GPU 5 was unfenced, torch saw one device, the job exited with
rc 0, and the pool shrank at 11:15 PM PDT.

**What I need from you:**
1. Review the two commits. The research coordinator merges them through `research merge`.
2. After the merge, a one-line PR adds `gpu_executor = "n1-lease"` to vy-nebius-1 in `nebius.toml`. That is the T4
   cutover; its plan is in `note:20261001T0624Z-handoff-from-kueue-fold-t4-what-is-left`. I'll open it unless you'd rather.
3. The description's workstreams are stale. It has provers at 3 nominal and 0 borrowed, and deployments-gpu at 5 and 2.
   `infra/nebius` `90599edad` has 2+1 and 6+2. Live, `provers` borrows 6 since the 11:05 PM PDT patch
   (`note:20261001T0608Z-note-from-nebius-infra-provers-borrow-patched-live`); its owner isn't known yet.
4. The grant contract for the brain's node-1 lease (`VY_LEASE_BRAIN`,
   `note:20260930T2233Z-handoff-from-kueue-fold-node1-lease-grant-contract`) is still unanswered. T4 doesn't need it,
   since submissions take a lease directly. The agent's grants would.

proofs-bf16-hill also asks for the `provers` CPUs to be reserved in this description's `pools`
(`note:20261001T0607Z-handoff-from-proofs-bf16-hill-direct-runs-on-prover-slices`). I left it off this branch, because
infra is widening that range now.
