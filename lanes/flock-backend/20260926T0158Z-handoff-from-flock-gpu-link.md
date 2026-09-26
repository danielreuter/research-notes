---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T01:58Z
---

# gemm_coordinate K = 2048 on the 4090 (fp8-ada): layout Chunk(2). CPU and GPU selftests pass; 4,096 VUs in 0.42–0.44 s

- **Layout.** `Chunk(n)` generalises the K = 1536 BF16 layout (which is `Chunk(3)`, statement unchanged) to any row of
  whole BLAKE3 chunks, with 32 units per chunk. Each block is (VU, chunk): 16 + 16 compressions and 32 units, `k_log` 20.
  Cross-chunk accumulators are committed public words.
  - An 8-bit K = 2048 row (2,048 bytes, 64 units) is `Chunk(2)`; K = 8192 is `Chunk(8)`. 16-bit K = 2048 is `Chunk(4)`,
    and K = 8192 is `Chunk(16)`.
  - `Layout::of(row_bytes, units)` picks it from the instance file, so your writer needs no new fields. Set `k`, `units`
    (K / 32 or K / 16) and `row_bytes`.
  - For layouts other than `Chunk(3)`, the statement digest adds the tag "layout chunk: …, n chunks per VU".
- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ 758a8edf, SM = 89.
- **Inputs.** fp8-ada has no captured sets, so these are synthetic E4M3 operands, 2,048 words each, drawn with
  `rng([seed, i])` and chained with `tc_dot` (ADA_E4M3_M16N8K32). I made them with `inst_k.py`, which calls your
  `instances.statement` with K = 2048. The netlist is e66262a0, unchanged.
- **Evidence:** RTX 4090, loopback verifier, run r20260926-015154-6860, art:aeb39daf (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m24) and 64 VUs (m27).
  - 2,048 VUs (m32): 0.23–0.26 s end to end.
  - 4,096 VUs (m33): **0.42–0.44 s**, about 9.5 k VU/s.
  - The two reps prove in 0.24 s and 0.17 s.
  - 4,096 VUs is the most that fits in 24 GB. Larger batches are a union over sub-batches.
- **For the cell:** use the captured-set batch size for this K, 6,272 VUs from #101's `gemm-coordinate-*-k2048`, as two
  sub-batches on the 4090. Its synthetic stream at K = 2048 is `flock-gpu-link-synthetic-fp8-ada-k2048` in my file. Name
  yours as you prefer.
