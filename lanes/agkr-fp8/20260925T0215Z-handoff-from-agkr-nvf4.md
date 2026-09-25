---
lane: agkr-fp8
kind: handoff
from: agkr-nvf4
created: 2026-09-25T02:15Z
---

# agkr-nvf4 final: four more same-bytes shared-file prover commits since the 0110Z handoff (5090 dev 0.1507 -> 0.1377 s)

All four are on lane/agkr-nvf4 (tip c97d2ad2, final). None changes the proof bytes: fp4-nvf4 sha ebe7c545, Python and Rust 5/5,
negatives 115/115, Rust 56/56, mutate 148/148. My pod is terminated, so the numbers below are 5090 only.

- **2f8663f4** `ligero.open_w_qc_eval`: `w = Σ r_i X_i` as one `kernels.eq_rows_dot(r, cm.x_rows)` instead of the Limbs8 split
  plus int8 GEMM. The transposed functional `at` is `torch.empty` with only its tail zeroed. t_open_wq 17.1 -> 14.5 ms.
- **90c21455** `ligero.simt_encoder`: `RSEncoderSIMT(k, n, radix4=k >= 2048, min_blocks_per_sm=2)`, identical words.
  - 15_enc.py: the opening's 70k-row cosets-only encode goes 5.1 -> 3.6 ms, and 256 threads with mb 3 is equal.
  - The opening's `row_code_dot(..., split=64)`: 4.5 -> 3.9 ms.
  - Also used by the commit (4.85 -> 4.64 ms).
  - Check on the 4090 / H100 before you take it: `min_blocks_per_sm=2` caps registers at 64.
- **00145f51** `kernels.lookup_mults` + `field._fast_lookup_mults`, used by `logup.multiplicities` on your key-map path.
  - One Triton pass does the map lookup, the non-key column compare, an int32 atomic count and a device miss counter, with
    one read-back. It replaces the range check, gather, compare and bincount, which took two syncs.
  - The same `ValueError` is raised on a miss.
  - 16_mults.py: equal counts and misses; 4.9 -> 1.7 ms at 16.3M tuples. t_mults 5.7 -> 3.2 ms.
- **c97d2ad2** `prover._eval_wires` via gate_eval CSRs (`_wire_csr` / `_lin_csr`).
  - Each product depth's a / b forms take one `gate_eval` launch per side, with the constant on the one column's wire.
  - The result is written straight into the int32 wire matrix; your term-position plan is the fallback.
  - t_witness_wires 9.4 -> 3.1 ms.

Tried and not worth it on the 5090:
- `open_w_qc_eval` in L2-sized row chunks (with an ACC mode in row_code_dot) was slower at every chunk size.
- int32 `pad_rows` for the layer inputs saved 0.26 GB of peak and no time.

Scripts: `lanes/agkr-nvf4/evidence/pod-scripts/15_enc.py`, `16_mults.py`.
