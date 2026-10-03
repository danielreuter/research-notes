---
id: 20261003T1528Z-alert-from-node2-ops-circuits-1430z-window-ended-early
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1), who booked the window; please relay to circuits (thread 1791005852.369829). I've touched nothing.

# On node 2, circuits' 14:30Z window ended at 15:21Z, but `fill/windows` holds the node until 17:00Z

- **What I see:**
  - Circuits' run `r20261003-143852-065f` (`/workspace/jobs/runs/`, Qwen3-235B-A22B TP8 row `…bi-eager`) stopped at 15:21:37Z with `MATCH FAIL -> stop`.
  - TP2 match capture and check passed: rc 0, 6080 collectives, 0 mismatches.
  - `fold_match (derived_QWEN3_235B_A22B_tp8)` returned rc 1, with every `fold_per_rank` leg false. Details are in the run's `failure.json` and `stdout.log`.
  - The `circuits-tp8` lease (14:30:01Z–17:00:01Z) was gone by 15:21:56Z. The node is free (8/8, `timed False`), and no circuits process is left.
- **Effect:** the line `2026-10-03T14:30Z 150` keeps fill to jobs that clear 17:00Z, so the node sits idle until then. Memory accounting's series `…141820Z` (about 25 min) waits in the queue. The window also pauses slot d and keeps cores 48–123 for circuits.
- **Ask:** if circuits isn't relaunching, shorten the line to end now, as at 09:40Z. Fill would then start the series, and the 15Z/16Z backup would run. If it is relaunching, nothing to do. Either way, the 17:00Z compute accounting line is unaffected.
- **Mine:** I'll take no action. Backups stay held while the line stands.
