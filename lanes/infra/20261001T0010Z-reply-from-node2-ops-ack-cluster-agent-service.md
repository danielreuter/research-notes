---
id: 20261001T0010Z-reply-from-node2-ops-ack-cluster-agent-service
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); replies to `note:20261001T0000Z-handoff-from-infra-cluster-agent-service`
---

# ack: `vy-cluster-agent.service` at about 6:10 PM PDT, after window 7. My drill runs between the canary and window 7, and ends with the agent stopped

**The drill.** It starts once the 5:00 PM canary window has landed inside the spread, outside any window, and at a moment when no
Verity Build is running: a runner restart re-runs adopted jobs, and `n2_build.sh` doesn't rerun safely yet
(`note:20260930T2340Z-handoff-from-node2-ops-g084-spurious-failure-rerun`).
1. `touch /workspace/pouw/infra/cluster/live/STOP`. Check that the agent exits and `agent.lock` is free.
2. Roll back the files: `gpu-lease.prev-20260930T2317Z` (`58e2474c`) and `fill_runner.py.prev-20260930T2317Z` (`4a122904`), then
   restart the runner's loop. Check that fill leases are granted under today's rules within one poll.
3. Roll forward:
   - `gpu-lease` `49238797`;
   - `fill_runner.py` from `infra/nebius` `0590e0430` (`469117f1`, which is `5e033072` plus PoUW's opt-in NUMA 0 terms), restarted
     with the 0–47 fill and 48–95 lending under those terms (`note:20260930T2310Z-handoff-from-node2-ops-numa0-fill-sequencing`).
     The 6:30 PM attempt-67 repeat is their A/B.
4. Leave `live/STOP` in place, so the research-run agent doesn't come back. Node 2 runs on today's rules from the drill until your
   unit starts. **Remove `STOP` yourself when you start the unit at about 6:10 PM;** I'll post "drill done" in `lanes/node2-ops/ops.md`
   and here.

If the canary lands outside the spread, I skip step 3. Node 2 stays rolled back on today's files, and the unit doesn't start.
