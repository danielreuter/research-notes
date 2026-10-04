---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `dense-matmul-hardness/sm120` (δ = 0.25): — until its accuracy check is stated

30 Sep 2026, 08:25Z. Independent assessor (bc-d7d4b0d1). The row says that for random dense matrices any algorithm meeting "the required accuracy" performs at least (1 − δ)·mkn multiply-adds, over both kinds of core, with placeholder δ = 0.25.

**The answer turns entirely on the unstated accuracy check:**
- **Bit-exact (Pearl-C's check): δ = 0.** No rewrite reduces the multiply-adds. Strassen's pre-adds leave FP8, so its sub-products run at FP16's 2.00 per MAC, and the cheapest bit-exact route costs 1.80× the chain (`no-exact-rewrite/sm120-e4m3`, B; `r20260930-060338-26b9`, `r20260930-055203-10e8`).
- **Ordinary accuracy** (FP32 accumulation with a relative tolerance): L Strassen levels do (7/8)^L of the multiply-adds, which is textbook. Two levels save 23%, inside δ = 0.25, but three save 33%, and FP32-accumulated Strassen at three levels usually meets a loose tolerance on random matrices. The placeholder then survives only a check strict enough to forbid a third level. Rank-48 4 × 4 schemes (0.75 per level) break it at two.

**Rating: —** (not rateable until the check is named). The measurement that pins it is the one queued: the fastest Strassen kernel that passes the named check.

## Update 09:00Z: a timed one-level Strassen

A one-level Strassen of E4M3 with FP16 cuBLASLt sub-products (pre- and post-adds timed; a time bound, not bit-exact) runs at 136.5 effective TMAC/s at 8,192³ and 178.3 at 16,384³. cuBLASLt E4M3 runs at 378.8 and 389.4 (`r20260930-085618-5cfa`). So Strassen is **2.2–2.8× slower** than the plain FP8 GEMM, past the 1.80× bound computed from instruction rates, since a real kernel also pays its adds and memory. At FP8, ordinary accuracy included, one Strassen level saves nothing here, so δ ≤ 0 from Strassen on this card at these shapes. The rating stays — until the accuracy check is named, but no named check can make Strassen pay at FP8 on sm_120.

Provenance (decision 08:58Z): the kernels and scripts (`simt_gemm_sm120.cu`, `gemm_fill_sm120.sh`) and the fill jobs that ran them were written by bc-c7421547 under the assessor's id; the assessor (bc-d7d4b0d1) reviewed them and adopted them and run `r20260930-085618-5cfa` as evidence.
