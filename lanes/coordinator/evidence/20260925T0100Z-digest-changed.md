Daily digest, Thu Sep 24. Compared with this morning's 11:00 AM PT render (main `22741456`). Every change below is independently verified (verify-po) unless marked.

- **Table 2, A-GKR column: all three gaps filled (was 2 of 5 rows, now 5 of 5).**
  - H100 FP8: — → **1.1e8×** (0.688 s, art:2e7baba7).
  - RTX 4090 FP8: — → **3.0e7×** (1.13 s, art:1b4fd4a1).
  - RTX 5090 NVFP4: — → **2.5e7×** (0.1905 s, art:49757870). **PROVISIONAL, pending red-team-lk:** its statement uses circuit rewrites (merged tagged lookup table, depth-1 flatten) now under independent red-team; pulled if a hole is found. (Table 2's renderer is frozen and has no marker, so the flag lives here.)
- **Table 2, B-Ligero column: four rows faster** (lane arith's arithmetic-phase kernels and full warm-up pass):
  - RTX 4090 FP8 2.4e6× → **2.2e6×** (0.0907 → 0.0840 s, art:bb75ba4f).
  - A100 BF16 6.0e6× → **5.9e6×** (0.2413 → 0.2374 s, art:5bcbf3fb).
  - H100 BF16 1.0e7× → **8.9e6×** (0.1292 → 0.1131 s, art:e3362256).
  - H100 FP8 1.2e7× → **1.1e7×** (0.0738 → 0.0706 s, art:709ab20c).
- **Table 2, unchanged:** SP1 column (empty: SP1 cannot reach 2^-128, see D1), B-Ligero + in-proof hash column, A100/H100 BF16 A-GKR.
- **Table 3:** new A-GKR rows for H100 FP8, 4090 FP8 and 5090 NVFP4; the four faster B-Ligero cells' phase splits.
- **D3 (verifier cost): all 12 cells measured** (was 1 measured + 11 placeholders). The four H100 rows now use a live verifier on a separate host in the same datacenter (before: on the prover's own pod). Verifier CPU per batch, e.g. A100 BF16 B-Ligero 0.845 s (placeholder) → 8.56 s; H100 BF16 B-Ligero 7.0 s (loopback) → 8.72 s (77 cores to keep pace); 4090 FP8 B-Ligero 0.227 → 2.26 s; 5090 NVFP4 B-Ligero 0.246 → 1.67 s; A-GKR A100 / H100 14.6 / 13.8 s (CPU re-verification). Live tax 1.00–1.37×.
- **D1 (security):** SP1 reaches only ~100 bits, capped by its field, and cannot reach 2^-128 without protocol changes: SP1 stock ~2^-94.5 per proof (A100, 22 shards), SP1 precompile ~2^-96.0 (8 shards), 2^-99.0 per shard. A-GKR GPU row now names SHA-512 Merkle. Rows renamed "SP1 stock" / "SP1 precompile" (Table 2's frozen footnote still reads "modified SP1 (TC_DOT chip)").
- **D2:** shows the fastest *verified* result per cell (e.g. SP1 precompile A100 4.26 s unverified → 5.81 s verified). New row "SP1 stock, FRI query count raised": A100 BF16 21.05 s (stock 18.52 s), still only 2^-95.46 per proof.
- **Held out of Table 2 (not yet counted):** 4090 FP8 A-GKR 0.490 s (art:45c5be4a) on a rewritten statement, waiting for verify-po and red-team-lk.
