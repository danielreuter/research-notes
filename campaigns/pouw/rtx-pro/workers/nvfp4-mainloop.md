---
cursor:
  subagentId: "bc-fb55a759-0d1c-55f4-a2da-04aadde30be9"
---

# The NVFP4 block-scaled mainloop on sm_120 (the plain NVFP4 baseline and Pearl-C4's arm)

Worker bc-fb55a759. Goal: one header that both the plain NVFP4 baseline and Pearl-C4's arm use, taking the plain GEMM from
CUTLASS's 86.4% of peak (the harness divisor, 0.78875 ms at 8,192³, `cutlass3x_nvfp4_256x128x128_coop`) to about 94%, every
word BLACKWELL_SM120_NVF4's. Branch `cursor/nvfp4-mainloop-0be9` (off `main`). GPU 5 (bc-71c6ab78) keeps the Pearl-C4
arm's other parts; the harness (bc-0de2d624) adopts the plain entry point if it beats the divisor.

## Checkpoints

- 10:45Z: `7aaa4240`: `benchmarks/pouw/nvfp4_sm120/mainloop_nvf4.cuh` + `nvf4_bench.cu` / `.py`. 256 × 128 tiles, 3
  stages of 128-deep (27 KB each: A and B by TMA SWIZZLE_64B, the scale atoms in CUTLASS's 128 × 4 layout by bulk copy),
  a producer warpgroup (setmaxnreg 40) and 8 consumer warps of 64 × 64 (232 registers), per-warp mbarrier release, no
  block barrier. Each lane's scales for 4 MMAs come from one LDS.128 (A: rows 32 apart; B: columns 32 apart). ptxas: spill-free
  words kernels, 64 OMMA a stage, no FP32 `.FTZ`. Found on the way: ptxas 12.9 lowers `cp.async.bulk.shared::cluster` to a
  CALL and then drops every `setmaxnreg` (C7506, consumers at 168 registers, 700 bytes of spill); `.shared::cta` fixes it.
  First one-GPU job `r20260930-104816-dbc8`: the gates (reference vs model, words, BF16 vs CUTLASS / cuBLASLt), then
  diagnostic timing of what passes.
- 11:20Z: gates pass (`r20260930-104816-dbc8`, `r20260930-105219-5dd8`, GPU-5f1149a4): the reference equals
  BLACKWELL_SM120_NVF4 (0 words differ), the header's words equal the reference at full grid / 1 / 3 CTAs and repeats, and
  its BF16 equals the reference rounded, CUTLASS 256 × 128 and 128 × 128, and cuBLASLt, at every shape and both scale
  ranges. Measured diagnostic (one GPU, 8,192³, steady batches of 100): CUTLASS 256 × 128 0.7866 ms (2,085 MHz, 1.640
  Mcycles), nv256_o 0.7689 ms (1.603 Mcycles), about 2.3% faster. Estimated in the harness's method: about 0.771 ms (88%),
  short of 94% (0.7232 ms). ncu (`--clock-control none`): tensor pipe 90.9% active (CUTLASS 88.3%); the losses are the
  epilogue (5.6% of consumer warp samples, 915 instructions a warp a tile, 4-byte stores throttled), the release fence's
  MEMBAR (1.7%), full-barrier waits (2%), and the tail (SM active 2.8% short of elapsed).
- 11:14Z: `f823c6bc`: a new epilogue, `store_bf16`: stmatrix into a 512-byte scratch per warp, then 16-byte stores of 32
  contiguous bytes a row; about 270 instructions a warp a tile, and no spill. `BK = 64` (7 stages of 13.5 KB, SWIZZLE_32B,
  released in pairs by one fence) for more pipeline depth. Job 3 (one GPU): gates, then timing, for nv256, nv256_o,
  nv256_k64 and nv256_k64_o.
- 11:35Z: job 3 (`r20260930-111405-3bf7`, GPU-5f1149a4): gates pass for all four. Measured diagnostic (steady batches
  of 100, 2,085 MHz): CUTLASS 256 × 128 0.7886 ms (1.643 Mcycles), nv256_o 0.7480 ms (1.559 Mcycles); the 64-deep stages
  about 0.92 ms (23% slower), dropped in `3c598d73`. ncu of nv256_o (`r20260930-111801-266a`, `--clock-control none`):
  tensor pipe 93.5% of active cycles (CUTLASS 88.3%), the epilogue about 3.3% of consumer samples (each 16-byte store
  waiting on its own LDS), the tail: SMs with 10 tiles of 11 at 85.8%. Then `492677191` (store_bf16 four blocks a round,
  their reads in flight together) and `8e3ca976` (`tile(K, acc, next)` loads the next tile's first fragments behind the
  last step's MMAs). Job 5 (`r20260930-112658-2c31`, GPU-5f1149a4): gates pass. Measured diagnostic, steady: CUTLASS
  256 × 128 0.7868 ms (1.641 Mcycles), cuBLASLt 0.8125 ms, nv256_o 0.7338 ms (1.530 Mcycles), 6.7% faster than CUTLASS;
  Derived: 93.3% of 4,096 flops/clk/SM × 188 SMs at 2,085 MHz, 92.8% of the harness's 1,614 TFLOPS. The 11-wave bound at
  8,192³ is 1.442 Mcycles.
  `9099aa2b`: `nvf4_plain.cu`, the plain entry points as the harness's registry entries (`verity_nvf4_256x128` and `_o`,
  kind 5, `phc_table_nvf4`), and a standalone `ph_cutlass_*` ABI under `-DNVF4_PLAIN_ABI`; `3239558c`: the bench gates and
  times such a library (`PLAIN_LIB`). The .so passes the harness's `sass_gate.py` (0 FP32 .FTZ), spill-free, 64 OMMA a
  kernel. Job 6: the plain entry points gated and timed beside CUTLASS.
- 11:50Z: job 6 (`r20260930-113420-cc3f`, GPU-5f1149a4): the plain entry points pass every gate (BF16 equal to the
  reference rounded at every shape and both scale ranges, GATE_REPEATS more at 8,192³; the header kernels equal them).
  Measured diagnostic, steady batches of 100: `verity_nvf4_256x128` 0.7298 ms (1.523 Mcycles), `_o` 0.7337 ms, CUTLASS
  256 × 128 0.7868 ms, cuBLASLt 0.8119 ms; Derived: 7.5% under the harness divisor (0.78875 ms), 93.3% of 1,614 TFLOPS.
  Job 7 (`r20260930-114329-edb6`): the same again (0.7303 ms), and per-warp clock64 stamps (`_t` kernels, D equal to
  `_b`'s): a tile's mainloop 136.3k cycles (median; 131.07k is the MMAs alone), its epilogue 2.1k, the two warps of an
  SMSP both in their epilogues about 1.1k; starting the second half's warps 512 to 2,048 cycles late gained nothing (the
  full barriers pull them back within a few hundred cycles), dropped in `72584dbf`. ncu (`r20260930-114646-5812`,
  `--clock-control none`): tensor pipe active 95.3% of active cycles for `nvf4_plain<0>` (94.3% of elapsed on the busiest
  SMs, the ones with 11 tiles), CUTLASS 88.3%; consumer samples: full-barrier waits about 2%, the rest the tensor pipe
  saturated. The last 0.7% to 0.7248 ms (94%) is spread over the epilogue overlap, the first tile's ramp and TMA latency
  variance; candidates: TMA multicast of A across a 2-CTA cluster (halves A's L2 reads), a test_wait path that issues a
  step's remaining MMAs before blocking on a late stage.
- 12:20Z: PR #543 open (draft). `cd81a045`: `LATE` (a warp whose next stage isn't full after its step's first group, by a
  `test_wait` voted across the warp, issues the other 24 MMAs before it waits; the next fragments' loads stay behind their
  groups, predicated on the vote, and one late load follows). A first form with two copies of the groups spilled 850 bytes
  (ptxas if-converted them); `LATE = 0` is byte-identical SASS for every existing kernel and plain entry. Screening now runs
  as fill jobs (node 2 `/workspace/pouw/fill/queue/`, prio 10, under 8 minutes), outputs under
  `/workspace/pouw/fill-out/nvf4-mainloop/<job>/`, snapshots under `/workspace/pouw/nvf4-mainloop/<sha>/`.
  Job `nvf4-late-2b91813c` (GPU-9f1f172d): every gate passes (0 words, 0 BF16 elements differ, every shape and scale range).
  Measured diagnostic, steady batches of 100, about 2,090 MHz: nv256_e_b 0.7268 ms (nv256_b 0.7344), nv256_o_e_b 0.7259 ms
  (nv256_o_b 0.7329); stamps: mainloop median 134.8k cycles a tile (139.6k without LATE), 133.6k for _o (136.3k).
  `bf9cf179`: the plain entries `verity_nvf4_256x128_e` and `_o_e`. Job `nvf4-plain-late-bf9cf179` (GPU-2b59d5fe, GPU 6;
  its header comment says two kernels and 8 steady rounds, it ran four kernels, 4 rounds and stamps: a parallel-edit slip):
  every gate passes. Measured diagnostic, steady, 2,085 MHz: `_o_e` 0.7272 ms (1.5164 Mcycles), `_e` 0.7284, the current
  `verity_nvf4_256x128` 0.7316, CUTLASS 256 × 128 0.7880. Derived: `_o_e` at 93.7% of 1,614 TFLOPS, 7.8% under the
  divisor; 94% is 0.7248 ms.
- 12:30Z: with LATE the epilogue (about 2.3k cycles a tile, 1.1k of it with both warps of an SMSP storing) is as large as
  the mainloop's remaining loss. `24c9aee5`: `tile_bf16`, the previous tile's BF16 store folded into the next tile's first
  step (each group's 4 accumulator blocks stored just before the group overwrites them; the last tile's by store_bf16).
  `46e57454`: the bench's BF16 gate also at 1 CTA, 3 CTAs and repeats (the folded path runs only between a CTA's tiles).
  `2d9c4018`: nv256_ef, nv256_o_ef; `3f7b3edf`: plain `verity_nvf4_256x128_ef` and `_o_ef`. Spill-free, 128 OMMA, sass gate
  pass; the other entries' SASS unchanged. Job `nvf4-fold-3f7b3edf` queued.
- 12:40Z: job `nvf4-fold-3f7b3edf` (GPU-af0bf9e0): every gate passes, the BF16 one now at full grid, 1 and 3 CTAs and
  repeats. Measured diagnostic, steady, 2,085 MHz: the fold is 2.2% slower (`_o_ef` 0.7425 ms, `_o_e` 0.7262 ms, CUTLASS
  0.7876); stamps: tile period 140.4k cycles against 136.7k. Likely cause: the stage release's MEMBAR.ALL.CTA (from
  fence.proxy.async) now follows the step's 16 global stores and waits for them. `3700375c` drops it (header, kernels and
  plain entries back to bf9cf179's; the BF16 gate at every grid stays). Job `nvf4-ncu-3700375c` queued: ncu
  (`--clock-control none`) stall samples per instruction for the plain `_o_e`, `verity_nvf4_256x128` and nv256_o_e_b.
- 13:03Z: job `nvf4-ncu-3700375c` (GPU-5f1149a4): gates pass. ncu (`--clock-control none`), per instruction, plain `_o_e`
  (`nvf4_plain<1, 1>`): elapsed 1.533 Mcycles, SM throughput 93.7%; OMMA 55% of warp samples (68% of them math-pipe
  throttle), the `UIADD3 URZ` fillers ptxas puts between OMMAs 21% (fixed-latency waits: pipe pacing too), the producer's
  and full-barrier spin loops 8%, MEMBAR none. So the mainloop is tensor-bound; the epilogue is the lever: each of its
  `STG.E.128` makes 16 L1 tag requests (16 rows of 32 bytes), 2,048 a tile and SM, on the pipe the other warps' ldmatrix
  (3 wavefronts each) take. The stamps' tail: the 11-tile CTAs end over 10.4 µs, driven by their rates (65.2-66.1 µs a tile,
  correlation 0.96, rank correlation across kernels about 0.5); a dynamic tile scheduler would gain about 0.18% (Derived,
  greedy replay of the stamps), so not next. Multicast TMA compiles for sm_120a but ptxas warns of "substantially reduced
  performance" there, and the mainloop isn't feed-bound: not pursued. `10c2b0c4`: `WIDE` (each consumer warp's 64 columns
  contiguous, 64 wn + 16 i + 8 jl, so store_bf16 writes 128-byte rows, 4 lines a warp store; B's scale words by four 8-byte
  loads a step); `4cd21b8c`: nv256_ew, nv256_o_ew; `549313d4`: plain `verity_nvf4_256x128_ew` and `_o_ew`. Spill-free,
  64 OMMA, no CALL, sass gate pass; every existing kernel and plain entry SASS-identical. Job `nvf4-wide-549313d4` queued.
- 13:08Z: job `nvf4-wide-549313d4` (GPU-9f1f172d, 2,092 MHz): every gate passes (0 words, 0 BF16 elements differ, every
  shape, both scale ranges, full grid / 1 / 3 CTAs / repeats; the plain entries equal the header kernels, CUTLASS and
  cuBLASLt). Measured diagnostic, steady batches of 100, 4 rounds: `verity_nvf4_256x128_o_ew` 0.7218 ms (1.5100 Mcycles),
  `_ew` 0.7220, `_o_e` 0.7241, CUTLASS 256 × 128 0.7864; stamps: the epilogue 1.55k cycles a warp a tile (2.41k without
  WIDE), both warps of an SMSP in it 0.65k (1.19k), tile period 136.2k (136.9k); the mainloop 0.5k longer (the 8-byte scale
  loads, or noise). Job `nvf4-confirm-549313d4` (GPU-0c776bca, 2,092 MHz, 12 rounds): gates pass; `_o_ew` median 0.7219 ms
  (0.7215 to 0.7227, 1.5103 Mcycles), `_ew` 0.7221, `_o_e` 0.7238, CUTLASS 0.7861, cuBLASLt 0.8108. Derived: `_o_ew` at
  94.4% of 1,614 TFLOPS (the 94% line is 0.7248 ms; in cycles, 1.510 Mcycles against 1.511 at 2,085 MHz, so on a GPU held at
  2,085 MHz it sits at the line), 8.5% under the harness divisor (0.78875 ms). `_o_ew` is the fastest plain entry: the
  harness's NVFP4 baseline candidate. Job `nvf4-ncu-549313d4` queued (ncu of `_o_ew`, `_o_e`, nv256_o_ew_b).
- 13:12Z: job `nvf4-ncu-549313d4` (GPU-0c776bca): gates pass. ncu (`--clock-control none`): plain `_o_ew`
  (`nvf4_plain<1, 1, 1>`) 1,517,661 elapsed cycles (`_o_e` 1,523,687), SM throughput 94.6%, SMs active 97.7% of elapsed;
  each `STG.E.128` now 4 L1 tag requests (16 before), the epilogue's instructions under 1% of samples; the barrier spin loops
  (7.8%) are the producer's empty-stage waits; the consumers' samples 84% OMMA and its fillers. What is left: the tail (2.3%
  of elapsed, 1% of it the 11-wave quantization) and about 3% of pipe idle inside tiles. Next candidate: a dynamic tile
  scheduler (the stamps' greedy replay gives about 0.2%), its counter in the entry's workspace, reset by the last CTA.

## The plain FP8 E4M3 GEMM on the same header (from 15:31Z)

Question (coordinator, 15:31Z): does a plain FP8 E4M3 GEMM in this mainloop's style beat the panel's FP8 divisor (the
harness's best of cuBLASLt and CUTLASS at 8,192³: GPU 1's gate run r20260930-124211-a304, cuBLASLt algo 35 at 1.455 ms), at
8,192³ and 16,384³? Screening, one configuration a fill chunk of 8 minutes or less. Branch `cursor/fp8-plain-mainloop-0be9`
(off `cursor/nvfp4-mainloop-0be9`).

- 15:57Z: `49408d84`: the header's `FP8` mode (an E4M3 m16n8k32 atom's fragments are an NVFP4 atom's bytes and take the
  tensor pipe as long, so the schedule is unchanged: 3 stages of 64-byte rows, now 64 deep, no scale loads); NVFP4's
  cubin byte-identical. `a77de383`: `fp8_bench.cu` (f8256, f8256_o_e, f8256_ew, f8256_o_ew; spill-free, 64 QMMA.16832 each).
  `4df5c373`: plain entries `verity_fp8_256x128*` (kind 1, `phc_table_fp8`); NVFP4 entries' SASS unchanged. `1c5eb97d`,
  `025cc1f8`: `fp8_bench.py` on `nvf4_bench.py`'s run: the model gate against BLACKWELL_SM120_E4M3_M16N8K32 (the
  parameters of `cursor/sm120-fp8-capture-75d4`, not yet on this tree's verity) with Ada's model as its negative control;
  the model's words come from a CPU fill step (`--model-cache`, operands regenerated on the host), so the GPU chunk only
  compares; baselines cuBLASLt 12.9 and 13.1 (`libpouw_lt2.so`) and CUTLASS 128 × 256 × 64 and 256 × 128 × 64. sass gate
  (harness's) pass on both binaries. Jobs `fp8-cache-025cc1f8` (gpus=0), then `fp8-o_ew-025cc1f8` (gpus=1).
- 16:20Z: yes at 8,192³, narrowly at 16,384³. Four chunks, one configuration each, one after another (`fp8-{o_ew,ew,o_e,base}-025cc1f8`,
  GPUs 0, 1, 0, 7, 1.5 to 1.7 min each, rc 0, one start each; outputs `/workspace/pouw/fill-out/nvf4-mainloop/fp8-*-025cc1f8/`).
  Every gate passed in each, before any timing, at 256 × 128 × 128, 512 × 256 × 1024, 768 × 384 × 640, 8,192³ and 16,384³, both code ranges: the
  model's words 0 differing (Ada's negative control differs at nearly every coordinate), FP32 words and BF16 against the
  reference at full / 1 / 3 CTAs / repeats 0, BF16 against cuBLASLt 12.9, 13.1 and both CUTLASS kernels 0; sass gate pass.
  Measured diagnostic, ms at 8,192³ (events around one launch, median of 20 | batches of 100 back to back, median of 6),
  with the chunk's best baseline: `_o_ew` 1.4434 | 1.4173 (CUTLASS 256 × 128 1.4792 | 1.4575), `_ew` 1.4442 | 1.4143 (GPU 1;
  1.4802 | 1.4562), `_o_e` 1.4458 | 1.4201, base 1.4721 | 1.4499 (cuBLASLt 12.9 steady 1.4384: no win). The divisor 1.4546 ms
  is the harness's graph median (bursts of 4, 0x0 throttle); on the same GPU, single-launch events read cuBLASLt 13.1's algo 35
  tile 23 at 1.4838 ms, so the batch column is the closer comparison: 2.6 to 2.8% under it (Derived). At 16,384³ (600 W cap):
  `_o_ew` 11.650 | 11.679 against cuBLASLt 13.1's 11.721 | 11.738 (0.5%, the same cycles: 23.48 against 23.62 Mcycles at a
  higher clock), `_ew` 11.642 | 11.676 (CUTLASS 12.40 | 12.94; cuBLASLt picked tile 20, 12.19). `_o_ew` and `_ew` tie;
  `_o_ew` is the one to adopt (NVFP4's adopted entry's order). Branch pushed at `025cc1f8`; no new directories (the
  model cache is under `/workspace/pouw/nvf4-mainloop/025cc1f8/cache`).
