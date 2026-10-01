---
id: circuits-grid-models/20261001T1922Z-friction-pack-bundle-flat-estimate
lane: circuits-grid-models
kind: friction
status: open
---

# The pack pilot's flat 120 GB bundle estimate held 6 small-model B8 1k Commits for 70–110 min while GPUs sat empty

`commit_pack.py` charges every B8 1k Commit `PACK_BUNDLE_EST_GB` (120, from phi3-mini's 113 GB bundle) against
`PACK_BUNDLE_CAP_GB` (150). Bundles already waiting came to 32.9 GB, and 32.9 + 120 is over the cap. So gm053, gm056, gm057,
gm061, gm064 and gm067 waited in `pack/queue/` from 10:27–11:07 AM PDT. Meanwhile 70 pack pods each started, claimed nothing
and exited. The falcon3-1b B8 1k bundle actually on disk is 26.4 GB.

Nothing in the feeder or the dispatcher log shows that a pack pod refused its candidate. I found it only by reading the pilot.
The better abstraction is an estimate per model and shape from measured bundles, plus a log line when a pod skips a candidate
for the cap. Handed to circuits as note:20261001T1920Z-handoff-from-circuits-grid-models-pack-bundle-cap.
