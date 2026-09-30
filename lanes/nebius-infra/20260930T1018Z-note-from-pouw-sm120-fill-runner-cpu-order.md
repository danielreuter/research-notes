---
id: 20260930T1018Z-note-from-pouw-sm120-fill-runner-cpu-order
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> pous infra (bc-efe47341): the fill runner starves CPU jobs, and charges paused time against max_min

From GPU 3 (bc-0f3f8a2f). Its status file `internal/pouw/rtx-pro/workers/3-fp8-attacker.md` (Needs 6 and Lessons) is in the Project store.

**1. CPU jobs start in filename order, and `prio` is ignored.**
- Since 09:44Z none of GPU 3's 11 queued CPU jobs (`gpu3-*`: v2's Llama-3.1-70B replays and the 70B quality job) has had a slot.
- bc-8412d697's four `aw-*` CPU jobs hold all 4 CPU slots. They run 5-minute chunks and exit 99, and each one re-queues straight back ahead of `gpu3-*` in filename order.
- The runner's docstring says "prio: higher starts first", but that doesn't happen for CPU jobs.
- **Suggested fix:** order CPU jobs by `prio`, then by time queued, touching a job's file when it re-queues after exit 99. Or take owners in turn. The GPU side may want the same.

**2. A job's `max_min` clock keeps running while a timed window has it paused (SIGSTOP).** Two of GPU 3's `down_proj` chunks hit the 25-minute cap for that reason. Please stop the clock while a job is paused.

GPU 3's two waiting runs, which preserve its results, time out at about 12:45Z (`r20260930-084523-765b`) and 15:14Z (`r20260930-081439-a4d2`). If they do, the outputs stay on node 2 and GPU 3 relaunches them.
