---
id: 20261010T1012Z-alert-held-idle-stale-6223799b
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
tags: [warn]
repo: danielreuter/verity
origin: vy-monitors@vy-nebius-1 (research monitors, research/monitors.py)
monitor: held-idle-stale
key: "held-idle-stale|stale"
owners: [infra]
severity: warn
---

# Held-idle panel: no reading for 72 minutes: the newest completed hour in it is 08:00Z (node 1's /workspace/usage/held-idle-hourly.jsonl).

*Held-idle panel: no reading for 72 minutes*: the newest completed hour in it is 08:00Z (node 1's `/workspace/usage/held-idle-hourly.jsonl`).

What to do: Check `verity-console.service` and its timer on node 1 (`journalctl -u verity-console -n 50`).
