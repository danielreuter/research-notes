---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T05:50Z
---

# agkr-bound revised estimate: correction (the prover cost is higher than 0540Z said)

A correction to the "expected prover-cost delta" in my 0540Z estimate. **It strengthens the "does not fit" answer, and it
bears on option (a).**

The A-GKR layered GKR (`gpu/circuit.py::layers`) is built this way:

- Each product-depth layer spans **every wire** of the unit, carrying the ones it does not compute as pass-through gates.
- The assertion layer spans every assert.

So an in-circuit Poseidon2 widens every layer the prover pays for, not just the commitment:

- **Route (i), depth-1 (the only route that keeps one product layer).** Each S-box commits x², x³, x⁴ and x⁷, the same
  852 rows per permutation as B-Ligero. With 2 permutations per unit, BF16 becomes:
  - 264 → about 1,970 committed columns (7.5×);
  - 290 → about 3,700 wires, so log2 of the width rises from 9 to 12 (8×);
  - 29 → about 1,730 asserts.

  E4M3 and NVFP4 are about 4.5–5× on columns.
- **Route (ii), depth-3 S-boxes.** This adds 3 product layers, each spanning every wire, including the pass-throughs. It is
  no cheaper than (i) under this layer structure, and it adds depth > 1, which the fast prover has never proved.

**Revised expected t.total:**

| relation | multiple | A100 time |
|---|---|---|
| BF16 | about 4–8× | about 3.5–7 s (from 0.84 s) |
| FP8 / NVFP4 | about 3–6× | — |

For comparison, B-Ligero with the in-proof hash takes 0.897 s on A100 BF16. The RTX 4090 (24 GB) would need 2–4 sub-batches
at 4096 VUs.

Reading: keeping A-GKR competitive under the committed relation would need a different layer structure first. One
candidate is a third statement segment, beside unit and epilogue, that holds only the sponge. It would be deep and narrow:
about 87 product layers of about 24–48 wires, with only the 16 rate lanes and 8 capacity lanes committed, chained to the
unit's operand columns. That trades commitment for about 87 × 25 extra sequential sumcheck rounds, and it needs a fast
prover that handles depth > 1. That is a design task, not a measurement. The pod-hours and $ in 0540Z assumed route (i) works first time. With this layer
structure, option (b), development only, is the realistic scope for today, and (c) remains fine.
