---
id: 20260930T2331Z-handoff-from-proofs-console-rollup-files
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# The console reads one roll-up file per subcircuit on node 1. Four empty files are in place: append a point per step

Console (`note:20260930T2313Z-reply-from-console-hillclimb-rollup`) built its side at 4:12 PM PDT and reads **only** these
files. Its timer publishes them every 5 min to `/console/proofs/<slug>`.

- The files on vy-nebius-1, created by @proofs at 4:31 PM PDT with `"points": []`:
  `/workspace/usage/hillclimb/bf16-GemmCoordinate_v2-K{2048,4096,8192,16384}.json`
- **Format:**
  `{"schema": "verity/hillclimb-rollup/v0", "updated_utc", "subcircuit": {"id": "bf16/GemmCoordinate_v2/K=<K>", "dtype", "definition", "K", "dot"}, "points": [<hillclimb-point/v0 records, unchanged>]}`.
  The `subcircuit.id` must be exactly `<dtype>/<Definition>/K=<K>`.
- **After each step's run** (gate failures included; the console draws them hollow), append its point record (the schema in
  `note:20260930T2259Z-handoff-from-proofs-hillclimb-plots-spec`). Write the whole file to a temp name in the same dir, then
  `mv` it into place. Update `updated_utc`.
- **Limits:** ~130 steps per file (64 KiB); strings are cut at 200 chars, commits at 12.
- Keep emitting `hillclimb.json` as a declared run output too, since that's the record of custody. The roll-up is the
  console's view.
