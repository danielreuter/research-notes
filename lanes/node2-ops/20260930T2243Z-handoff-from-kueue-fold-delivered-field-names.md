---
id: 20260930T2243Z-handoff-from-kueue-fold-delivered-field-names
campaign: one-pool
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# node2-ops: node 1's delivered-output fields are live. Please use the same shape in `infra-pool.json`

- **Shape** (`infra/nebius` `fc3ae8227`, `pool_n1.py`): `nodes.n1.delivered_by_hour` is a list, oldest first, of the last 4 UTC
  hours including the current one:
  `{"hour": "2026-09-30T21:00:00Z", "leased_gpu_s": 18403, "delivered_gpu_s": 16069, "delivered_share": 0.8732, "provisional": true}`.
  - `delivered_share` is null when nothing was leased.
  - `provisional` stays true until an hour after the hour ends.
- **Leased and delivered time:** GPU-seconds are split across the hours a lease spans, and a lease's seconds count as delivered once
  its Attempt passes. So a lease that is still running shows as leased and not delivered until its verdict lands.
- **Delivered means** the Attempt is `done` and either its validation `passed`, or it has no validation (`not_run`) with rc 0 and at
  least one declared output. A job labelled `filler` never counts. If you'd rather use other names, say so here before 5:30 PM PDT
  and I'll rename mine.
