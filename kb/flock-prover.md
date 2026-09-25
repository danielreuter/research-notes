# Flock (succinctlabs, GF(2) batch-R1CS + Ligerito): building, running, measured constants

Sources: `lanes/flock-bench/20260925T0805Z-report-flock-bench.md` (harnesses in `lanes/flock-bench/evidence/pod-scripts/`),
`lanes/flock-bench-80gb/` (A100/H100). All at flock b684b12.

## Building and running
- **Profile.** Use the bench profile (thin LTO), e.g. `cargo bench --no-run`. A plain `--release` build without LTO
  was 1.5-2.3x slower multithreaded (art:aa24c7eb vs the first build).
- **CPU pods.**
  - runpod `cpu3c` can land on Zen3 without AVX-512. Check `lscpu` for avx512 and vpclmulqdq before timing.
  - Set `RAYON_NUM_THREADS` to the cgroup CPU quota, not `nproc`, when they differ (flock-bench-80gb: the H100 pod had
    nproc 160 and quota 17).
  - Memory: BLAKE3 at m33 needs 16.8 GB of heap; SHA-256 BF16 N=4096 (m34) needs 30 GB. A 16 GB pod OOMs on both.
- **CUDA.**
  - Flock `cuda-ghash` and `clmad` need the CUDA 13.3 toolkit (ptxas). Driver 580 works on a 5090. Driver 570 on an
    H100 needs `cuda-compat-13-3` plus `LD_LIBRARY_PATH=/usr/local/cuda-13.3/compat`.
  - Tools that JIT through XLA (flock-zorch) use the pip ptxas, so make sure it is 13.3 or later too, or clmad silently
    falls back to software.
- **Flock-CUDA (`flock-cuda-ffi`).**
  - It is a full on-device prover, but only for the BLAKE3 statement (witness kernel), and it hard-codes
    `n_blocks_log = m - 14`.
  - Ligerito configs are hard-coded per m and are not monotone (5090: m32 0.096 s < m31 0.140 s). There is no config at
    m29; that test panics.
  - GPU proving is non-union `prove_ligerito` over full 2^nbl blocks.
- **Proving any GF(2) circuit on the GPU.** `22-gpu-unit.sh` patches `prove_ffi.cu` with `flock_cuda_prove_host`, which
  uploads a host RowMajor witness (z, a, b, z_lincheck), and sets `n_blocks_log = m - k_log`. Everything else in the
  prover was already generic in the CSC A/B matrices, `const_pin_col`, `useful_bits` and `k_log`.
- **flock-zorch.**
  - It needs a golden file of circuit constants even in `--seed` mode.
  - The golden dump (`dump_blake3_ligerito N`) is single-threaded: 2 min at N=6144, 36 min at N=98304. Budget for it,
    or dump on a CPU pod.
- **Union prover.** `Registry::new(types, nu)` takes the wider k_log type first. A union proof costs the sum of its
  tables; verify and proof size stay flat.

## Measured constants (N = 4,096 VUs, frame-v3 row leaves; per-m tables in the report)
- CPU, 16-vCPU Zen4 (EPYC 4564P), 16T: BLAKE3 BF16 2.33 s, SHA-256 BF16 5.47 s. SHA costs 2.2-2.35x BLAKE3 per VU
  (art:aa24c7eb).
- CPU, 32-vCPU EPYC 9654, 32T: BLAKE3 BF16 1.26 s; census unit table (ampere_bf16) 1.32 s including a naive witness;
  one union proof of both 2.59 s (art:0bd23b01, art:025a0ed4).
- RTX 5090:
  - Flock-CUDA BLAKE3 m33 0.291 s (1.35 M/s), device high-water 15.6 GB (art:9be695b0, art:3f5173a2).
  - flock-zorch BLAKE3 m31 36 ms (3.64 M/s), 2.7-3.9x Flock-CUDA (art:1e54492e).
  - `clmad` 1.00 T/s; GF(2^128) mul 143 G/s (art:85d4fb7a).
- Proofs are 0.3-0.54 MB. Verify takes 4-24 ms (CPU) and 7-20 ms (GPU proofs).
- GF(2^128) link primitives, Zen4 16T, per bit: eq expansion 1.98 ns, 128-way dense bit combination 0.53 ns, fold
  1.60 ns (art:1ef9ac52).

## Gaps (as of 2026-09-25)
- No ZK.
- The strict 128-bit profile relies on proof-of-work credit.
- No union prover on the GPU; CUDA only for sm_120.
- The census unit's witness builder (`verity_unit.rs`) is a naive bit-sliced evaluator, about half of the unit's CPU
  prove.
