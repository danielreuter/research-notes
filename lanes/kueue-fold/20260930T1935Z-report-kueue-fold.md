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

## Log

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
- 19:47Z **step 3 ready; blocked on node 2's Verity pool.**
  - Node 2's staged runtime works: Python 3.12.14, torch 2.13.0+cu129, vLLM 0.28.1rc1 (an import at nice 19 on CPUs 48–95).
  - `n2_build.sh` is on `infra/nebius` (`df77cc6b2`). `submit` (node 1) stages the tree, checkpoint and stamps, then queues a
    `project=verity` fill job. `run` (node 2) does the Build with node 1's paths, sends the row and run back, publishes the Attempt into
    node 1's store, and submits the Commit with `dispatch.py submit config-run n2-build/KEY --task 1`.
  - HF: node 2 uses `HF_HOME=/workspace/jobs/hf`, and node 1 now has `/workspace/jobs/hf -> /workspace/hf`, so recorded paths resolve on
    both nodes. I dropped the bind mount: sudo's `use_pty` would put the Build outside the process group that the fill runner's
    SIGSTOP reaches.
  - The live `fill_runner.py` (`7444de9f`) runs Verity CPU jobs only when no PoUW CPU job is queued, and PoUW has 22 queued. The proof
    waits for node2-ops' deploy of the Verity pool (CPUs 48–95).
- 19:40Z **steward's reply** (`note:20260930T1940Z-reply-from-nebius-infra-steward-fold-constraints`):
  - Keep k3s and Kueue on node 1 as a capacity-only runtime: one `node1` ClusterQueue, with no cohort and no borrowing. The central
    scheduler submits batch Jobs and picks the priority.
  - `kueue.yaml`'s priorities are policy.
  - Gap: Kueue pods float onto the check-slot CPUs 8–95.
- 20:03Z **checkpoint.**
  - Node 1: 1.8% GPU busy over 20 min. All 8 GPUs are held: 6 Commits (about 50 of 96 GB each), M0 on GPU 6, one sweep. The GPUs
    are RTX PRO 6000 Blackwell (sm_120), the same as node 2's.
  - Co-location, for backfill guests on a held but idle GPU: vLLM's `gpu_memory_utilization` is a fraction of total memory, and each
    Commit phase starts a new engine. So a guest can't change a running Commit's KV cache; it can only make a later phase fail to
    start. The guard is a guest cap of 20 GB and killing the guest when the owner's process set changes.
  - PoUW's running GPU jobs (e.g. `hsplit-*`) are clock-locked timing screens, so they can't co-locate. I've asked PoUW for untimed
    jobs (`note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`). The runner gets built when one is named, not before.
  - Step 3 is still blocked on node2-ops deploying `ce30461ac`.
- 20:12Z **node 2's Verity pool is live**: node2-ops deployed `ce30461ac` at 20:08:24Z (runner sha `4a122904`, byte for byte the
  commit). `n2_build.sh submit` now takes the config-run item a lane gives `dispatch.py`, so the Build and its Commit get exactly the
  item's envs and resources (`infra/nebius` `918e02426`). A node-2 Build's `MemoryMax` is 3× its node-1 request, in 64–256 GB
  (`d7c40c559`): node 1 only requests, and Builds have used 2–3× that.
  - **Proof Build submitted:** epoch-run's `cov-g188` (Llama-3.2-1B, whose Build passed on node 1 in 225 s), rebuilt in its own sweep
    dir `/workspace/jobs/n2proof/cov-g188`, campaign `kueue-fold-n2-proof`. Its Commit goes through node 1's dispatcher at the
    item's own priority, behind epoch-run's queued Commits. Comparing the two Builds' outputs is a free reproducibility check.
- 20:10Z **step 4 first slice:** `tools/cluster/src/cluster/nebius1.py` on `cursor/node1-observer-9bf0` (`f21e5a747`, off #586).
  It reads node 1's Kueue pods, Workloads and DCGM GPU-to-pod labels as the model's allocations and queue, and plans beside Kueue.
  All 8 GPUs are attributed. The first divergence went to cluster-build
  (`note:20260930T2010Z-handoff-from-kueue-fold-nebius1-observer`).
- 20:08Z steward: sweeps in `provers` aren't policy, so they move to `backfill`. I asked backend-sweep-2 and assumption-sweeps to
  write their items that way. Co-location has his four conditions; the exporter work is on hold until PoUW names an untimed job.
- 1:37 PM PDT **checkpoint.**
  - **Step 3 is live.**
    - The proof Build ran on node 2 and matched node 1's digests.
    - Its return path failed once: uid 1000 couldn't read research's home when `uv` looked for `uv.toml`. Fixed (`1611d11cd`).
    - Custody now goes through a one-off pod holding `research-r2` (`fe001669a`): 8 of 8 preserved.
    - Node 2 cleans up after the return (`19d1e8c6c`).
    - The script lives at `/workspace/verity-guest/bin/n2_build.sh` on both nodes, and `submit KEY -` reads the item from stdin.
    - Told vllm-coordinator (`note:20260930T2025Z-handoff-from-kueue-fold-builds-on-node2-how-to-submit`) and infra.
    - The proof Commit `nd-n2-build-5cfa1ffd77-gpu-0` is 7th of 10 pending in `deployments-gpu`.
  - **Step 4:** cluster-build's interface is accepted, and the observe half is a pull, `nebius1 --report` (`f7f9b5ca7`). The act half
    comes after node 2's agent and the `research run` path (infra's order).
  - **Measured:**
    - Node 1: GPU 1.6% busy over 1 h (DCGM), CPU 27.7%.
    - Node 2: GPU 61% util over 30 min (node2-ops' sampler), CPU 15% (10 s).
  - Asked PoUW for CPU overflow onto node 1 too (`note:20260930T2037Z-handoff-from-kueue-fold-node1-cpu-overflow-too`).
