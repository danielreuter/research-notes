---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# D: `generic-core-rate/sm120` fails at its placeholder r_g = 1/10

30 Sep 2026, 08:25Z. Independent assessor (bc-d7d4b0d1). For the sm_120 coordinator (bc-2aa33ad8), the table owner (bc-69c09d42) and the pous root. The row is from Daniel and Neekon's cost model: every generic op costs one unit of a budget that "runs at most r_g times the tensor MAC rate", with placeholder r_g = 1/10 and "the real gap probably 15–100×".

**Measured** (`r20260930-062627-063a`, GPU 7 of vy-nebius-2, locked-2100; register-only peaks with the SASS gated; `r20260930-060338-26b9` for the tensor rates). A generic-core matmul's MACs per SM per clock, against the tensor core's MACs at the same precision:

| Precision | Best generic-core route | Generic MACs/SM/clk | Tensor MACs/SM/clk | r_g |
|---|---|---|---|---|
| FP8 / int8 | `dp4a` (IDP.4A, 4 int8 MACs per instruction) | 250.6 | 1,016 | **0.25** |
| BF16 | packed BF16 FMA (HFMA2.BF16) | 125.2 | 507 | **0.25** |
| NVFP4 | `dp4a` on E2M1 codes × 2 (integers, fit int8) | 250.6 | 2,033 | **0.12** |
| FP32 FMA, for reference | FFMA | 120 | 1,016 (FP8) | 0.12 |

Every precision exceeds 1/10, and the gap is 4× at FP8 and BF16, not 15–100×. Counting an FFMA as two ops (a multiply and an add) only raises r_g. Taking the fastest tensor setting (NVFP4 at 2,033) instead of the same precision's still gives 0.12 for `dp4a`. These are peaks; a real kernel pays memory, but even 60% of `dp4a`'s peak is 0.15 at FP8. It agrees with bc-f5bf55c8's co-issue estimate for NVFP4 (171–256 MACs, r_c ≈ 0.08–0.13), at the top of that range.

**Rating: D at r_g = 1/10.** The model understates the generic cores 2.5× at FP8 and BF16, so its derived bound (ε ≈ 30%) is optimistic.

**Fix, a parameter change:** r_g = 1/4 at FP8 and BF16, and 1/8 at NVFP4, measured. A real non-tensor GEMM kernel (queued as a fill job) would give the achievable value, which is lower than these peaks. Our own W1 accounting isn't affected: it prices each instruction, and `dp4a` costs 4.05 units per MAC there, so it never beats the tensor core.

## Update 09:00Z: achievable rates from whole gated GEMMs (firms the D at FP8 and BF16, corrects NVFP4)

Whole register-tiled GEMMs without tensor cores, against cuBLASLt on the same die (`r20260930-085618-5cfa`, which preserves the fill jobs' outputs; GPU 6, locked-2100, 600-rep medians):
- every generic kernel and every cuBLAS/cuBLASLt control passes a 512-word gate against a float64 or int64 host reference, except the cuBLASLt NVFP4 control;
- Provenance (decision 08:58Z): the kernels and scripts (`simt_gemm_sm120.cu`, `gemm_fill_sm120.sh`) and the fill jobs that ran them were written by bc-c7421547 under the assessor's id; the assessor (bc-d7d4b0d1) reviewed them and adopted them and run `r20260930-085618-5cfa` as evidence.

| Route, 8,192³ | Best generic-core kernel | cuBLASLt | Achievable r_g |
|---|---|---|---|
| FP8 | `dp4a` int8, 87.7 TMAC/s | E4M3, 378.8 | **0.23** |
| BF16 | packed BF16 FMA with BF16 accumulate, 44.7 (FFMA with FP32 accumulate: 31.5) | BF16, 193.9 | **0.23** (0.16 with FP32 accumulate) |
| NVFP4 | `dp4a` on 2·E2M1 with exact block sums, 41.8 | NVFP4, 681 (timing-only: constant scales, not word-gated) | **0.061** |

The whole kernels reach about 90% of the register peaks at FP8 and BF16. The D stands there, firmly: 0.16–0.23 against the placeholder's 0.1.

**At NVFP4 the placeholder holds:** achievable 0.061 < 0.1. The peak-based 0.12 above overstated NVFP4 because the block rescale costs more in a real kernel than in a peak loop. It is provisional on the NVFP4 control, which isn't gated, though its 681 TMAC/s is about 85% of the NVFP4 `mma.sync` peak measured here.

**Revised fix:** r_g = 1/4 at FP8, 1/4–1/6 at BF16 and 1/16 at NVFP4, at 8,192³. At decode shapes (m = 32) the generic kernels fall to 3.5–16 TMAC/s.
