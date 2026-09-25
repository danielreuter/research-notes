---
lane: flock-bench
kind: report
created: 2026-09-25T08:05Z
status: final
---

CHECKPOINT 4fbfb71 (09:54Z) [final] 09:58Z FINAL: census unit + BLAKE3 leaves N=4096 on 5090 BF16 0.42-0.58s (1.6-2.2x B-Ligero bare, 18-25x under +blake3), FP8 0.20-0.39s; CPU one union proof 2.59/1.26s; handoffs coord 0945Z+0946Z; pods terminated; ~$4; 64MB fetched pre-freeze
CHECKPOINT 15f74f3 (09:29Z) [open] 09:30Z one Flock union proof BLAKE3 leaves+unit (CPU 32T) art:025a0ed4: BF16 4096VU 2.59s/24ms/523KB/15GB RSS, FP8 1.26s/500KB; 5090 hopper units art:e4f684ac (m32 0.29s). 80gb inbox read (parallel harness). Next: zorch m31, report+handoffs
CHECKPOINT 806a2f73 (09:12Z) [open] 09:13Z unit circuit on Flock CPU (EPYC9654 32vCPU) art:0bd23b01: BF16 4096VU m32 prove 1.32s (0.66 naive witness) verify 4ms 461KB 8.2GB; BLAKE3 same host m33 1.26s; per-slot-bit ~equal; tamper rejected. GPU unit via patched Flock-CUDA host-witness building (r20260925-091040-8ec8)
CHECKPOINT none (09:03Z) [open] 09:03Z NEW PRIORITY (coord 0830Z handoff) taken: census unit exported to Flock block-R1CS (BF16 7687 rows/2^13, 235k nnz), smoke 64VU prove .085s verify ok; full unit+BLAKE3 sweep on 32vCPU Zen4 r20260925-090255-c8f0; zorch B still running
CHECKPOINT none (08:44Z) [open] 08:44Z CPU Zen4 table done (thin LTO); link prims measured (eq 2ns/bit, count .5, fold 1.6 @16T); zorch part B running on 5090 (r20260925-082947-b255); Flock-CUDA reps next; CPU pods terminated
CHECKPOINT a816a2b1 (08:28Z) [open] CPU Zen4 16T sweep done art:aa24c7eb (BLAKE3 BF16 N=4096 2.33s/433KB/14ms verify; SHA 5.47s/479KB); Flock-CUDA 5090 m26-33 verified (m33 0.29s); zorch running; next: CUDA reps, zorch, link estimate
CHECKPOINT a816a2b1 (08:05Z) [open] pods up (cpu3c 8vCPU Zen5 only; 16/32 sold out; 5090 community); CUDA13.3 clmad 5090: 1.00 TCLMAD/s, 143 GMul/s karatsuba; harness verity_shape.rs written; next: CPU flock runs, Flock-CUDA + flock-zorch on 5090

# flock-bench: Flock on verity's frame-v3 row-leaf batch

Goal (launch message): ground `docs/hash-proving-survey.md` §2/§3.1/§3.8/§3.9/§4.2-4.3/§6 "Flock plus link" projections
in measurements at our batch shape. No repo commits (no reusable harness in the repo; harnesses live in
`evidence/pod-scripts/`). Handoffs received:
- `20260925T0830Z-handoff-from-coordinator.md` (NEW PRIORITY): prove the binary-backend unit circuit (census `internal/binary-census/`) plus the
  BLAKE3 table at 4,096 VUs on pod CPU and the 5090. Report "flock-bench: binary backend numbers" against the B-Ligero
  Table 2 cells and the census projection; do not build on the link doc. Taken, see "Binary-backend unit circuit" below.
- `20260925T0900Z-handoff-from-flock-bench-80gb.md` (who writes the unit harness?): answered 0904Z by pointing it
  at mine. `20260925T0915Z-handoff-from-flock-bench-80gb.md`: it wrote a
  parallel harness (`unit_shape`) and is running A100/H100. Read, not re-run here: its numbers are its own lane's
  deliverable. I adopted its cgroup gotcha as a check (`nproc` = 32 on my CPU pod, so 32T was not oversubscribed).
- `20260925T0946Z-handoff-from-coordinator.md` (laptop disk under 3 GiB): taken. No fetches after 09:49Z; everything
  in R2 via `--preserve`. My runs already fetched to `~/.research/runs` total 64 MB (largest r20260925-082947-b255, 25 MB).

## What was proved (the shape)

An instance (VU) = 2 leaves (x row, W column), K = 1536 words, BF16 (3,072 B) or FP8 (1,536 B) per leaf.
`verity_shape.rs` (pod-scripts) builds exactly the compressions of the frame-v3 row digests
(`packages/verity/src/verity/commitments/rowleaf.py`) and asserts each recomputed row digest equals the reference crate
(`blake3::keyed_hash`, `sha2::Sha256`) before proving:

| leaf | compressions per leaf | per VU | N=4096 batch | slots (pow2) | Flock m |
| --- | --- | --- | --- | --- | --- |
| `blake3-keyed/row/v2` BF16 | 48 (3 chunks x 16; 2 parents native) | 96 | 393,216 | 2^19 | 33 |
| `blake3-keyed/row/v2` FP8 | 24 (16 + 8; 1 parent native) | 48 | 196,608 | 2^18 | 32 |
| `sha256/row/v1` BF16 | 49 (48 data + 1 pad; 64-B prefix = native midstate) | 98 | 401,408 | 2^19 | 34 |
| `sha256/row/v1` FP8 | 25 (24 + 1) | 50 | 204,800 | 2^18 | 33 |

Proved as a batch of independent compressions (`Blake3Setup` / `Sha256HybridSetup::prove_fast`, default `Fast`
Ligerito profile, SHA-256 Merkle + FS). NOT modelled: the chaining wiring cv_out[j] = cv_in[j+1] inside a leaf and the
public per-leaf endpoints (key/IV/midstate in, chunk CV / digest out). The paper puts IO glue at < 5 % of prover time
(estimate below). Proving cost is data-oblivious; the GPU provers used their own (random) compressions at the same
slot counts.

## Results

Artifacts: CPU Zen4 art:aa24c7eb (run r20260925-081335-316c), CPU Zen5 art:59d7c080 (r20260925-081834-ea01),
clmad/f128 5090 art:85d4fb7a (r20260925-080044-f067), link primitives art:1ef9ac52 (r20260925-083838-fc14),
GPU: see below.

### CPU, Flock b684b12 (bench profile, thin LTO), AMD EPYC 4564P (Zen4, AVX-512 + VPCLMULQDQ), 16 vCPU / 32 GB

prove = best of 3 (2 at N=4096) after one warm-up; verify = Rust verifier, same threads; proof = `R1csProofBundleLigerito::to_bytes`;
peak = process heap high-water (includes the inputs).

| hash | prec | N | compressions | m | prove 16T s | prove 1T s | verify 16T ms | proof KiB | peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BLAKE3 | BF16 | 64 | 6,144 | 27 | 0.058 | 0.214 | 10.7 | 308 | 0.9 |
| BLAKE3 | BF16 | 1024 | 98,304 | 31 | 0.584 | 2.53 | 15.2 | 393 | 4.3 |
| BLAKE3 | BF16 | 4096 | 393,216 | 33 | **2.33** | 9.84 | 14.0 | 423 | 16.4 |
| BLAKE3 | FP8 | 64 | 3,072 | 26 | 0.043 | 0.149 | 11.4 | 295 | 0.7 |
| BLAKE3 | FP8 | 1024 | 49,152 | 30 | 0.305 | 1.34 | 12.7 | 365 | 2.7 |
| BLAKE3 | FP8 | 4096 | 196,608 | 32 | **1.15** | 5.19 | 12.1 | 408 | 8.0 |
| SHA-256 | BF16 | 64 | 6,272 | 28 | 0.128 | 0.527 | 12.9 | 269 | 1.1 |
| SHA-256 | BF16 | 1024 | 100,352 | 32 | 1.22 | 5.46 | 12.7 | 423 | 8.2 |
| SHA-256 | BF16 | 4096 | 401,408 | 34 | **5.47** | 22.8 | 13.4 | 468 | 30.2 |
| SHA-256 | FP8 | 64 | 3,200 | 27 | 0.076 | 0.282 | 16.7 | 324 | 0.9 |
| SHA-256 | FP8 | 1024 | 51,200 | 31 | 0.641 | 2.97 | 13.9 | 408 | 4.4 |
| SHA-256 | FP8 | 4096 | 204,800 | 33 | **2.55** | 11.6 | 12.2 | 438 | 17.2 |

- Throughput at N=4096: BLAKE3 169k/s (16T), 40k/s (1T); SHA-256 73-80k/s (16T), 17.6k/s (1T). SHA-256/BLAKE3
  per VU = 2.35x (BF16), 2.2x (FP8). 16T/1T = 4.2-4.6x on this 16-vCPU (8 core + SMT) pod.
- Linear in batch above N=1024 (prove per VU 570 us BLAKE3 BF16, 1.2-1.3 ms SHA BF16); N=64 pays a fixed ~50-130 ms.
- Proof 0.27-0.47 MiB and verify 11-17 ms, nearly flat in N.
- Memory: SHA-256 BF16 N=4096 peaks at 30.2 GiB (fits 32 GB only just); BLAKE3 BF16 N=4096 16.4 GiB. On a 16 GB pod
  (EPYC 9655P, 8 vCPU) both m33/m34 points were OOM-killed.
- Cross-check: flock's own `blake3_proof` at 2^13 / 2^17 random compressions, 8T on the same pod: 66 ms / 0.73 s;
  `sha2_proof` 150 ms / 1.45 s (proof sizes 350 / 435 KiB and 280 / 465 KiB). Consistent with the table.
- Zen5 8-vCPU pod (art:59d7c080), same build: BLAKE3 BF16 N=1024 1.07 s (8T) / 2.56 s (1T); SHA BF16 N=1024 1.62 s / 5.48 s.
  Single-thread rate matches Zen4 (~39k BLAKE3/s); MT on that shared 8-vCPU slice is noisy. The first (release,
  no LTO) build was 1.5-2.3x slower MT: use the bench profile.

### GPU, RTX 5090 (runpod community, driver 580.65.06, CUDA 13.3 V13.3.73)

`clmad` microbenches (flock `cuda-ghash`, art:85d4fb7a): raw 1.00 T CLMAD/s; GF(2^128) mul 143 G/s (Karatsuba+clmad),
106 G/s schoolbook, 70 G/s binius-style, 18.6 G/s software shift-XOR (7.7x); 40 CLMAD SASS instructions in the binary.
Driver 580 is enough when ptxas 13.3 assembles AOT (the survey's "needs CUDA 13.3" is a toolkit, not driver, floor).

Flock-CUDA (flock `cuda-ghash` + `flock-cuda-ffi` roundtrip, BLAKE3 only, on-device witness generation, steady prove
after one warm-up, proof verified by the Rust verifier; proof size = bincode of `R1csProofLigerito` + 4 KiB commitment):
art:9be695b0 (run r20260925-091303-5375), 3 reps, spread about 1 %. Random BLAKE3 compressions fill all 2^(m-14) slots:

| m | slots | our batch at this m | prove s | verify ms | proof KB (incl. 4.1 KB commitment) |
| --- | --- | --- | --- | --- | --- |
| 26 | 4,096 | FP8 N=64 (3,072) | 0.105 | 14 | 408 |
| 27 | 8,192 | BF16 N=64 (6,144) | 0.057 | 16 | 422 |
| 30 | 65,536 | FP8 N=1024 (49,152) | 0.107 | 18 | 479 |
| 31 | 131,072 | BF16 N=1024 (98,304) | 0.140 | 16 | 507 |
| 32 | 262,144 | FP8 N=4096 (196,608) | **0.096** | 16 | 522 |
| 33 | 524,288 | BF16 N=4096 (393,216) | **0.291** | 18 | 538 |

Not monotone in m: each m has its own hard-coded Ligerito config, and m26/m30/m31 have worse ones than m27/m32. At N=4096,
BF16 is 1.35 M BLAKE3/s (8.0x the 16-vCPU Zen4 pod, 4.3x the 32-vCPU EPYC 9654). Host RSS 0.8 GB. Device memory high-water (nvidia-smi at 20 ms, art:3f5173a2): m32 8.2 GB, m33 15.6 GB. There is no config at m=29 (the test panics), which matters for the unit circuit below.

flock-zorch (fractalyze, JAX/XLA + clmad, BLAKE3; art:1e54492e, run r20260925-082947-b255). Throughput mode proves from
a packed witness, so the witness is excluded; seed mode generates it on device:

| m | hashes (full slots) | throughput-mode prove ms | seed-mode ms | host RSS GB |
| --- | --- | --- | --- | --- |
| 27 | 8,192 | 21.0 | 20.1 | 2.4 |
| 31 | 131,072 | **36.0** (3.64 M/s) | 37.7 | 5.8 |

zorch is 2.7x faster than Flock-CUDA at m27 and 3.9x at m31. Its README floor (2.36 M/s at 2^17) is beaten at 3.64 M/s.
Linear extrapolation at 59.6 G slot-bits/s puts m33 (BF16 N=4096) near 0.14 s; that point was not run. zorch needs a
golden file of circuit constants even in seed mode, and the golden dump is single-threaded: m31 took about 35 min, so
m32/m33 and all SHA-256 points were skipped. zorch is BLAKE3/SHA/Keccak only; it cannot run the unit circuit below.

## Binary-backend unit circuit (coordinator 0830Z priority)

**Export.** `export_unit.py` turns the census unit (`internal/binary-census/unit.py`, `gf2.py`, copied) into a Flock
`BlockR1cs` over GF(2) with C = I and one row per committed bit:
- inputs and the constant wire: A = B = {i};
- an AND row: its two input forms (a form's constant term goes to the constant column);
- an assertion L = 0: (L + z_j)·1 = z_j;
- a non-trivial output bit: a copy row (f)·1 = z_j.

It evaluates 64 random valid vectors bit-sliced and checks every row before writing. `verity_unit.rs` (installed as
`crates/flock-prover/src/r1cs_hashes/verity_unit.rs`) loads it at k_log 13 with a bit-sliced 8-instance witness.
`VerityUnitSetup` is the unit table alone; `CombinedSetup` is ONE union proof over two tables, the BLAKE3 row-leaf
compressions (checked against `blake3::keyed_hash`) and the unit table, at the same VU count. Not modelled: glue making
the unit's input bits equal the leaf message bits; the survey puts IO glue under 5 %.

| pipeline | units / VU | useful bits (2^13 slot) | ANDs | asserts | copies | nnz(A)+nnz(B) |
| --- | --- | --- | --- | --- | --- | --- |
| ampere_bf16 | 96 | 7,687 | 7,100 | 33 | 9 | 235,134 |
| hopper_bf16 | 96 | 7,305 | 6,718 | 33 | 9 | 241,107 |
| ada_e4m3 | 48 | 7,373 | 6,744 | 65 | 19 | 221,085 |
| hopper_e4m3 | 48 | 7,003 | 6,374 | 65 | 19 | 234,352 |

AND counts match the census exactly; committed bits are 34-66 above the census's, from the copy rows and the constant wire.
Controls: a NaN operand planted at unit n/2 makes `verify` fail on CPU (both formats) and on GPU (Lincheck
ConsistencyFailed "sumcheck-final"); proof-tamper control passes.

### CPU: Flock b684b12, AMD EPYC 9654, 32 vCPU pod, 32 threads (16T in brackets)

Unit alone: art:0bd23b01 (r20260925-090255-c8f0) and art:469d0d63 (hopper, r20260925-091444-d620). One union proof:
art:025a0ed4 (r20260925-091845-2c75). prove = best of 2-3 after a warm-up and includes witness generation, which
`prove_fast` rebuilds on every call. "cold witness" = one separate first call of the witness builder, which includes
page-faulting its buffers; it is only a rough upper bound on the witness share of prove. peak = process heap
high-water, including inputs (unit, BLAKE3), or max RSS (union).

| table | N VUs | m | prove s, 32T [16T] | cold witness s | verify ms | proof KB | peak GB (4096) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unit ampere_bf16 | 64 / 1024 / 4096 | 26 / 30 / 32 | 0.095 / 0.364 / **1.32** [1.93] | 0.02 / 0.21 / 0.66 | 4.2 / 4.3 / 4.4 | 345 / 416 / 461 | 8.2 |
| unit hopper_bf16 | 64 / 1024 / 4096 | 26 / 30 / 32 | 0.091 / 0.417 / **1.26** | 0.03 / 0.22 / 1.20 | 3.6 / 4.8 / 4.4 | 337 / 409 / 453 | 8.1 |
| unit ada_e4m3 | 64 / 1024 / 4096 | 25 / 29 / 31 | 0.087 / 0.238 / **0.684** [0.953] | 0.02 / 0.08 / 0.47 | 4.0 / 4.5 / 4.0 | 324 / 322 / 438 | 4.0 |
| unit hopper_e4m3 | 64 / 1024 / 4096 | 25 / 29 / 31 | 0.050 / 0.245 / **0.718** | 0.01 / 0.10 / 0.41 | 3.8 / 4.6 / 4.2 | 316 / 318 / 430 | 3.9 |
| BLAKE3 leaves BF16 | 64 / 1024 / 4096 | 27 / 31 / 33 | 0.077 / 0.364 / **1.26** [1.76] | | 6.8 / 6.3 / 7.7 | 316 / 402 / 433 | 16.8 |
| BLAKE3 leaves FP8 | 64 / 1024 / 4096 | 26 / 30 / 32 | 0.120 / 0.236 / **0.672** [0.755] | | 8.0 / 7.6 / 6.9 | 302 / 373 / 418 | 8.2 |
| **union BLAKE3 + ampere_bf16** | 64 / 1024 / 4096 | 27 / 31 / 33 | 0.126 / 0.801 / **2.59** | | 8.5 / 8.2 / 24 | 406 / 492 / 523 | 15.4 RSS |
| **union BLAKE3 + hopper_bf16** | 4096 | 33 | **2.51** | | 9.0 | 519 | |
| **union BLAKE3 + ada_e4m3** | 64 / 1024 / 4096 | 26 / 30 / 32 | 0.113 / 0.395 / **1.26** | | 9.6 / 7.6 / 7.5 | 388 / 459 / 504 | |
| **union BLAKE3 + hopper_e4m3** | 4096 | 32 | **1.26** | | 7.5 | 500 | |

- Per slot bit, including witness generation, the unit table costs 0.29-0.33 ns and BLAKE3 0.147-0.156 ns: about 2x.
  Most of the gap is my unoptimized witness builder, whose cold standalone time (0.41-1.20 s at N=4096) is 30-95 % of
  unit prove. Flock's own BLAKE3 witness is under 10 % of its prove. The prove core alone was not isolated on CPU. On
  the GPU, where the unit witness is built outside prove, the unit table proves (minus upload) in 0.2-1.7x Flock-CUDA's
  BLAKE3 time at the same m (m26/30/31/32; next section). So the census's key assumption, that Flock's BLAKE3 rate carries over per slot bit, holds for the
  prover proper; the unit's witness generation still needs a real implementation.
- The union proof costs the sum of the two tables (BF16 2.59 s against 1.32 + 1.26). Verify and proof size barely
  move: 8-24 ms, about 0.5 MB.

### GPU: RTX 5090, Flock-CUDA patched for host witnesses

`22-gpu-unit.sh` patches `cuda-ghash/prove_ffi.cu`: it replaces the hard-coded `n_blocks_log = m - 14` with
`m - k_log` and adds `flock_cuda_prove_host`, which uploads a host-built RowMajor witness (z, a, b, z_lincheck).
The GPU prover is the non-union `prove_ligerito` (full 2^nbl blocks, so N=4096 BF16 = 393,216 units proves 2^19 =
524,288 blocks); the Rust `verify_ligerito` checks every proof. prove = steady state after a warm-up, including the
host-to-device witness upload (shown separately). Unit tables: art:7218310f (r20260925-091040-8ec8, 3 reps) and
art:e4f684ac (r20260925-091930-31a7, 2 reps).

| pipeline | m (our N) | prove s | of which upload s | verify ms | proof KB |
| --- | --- | --- | --- | --- | --- |
| ampere_bf16 | 26 (64) / 30 (1024) / 32 (4096) | 0.028 / 0.127 / **0.257** | 0.003 / 0.037 / 0.133 | 8 / 10 / 9 | 404 / 474 / 518 |
| hopper_bf16 | 26 / 30 / 32 | 0.073 / 0.089 / **0.291** | 0.003 / 0.039 / 0.133 | 8 / 10 / 9 | 404 / 474 / 518 |
| ada_e4m3 | 25 (64) / 30 (1024, padded; m29 has no config) / 31 (4096) | 0.032 / 0.116 / **0.295** | 0.002 / 0.038 / 0.069 | 7 / 10 / 8 | 391 / 474 / 503 |
| hopper_e4m3 | 25 / 30 (padded) / 31 | 0.084 / 0.137 / **0.173** | 0.002 / 0.039 / 0.069 | 7 / 10 / 9 | 391 / 474 / 503 |

- The spread between circuits at the same m (up to 2.6x at m25-26; ada 0.295 s against hopper_e4m3 0.173 s at m31) is
  real: the runs did not overlap zorch. It is not explained by the constant column's degree (ada's is highest) or the
  max row degree. Treat 0.17-0.30 s as the per-circuit range at N=4096.
- The host witness build (0.28 s at m32, CPU) is outside prove; an on-device witness, like Flock-CUDA's own BLAKE3
  path, would also remove the 0.13 s upload. Device-only unit prove at m32 is therefore about 0.12-0.16 s.
- Device memory high-water (art:3f5173a2): ampere m32 8.0 GB, ada m31 4.3 GB. Run one after the other, unit
  and BLAKE3 peak at 15.6 GB, which fits a 24 GB 4090.
- No union prover on GPU, so relation + leaves on the 5090 is two proofs (the CPU union costs the sum, so two proofs
  is a fair model).

### Against B-Ligero and the census (N = 4,096 VUs)

B-Ligero cells are from `lanes/coordinator/20260923T2250Z-device-wave-inputs.md:46` and were measured on an RTX 4090.
Ours are on a 5090, which typically runs 1.3-1.7x faster, so the ratios below flatter the binary backend by about that.
Census projections are from `docs/binary-backend-census.md`.

| line | B-Ligero 4090 bare | B-Ligero +blake3 | census 5090 | Flock 5090: unit | Flock 5090: unit + BLAKE3 leaves | Flock CPU 32 vCPU: union |
| --- | --- | --- | --- | --- | --- | --- |
| BF16 (hopper) | 0.261 s | 10.70 s | 0.083 s unit, 0.25 s + BLAKE3 | 0.29 s (0.16 device-only) | 0.29 + 0.29 = **0.58 s** (0.45 device-only) | 2.51 s |
| BF16 (ampere) | - | - | same | 0.26 s (0.12) | **0.55 s** (0.42) | 2.59 s |
| FP8 (ada) | 0.170 s | 5.22 s (best 4.70) | 0.125 s + BLAKE3 | 0.30 s (0.23) | 0.30 + 0.10 = **0.39 s** (0.32) | 1.26 s |
| FP8 (hopper_e4m3) | - | - | same | 0.17 s (0.10) | **0.27 s** (0.20) | 1.26 s |

- **Relation plus BLAKE3 leaves, binary backend on a 5090:** BF16 0.42-0.58 s, which is 1.6-2.2x B-Ligero bare and
  18-25x faster than B-Ligero +blake3. FP8 0.20-0.39 s, which is 1.2-2.3x bare and 12-26x faster than +blake3.
- **Relation alone:** 0.10-0.30 s, which is 0.5-1.8x B-Ligero bare. The census projected 0.083 s for BF16, and 0.25 s
  with BLAKE3, which is about 1x bare. The census assumed zorch-grade kernels; Flock-CUDA is 2.7-3.9x slower than zorch on BLAKE3 (above). At zorch's
  measured rate the unit would take about 0.07 s and BLAKE3 about 0.14 s, 0.21 s together. That is close to the census's
  0.25 s, but zorch cannot run the unit today.
- **CPU:** the census's 0.88 s on 10 M4 cores assumed the paper's M4 Max rate (661k BLAKE3/s). This 32-vCPU pod does
  311k/s (2.1x slower), and the naive unit witness doubles the unit table's cost. Together these give 2.9x the
  census's time (2.59 s).
- A100/H100: flock-bench-80gb's lane (its own harness, 0915Z handoff).

## Link estimate (survey §3.8; estimate only, nothing built)

This is the Flock + link route: a prime-field relation plus a separate binary hash proof. The binary-backend route above
needs no cross-field link, only in-proof glue. Per the coordinator, the link doc is queued for red-team review; nothing
here builds on it beyond pricing its §3.8 steps.

Measured primitives: art:1ef9ac52, Zen4 16T, per shared bit, GF(2^128). eq(r, i) expansion 1.98 ns; 128-way bit-count
dense combination Σ_i C_{t,i}·b_i 0.53 ns; fold 1.60 ns. A BF16 N=4096 batch shares 2 × 3,072 B × 8 × 4,096 =
2.01e8 bits.

| term | per point, CPU 16T | GPU (derived from 143 GMul/s, not run) | for 2^-128 (2 points or GF(2^256)) |
| --- | --- | --- | --- |
| prover: eq + dense combination + y = ẑ(r) claim (materialized) | about 0.51 s | about 1.4 ms eq plus a memory-bound pass | x2: about 1.0 s CPU |
| verifier: eq + dense combination (O(N), no succinct shortcut in §3.8) | about 0.72 s (about 30 ms if eq is streamed) | - | x2: about 1.4 s CPU |
| prime side: N booleanity rows | B-Ligero +512 bit rows per BF16 unit (+14 %, so about +0.04 s on 0.261 s if linear); A-GKR +512/k elements per unit | | |
| prime side: u_t commitment | 128 × 29 ≈ 3.7k elements, negligible | | x2 |
| binary side: y = ẑ(r) through the IO slot | one more batched evaluation claim in Flock's opening; Flock's verify is 8-24 ms, so it is small | | |

Flock + link, BF16 N=4096, 5090:
- B-Ligero bare × 1.14 gives 0.30 s.
- The Flock-CUDA BLAKE3 proof adds 0.29 s (about 0.14 s at zorch's rate).
- The link prover on GPU adds a few ms.
- Total: about 0.45-0.60 s, which is 1.7-2.3x bare. The survey says about 2x.

The load-bearing new cost is the verifier. The link's O(N) eq and dense combination take about 0.7-1.4 s on CPU, which
is 30-170x Flock's own verify. That matches the survey's "on the order of B-Ligero's verifier" only if B-Ligero's
verifier is already around 1 s.

## Survey projections vs measured

| survey claim | measured here | verdict |
| --- | --- | --- |
| §4.2: hash proof about 0.17 s on a 5090 (zorch floor) | zorch m31 36 ms, so m33 about 0.14 s extrapolated; Flock-CUDA m33 0.291 s | holds for zorch; Flock-CUDA is 1.7x |
| §4.2: about 0.6 s on 32 CPU cores | 1.26 s on 32 vCPU (EPYC 9654, 16 cores with SMT); 2.33 s on 16 vCPU Zen4 | about 2x optimistic per vCPU; a 32-physical-core part is unmeasured |
| §4.2: Flock + link BF16 about 2x total (GPU) | 1.7-2.3x (table above; 4090 vs 5090 caveat) | holds |
| §4.3: 393k BLAKE3 in about 1.5 s on 12 threads | 1.77 s at 16T (EPYC 9654), 2.33 s at 16T (Zen4 16 vCPU) | about 1.5-2x optimistic |
| §2/§4.2: SHA-256 about 2x BLAKE3 | 2.2-2.35x per VU (CPU) | holds |
| §2: proofs 200-558 KiB, verify about 6 ms | 295-523 KiB; verify 4-24 ms (CPU), 7-19 ms (GPU proofs) | holds; verify 1-4x |
| §2: flock-zorch 2.36 M BLAKE3/s at 2^17 ("stale, a floor") | 3.64 M/s at 2^17 | beaten (it was a floor) |
| §3.9: Flock `cuda-ghash` has no public throughput | 1.35 M/s at N=4096 BF16 (m33 0.291 s); per-m configs non-monotone; no m29 config | now measured |
| §3.9/§4.1: `clmad` rate unmeasured | 5090: 1.00 T CLMAD/s; GF(2^128) mul 143 G/s | now measured (H100: 80gb lane) |
| §3.9: needs CUDA 13.3 | toolkit 13.3 with driver 580 works | toolkit floor, not driver |
| census: unit table at Flock's BLAKE3 rate per slot bit | GPU, witness outside prove: 0.2-1.7x BLAKE3 at the same m. CPU with my naive witness inside prove: 2x | holds for the prover; unit witness gen needs work |
| census: 5090 BF16 relation + BLAKE3 about 0.25 s | 0.42-0.58 s on Flock-CUDA; about 0.21 s if both ran at zorch rate | 1.7-2.3x on today's GPU code |
