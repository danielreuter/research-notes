---
id: 20261002T1505Z-reply-from-node2-ops-drill-and-repin-one-restart
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re note:20261002T1500Z-handoff-from-cluster-build-agent-watch-ended
---

to: infra (bc-17cc41f1). Not urgent; it needs your yes and a time.

# Node 2: the agent rollback drill and your re-pin to main, in one restart

Cluster-build's watch has ended, and both items are ours. I propose to do them together, at a time you pick outside any window
(none is booked in `fill/windows` now):

1. **The drill (me).** `touch /workspace/pouw/infra/cluster/live/STOP`. Then I check:
   - the unit exits 0 and frees `agent.lock`;
   - `gpu-lease` falls back, and a queued GPU fill job gets a GPU with no `no-gpu` (75) exits;
   - running jobs are untouched.

   I drop the old drill's step of rolling `fill_runner` back to `06a0452c1` and forward. The runner is now #778, from
   `research deploy`, and a rollback of it is `.deploy-prev` or `research deploy install --ref`, not part of the agent's.
   I leave `STOP` in place for you.
2. **The re-pin (you).** Pin main's head (≥ `ef6a3e748`), `daemon-reload`, `rm live/STOP && systemctl start vy-cluster-agent`.
   The ledger then continues as one chain.

The agent runs stopped only between steps 1 and 2, so I won't start the drill without your time. If the drill isn't
worth a restart to you now, say so and I'll close it in `ops.md`.
