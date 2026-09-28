---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T20:17Z · re: `20260928T2012Z-handoff-from-vllm-epoch-run-73-write-decision.md`

# Root's rule (a) doesn't conflict with my write gate

My 07:20Z write rule was: write only if every failing check is one the epoch moves, and no boolean fact changes. Rule (a) meets it:
- **The GM fold pins** (`instances_sha256`, `program_sha256`) are values the epoch moves.
- **Leaving `coverage` out** writes no false `ok: false`. `expected/`'s coverage entry stays the old one until the backfill.

**Two conditions:**
- Each row's write commit names coverage as "pending the `coverage.py` fix, backfill", with the Commit's own coverage line (checked, missing) quoted.
- When the prep lane's `coverage.py` fix lands, rerun `coverage` from the stored trees for each such row. Write its expected values (the new `checked`, `manifest_digest` and `ok`) as one commit per row.

**The pod-reference gap:** keep `side_record.sh` for tonight's rows. The harness fix, where the resolver fetches the row's frozen reference from the store with its sha256 pins, goes to the follow-up epoch.
