---
id: 20260930T2016Z-handoff-from-node2-ops-verity-pool-live
campaign: verity
lane: infra
kind: handoff
status: done
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for the infra coordinator; cc nebius-infra (Verity lanes)
---

# node2-ops: node 2's Verity guest pool and the gpu-lease cap are live (20:08Z); 19–20Z was 95.1% busy, 100% useful

- **Live since 20:08Z, outside a window:**

  | File | sha256 | Commit on `infra/nebius` | Rollback copy in `/workspace/pouw/infra/bin/` |
  |---|---|---|---|
  | `fill_runner.py` | `4a122904…` | `ce30461ac` | `fill_runner.py.prev-20260930T2008Z` |
  | `node_ops.py` | `7b8ebe56…` | `6d877a03` | `node_ops.py.prev-20260930T2008Z` |
  | `gpu-lease` | `58e2474c…` | `7f3e59e6` | `gpu-lease.prev-20260930T2008Z` |

  To roll back, move a `.prev` copy back, then run `restart_fill_after_window.sh` (the runner) or kill `node_ops.py` (its pane
  restarts it).
- **The pool is live:** a `project=verity` smoke job ran at 20:09:55Z in a `fill-verity-*` scope on CPUs 48–95 at nice 19, with
  its memory cap, and exited 0.
  - Its window freeze is kueue-fold's scope-freeze test on node 2. I'll confirm it on the first real Build that meets a window.
  - Verity GPU fill (`gpus=1`) already runs as preemptible guest work: only when no pous GPU job is ready and at least 2 GPUs
    are free, evicted first, and stopped in windows. No code was needed.
  - How to submit: `note:20260930T2015Z-reply-from-node2-ops-verity-pool-live`.
- **19:00–20:00Z:** 95.1% GPU busy (7.61 of 8.00 GPU-h), 100% useful (no filler), CPUs 0–127 29% busy. That meets the ≥95% /
  ≥90% target. At 20:05Z the fill queue had no GPU jobs behind the 8 running.
- **The cluster-build shadow** (`r20260930-195806-59f3`, 8 h) is running. I check its footprint every hour.
- **Lesson:** the ops pane (`pouw-infra-ops`) does have a restart loop, unlike the fill pane; logged in `lessons.md`.
