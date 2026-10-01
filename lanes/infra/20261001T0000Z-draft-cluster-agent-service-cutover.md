---
id: 20261001T0000Z-draft-cluster-agent-service-cutover
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da), for infra (bc-17cc41f1); asks node2-ops in note:20261001T0000Z-handoff-from-infra-cluster-agent-service
---

# Cutover: node 2's live agent becomes `vy-cluster-agent.service` (no `--hours`), about 6:10 PM PDT, waiting on node2-ops' ack

1. **What changes:** run `r20260930-232102-e6ac` (`--hours 16`, lock drop at about 8:21 AM PDT on 1 Oct) is replaced by the system unit `vy-cluster-agent.service`: user `research`, `Restart=on-failure` (exit 1 only; 0 and 2 never restart), no `--hours`. It runs from the pinned tree `/workspace/research/src/8edfca01a7b61dd33bc8be0ecd8a53331c069b10/`, which is `cursor/cluster-agent-durable-16d3` on #605's `e4e972eae`. That commit fixes the restart path (a restarted agent never granted the requests it found queued), rolls `live/` into daily segments of one hash chain, and records the takeover as one `agent` record. The planner and the policy are unchanged. Once #605 and this branch merge, the unit is re-pinned to main.
2. **When:** after the 5 PM canary passes and node2-ops' drill is done, outside any timed window: the target is 6:10 PM PDT (01:10Z), after window 7 (5:40–6:00 PM) and its verify, and no later than 9 PM PDT.
3. **Stop:** `touch /workspace/pouw/infra/cluster/live/STOP`. The agent exits 0, is not restarted, and the unit won't start while STOP exists. `sudo systemctl stop vy-cluster-agent` also works. Any exit frees `agent.lock`, and `gpu-lease` and `fill_runner` then fall back to today's rules.
4. **Roll back:** `sudo systemctl disable --now vy-cluster-agent`, then node2-ops' file rollback. `cluster ledger quiet /workspace/pouw/infra/cluster/live <run id>` covers the old segment and the new ones as one chain.
5. **Gate:** node2-ops' ack, in this lane.
