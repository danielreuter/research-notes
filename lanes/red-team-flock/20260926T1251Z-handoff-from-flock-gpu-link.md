---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T13:01Z
---

# Short re-look: two prover-side fixes for ChunkTail on the GPU (PR #75 @ ea27aa86). There is no verifier change

- **Claim cap:** the CUDA `max_extra` went from 16 to 64 region claims. ChunkTail with the epilogue has 18.
  `PureStmt::new` now asserts 2 × regions ≤ `MAX_EXTRA_CLAIMS` (64). No layout comes near it: the most is 18.
- **Deadlock:** `PureStmt::tail_chain` (ChunkTail's continuation-unit accumulators, used only by the prover's `c_in`) is
  now sequential and precomputed by `PureStmt::prepare`. Its parallel initialiser deadlocked under rayon. The values are
  unchanged.
- **Unchanged:** the statement digests, Δ, regions, publics and verifier code.
- **Evidence:** PR #75. GPU selftests pass for ChunkTail(4) and ChunkTail(17) on an L4, and there are two new unit tests.
