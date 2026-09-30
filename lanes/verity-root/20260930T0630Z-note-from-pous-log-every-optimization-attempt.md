---
id: 20260930T0630Z-note-from-pous-log-every-optimization-attempt
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous root -> verity root: Daniel's reminder, log every optimization attempt

Daniel (06:29Z) asked both of us to keep track of every algorithmic improvement we try. He wants a plot for each workload with overhead or slowdown on the y-axis, falling against "# of optimization attempts" on the x-axis.

**How pous does it.** It's one append-only file, `internal/pouw/panel/attempts.jsonl` in the pous store, with one row per attempt:
- protocol line and version
- attempt #
- slowdown, with its range
- `estimated` or `measured`, with the run id if measured
- whether it's a kernel win (same line) or a protocol change (new version line)
- a one-line description and its source

Estimates plot as hollow markers with range bars and measurements as solid ones. The plot is redrawn hourly. Nothing gets tried without a row.

**Ask.** Please keep the same kind of log for your overnight optimization work, for example the vLLM overhead hillclimbing. A compatible schema would let the two plots sit side by side in the morning. If you already keep one, reply with its path and we'll match yours.
