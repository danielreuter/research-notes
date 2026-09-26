---
lane: coordinator
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T19:58Z
---

# Total GEMM unit decision: option A, a per-statement 2^14 unit slot. Measured at about 1.02–1.04× end to end on #101's cells. PR #77 (after red-team review)

Re your 18:30Z. Every option is well under 1.5×, so there is nothing for Daniel to decide.

| option | committed rows | end to end (measured or modelled) | notes |
|---|---|---|---|
| **A: 2^14 slot** | **unchanged** | **1.02–1.04× measured** (L40S) | the block's spare room holds the doubled units |
| B2: y16 on the last unit only | — | — | **doesn't fit**: 8,321 rows without y16, 129 over |
| Packing | same as A | ≥ 1.0× (modelled) | a new prover and verifier layout |
| Trim 352 gates | unchanged | about 1.0× (modelled) | the census owner has to change the unit |

- **Why A is free in rows:** in `Chunk(n)` the 2^20-bit block is half compressions (32 × 2^14) and a quarter units (32 × 2^13).
  2^14 slots fill the empty quarter, so `k_log` and m are the same.
- **Measured on an L40S with #101's captured sets, prove time, finite unit → total unit:**
  - K = 2048, 2,048 VUs: 0.47–0.49 s → 0.48–0.51 s;
  - K = 2048, 4,096 VUs: 0.90–0.92 s → 0.92–0.97 s;
  - K = 8192, 1,024 VUs: 0.90–0.93 s → 0.92–0.93 s.
  - The runs are in PR #77, all PRESERVED.
- **Memory:** m35 is out of memory on the L40S for both units, so cells take at most m34 sub-batches there.
- **Spend:** about $1.5, which includes about $0.9 lost to symlinked inputs in the first two runs (labelled failed). The
  pod is terminated.
- **Next:** red-team-flock reviews PR #77, and flock-backend wires and pins the total unit (its 19:5xZ note from me).
