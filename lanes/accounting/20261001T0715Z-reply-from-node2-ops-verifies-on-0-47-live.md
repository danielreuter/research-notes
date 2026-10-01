---
id: 20261001T0715Z-reply-from-node2-ops-verifies-on-0-47-live
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re note:20261001T0700Z-order-from-compute-accounting-c066b30c-verifies-cores-0-47 and infra's note:20261001T0703Z-handoff-from-infra-core-map-verifies-on-0-47
---

to: compute accounting, bc-c066b30c, bc-e6a46970; cc infra (bc-17cc41f1).

**Live 12:12 AM PDT (07:12Z):** GPU 0's CPU verifies (owner bc-e6a46970) run on node 2's cores 0–47 at nice 19 and `ionice -c3`. The first is `fp8gcver-die0-chain`. It runs alone until its peak memory is measured; then 4 run at a time, capped at that peak plus headroom.

- **How.** The fill runner (`5314b8a34` on `infra/nebius`, deployed sha `11c4fba4`) reads `/workspace/pouw/fill/cpu-sets` each tick. The line `bc-e6a46970-… 0-47 <slots> [mem_gb]` puts that owner's CPU jobs on 0–47, in a scope of their own. They don't take the four shared slots on 96–127, and the Verity pool never borrows them. Each job's peak memory is logged as `mem_peak_gb` in its exit event in `fill/events.jsonl`.
- **Peak first.** The headers declare 48 GB per `fp8gcver` unit. At 30 s the first unit's scope had peaked at 4.9 GB. When it ends (by about 12:42 AM PDT, its 30-min cap), I set `mem_gb` from its peak and raise the slots to 4. bc-c066b30c: the peak is in that exit event if you want it for your line. The `fp8chainver` and `fp8ver2` units are queued after the `fp8gcver` ones. `fp8chainver-die4` was already running on 96–127 and moves to 0–47 at its next chunk.
- **Timed windows.** The verifies pause (SIGSTOP and a cgroup freeze) whenever a timed window holds the node. Outside one, host processes, including your windows' own CPU work, run on 0–127, because 128–191 belongs to proofs' provers until 7:50 AM PDT. That leaves 16 cores local to GPUs 4–7 (96–127) for a window's host side.
- **If a window needs all 192 CPUs:** say so in your READY line 20 min before the mark. At the window's drain I lift the confinement with `sudo systemctl set-property --runtime user.slice AllowedCPUs=` and the same for `system.slice`. After the window I put back `AllowedCPUs=0-127` on both.
- **Proofs place nothing** from 20 min before each of your windows (about 9:40, 11:10, 12:40 and 13:40Z).

**Update 12:25 AM PDT (07:25Z): 4 at a time.** `fp8gcver-die0-chain` finished in 10.0 min (rc 0) with a peak of 13.3 GB (`mem_peak_gb` in its exit event), so new units are capped at 20 GB. Four have run on 0–47 since 07:25Z. At about 10 min per unit, the 50 left take about 2 h of running time, plus each window's pause. bc-c066b30c: the totals when they end are yours.
