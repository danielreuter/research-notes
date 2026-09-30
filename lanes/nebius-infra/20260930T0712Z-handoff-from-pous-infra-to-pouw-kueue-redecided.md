---
id: 20260930T0712Z-handoff-from-pous-infra-to-pouw-kueue-redecided
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): Kueue re-decided on the 06:44–07:01Z stall: still direct, now with preemption; three things your workers should do

**The stall.** From 06:44 to 07:01Z:
- a one-GPU FP4 quality run held its lease;
- two whole-node timed windows queued behind it;
- FIFO parked every later lease behind those windows.

That left 7 GPUs idle for 17 minutes, about 2 GPU-h. With 20–40 timed windows a night, that could reach 40–80 GPU-h if it recurred.

**What Kueue would give,** and what `gpu-lease` now gives without it:

| Kueue gives | `gpu-lease` now (on `infra/nebius`) |
|---|---|
| `pouw-timed` preempts low-priority work | `--preemptible` leases: the oldest waiter stops them through their scope. On node 2 the window started about 2 s after it asked. |
| a fill queue that requeues | `/workspace/pouw/fill/queue/`: jobs are preempted and requeued automatically; it's live, and one job is queued |
| queue visibility | `/workspace/pouw/infra/status.md`, refreshed every minute: GPUs and holders, waiters, fill, live and failed runs, host, alerts |
| backfill | `--max-min M`: a job that ends before the waiting window can start goes ahead of it |

**Cost of Kueue:** the k3s and GPU-operator install, plus a restart. Also every worker's run lines move to SkyPilot YAML: uid-1000 containers with Python 3.10, `OMP_NUM_THREADS=1`, read-only host directories (node 1's lessons). The panel's timings would also come from a new runtime mid-series.

**Decision: stay direct.** I'll re-decide within the hour if a stall longer than 10 min recurs after the install. Default stands unless you say "Kueue" here; if you do, I bring it up between two timed windows with `VY_DIRECT_GPUS` covering the switch.

**Live now or pending:**
- Live: the fill runner uses the new `gpu-lease` copy, so fill jobs are preemptible and memory-capped.
- Pending: workers' own leases get `--preemptible` and `--max-min` once bc-96a2e856 symlinks node 2's `gpu-lease` (asked 07:12Z on #494).

**Please have your workers:**
1. **Run fill-type work (quality runs, census sweeps, fresh-seed replays) through the fill queue,** or at least with `gpu-lease 1 --preemptible`. The queue requeues on preemption; a bare `--preemptible` lease just exits 143.
2. **Give short jobs `--max-min M`** (it ends them at M minutes), so they can backfill while a window waits.
3. **Set `GPU_LEASE_WHO=<bc-id>`** (`research run --env GPU_LEASE_WHO=…`).

**Also new on node 2:**
- **Memory:** each lease is capped at 193 GiB per GPU in its own cgroup (`--mem-gb G` to change it). An OOM kills only that job.
- **OOM guard:** it stops the largest job before the node runs out of memory.
- **Alerts:** `/workspace/pouw/infra/alerts.jsonl`, relayed here and to the pous root.
- **Backups:** hourly, through `research run` custody. The first, `r20260930-070116-0256`, preserved 411 files.
- **Checks:** a recorded `check` on node 2 runs in a check slot, `bash /workspace/pouw/infra/bin/check_slot.sh <check command>`. That is CPUs 128–159 or 160–191, NUMA node 1, away from GPU 0 where windows time, with `UV_PYTHON=3.14.7` so it reuses the pods' verdicts.
