---
lane: flock-bench
kind: report
created: 2026-09-25T08:05Z
status: open
---

CHECKPOINT 806a2f73 (09:12Z) [open] 09:13Z unit circuit on Flock CPU (EPYC9654 32vCPU) art:0bd23b01: BF16 4096VU m32 prove 1.32s (0.66 naive witness) verify 4ms 461KB 8.2GB; BLAKE3 same host m33 1.26s; per-slot-bit ~equal; tamper rejected. GPU unit via patched Flock-CUDA host-witness building (r20260925-091040-8ec8)
CHECKPOINT none (09:03Z) [open] 09:03Z NEW PRIORITY (coord 0830Z handoff) taken: census unit exported to Flock block-R1CS (BF16 7687 rows/2^13, 235k nnz), smoke 64VU prove .085s verify ok; full unit+BLAKE3 sweep on 32vCPU Zen4 r20260925-090255-c8f0; zorch B still running
CHECKPOINT none (08:44Z) [open] 08:44Z CPU Zen4 table done (thin LTO); link prims measured (eq 2ns/bit, count .5, fold 1.6 @16T); zorch part B running on 5090 (r20260925-082947-b255); Flock-CUDA reps next; CPU pods terminated
CHECKPOINT a816a2b1 (08:28Z) [open] CPU Zen4 16T sweep done art:aa24c7eb (BLAKE3 BF16 N=4096 2.33s/433KB/14ms verify; SHA 5.47s/479KB); Flock-CUDA 5090 m26-33 verified (m33 0.29s); zorch running; next: CUDA reps, zorch, link estimate
CHECKPOINT a816a2b1 (08:05Z) [open] pods up (cpu3c 8vCPU Zen5 only; 16/32 sold out; 5090 community); CUDA13.3 clmad 5090: 1.00 TCLMAD/s, 143 GMul/s karatsuba; harness verity_shape.rs written; next: CPU flock runs, Flock-CUDA + flock-zorch on 5090

# flock-bench: Flock on verity's frame-v3 row-leaf batch

Goal (launch message): ground `docs/hash-proving-survey.md` §2/§3.1/§3.8/§3.9/§4.2-4.3/§6 "Flock plus link" projections
in measurements at our batch shape. No repo commits (no reusable harness in the repo; harnesses live in
`evidence/pod-scripts/`). Handoffs received: none (inbox empty at start and at every checkpoint).

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
PENDING-REPS (first single-sample pass, r20260925-081807-9691: m26 0.104 s, m27 0.056 s, m30 0.104 s, m31 0.139 s,
m32 0.093 s, m33 0.293 s; proof 395-521 KiB; verify 15-17 ms; host RSS 0.8 GB).

flock-zorch: PENDING.

## Link estimate (survey §3.8; estimate only, nothing built)

PENDING

## Survey projections vs measured

PENDING
