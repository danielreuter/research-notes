---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-gpu-link · kind: handoff · from: coordinator · created: 2026-09-26T18:30Z

# Total GEMM unit: choose the slot option by end-to-end GEMM cost, not gate count (re flock-backend's 18:55Z handoff)

**The problem:** the total `tc_dot16` unit is 8,449 rows, which doesn't fit the 2^13-row slot.
- Option A, a 2^14 slot, is only about 52% full.
- If proving cost scales with table rows, padding included, A roughly doubles GEMM time, not the 1.05× the gate count
  suggests.

**Before anyone builds A, compare end-to-end GEMM cost for #101's K = 2048 cell (and K = 8192) for each option.**
Measure or model it: rows committed, prover time, and total cell time.

| Option | What it is | Rough expectation, if cost scales with rows |
|---|---|---|
| A | 2^14 slot per unit | about 2× |
| B2 | BF16 output word only on each chain's last unit: 127 of 128 units at K = 2048 lose the output epilogue. Check whether those units then fit 2^13; the last unit takes a larger slot. | about 1.0× plus the last unit |
| Packing | units contiguous, without power-of-two slot alignment | about 1.19× (8,449 / 7,100), but it changes the prover and verifier layout |
| Trim | cut 352 gates, bringing 8,449 rows to 8,097 so it fits 2^13 | about 1.0×; needs the census owner's agreement (verity.ml.tc total semantics must be unchanged) |

**Rules:**
- **Pick the cheapest option that keeps total semantics** (every bit pattern, NaN and infinity, as the hardware).
- **flock-gpu-link, as the Rust/CUDA owner, decides the implementation.** red-team-flock reviews it before any cell runs, as
  planned.
- **Any option under 10× is within Daniel's rule,** so he needs to decide nothing unless every option exceeds about 1.5×.
  In that case, send me the numbers and don't build yet.

Copied to flock-gpu-link and flock-backend.
