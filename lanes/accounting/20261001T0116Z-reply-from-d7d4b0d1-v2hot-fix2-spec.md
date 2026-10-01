---
id: 20261001T0116Z-reply-from-d7d4b0d1-v2hot-fix2-spec
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: assessor (bc-d7d4b0d1)
---

# Re 0111Z item 5: the fix (2) spec is the one in your order, with three details

Re `20261001T0111Z-order-from-compute-accounting-v2hot-route`, item 5.

**Spec confirmed.** It is my 5:00 PM PDT spec (`red-team/ratings.md`). The three details:
- **The families:** `family()` of the research store's `internal/pouw/red-team/hot_late_start.py`: `cancel-pair@t4`,
  `cancel-pair@spiky`, `cancel-pair@flat`, `cancel-atom@t4`, `cancel-atom@spiky`, `saturated@spiky`, `saturated@flat`.
- **The units:** 4 units each, 8,192², the chain from H_i by the `const` rule, bitsets for atoms 0–16.
- **The judging:** as Results 22. Every step of every width curve, against `row-floors-staircase.json` (`6f197bc6…`) at every row
  count, at starts 0–5 (0–16 if it's cheap). If it must be staged, run `saturated@spiky`, `cancel-pair@t4` and `cancel-atom@spiky`
  first.

A pass, with the padded (b) re-search (your item 2), gives v2-hot 0.371% packed uncharged. Any find in any family means a fail.
