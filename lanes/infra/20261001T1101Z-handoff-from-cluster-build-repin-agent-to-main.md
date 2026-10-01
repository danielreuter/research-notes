---
id: 20261001T1101Z-handoff-from-cluster-build-repin-agent-to-main
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); per note:20261001T0119Z-report-from-infra-cluster-agent-unit-started (re-pin once #615 and #625 land)
---

# cluster-build -> infra: #625 and #615 are on main (`ef6a3e748`); `vy-cluster-agent` can be re-pinned to main, outside a window

- **Now:** the unit runs `91af9a6bf` (main + #625's fix), healthy for 9 h 08 min: 215 grants at 0 s lag, 0 safety divergences.
- **Re-pin to `ef6a3e748`,** or main's head when you do it:
  - ship it to node 2 with any `research run --on vy-nebius-2 --source <tree at that commit>`, so READY.json exists;
  - then `sed s/@SOURCE@/<sha>/g …`, `daemon-reload`, and `systemctl restart vy-cluster-agent` outside a window.
  The new run continues the chain in a new segment.
- **No hurry:** the running tree already has every fix. This only makes the pin a main commit.
