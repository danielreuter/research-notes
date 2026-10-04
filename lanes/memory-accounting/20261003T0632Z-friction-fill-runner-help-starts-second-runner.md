---
id: memory-accounting/20261003T0632Z-friction-fill-runner-help-starts-second-runner
lane: memory-accounting
kind: friction
status: open
---

# `fill_runner.py --help` starts a second runner instead of printing usage

On node 2 (vy-nebius-2) at 2026-10-03 05:37Z, a soak-prep worker ran
`python3 /workspace/pouw/infra/bin/fill_runner.py --help` to read the fence syntax. The script only parses the
`fence` subcommand; any other argument (including `--help`) falls through to "run the daemon", so a **second runner
started** on a node that already had one. The orphan adopted the running PoUS vLLM series job and launched the next
on GPU 7. The worker stopped only its own runner's PID; the orphaned series job finished rc 0, but its leftover
`running/` marker blocked the series until node2-ops cleared it (filed done 06:07Z). No other lane's job was lost.

Cost: ~30 min of a confused series plus node2-ops attention. Fix is infra's (their live scheduler), not safe to patch
during circuits' headline window. Reported on Slack `1791009094.781129` with the fix: (a) reject unknown args / `--help`
with usage; (b) take a flock single-instance lock on a pidfile so a second runner can't start. Offered a diff.
