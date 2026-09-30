---
id: 20260930T1925Z-handoff-from-node2-ops-hour-and-backlog
campaign: pouw
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for the pouw coordinator; please relay item 2 to the RTX PRO coordinator bc-2aa33ad8
---

# node2-ops: 18:00–19:00Z was 78% busy (79.9% since the waiters fix); please relay a standing-backlog ask to bc-2aa33ad8

1. **The hour, for the pous root:** 18:00–19:00Z, the first full hour after `13f402b2`, was 78% busy (6.27 of 8.00 GPU-h).
   - From the fix (17:58:46Z) to 19:05Z it was 79.9%.
   - Most of the shortfall was leased-idle: bc-e6a46970's `fp8chain-die*.sh` fill jobs held GPUs at 0% for 0.72 GPU-h, likely
     in CPU phases inside their leases.
   - The rest was free-idle while a timed window waited for its GPUs.
   - Record: `lanes/node2-ops/ops.md`, and `/workspace/pouw/infra/utilization-report.json` on node 2.
2. **For bc-2aa33ad8: a standing GPU backlog in priority order** (Daniel's priority 2, 18:50Z; the target proposed to him is
   at least 95% GPU busy, with at least 90% of that useful). The ask:
   - Keep at least 8 GPU-hours of useful `gpus=1` fill jobs queued, ordered by `prio=`, so no GPU waits on a lane's turn.
   - Each hour, when the queue runs dry, I'll name the missing work and its owner in ops.md.
   - Jobs that hold a GPU while working on the CPU (the `fp8chain-die*` pattern above): prepare outside the lease, or give them
     a lower `prio` than GPU-heavy jobs, as the fill header already advises.
   - **Filler:** a job that is filler says so in its header, e.g. `# fill: ... filler=<why>`. The runner already parses any
     `key=value`, so this needs no code change. Everything unlabeled counts as useful. Filler runs only when nothing useful is
     queued, and never ε_R or seed padding (the pous root, 15:27Z). The hourly report shows the useful share against the filler
     share from this label.
3. **CPU fill outside timed windows:** useful `gpus=0` jobs (verifies, tests, Lean, censuses, captures) are welcome on the
   pous CPU set (96–127); the runner freezes them in windows. This doesn't go through the held Verity CPU pool.
   - Which lanes have CPU work to queue? CPU is 18–26% busy today.
