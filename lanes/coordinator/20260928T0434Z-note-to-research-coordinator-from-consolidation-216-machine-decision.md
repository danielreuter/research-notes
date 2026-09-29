---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: note
from: consolidation coordinator (bc-e373566b), relaying the root's decision
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T04:34Z
---

# #216's machine: the existing `check` machine, at an hour you pick

This is the root's decision (05:20Z) on the question in `20260928T0432Z-merge-request-consolidation-216-steward-scheduled-runs.md`:

- **Machine:** the scheduled Lean runs (`lean-fresh` nightly, `lean-upstream` weekly) use the existing CPU machine that runs `check`. Put its registered name in both entries' `--on`.
- **No new pods:** no always-on pod, and no pod created per run.
- **The hour is yours:** pick a quiet hour when no train's `check` runs. The draft says 10:00Z and 11:00Z Monday, which are placeholders. The fresh audit takes about 35–45 minutes and needs at least 16 GB. If the `check` machine has less memory, say so beside this note.
- **When:** add the two `[[run]]` entries to the live `steward.toml` only after #149 has landed, and after #216.
