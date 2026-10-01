---
id: 20261001T0119Z-report-from-infra-cluster-agent-unit-started
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da); follows note:20261001T0000Z-draft-cluster-agent-service-cutover
---

# Node 2's agent is now `vy-cluster-agent.service` (no `--hours`), live since 6:17:28 PM PDT, pinned to `b3b225e0f`

1. **What:** systemd unit, user `research`, `Restart=on-failure`, `--mode live --roll --stop-file live/STOP`, from the
   content-addressed tree `b3b225e0f6414ce471a760e8d499d02b1f4162a0` (merge of #615 and #625; re-pin to main once both land).
2. **When:** handover at 6:17:28 PM PDT, outside a window; the old pid 4012339 had already exited on node2-ops' STOP at 5:55 PM.
3. **Ledger:** one chain over daily/256 MiB segments under `live/`; the new segment starts at seq 528 chained to the old last
   hash, `cluster ledger verify live/` intact, `ledger quiet live/ RUN` reads across segments.
4. **Stop:** `touch /workspace/pouw/infra/cluster/live/STOP` (stays stopped) or `sudo systemctl stop vy-cluster-agent`.
5. **Roll back:** `sudo systemctl disable --now vy-cluster-agent`, then node2-ops' file rollback to fill_runner `06a0452c1`.
