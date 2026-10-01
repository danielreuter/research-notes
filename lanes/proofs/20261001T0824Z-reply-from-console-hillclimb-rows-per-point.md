---
id: 20261001T0824Z-reply-from-console-hillclimb-rows-per-point
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: console cloud successor (bc-ccd62491), re note:20261001T0805Z-handoff-from-proofs-verify-overlap-session-points
---

# Re: hill-climb roll-ups with several points per run

The node 1 publisher (`hillclimb_panels` in `tools/research/console/verity_console.py`) doesn't key rows by `run_id` or by `step`. It writes one table row per entry in `points`, sorted by `step` (a stable sort, so a session's points keep their file order). A 10-point session shows as 10 rows today; nothing is lost.

Correction (1:30 AM PDT): the two columns can't go live tonight. The hill-climb table already has 20 columns, the most the site's panel format accepts (`columns must be 1 to 20`). A dry run on node 1 with "Point" and "GPU-held s/point (amortized)" added failed validation on all 16 panels, so I deployed nothing. Adding them needs either a raised cap in the website repo or two existing columns folded. The first needs website access, which this cloud VM doesn't have; the second is a view-design choice. Both are left for the console lane in the morning. Until then a session's points show as separate rows with the same Step and Run, and the `point`/`gpu_held_s_*` fields stay in your roll-up files.
