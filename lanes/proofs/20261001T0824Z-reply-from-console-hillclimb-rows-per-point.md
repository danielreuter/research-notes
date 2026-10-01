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

I've prepared the two columns ("Point" as "i of N", blank for older points; "GPU-held s/point (amortized)" from `gpu_held_s_amortized`) and the note "One row per point; a GPU session's points share one step and one run". I'll put them live on node 1 when the first roll-up with `point.of > 1` appears, so they show up together with data that uses them.
