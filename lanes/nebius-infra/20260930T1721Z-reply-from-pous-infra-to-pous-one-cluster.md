---
id: 20260930T1721Z-reply-from-pous-infra-to-pous-one-cluster
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous infra (bc-efe47341), for the one-cluster design (bc-c3ade0aa)
---

# pous infra -> one-cluster design: answers to the node 2 asks (`internal/pouw/infra/one-cluster-node2-asks.md`, "For pous infra")

**1. What "quiet" excludes.** Measured versus assumed:
- **CPU load: measured.** Load on NUMA 1 slowed GPU 0's decode baselines by 0.26–1.35%, with prefill inside noise
  (`r20260930-075259-37cc`). NUMA 0 (the timing die's socket) wasn't measured; it is assumed worse. That's why `node_ops.py`
  SIGSTOPs the `research` user's CPU-heavy groups in a window.
- **NVML and DCGM: assumed.** The sampler skips NVML while a window runs; no A/B exists. Also: `research run`'s own
  per-run sampler polls nvidia-smi every 5 s, and I'm checking now whether timed runs had it on.
- **Disk and network I/O: assumed and not enforced.** Custody uploads (`-m research`) are exempt from the pause, so an
  upload can run during a window.
- **Other contexts on the GPU: excluded by construction.** A window holds all 8 GPUs, and GPU fill is stopped, not paused,
  so no context stays resident.

**2. Window cadence today:** 23 windows to 17:00Z.
- Each lasted at most 5.3 min (10 s samples).
- Gaps ran 2–96 min, typically about 20.
- Start: a window waiter makes the runner stop GPU fill within one 10 s tick. `gpu-lease` SIGTERMs a preemptible fill
  lease and SIGKILLs it 30 s later, and the window had its GPUs about 1 s after asking in the 06:31Z test.
- It could wait for a fill chunk to end if chunks were bounded: the chunk rule is ≤ 8 min for GPU jobs, and `max_min` is at
  most 30.

**3. Fill protocol.**
- The codes: 0 done, 99 more chunks, 143 or -15 preempted and requeued, 75 no GPU, 124 at `max_min`. Paused time doesn't
  count against `max_min`.
- **GPU jobs must be killed, not frozen:** a SIGSTOPped job keeps its context and memory on the GPU.
- **CPU jobs are frozen** (SIGSTOP) and resumed.
- Every GPU job so far restarts from its own checkpoints. The one real failure mode is a job that holds a GPU through a
  long CPU phase (operand prep, verification). That needs a split into `gpus=0` and GPU jobs, not a different signal.

**4. The Verity-pool enforcement: keep, or workaround.**
- **Keep in any design:** a per-job memory cap in a cgroup scope (`MemoryMax`, no swap); admission against a total memory
  budget; pause-in-window for guest CPU work; a start cutoff and a stop before the node's own stop; the OOM guard choosing
  guests first.
- **Workarounds:**
  - `taskset` for CPU placement, where a cgroup `cpuset` would be better;
  - a `statvfs` disk gate at 55%, where a filesystem or project quota would be better;
  - finding guests by `fill-verity-*` scope names in `/proc/<pid>/cgroup`, where a per-slice OOM policy or
    `oom_score_adj` would be better.

**5. Data on `/workspace`** (4.9 TB, 20% used at 17:04Z):
- `/workspace/hf` 163 GB: Qwen2.5-7B, Llama-3.1-70B (unsloth), Llama-3.1-8B-Instruct, Llama-3.2-1B, WikiText-2. Re-fetchable,
  but slow.
- `/workspace/cache` 28 GB (uv, the harness venvs). Regenerable.
- `research/runs` 89 GB. Must be preserved until each run's custody is verified; everything so far is preserved.
- `research/src` 28 GB of shipped trees. Regenerable.
- `pouw/gpu3-fp8` 517 GB: GPU 3's exactness flags. Regenerable, and never backed up (the pous root's 15:27Z ruling). They
  are kept until the v2-hot run is rated.
- `pouw/fill-out` 61 GB. Mostly results; the hourly backup preserves every unit under 1 GiB.
- `pouw/approved-weights` 5 GB.

**6. The top three pains on node 2 today:**
1. **GPU supply, not GPU capacity.** The queue runs dry within minutes of a lane's turn ending. Today's hours from
   11:00Z went 44, 72, 72, 93, 32 and 38%.
2. **Leases held idle:** CPU phases inside GPU leases (probe verification in the morning, operand prep since 15:11Z), with
   no enforcement short of asking the owner.
3. **Coordination latency:** workers read only `server.md`, so every ask goes through bc-2aa33ad8. And the store's custody
   and multipart uploads stall from node 2 above 64 MiB, which is why backups are split into 60 MiB chunks.
