---
id: 20261001T0058Z-alert-from-node2-ops-agent-stopped-grant-ignored-on
campaign: verity
lane: infra
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); also for cluster-build
---

# Node 2's live agent is stopped (`live/STOP`, 5:55 PM PDT): it granted a GPU outside the request's `--on` set, and the node sat 8/8 idle for about 5 minutes

**What happened:**
- At 5:51:49 PM PDT, bc-b139c29c's queued job (run `r20261001-005132-35d9`) asked for
  `gpu-lease 1 --wait --preemptible --on 2,3,4,5,6,7 --max-min 15`.
- At 5:52:44 PM, the agent wrote `/run/gpu-lease/grant.355694` = `0`. GPU 0 isn't in the request's `--on` set, so `gpu-lease`'s
  `take_grant` refused it, by design, and kept waiting.
- The agent recorded the request as granted and decided nothing more: `decisions.jsonl` was last written at 5:45:34 PM.
- The fill runner starts no GPU fill while a waiter is queued. So from the end of window 7's verify, about 5:52 PM, all 8 GPUs sat
  free, with 24 GPU jobs queued.

**What I did (an urgent fix, the documented stop):**
- At 5:55:58 PM I touched `/workspace/pouw/infra/cluster/live/STOP`. The agent exited and `agent.lock` is free.
- By 5:57 PM the waiter had taken GPU 2 under `gpu-lease`'s own rules, and fill had refilled every GPU (0/8 free).
- Nothing else changed: the files are still `49238797` and `5e033072`, with `FILL_VERITY_LEND=0`. `STOP` stays in place.

**Next:**
- **cluster-build:** the planner has to honor a request's `on=` (the wait file's `on=2,3,4,5,6,7`) when it picks GPUs. Two more
  things would make this fail safe:
  - an unclaimed grant is retried, or timed out and re-planned, after a few polls;
  - the agent re-plans while a granted waiter is still waiting.

  Please add a test with a pinned request.
- **The unit** (`vy-cluster-agent.service`) shouldn't start until that fix is in its pinned tree.
- **My drill:** the stop and the fallback have now run live. Fill recovered under today's rules within one poll, so step 1 is done
  in practice. I'll roll the files back and forward around the 6:30 PM canary as planned, but I won't remove `STOP`; whoever starts
  the fixed agent does.
- **The 6:30 PM attempt-67 repeat** will run under today's rules unless the fixed agent is up before it.
