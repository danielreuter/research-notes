# Jolt (a16z) zkVM: measured facts and gotchas

Sources: lane jolt-scout report (`lanes/jolt-scout/20260925T0647Z-report-jolt-scout.md`), scripts in
`lanes/jolt-scout/evidence/pod-scripts/`, a16z/jolt main @ 922af71c (2026-09-24), PR #1618 head 66e33a9e. Pod: RTX 4090
24 GB + Ryzen 9 7950X (16 vCPU), 124 GB RAM.

## What exists (2026-09-25)
- Main: RV64IMAC, Twist/Shout, Dory PCS over BN254 (default) or Akita lattice PCS (`akita` feature, merged
  2026-09-15). ZK = BlindFold (`zk` feature, Dory only; `akita`+`zk` is a compile error). Transcript LegacyBlake2b.
- No GPU prover on main. The old ICICLE feature only ever accelerated HyperKZG-era G1 MSMs; it was removed (#779
  2025-07-15, #822 2025-08-01) before the SDK moved to Dory (fd3ffb6a 2025-07-30), and the last rev that has it
  (4c259be477) does not compile with `--features icicle` and panics on CPU. Do not revive it.
- CUDA = draft PR #1618 (curve/Dory only, `jolt-prover --features profiling,cuda`, `profile --backend cuda`). Lattice
  Jolt has no CUDA (Metal-only draft #1733). LayerZero "Jolt Pro" is closed source.

## Security (curve Jolt, no accountant upstream)
- ~100-bit computational: Dory binding rests on BN254 DL/SXDH; GT DLP by SexTNFS ~2^99.7 (eprint 2017/334).
- Sumcheck challenges are 125-bit masked (`jolt-field/src/bn254/mod.rs` `from_challenge_bytes`), so the statistical
  error is about 2^-110 (jolt-scout estimate). Neither a 2^-128 target nor 2^-128 achieved: drill-down only for Table 2.

## Building on a pod
- Guests build through the `jolt` CLI: `cargo install --locked --path .` in the checkout first ("failed to run jolt").
  `jolt-prover profile` runs `jolt build -p {name}-guest` in the CWD, so run it from the workspace root.
- PR #1618 CUDA build: CUDA 12.4's nvcc fails (`llc: -split-compile=0`, then `kernels_all.cu(91) unsupported
  operation`). Install `cuda-nvcc-12-9 cuda-cudart-dev-12-9` (NVIDIA apt repo), point `JOLT_NVCC` at a wrapper that drops
  `--split-compile=0`, `JOLT_CUDA_ARCH=sm_89`. Build ~4 min on 16 vCPU (`30-pr1618.sh`).
- `profile` takes only built-in workloads; `32-pr1618-vu-patch.py` adds `JOLT_PROFILE_GUEST`/`JOLT_PROFILE_INPUT` (postcard
  input bytes, one encoding per argument, concatenated; `vu-input/` writes them). `profile` does not verify the proof.
- The prover pads to the next power of two of the actual trace; `--scale`/`max_trace_length` is only an upper bound.

## Measured (4090 pod)
- VU guest (`vu-k1536/`, bare.rs kernel verbatim, rows as one `serde_bytes::ByteBuf`), main, CPU, Dory, non-ZK:
  kernel 34.1k cycles/VU; bare statement 43.8k/VU incl. input decode; frame-v3 SHA-256 row digests (2 rows x 49
  compressions, `jolt_inlines_sha2`) +195.0k/VU (~1,990 cycles/compression), committed total 239.5k/VU.
  Passing rows as `Vec<u64>` instead costs ~100k cycles/VU of postcard varint decode.
- CPU prove (main, all verified): B=16 bare 2^20 9.5 s, committed 2^22 21 s; B=64 bare 2^22 19 s, committed 2^24
  55-62 s, peak RSS 7.4 GB. Verify 0.07-0.2 s. BlindFold ZK adds 3-5% prove time at B=16 (verify 0.16 s).
- PR #1618 sha2-chain prove, cuda vs optimized CPU: 2^20 1.56 vs 4.80 s; 2^22 2.46 vs 14.18 s; 2^24 5.83 vs 46.53 s
  (8.0x). GPU memory 12.7 GB at 2^24, so 2^25 does not fit a 24 GB card. Process wall adds ~9 s of trace/preprocess.
- PR #1618's older SDK base traces the same VU guest ~18% longer (B=16 committed 4,509,134 vs 3,832,804 on main).
