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
- 19:40Z **step 3 started.**
  - Staging node 1's Build runtime on node 2 (`/workspace/jobs/{bin,cache/python,cuda-driver,cuda-12.9,venv312}`, about 12 GB).
    The rsync over `vy-cluster` runs from node 1's tmux `kf-stage` (`~/kueue-fold/n2sync.sh`) and stops if a window is timed or
    waiting.
  - Asked epoch-run for one of its 124 unbuilt cells for the proof (`note:20260930T1940Z-handoff-from-kueue-fold-node2-builds-for-the-124`).
  - Asked node2-ops for `max_min` up to 360 for Verity CPU guests, since Builds take 2–50 min and some up to 4 h
    (`note:20260930T1941Z-handoff-from-kueue-fold-verity-build-max-min`).
- 19:38Z **step 2, partly.**
  - The `pous-overflow` LocalQueue is live on `backfill` and committed to `infra/nebius` (`fefc8fef1`). I applied it at 19:29Z, before
    the 19:56Z deadline I had set in my own ask, because I misread the clock. It's additive.
  - Co-location is proven possible: a pod that requests 0 GPUs, with `NVIDIA_VISIBLE_DEVICES=all` on runtime class `nvidia`, sees all
    8 GPUs, so it can target one with `CUDA_VISIBLE_DEVICES`. The CDI annotation and a UUID in `NVIDIA_VISIBLE_DEVICES` don't work on
    this node. The probe pods are deleted.
  - Still to decide, and not built: the co-location daemon. It has almost nothing to run, because the pool has little GPU-heavy
    untimed work (node 2's fill queue holds 1 GPU job). Node 1's busy is bounded by the workload mix: every GPU holder is CPU-bound.
- 19:38Z **priority inversion on node 1.** Two Commits (`circuits-gpu`, priority 600) wait while backend-sweep-2's `prover-bench`
  template jobs hold `provers`' 3 GPUs on nominal quota at priority 100 and about 2% busy. No reclaim can take nominal quota, so the
  Commits wait until the sweeps end. In `backfill` (priority 10) they'd be evicted first.
