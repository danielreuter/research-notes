---
lane: red-team-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T11:46Z
---

# From now on: launch every run with --custody-r2, and never `research fetch --all` to the laptop

The laptop has about 2.5 GiB free, and `~/.research/runs` grew 0.5 GB in an hour from full fetches of pod runs. Rules, effective
now (root, 4:42 AM PT):
- **Launch:** `research run --on <pod> --project verity --custody-r2 [--custody-ttl 6h] -- ...`. The pod publishes the
  attempt and every run file, logs and telemetry included, to R2 with its own minted key. That's custody without the laptop
  (F1 passed on exactly this). Set `--custody-ttl` to outlast the run.
- **Don't** run `research fetch --all` (or `fetch` of big files) for runs on your pods. The small records `status` pulls
  (job.json, status.json, result.json...) are fine and automatic.
- **Inspect on the pod** (`research pods ssh <pod> -- ...`), or read from R2: `research data preserved <run>` to check custody,
  and `research data fetch <art> --path <glob>` for one small file only if you truly need it locally.
- **FINAL's custody check** accepts R2 custody for `--custody-r2` runs. You don't need a laptop copy.
- If a run already on your pod was launched without `--custody-r2`, push its outputs from the pod side (`data put --preserve`)
  instead of fetching.
If laptop free space drops below 1.8 GiB, I'll stop the lowest-value laptop lane, so please keep to this.
