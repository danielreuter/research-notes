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
- RTX 4090 (sm_89, driver 580.159, CUDA 13.3 AOT; hash-commit): `clmad_peak` 0.67 T/s; GF(2^128) mul schoolbook+clmad 75 G/s,
  binius+clmad ~50 G/s, software 17 G/s (art:855d5a32).
- H100 NVL (sm_90, driver 580.126 with CUDA 13.3 AOT, no cuda-compat needed; hash-commit-2): `clmad_peak` 7.51 T/s;
  binius+clmad 575-607 G/s, schoolbook 363-371, karatsuba 325, software 7-10 (art:31a799a7). So the ~8x H100-over-consumer
  clmad rate reproduces on a second H100 (NVL clocks a bit lower than SXM); 11x the 4090.
- H100 80GB (sm_90; Xeon 8468 host, 16T) (flock-bench-80gb report):
  - `clmad` 8.33-8.40 T/s; GF(2^128) mul 690-695 G/s (binius+clmad) (art:7b941558).
  - Flock-CUDA builds for sm_90 with one sed on `flock-cuda-ffi/build.rs` (`compute_120,code=sm_120` -> 90, and the
    cuda-13.3 lib path). BLAKE3 m32 0.098 s, m33 0.30 s: the same as the 5090 despite 8.4x its clmad rate. nsys kernel
    time per prove is 0.047 s (m32) and 0.092 s (m33); the rest is cudaDeviceSynchronize/cudaMemcpy host glue
    (art:876ab350, art:b6148b4a). Flock-CUDA is host-bound, not clmad-bound.
  - Census unit on the GPU (the `flock_cuda_prove_host` port): hopper_bf16 m32 0.445 s, of which 0.25-0.29 s is the
    pageable 2.15 GB H2D upload (kernels 0.045 s); hopper_e4m3 m31 0.232 s (0.126 s upload, kernels 0.024 s) (art:83f2d55d).
  - CPU 16T, one union proof unit + BLAKE3: hopper_bf16 1.32 s, hopper_e4m3 0.74 s, 25.6 / 15.1 GB heap. The union is ~26%
    cheaper than the separate tables on this host (art:8b4c35bf).
- Proofs are 0.3-0.54 MB. Verify takes 4-24 ms (CPU) and 7-20 ms (GPU proofs).
- GF(2^128) link primitives, Zen4 16T, per bit: eq expansion 1.98 ns, 128-way dense bit combination 0.53 ns, fold
  1.60 ns (art:1ef9ac52).

## Link L red-team (red-team-link, 2026-09-25, `lanes/red-team-link/20260925T0957Z-report-red-team-link.md`, art:beeefd44)
- Verdict: CLEARED WITH CONDITIONS. The parity argument holds.
- The link claims can't go into Flock's GF(2^128) opening as one batch: the reduction costs about 2m/2^128 (2^-122 at m33) and
  loses the two-point squaring. Use one point over GF(2^256), or independent reductions.
- Flock's coins after root_B must be the live verifier's, or absorb root_F, the link points and y. Fiat–Shamir seeded from
  root_B alone breaks it.
- Today's Flock verity-shape runs are independent compressions: no chain glue, endpoints, counters or flags. Every block is
  forgeable until P_B pins them.
- Over BabyBear, keep 2^(w_u+1) ≤ p-1, so at most 21,845 BF16 VUs per linked proof (40,959 with σ sent in the clear). Never
  range-check u as 2×16-bit limbs.
- SHA-256 leaves need a big-endian Λ.

## Soundness under TABLES accounting and the 2^-128 profile (flock-128, 2026-09-25, `lanes/flock-128/20260925T1018Z-report-flock-128.md`)
- The ledger is built from the squeezes actually made. A `Challenger` wrapper logs every call site
  (`lanes/flock-128/evidence/pod-scripts/site_census.rs`), and `evidence/accounting.py` assigns each site its degree.
- With no grinding credit, `Fast` is 2^-110.0 per whole proof with live coins and 2^-50 under Fiat-Shamir (x2^60).
  `Fast100` is 2^-97.8. The F128 PIOP union alone is 2^-118.4, so no single-run F128 profile reaches 2^-128.
- **flock-128-r2** = 2 sequential `Fast100` runs, with a separate domain per rep and live verifier coins: 2^-195.5, and
  about 2^-194.6 for the GPU pair. It needs no code change. It cannot reach 2^-128 under Fiat-Shamir: (2^60 eps)^2 = 2^-75.6.
- Cost of r2 against Fast at 4096 VUs: CPU union 2.00x (BF16) and 1.94x (FP8); H100 Flock-CUDA pair 1.00x and 0.91x.
  Proofs are 2.0x larger; verify takes 1.5-1.8x as long.
- GOTCHA: Flock-CUDA's `Fast` grinding costs 0.11-0.18 s per GPU proof (BLAKE3 m33: fast 0.226 s, fast100 0.099 s).
  That is about half of today's GPU wall time. On CPU the same grinding is only 2-8%.
- The CUDA path takes any profile: set `profile` in `gpu_roundtrip.rs`'s `PcsParams`, and the FFI takes every
  schedule from it (0 = grinding site absent). `Fast100` roundtrips verify on sm_90. Flock-CUDA uses SHA-256 for
  its transcript and Merkle trees (`CUDA_HASH`); the CPU uses BLAKE3.
- Patch and harness: `lanes/flock-128/evidence/pod-scripts/g128_patch.py` (GPU) and `unit_shape128.rs` (CPU).

## Gaps (as of 2026-09-25)
- No ZK.
- The strict 128-bit profile relies on proof-of-work credit. Without that credit, 2^-128 needs flock-128-r2 (two
  live-coin runs), as above.
- No union prover on the GPU. Upstream build.rs targets only sm_120; sm_90 works with the sed above.
- The census unit's witness builder (`verity_unit.rs`) is a naive bit-sliced evaluator, about half of the unit's CPU
  prove.

## Red-team verdict on flock-128-r2 (red-team-flock, 2026-09-25 4:30 AM PT, `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`)
- **NOT GRANTED.** Grantable, with conditions, after R1–R8 and a re-audit of the live challenger. Until then route (a) has
  no 2^-128 Flock cell.
- **Terms: HOLD.** 2^-195.5 reproduced. Fast100 queries give 2^-97.77 per run (m30: 2^-98.04), from the TOMLs. The
  Johnson-regime MCA is proven (Haböck ePrint 2025/2110; BCHKS25). The stratified sampler is exactly (1−γ)^Q. The 7 fixed
  inner zerocheck coordinates lose nothing on the x86/CUDA RS path. No grinding credit is taken.
- **BREAK: the reps aren't bound to one commitment.** Each rep commits its own root, and the Mixed binding absorbs only the
  registry, counts and root, with no public I/O. So rep 2 can prove another witness and the error stays at 2^-97.8.
  Demo: art:8d04b53f (`lanes/red-team-flock/evidence/rtf_unlinked_reps.rs`, run r20260925-112210-2d3d).
- **GAP: no live challenger.** Flock's verifier is Fiat–Shamir only (at most 2^-75.6 for r2).
- **GAP: the AG r₁ path** (aarch64 only) gives the prover about 14 bits of nonce choice, even with live coins.
- **Conditions:**
  - R1: one commitment per table, reused by both reps, or `root_rep0 == root_rep1` before any rep-1 coin. The link binds
    that root. The commit is deterministic, so this is free. If the link claims open in both reps, C1 squares to about
    2^-244.
  - R2: commit before coin, plus a final replay that checks every message against the coins issued.
  - R3: `fork_from_seed` must be live. An FS child seeded from the fork seed, as in the merged opening's concurrent
    multipoint/anchor child, costs about 2^-122 over two runs, which fails.
  - R4: PoW and nonce sites return pure verifier coins.
  - R5: Flock's coins go out only after root_F, the link points and y.
  - R6: Flock-CUDA squeezes on the device (`zc_challenger_device.cuh`) and needs a live path, not yet costed.
  - R7: the verifier pins Fast100, reps = 2 and the RS flavour from configuration, and rejects lone reps and AG proofs.
  - R8: evidence is the live session record only.
- **Implementation checks that hold:** profile downgrades are rejected (exact `commitment.params == expected`: the Fast
  proof, relabelled params, and rep 0 replayed as rep 1 were all rejected). The padding contract is benign.
- **Hashes:** red-team-flock reports BLAKE3 Merkle and transcript (32-byte, custom chained transcript) on the CPU path.
  flock-128 found Flock-CUDA uses SHA-256 (`CUDA_HASH`). Table 1 names the hash per line.
- **Composition with the fixes:**
  - A-GKR route: 2^-130.2, set by A-GKR. If the accountant counts A-GKR's hash budget (2^-127.7), it misses 2^-128
    whatever Flock does. C8 accounting question, open.
  - B-Ligero: 2^-128.05 + 2^-195.5 still passes.
- **Negatives to keep:** report §5 (10 items). The first: reps with different roots are rejected.

## Flock-CUDA host glue (flock-glue, 2026-09-25; profile b684b12 `Fast`, about 2^-100, not cleared)
Report: `lanes/flock-glue/20260925T1011Z-report-flock-glue.md`.

- **Host PoW grinding is the hidden cost.** `FsChallenger` grinds every PoW site on the host with single-thread SHA-256.
  That costs 0.09–0.14 s per unit proof and 0.25–0.27 s per BLAKE3 proof at 4096 VUs, or 0.20–0.33 s per batch.
  - `pow_grind.cuh` `search_sha256_proof_of_work_nonce` returns the same minimal nonce, so routing grinding there
    leaves the proofs unchanged.
  - Keep sites under 8 bits on the host, because the GPU round trip loses there. A cutoff of 12 leaves 0.5–1.9 ms gaps.
  - The patch is in `lanes/flock-glue/evidence/flock-glue-b684b12-tracked.patch`.
- **The unit witness can be built on the device.** One CTA per 32 VUs, bit-sliced over the level-ordered census
  netlist, matches the host witness bit for bit (z, a, b and the byte-packed z_lincheck).
  - It takes 47 ms on A100 and 21 ms on H100 at BF16, and 10 ms on H100 FP8. The time is nearly independent of the VU
    count.
  - It's latency-bound at about 1,600–1,900 cycles per level, with 96 units in series per VU. Kernel knobs and 64 VUs
    per CTA don't help.
  - It replaces the 2.15 GB pageable upload, which takes 0.38 s on A100 and 1.0 s on H100.
- **Every `cudaDeviceSynchronize()` in `prove_ffi.cu` and `ligerito_f256.cuh` defeats side streams.** Change them to
  `cudaStreamSynchronize(0)` before overlapping anything with a proof. Even then, overlapping the witness with the
  BLAKE3 proof gains nothing on H100 at 4096 VUs, where the two compete for SMs. It saves 19 ms on A100.
- **Idle-gap floor.** About 16–17 ms of idle GPU time per batch, in about 1,500–2,000 gaps, from host FS round trips and
  launches. After the fixes above, Flock-CUDA's proof kernels alone run at 1.00x, 1.24x and 1.05x B-Ligero bare (A100
  BF16, H100 BF16, H100 FP8).
- **Harness pitfall.** Building `BlockR1cs` for BLAKE3 per call costs about 1 s. Cache the statement and its digest once
  (the `stmt()` cache in `gen_test.py`).

## Live coins (flock-live, 2026-09-25 5:22 AM PT, `lanes/coordinator/20260925T1222Z-handoff-from-flock-live.md`)
- R1–R8 are implemented on `lane/flock-live` @ a43f6254, **not merged** and **not granted**: red-team-flock is re-auditing.
  All negatives reject except link negatives 10 and 11, which need a `Commit(roots)` → `Coins(points)` → `Link(y)` exchange
  before the first rep round.
- Flock-CUDA's prove path draws challenges only from the host `FsChallenger`.
- A live session is about 220 round trips per table (both reps), about 74 KB up and 30 KB down.
- Live cost on the H100 pair at 4,096 VUs: BF16 0.982 s (1.24× FS), FP8 0.526 s (1.30× FS). Price the live verifier's RTT
  into the prover time.
- R5 is a gate: the server refuses coins until a `Link` message arrives (an opaque stub today). The C2 order is link points
  as a verifier coin slot after root_F and root_B, then y, then Flock's coins, so root_B must be committed before Flock's
  first round.
- Flock's union prover commits and binds inside `prove_fast_ligerito_union`, so a session driver needs a commit-then-prove
  split or the exchange above. Negative 15 (cross-session replay against both reps) passes.
