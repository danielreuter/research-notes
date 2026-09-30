---
id: node2-ops-ops
campaign: pouw
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), worker of the infra coordinator (bc-17cc41f1)
---

# node2-ops: operations log for vy-nebius-2 (newest first)

Takes over node-2 ops from pous infra (bc-efe47341). Owns ticks only while `/workspace/pouw/infra/ops-owner` on node 2 reads
`bc-c0738ef6-f6bb-5c95-a44f-8e08ff9f35fd`; otherwise standby. Runs until 2026-10-07T14:55Z (node self-stop).
Timers: hourly `5 * * * *`, alerts `2,17,32,47 * * * *`, final backups 2026-10-07T09:00Z and 13:30Z.

## Open items

- Nebius key rotation: Daniel ruled 18:42Z "not now, rotate later". Open, not urgent; no action from node2-ops until he says so.

## Log

- 2026-09-30 18:52Z verity-top's two items (node-1 Grafana alerts; Verity-side infra agents) relayed to infra (`note:20260930T1852Z-handoff-from-node2-ops-verity-top-items`). Not node2-ops scope.

- 2026-09-30 18:49Z recorded Daniel's 18:42Z ruling: no Nebius key rotation now (open item above).

- 2026-09-30 18:47Z agent VM was reset (home and /workspace wiped); restored with an idempotent bootstrap kept in the Project store (`internal/node2-ops/bootstrap.sh`, no secrets). Owner file still absent -> standby.

- 2026-09-30 18:50Z armed: 4 timers on bc-c0738ef6; ssh, uv, research CLI (`vy-nebius-2` resolves) OK. Owner file absent -> standby.
