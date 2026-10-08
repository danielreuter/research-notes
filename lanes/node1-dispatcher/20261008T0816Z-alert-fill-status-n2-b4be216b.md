---
id: 20261008T0816Z-alert-fill-status-n2-b4be216b
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
tags: [warn]
repo: danielreuter/verity
origin: vy-monitors@vy-nebius-1 (research monitors, research/monitors.py)
monitor: fill-status-n2
key: "fill-status-n2|stale"
owners: [infra]
severity: warn
---

# Node 2's fill status is 1041 minutes old (/workspace/pouw/fill/status.txt: 2026-10-07T14:55:57Z free GPUs 8/8, kept free -, waiters -, timed False, window waiti

*Node 2's fill status is 1041 minutes old* (/workspace/pouw/fill/status.txt: `2026-10-07T14:55:57Z free GPUs 8/8, kept free -, waiters -, timed False, window waiting False, backfill False, queued 1 (gpu 1, cpu 0), done 1354, failed 30, he`), so the fill runner isn't ticking, and the node-2 monitors are skipped until it does.

What to do: Stale: restart node 2's fill runner (tmux `pouw-infra-fill`) after reading why it stopped; until its status is fresh, no monitor reads node 2. Unwatched: find the lease holding `timed` (`/run/gpu-lease` on node 2) and the window it belongs to; ask its owner to end it, or release it once it is dead.
