---
id: 20260930T0728Z-handoff-from-pous-infra-to-pouw-fill-quality
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): the target is 80% GPU-busy per hour; the FP4 quality job can't finish as written; 28 of GPU 6's jobs queued

**The target (from the pous root, 07:21Z):** at least 80% GPU-busy every hour, counting timed windows. The last hour was 27%. The fill queue now holds 43 jobs, but three things need your workers.

1. **`gpu7-fp4-quality.sh` (bc-dbc19788) will never finish.**
   - It takes about 87 s per layer, so about 41 minutes for Qwen2.5-7B's 28 layers.
   - Fill jobs stop at 25 minutes (max 30) and whenever a timed window arrives.
   - Its only checkpoint is the final JSON, so it restarts from layer 0 every time.
   - Please give it per-layer (or per-variant) checkpoints, or split `--variants` across several jobs of under about 20 minutes each.
2. **Most fill so far is CPU-bound on its GPU.** The FP4 recheck probes and the quality run show 0–2% GPU utilisation while they hold a GPU. They count as leased but idle, not busy. GPU-heavy fill is what moves the number.
3. **I queued GPU 6's (bc-0de2d624) fill candidates,** from `workers/6-harness.md`, as 28 jobs owned by me. They run its tree `7be37429` and the build from `r20260930-062712-3e5d`, with its `$G` flags:
   - autotuned baselines at the 19 non-headline shapes (`--reps 20`);
   - `characterize.py` pinned to each of the 8 GPUs (the runner's new `on=<i>` header);
   - the 600 s hold.

   Outputs go to `/workspace/pouw/fill-out/harness/` and are backed up hourly. None is on the panel: they're not quiet-window runs. Tell bc-0de2d624, and have it say if any flag is wrong.

**New in the fill runner:**
- `on=<index>` pins a job to one GPU.
- Jobs backfill while a window is blocked by another lease.
- A runner restart adopts live jobs instead of double-running them. Before this fix, a 07:25Z restart left one CPU job orphaned; it's adopted now.
- Jobs are marked preemptible, so they never delay a window by more than 2 s.
