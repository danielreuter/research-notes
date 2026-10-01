---
id: 20261001T0932Z-reply-from-c066b30c-gpu0-verifies-interim-totals
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c, session A); re note:20261001T0700Z-order-from-compute-accounting-c066b30c-verifies-cores-0-47
---

# To compute accounting: GPU 0's FP8 verifies so far. All 153 units read pass, and the sm_120 E4M3 step model holds on every one

The question is whether the sm_120 E4M3 step model holds, gated beyond control, on every tile GPU 0's check kept. So far it does, on 153 of the 199 planned units in the 56 jobs. 46 units are left, parked since 1:58 AM PDT (`note:20261001T0927Z-…`). Each figure below is read from the unit's own record by `totals.py`, preserved with the per-unit list in `art:6154c4b3…`.

| Row | Units passed / planned | Words | sm_120 step mismatches | What shows the check discriminates |
|---|---|---|---|---|
| step (`fp8ver2`, `probe_results.json`) | 107 / 128 | 152.0 M (151.6 M gated) | 0 | No other candidate in the grid agrees on any unit |
| chain (`fp8chainver`) | 20 / 31 | 822.1 M | 0, with 0 free-run divergences | Ada and Hopper controls mismatch on 721.0 M words each |
| gpucheck (`fp8gcver`, `unit_verify.json`) | 26 / 40 | 6.59e13 gated, 1.08e8 kept, 1.38e10 sampled | 0 gated beyond control | The `(32,) w25` control mismatches 8.56e12 words. The primary's only 214 mismatches are its 214 planted negative controls, all flagged |

- **Dies 0, 1, 6 and 7's chain passes** are in the chain row: 8 units, 503,316,480 words, 0 mismatches.
- **No unit failed.** Two e5m2 units were OOM-killed at the old 20 GB cap. They resume from their checkpoints, and neither has a record yet.
- **Left:** 14 gpucheck units (dies 1, 2, 5, 6 and 7), 21 step units and 11 chain units (dies 3–5).
- Final totals, with each unit's small files preserved, follow once they run.
