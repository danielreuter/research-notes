---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T13:40Z
---

# M0's `verity/flock-circuit` statement review: it supports a NON_ZK_PROOF Table 1 row, if the row says what the unit covers

Asked for directly (13:26Z). The review is in the store at `private/red-team-reviews/m0-statement/review.md`, with its
evidence beside it. CPU only, $0.

- **What an accepted session claims:** the prover knows, for each instance, the input rows and salts behind the public
  row commitments (`b ‖ c`), and the pinned circuit maps those rows to the public outputs. Under that claim:
  - there's no shared-row table and no unit draw in either cell;
  - the units are template instances as stated, by the provisional unit cover.
- **On every proved instance, the circuit's outputs equal the IR reference:** 16 of 16 for attention and 1,024 of 1,024 for
  GEMM. Equality on all inputs isn't established here.
- **Recommended Table 1 rows:**
  - "C-Flock M0 (`verity/flock-circuit`, #83 @ e226a920). 16 × one attention query over T = 129 keys (d = 64; FA2 bf16
    tensor-core steps, softmax tails and EX2/RCP lookups in the circuit), on a synthetic set. `NON_ZK_PROOF`, interactive
    with live verifier coins (fast100 ×2). Outputs are public and equal the IR on every proved instance; the benchmark's
    input commitments are not hiding. L40S prover, CPU verifier on a separate host. **2.92 s** prover end-to-end
    (verification excluded). 9.42 M tensor-core-step ANDs per query, so 51.6 M/s (tails, lookups and in-circuit hashing
    proved but not counted)."
  - "C-Flock M0 (as above). 1,024 × one K = 2048 bf16 GEMM output coordinate (128 tensor-core steps, then the bf16
    epilogue), captured from Llama-3.2-1B through vLLM. Same class, coins and placement. **16.4 s** prover end-to-end
    (verification excluded). 1.10 M tensor-core-step ANDs per coordinate, so 69 M/s."
  - **Footnote:** "Units are template instances as stated, not derived from a model program's partition. No unit draw:
    every instance is proved. PR #83 and the Lean verifier of record (#142) are unmerged."
- **Don't print:**
  - "attention head" for the unit;
  - "private" or "hiding";
  - the fingerprint's `domain: finite`, which is a constant;
  - the AND count unqualified.
