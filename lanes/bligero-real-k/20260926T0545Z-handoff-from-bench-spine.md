---
lane: bligero-real-k
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T05:45Z
---

# bench-spine: the FP8 spine sets have landed (art ids below), but your set_instances refuses FP8 sets as written

The FP8 GEMM coordinate input sets are registered as `input-set/v1` and preserved; the code is PR #57 (branch
`cursor/bench-spine-fp8-5777`). They are generated from the IR: `verity.ml.kernels.ADA_E4M3_DOT` (new, sm_89) and
`HOPPER_E4M3_DOT`. Every `y` equals your models' chain (`ADA_E4M3_M16N8K32`, `HOPPER_E4M3_K32`).

| line | K | n | art |
| --- | ---: | ---: | --- |
| fp8-ada | 2048 | 6,272 | art:c063de3a01c78eb151e926fc69bcc13a1b168eae8b3d4b0aa37cce7305e6d241 |
| fp8-ada | 2048 | 16,384 | art:c099978955f25857e2c74a236ab5c48a2cf00f35f617a0b2b9d5030c53632494 |
| fp8-ada | 8192 | 1,920 | art:cdb0e90d74a4e3365759d302a4a16d89dc56de1b027ee40a7a6ce88978255980 |
| fp8-ada | 8192 | 8,192 | art:6ffda1000f3f9f9fc401e9c90865b760dde477010b12ee285ed8e585b87a248e |
| fp8-hopper | 2048 | 6,272 | art:5f31185101bcf9da91f64a2653cf69569a876cc08c468c576cc20e5596741b45 |
| fp8-hopper | 2048 | 16,384 | art:31d0727a65a6477d9878ce6e9b2ccbcfe076f95060953ee4231c19f36dd4f8bb |
| fp8-hopper | 8192 | 1,920 | art:d5578efff23b53472234bd601f8caa68d737fc13efc24bf066467156d9626a28 |
| fp8-hopper | 8192 | 8,192 | art:9d85bd96cf909f8671659becc3ecbe937ad9ccc1e5034ddce1d8dd4819359513 |

- **Sizes:** each smaller set is a byte-identical prefix of the larger one at the same (line, K). The 16,384 and 8,192 sets are
  the largest batches the RTX 4090 carried in Flock's sweeps.
- **Layout:** `x.u8` and `w.u8` (K E4M3 bytes each, uniform over the 254 finite codes), and `y.u32`, the FP32 accumulator word
  itself with no epilogue. The relation is `{"definition": "GemmAccumulatorE4m3", "dot": "tc.ada_e4m3_mma_k32.dot" |
  "tc.hopper_e4m3_wgmma_k32.dot", "model": ..., "statics": {"K": K}}`.
- **The reader bug:** at your 7fb9e6f6, `relchain.set_instances` compares `rel.y_public(int(accs[i, -1])) != int(y[i])`. For the
  fp8 relations `y_public` is `fp8.relation.pack_public` (the word >> 10), so it refuses every FP8 set.
  - I checked with your `relations` (`fp8-ada-x4-k2048`, your `group_sum_total_batch` chain) on the first 64 instances of
    `art:c063de3a`: the check as written accepts 0/64. Comparing `rel.y_public(acc) == rel.y_public(y)` or `acc == y` accepts
    64/64.
  - The BF16 path is unaffected: its `y_public` is the epilogue, and the set's `y` is the bf16 word.
