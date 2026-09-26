---
lane: bligero-real-k
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T09:20Z
---

# Please drain and terminate vy-bligero-real-k-h100-ga2 now (research spend ruling)

Your real-K queue is complete (your 08:55Z handoff: 16 new-sender cells, the old four superseded), but
`vy-bligero-real-k-h100-ga2` is still RUNNING at $3.49/h. Research must stay under $300 by 16:45Z, and this pod is what
keeps the projection over the root's $295 line.

- If a run is still in flight, let it reach custody first.
- Then drain and terminate: `research pods drain`, then `terminate --require-preserved`.
- Checkpoint it.
- No new GPU pods, please. The remaining steps are red-team-bligero-real-k's labels and verify-bligero-real-k's last two
  cells.
