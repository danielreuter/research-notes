---
cursor:
  subagentId: "bc-fb55a759-0d1c-55f4-a2da-04aadde30be9"
---

# Pearl-C's FP8 mainloop on sm_120 (a header GPU 1's kernel adopts)

Worker bc-fb55a759. Goal: `gemm_pearlc`'s mainloop at cuBLASLt's plain FP8 rate (757 TFLOPS at 8,192³, locked-2100), every C̃
word unchanged. Branch `cursor/pearl-c-fp8-mainloop-0be9`, stacked on GPU 1's `cursor/pearl-c-sm120-b44b` (`af274df9`).
GPU 1 (bc-18346d9c) owns the kernel, scheme and arm; GPU 2 (bc-7442ca43) the epilogue. I own the mainloop only.

## Checkpoints

- 07:55Z: started. Toolchain on this VM (nvcc 12.9.86, research CLI from `main`); node 2 reachable, `ncu` in `/usr/local/cuda`.
  Read GPU 1's kernel at `af274df9`: 128 × 128 tile, 8 warps (64 × 32 each), 64-byte stages × 4 by `cp.async` into a swizzled
  layout, `ldmatrix`, one `__syncthreads` per stage, 1 CTA/SM. Its SASS per stage: 32 QMMA, 12 LDSM, 4 LDGSTS, 1 BAR.
- 08:07Z: first drop `de18f07b` (restacked on GPU 1's `952e3ecc`): `mainloop_sm120.cuh`, CUTLASS's sm_120 warp-specialized
  schedule: a TMA producer warpgroup (setmaxnreg 40) and 8 consumer warps (232), 128-byte SWIZZLE_128B stages × 3 (99,376 B)
  on full/empty mbarriers, no block barrier, fragments one atom ahead, each window's FADD issued with the next window's first
  MMAs (from +0). ptxas: no spill in the loop (4 bytes once per tile at G = 4). First device job `r20260930-080635-d449`
  (one GPU, untimed): C̃ of `ml_ct` / `ml_ct_u` vs the fixture (CPU twin) on 1, 3 and all CTAs and vs `gemm_ct` / `gemm_ct_u`
  at 8,192³, diagnostic timings of what passes, an ncu profile (`--clock-control none`).
- 08:15Z: `d449` (GPU-fb680060): gates passed; Measured one-GPU diagnostic (events around one launch, round-robin) at 8,192³:
  `ml_ct` (v1) 1.597 ms, `ml_ct_u` (v2) 1.475, against `gemm_ct` 2.120 / `gemm_ct_u` 2.033 in the same run. ncu: tensor pipe
  active 92.4% (v1) and 97.4% (v2), GPU 1's 66–69%; v1's loss is ptxas bunching each window's 64 FADDs.
- 08:25Z: `r20260930-081946-0f13` (U knob `21a466c9`) and `r20260930-082731-bebf` (LATE release + skewed schedule
  `6bbd087a`): `ml_ct` 1.544 ms (712 TFLOPS), `ml_ct_u` 1.466 (750), `gemm_ct` 2.115 (Measured diagnostic, bebf). Skewed
  schedule slower (1.586 / 1.489, spills). Unroll-2 at G = 4 (`ml_ct_x2`, `_x2e`) failed the 8,192³ gate non-deterministically:
  not timed.
- 08:50Z: `r20260930-084600-778b` found the race: a consumer's empty-barrier arrive can overtake its own queued ldmatrix of
  that stage, so the next TMA refill lands under the read (one 16-byte fragment row wrong, always row block 3: the tile's last
  stage's last A ldmatrix sits right before the arrive in the unroll-2 SASS). A `fence.proxy.async.shared::cta` before each
  release: 0/40 unroll-2 GEMMs wrong (25/40 without; a fence after the wait or a CTA membar don't help). Unroll-1 kernels were
  clean 40/40 but only because ptxas happened to wait on every scoreboard before their releases. Fixed in `7b417ee7`
  (`mbar_release`); gates at 40 repeats + timing of fenced vs unfenced in `r20260930-085511-2370`.
- 09:20Z: `2370` (GPU-5f1149a4): the fenced build passed every gate, the unroll-2 kernels 40/40 at 8,192³; the fence is free
  (`ml_ct` 1.5496 fenced, 1.5502 unfenced). Measured one-GPU diagnostic: `ml_ct_x2` (v1) 1.5388 ms (714.5 TFLOPS),
  `ml_ct_u` (v2) 1.4707 (747.6), `gemm_ct` 2.1148, `gemm_ct_u` 2.0269. v2 is at the target; v1 needs about 0.6% more. The SASS
  says why v1 lags: QMMA is fixed-latency, 16 cycles apart per warp, and a warp's loop costs 1.066 (`ml_ct`), 1.049 (`x2`)
  of 16 × its QMMAs in stall cycles against 1.02-1.03 for v2, and the two warps sharing a sub-partition run in lockstep, so
  their FADD bursts coincide. No packed FADD on sm_120 (`add.rn.f32x2` lowers to two FADDs). `cb272bf1`: `RP`, the producer's
  registers (24 gives the consumers 240: `ml_ct_x2r` spills 8 bytes against `x2`'s 184, and its loop costs 1.024).
  `r20260930-091857-c47a`: gates and timing of `x2r`, a start delay for warps 4-7 (so partners' bursts interleave), the
  128 × 64 / 64 × 64 / 128 × 32 tiles, and cuBLASLt's FP8 GEMM (the harness's `lt.cu`) in the same round-robin.
- 09:35Z: `c47a` never ran (`research run` has no `--detach`); rerun as `r20260930-092248-2bb1` (GPU-4352a609): every gate
  passed. Measured one-GPU diagnostic, cuBLASLt 13.1.1.3 in the same round-robin: `ml_ct_x2r` (v1) 1.5307 ms (718.3 TFLOPS,
  1.036× cuBLASLt's 1.4778), `ml_ct_u_x2` (v2) 1.4755 (0.998×), `gemm_ct` 2.1195. The start delay changes nothing (x2r
  1.5313 / 1.5312 at 512 / 1,024 cycles): not lockstep. Panel attempts 34, 35 (v1-h1 / v2-h1, estimated). `356313e9`:
  `WM_ROWS` (16 gives 64 × 64 and 128 × 32 on 8 warps) and no alignment slack (so two 128 × 64 blocks of 2 stages fit an SM).
- 09:55Z: `r20260930-093112-4085` (GPU-5f1149a4): v1 1.5214 ms (722.7 TFLOPS, 1.033× cuBLASLt's 1.4724), v2 1.4667 (0.996×),
  every gate passed. The other tiles pass every gate but are slow: 128 × 64 at two blocks per SM 1.93-1.96 ms, 64 × 64 on 8
  warps 2.55, 128 × 32 3.19; cuBLASLt's own 128 × 64 algorithm takes 1.86 ms and its 64 × 64 2.46 (128 × 128 1.51, 128 × 256
  1.49). `r20260930-094247-446d` (GPU-1cd543c7): steady batches of 200 at the 600 W cap: v1 1.5055 ms at 2,085 MHz (3.139 M
  cycles), v2 1.4584 at 2,070 (3.021 M), cuBLASLt 1.4527 at 2,062 (2.997 M); ncu (`--clock-control none`): v1 3,131,004
  cycles, v2 3,015,672, tensor pipe 93.6% / 97.1%. So v1's last 3.5-4% is cycles, not clock: at 240 registers v1 is a few
  short (ptxas turns one A-fragment buffer into just-in-time loads and spills one `ldmatrix` address, 8 bytes), and adds 0.75
  warp-cycles per QMMA of short-scoreboard and 0.42 of dispatch stall that v2 hasn't. No unroll-2 v1 without the tail compiles
  spill-free (compile sweep: unroll 1-4, early/late release, 232/240 registers, two offset encodings). `79074f61`: the bench
  beside the header. `0ea222cd`: the tail kernels (`ml_ct_x2r_tail`, `ml_ct_u_x2_tail`: spill-free), each checking every tail
  byte against its source, with a negative control; `r20260930-095646-a203` gates and times them.
- 10:10Z: `a203` (GPU-5f1149a4) and `r20260930-100116-01f0` (GPU-1cd543c7, `e0e84b25`): the tail is right on the device.
  The tail kernels pass the twin gate (1, 3, all CTAs) and 8,192³ 5/5 and 3/3. The negative control (`@bad`, the tail
  checked against depth [128, 256)) fails both, 1,536 and 1,048,576 words. The tail's own cost, held without the check
  (`@nochk`): v1 1.5339 ms against 1.5276 (+0.4%), v2 1.4785 against 1.4740 (+0.3%). So attempts 34 / 35 stand (the call
  drops 0.588 ms against 0.589). The check itself (serial global reads) costs 0.05 ms and is the bench's, not the interface's.
  Under sustained load the ratio moves with each kernel's clock at the 600 W cap: v1 1.036-1.068× cuBLASLt over three steady
  runs, v2 1.000-1.016×.

## Interface (header `356313e9`; bench `mainloop_bench.cu` / `.py` at `e0e84b25` is a working caller)

The header `benchmarks/pouw/pearl_c_sm120/mainloop_sm120.cuh` provides the tile's chain into the caller's registers, in the same
fragment layout `gemm_body` has now (warp tile 64 × 32, `total[MI][NI][4]` as mma.sync's m16n8 accumulators), so the epilogue
(C̃ stores, the peel, U, y, GPU 2's fused digests) keeps its arithmetic.

- **Adopt (prefill, 128 × 128):** `#include "mainloop_sm120.cuh"`, then
  v1 `using L = ml::Mainloop<128, 128, 4, 3, true, 1, 24>;` and v2 `ml::Mainloop<128, 128, 0, 3, true, 1, 40>;`, both
  with `ml.tile<2, true>(K, acc, total)`. The kernel is `__launch_bounds__(L::NT, 1)` (384 threads) with
  `extern __shared__ __align__(1024) uint8_t smem[]` and `L::SMEM` bytes of dynamic shared memory (98,352). Then
  `L ml(smem); ml.roles(maps, M, N, K, group);` and, per tile in `ml::raster` order,
  `float acc[L::MI][L::NI][4], total[L::MI][L::NI][4]; ml.tile<2, true>(K, acc, total);`. `total` is in gemm_body's layout:
  warp w < 8 at rows wm·64, cols wn·32 (wm = w / 4, wn = w % 4), element e of `total[mi][ni]` at row g + 16 mi + 8 (e / 2),
  col 2q + 8 ni + e % 2 (g = lane / 4, q = lane % 4). `mainloop_bench.cu`'s `ml_ct_body` is the whole caller.
- **The tail (the peel's rows):** `uint32_t p = ml.tail_wait();` gives P_A's 128 rows at `p` and P_B's 128 at
  `p + L::A_BYTES`, 128-byte rows in the SWIZZLE_128B layout (chunk c of row r at c ^ (r & 7)). Call `ml.tail_release()`
  once the epilogue is done with that stage.
- **Host:** four CUtensorMaps (A, B, P_A, P_B) as `ml::Maps` in device memory, UINT8 rank 2, globalDim {depth bytes, rows},
  box {128, TM} for A and P_A and {128, BN} for B and P_B, SWIZZLE_128B, L2 promotion 128B. `mainloop_bench.py`'s
  `Bench.tmap` / `Bench.maps` encode them.
- **After `roles()` only warps 0-7 are alive** (the producer warpgroup exits after its last TMA), so the epilogue can't
  use `__syncthreads`: use named barriers over 256 threads (`bar.sync 1, 256`).
- **Shared memory in the epilogue:** only the tail stage (32 KB at 128 × 128) belongs to the tile. The other two stages
  already hold the next tile's prefetch. GPU 2's quad-transpose scratch (8 KB per warp, 64 KB) doesn't fit. Either the
  digest uses the tail stage at 4 KB per warp (two 32-row halves), after a 256-thread named barrier that follows the peel's
  last read of P_A / P_B, or the consumers hold a second stage (this costs prefetch; not measured).
- **Spills (GPU 1's sass_gate refuses any):** with the tail, v1 and v2 compile spill-free (`ml_ct_x2r_tail`,
  `ml_ct_u_x2_tail`). v1 without it spills 8 bytes (one register, 1 STL + 1 LDL per two stages). In the kernel, with
  its epilogue, ptxas decides again. If `tile<2>` spills there, `tile<1, true>` is spill-free at about +1.6% (1.546-1.556 ms).
- **No `.FTZ` FP32 op in any `ml_` kernel** (the 09:34Z rule). Their only `.FTZ` is `F2I.FTZ.U32.TRUNC` of unsigned
  division. In the same build, GPU 1's `lines`, `plainq` and `stats_s5` carry `FADD.FTZ` from nvcc's own division and rsqrt
  sequences (no `-ftz` flag), which the harness's new SASS gate may flag.
- **The other tiles GPU 1 asked for (08:20Z)** are in the interface and pass every gate. 128 × 64 has 4 consumer warps
  (`CTAS = 2, RP = 24`: 232 registers each, 2 stages). 64 × 64 and 128 × 32 use `WM_ROWS = 16`: 8 warps of 16 × 32.
  All are slow at 8,192³ (Checkpoints, 09:55Z).
- **For K3 (two 4-warp CTAs per SM at 128 × 64):** 128 × 64 tiles cost about 25% of the mainloop on this part at 8,192³,
  and cuBLASLt's own 128 × 64 algorithm is as slow (1.86 ms against 1.49-1.52 at 128 × 256 and 128 × 128). So K3 in that
  shape would lose about 0.4 ms of mainloop to hide about 0.08 ms of hashing (Derived from those runs and GPU 2's 291 → 234
  W1/B). Two 3-stage pipelines fit 99 KB only with 64-byte stages, and v1's registers don't fit a 128 × 128 tile on 4 warps,
  so I see no K3 shape that keeps this mainloop's rate.

## Results

**The mainloop is within 5% of cuBLASLt on a one-GPU diagnostic basis. v2 is at parity; v1 is 3.3-3.7% slower in
round-robin and up to 6.8% slower under the power cap.** All Measured, every gate passed first. Round-robin single launches
against cuBLASLt 13.1.1.3's best FP8 algorithm on the same operands, 8,192³, clocks locked at 2,100 by the owner:

| Run (GPU) | v1 `ml_ct_x2r` | v2 `ml_ct_u_x2` | cuBLASLt | GPU 1's `gemm_ct` |
|---|---|---|---|---|
| `2bb1` (4352a609) | 1.5307 ms (1.036×) | 1.4755 (0.998×) | 1.4778 | 2.1195 |
| `4085` (5f1149a4) | 1.5214 (1.033×) | 1.4667 (0.996×) | 1.4724 | 2.1152 |
| `446d` (1cd543c7) | 1.5273 (1.037×) | 1.4692 (0.998×) | 1.4724 | 2.1192 |
| `a203` (5f1149a4) | 1.5278 (1.033×) | 1.4714 (0.995×) | 1.4793 | 2.1185 |
| `01f0` (1cd543c7) | 1.5276 (1.036×); with tail 1.5339 (1.040×) | 1.4740 (0.999×); with tail 1.4785 (1.002×) | 1.4749 | 2.1216 |

- **Other bases.** Under sustained load (200 back to back, 600 W cap), v1 is 1.036-1.068× and v2 1.000-1.016×. In ncu
  cycles (clock-free), v1 takes 1.038× v2's.
- **Against the harness's divisor.** At the round-robin ratios, the harness's 1.4457 ms (757 TFLOPS; another method and
  run) puts v1 at about 1.493-1.504 ms (731-736 TFLOPS) and v2 at about 1.439-1.449 ms (Derived).
- **Not harness-timed.** Its timed number comes with GPU 1's adoption, in the `-h1` arm.
- **Against GPU 1's current chain.** The mainloop is 1.38-1.39× faster (v1) and 1.38× (v2).
- **What v1 has left:** 3.5-4% of cycles, register-bound (Checkpoints, 09:55Z). ptxas is a few registers short at 240, the
  most the 384-thread split leaves.

## Needs

1. **GPU 1 (bc-18346d9c):** adopt the header at `356313e9`, per the Interface section; `mainloop_bench.cu` is a working
   caller. Measured rows come from your `-h1` arm, with the verifier and per-rep clocks.
2. **GPU 2 (bc-7442ca43):** the digest's scratch has to fit in the tail stage (32 KB, 4 KB per warp, after a 256-thread named
   barrier); say if the quad transpose can't.
3. **Coordinator:** a draft PR for `cursor/pearl-c-fp8-mainloop-0be9` (base `cursor/pearl-c-sm120-b44b`). This VM's `gh`
   is read-only.
