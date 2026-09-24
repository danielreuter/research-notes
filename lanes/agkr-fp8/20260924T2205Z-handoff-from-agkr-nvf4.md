# agkr-nvf4 -> agkr-fp8: GKR phase 2 was ~45% of the A-GKR prove on the 5090; one additive kernel fixes it (lane/agkr-nvf4 a8d471ba)

From agkr-nvf4, 22:05Z. This is probably worth taking for the FP8 cells too; it is a small change to shared files.

- Measured with sync timers around the prover (my `evidence/pod-scripts/05_profile.py` wraps `bench_result.main`): in `gkr._phase2`,
  `vf = mm_mod(ec.T, rows)` (the (6 x 2^17) @ (2^17 x 1024) fold of the layer input with eq(c*, .)) took **110 ms per layer**
  on the RTX 5090 (four float64 limb matmuls with M = 6; FP64 is slow on consumer parts). Over 4 unit layers that was 0.44 s of a 0.93 s prove.
- a8d471ba adds `gpu/kernels.py eq_rows_dot` (a Triton split-row dot, the same 32-bit-halves int64 accumulation as
  `row_code_dot_kernel`) and hooks it as `field._fast_eq_rows_dot`, which `gkr._phase2` uses on CUDA. The torch path is unchanged
  otherwise. It is bit-exact against `mm_mod` on 7 shapes, including P-1 extremes, and the fp4-nvf4 proof bytes are identical
  (sha256 fec5fc23... before and after). On my dev tree the fp4-nvf4 t.total went from 0.97 s to 0.53 s, and t_arith from 0.58 s to 0.14 s.
- Files: `backends/gkr/gpu/kernels.py` (+88, new kernel + wrapper), `field.py` (+2 hook lines), `gkr.py` (+3, the `if` around `vf`).
  To take it: `git cherry-pick a8d471ba`. It is independent of my multi-public chain change (3c769c6d and earlier).
- The FP8 layers are larger (48 steps), so the saving should be at least as big. On the 4090, FP64 is 1/64 rate as well.
