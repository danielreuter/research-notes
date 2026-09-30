---
id: 20260930T1935Z-report-kueue-fold
campaign: verity
lane: kueue-fold
kind: report
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), worker of the infra coordinator (bc-17cc41f1)
---

# kueue-fold: one pool: the vy-cluster key, node 1's idle GPUs, Verity Builds on node 2, and folding Kueue into the central scheduler

## Log (newest first)

- 19:35Z **step 1 live: `vy-cluster`.** An ed25519 key pair generated on node 1 as `research`, fingerprint
  `SHA256:oEAMog9bDv2d4vAXnrUr47DYkCmeOGjeISRIFD6fOeg`. The private key is at `~research/.ssh/vy-cluster` (mode 600) on both nodes,
  copied node to node with scp. The public key, commented `vy-cluster`, is in both nodes' `authorized_keys`, and the old files are
  kept as `authorized_keys.bak-20260930T1930Z`. Both nodes' `~/.ssh/config` gain `vy-n1` (10.80.0.18) and `vy-n2` (10.80.0.42).
  Tested: `ssh vy-n2` from node 1 and `ssh vy-n1` from node 2 both work.
- 19:30Z **baselines.**
  - Node 1: 1.0% GPU busy over the last hour (DCGM `GR_ENGINE_ACTIVE`), 0.8% over 3 h and 6 h; 34% CPU busy over 1 h.
  - Node 2: about 85% GPU utilization (nvidia-smi, a 10 s sample; node2-ops' hourly figure for 18–19Z is 78% busy); 37% CPU busy
    (5 s); RAM 68 of 1,716 GiB used.
- 19:30Z **finding: node 1's idle GPUs are not a quota problem.** All 8 GPUs are reserved (`deployments-gpu` 5/5, `provers` 3/3,
  plus one `circuits` pod on borrowed quota), and `backfill` can already borrow any unreserved GPU and is evicted first. The GPUs
  are held by work that doesn't use them:
  - **Commits:** 4 pods at 0–5%, each holding about 52 of 96 GB of GPU memory while one CPU core runs its replay for 15+ minutes.
    This is the in-pod CPU replay that PR A/B defers.
  - **Dispatcher sweeps:** 3 pods in `provers` at priority 100 (not `backfill`), each at about 2%.
  - **circuits:** the TP2 deferred pod, at 10%.
