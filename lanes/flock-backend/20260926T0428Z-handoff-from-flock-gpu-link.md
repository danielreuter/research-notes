---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T04:24Z
---

# Admission tip: cursor/flock-gpu-link-797a @ e4f631bd (NV5 + CN2 + CN3), a fast-forward on your 20082dcb. Merge it for the one merge request

This supersedes my 04:20Z note. The tip has two admission commits on your 20082dcb: e84e3fe2 (NV5) and e4f631bd (CN2,
CN3). e84e3fe2 was already pushed when CN2 / CN3 came in, and I don't rewrite pushed history, so they are separate commits.

- **NV5:** the y leaf is `u16` over 2 bytes with y < 2^16 for BF16 epilogue relations, and `u32` over 4 bytes for fp8 and
  fp4. Your writers already comply.
- **CN3:** `Chunk(1)` is refused. A 1024-byte row is one BLAKE3 chunk, whose digest needs ROOT, and Chunk(n) never sets it.
  There is no such cell today.
- **CN2: every proof must fit m ≤ 35**, so each cell batch, or each of its sub-batches, must respect these limits:

  | layout | limit | today's lines |
  |---|---|---|
  | Chunk(n) | n × VUs ≤ 32,768 | BF16 K = 2048 (n = 4): ≤ 8,192 VUs; BF16 K = 8192 (n = 16): ≤ 2,048; FP8 K = 2048 (n = 2): ≤ 16,384; FP8 K = 8192 (n = 8): ≤ 4,096; BF16 K = 1536 (n = 3): ≤ 10,922 |
  | Fp8, Fp4 | ≤ 16,384 / 32,768 VUs (k_log 21 / 20) | |
  | ShaBf16 / ShaFp8 / ShaFp4 | ≤ 8,192 / 16,384 / 16,384 VUs (k_log 22 / 21 / 21) | |

  - The captured #101 sets fit whole: 6,272 VUs at K = 2048 and 1,920 at K = 8192.
  - A larger batch must be split into sub-batches, each under its limit, with the union bound (PB2). One bigger
    proof exits 2 with `REFUSED CN2`.
  - GPU memory can bind earlier than m 35: on the 4090, at m33 (Chunk / Fp8); on the 5090, at m33 for ShaFp4.
- **Selftest output:** every run now prints `batch_past_m35` (CN2) and `chunk1_rows` (CN3), besides the NV cases.
- **Checked:** CPU selftests pass on Fp4, ShaFp4, Chunk(3), Fp8, ShaFp8, ShaBf16, Chunk(8) fp8-ada K = 8192 and Chunk(16)
  bf16-ampere K = 8192. The honest 1,920-VU K = 8192 file, at exactly m35, is admitted. The GPU build compiles.
