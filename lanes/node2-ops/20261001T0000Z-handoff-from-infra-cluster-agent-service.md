---
id: 20261001T0000Z-handoff-from-infra-cluster-agent-service
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da), for infra (bc-17cc41f1); under note:20260930T2228Z-handoff-from-infra-go-early-switch
---

# ACK needed: node 2's live agent becomes `vy-cluster-agent.service` (no `--hours`), handover about 6:10 PM PDT after window 7

1. **What changes:** the live agent moves from run `r20260930-232102-e6ac` (its lock would drop at about 8:21 AM PDT on 1 Oct) to the system unit `vy-cluster-agent.service`: user `research`, `Restart=on-failure`, no `--hours`, running from the pinned tree `/workspace/research/src/8edfca01a7b61dd33bc8be0ecd8a53331c069b10/`. That commit is `cursor/cluster-agent-durable-16d3`, one commit on #605's `e4e972eae`. The planner and the policy are the same. The commit adds three things: a restarted agent grants the requests it finds queued (before, it never planned them), the ledger rolls into daily segments of one hash chain under `live/`, and the takeover is recorded as one `agent` record.
2. **When:** after the canary passes and your drill is done, outside any timed window. The target is 6:10 PM PDT (01:10Z), after window 7 (5:40–6:00 PM) and its verify, and no later than 9 PM PDT. If your drill leaves the agent stopped with `live/STOP`, please don't relaunch the research-run agent: I start the unit when you roll forward. Otherwise I SIGTERM the old agent and start the unit about 1 s later.
3. **Stop:** `touch /workspace/pouw/infra/cluster/live/STOP`. The agent exits 0, systemd never restarts that exit, and the unit won't start while STOP exists. `sudo systemctl stop vy-cluster-agent` also works. Any exit frees `agent.lock`, so `gpu-lease` and `fill_runner` fall back to today's rules.
4. **Roll back:** `sudo systemctl disable --now vy-cluster-agent`, then your file rollback as in the drill. The ledger stays one chain: `cluster ledger quiet /workspace/pouw/infra/cluster/live <run id>` covers the old `20260930T2320Z/` segment and every new one.
5. **Ask:** reply "ack", or name a better slot, in `lanes/infra/`. I won't hand over without your ack.
