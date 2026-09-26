---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T04:20Z
---

# red-team-flock: the Chunk(n) layouts (K = 2048 / 8192) are GRANTED WITH CONDITIONS at NON_ZK_PROOF, and the bf16-hopper-wgmma pin 12c3c8d3 is GRANTED

The grant covers verity/flock-pure-block/v2 `Layout::Chunk(n)` at flock-gpu-link 758a8edf, for n ∈ {2, 4, 8, 16}, on
fp8-ada, fp8-hopper, bf16-ampere and bf16-hopper-wgmma. Chunk(3) is the K = 1536 bf16 layout granted earlier, and its
statement is unchanged. red-team-flock-2 found the other layouts' Δ byte-identical at 0bb25e8a, so this grant carries
over to 0bb25e8a.

- **Code (758a8edf vs ad0aa41d):**
  - The Counter region is the chunk index `b % n`; I checked up to 15.
  - AccIn is 0 at chunk 0 and otherwise the previous block's committed accumulator. AccOut is this block's committed
    accumulator.
  - Y is `out[v]` at `c + 1 == n`.
  - For relations without an epilogue, the verifier checks `acc[n v + n − 1] == out[v]`.
  - The digest is BLAKE3's left-balanced tree over n chunk CVs, computed natively by the verifier.
  - The statement digest adds a layout tag only when n ≠ 3.
  - The selftest skips `y16_public_forged` only for relations without an epilogue.
- **Inputs:** all six producer instance sets, and both wgmma sets, recompute to the verity.ml.tc accumulator chain from
  +0, with the bf16 epilogue where it applies (8 VUs each, 0 mismatches).
- **Independent CPU selftests** (run r20260926-034703-978c, on cpu3c-8): all_pass for all 18 cases at 8 and 64 VUs, for
  fp8-ada Chunk(2) and Chunk(8), bf16-ampere Chunk(4) and Chunk(16), fp8-hopper Chunk(2) and Chunk(8), and
  bf16-hopper-wgmma Chunk(4) and Chunk(16). The Chunk(3) bf16-hopper regression also passes. m ranges from 24 to 30.
  The negatives include `wrong_counter`, `next_block_acc_in_differs_from_committed_acc`,
  `committed_acc_differs_from_block_acc_out` and `y16_public_forged`.
- **wgmma pin 12c3c8d3:**
  - The hash reproduces, and the rows are identical to bf16-hopper's da1bbe2c; only the header name differs.
  - 400 units showed 0 mismatches between the pinned circuit and `tc_dot_total(HOPPER_BF16_WGMMA_K16)` with the F2fpBf16
    epilogue.
  - About 300k non-NaN words showed 0 mismatches between F2fpBf16 and f32_to_bf16.
- **Conditions:**
  - **CN1:** NV1 (red-team-flock-2) must land before any Chunk(n) cell is labelled.
  - **CN2:** m ≤ 35 per proof, that is, n × VUs ≤ 32,768 blocks. That is 2,048 VUs at Chunk(16) and 4,096 at Chunk(8).
    Larger proofs need the Ligerito bound re-derived.
  - **CN3:** Chunk(1) is not granted. `Layout::of` accepts 1024-byte rows, but a lone chunk needs the ROOT flag, which
    this block does not set. `Layout::of` should refuse Chunk(1).
  - PB1–PB4 carry over: the verifier generates its own instance files, and verifier identity is required.
- **Labels:** a `finding` label on the evidence arts aeb39daf, 0f5e418a, 854209a6, 71e39af5, 29e1ccf1, 511a98d2,
  8b8f7378 and e52774ac. These are selftest runs, not cells, so no proof_class label.
- **NVFP4:** the layouts (Fp4 and ShaFp4, notes 0236Z, 0255Z and 0300Z) were left to red-team-flock-2 as instructed.
