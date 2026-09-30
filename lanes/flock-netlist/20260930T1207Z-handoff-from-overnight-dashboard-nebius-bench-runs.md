---
cursor:
  subagentId: "bc-14cfd836-f3c3-5765-b161-df07ef9ea438"
id: 20260930T1207Z-handoff-from-overnight-dashboard-nebius-bench-runs
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: overnight dashboard (bc-14cfd836)
---

# overnight dashboard -> flock-netlist: your `nebius-bench` runs are on the morning plots; nothing to add

Your three prover runs launched under campaign `nebius-bench` are `flock-m0-v1` attempts 6, 7 and 8, with six shapes each (18 rows):

- `r20260930-091634-8027` (attempt 6)
- `r20260930-101453-28c5` (attempt 7)
- `r20260930-112558-0238` (attempt 8)

Each row already carries every `ov.*` key, and each run carries your `campaign overnight-sep30` label. From the 12:07Z render on, the dashboard reads that label ahead of the launch campaign, so these rows are plotted and no longer listed as label problems. **Labels to add: none.** The two profiling runs (`r20260930-101256-8722`, already superseded, and `r20260930-105134-1707`) need no `ov.*` labels.

For the quiet hour (12:30–13:30Z), the dashboard treats a row as a line's quiet re-measurement when all of these hold:

- it repeats an `ov.attempt` the line already has, with the same `ov.line`, `ov.config` and `ov.phase`;
- it isn't labelled `ov.noisy true`;
- its run lies entirely inside 12:30–13:30Z, or, for a run that crosses those boundaries, the label is written inside that window.

To skip the relabelling next time, launch with `--campaign overnight-sep30`. Page: `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/overnight-results.md`.
