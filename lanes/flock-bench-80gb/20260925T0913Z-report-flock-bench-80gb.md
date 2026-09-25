---
lane: flock-bench-80gb
kind: report
created: 2026-09-25T09:13Z
status: final
---

CHECKPOINT none (10:09Z) [final] FINAL 10:14Z: 4096VU binary backend (Flock-CUDA unit+BLAKE3) vs B-Ligero bare: A100 BF16 0.745s 3.1x, H100 BF16 0.745s 6.6x, H100 FP8 0.33s 4.7x; kernel floor 1.0-1.2x; host-bound. art:2a541cd8 art:8b4c35bf. Pods terminated, ~$3.2
CHECKPOINT none (10:09Z) [final] FINAL 10:12Z: 4096VU binary backend (Flock-CUDA unit+BLAKE3) vs B-Ligero bare: A100 BF16 0.745s 3.1x, H100 BF16 0.745s 6.6x, H100 FP8 0.33s 4.7x; kernel floor 1.0-1.2x; host-bound. art:2a541cd8 art:8b4c35bf. Pods terminated, ~$3.2
CHECKPOINT none (09:53Z) [open] 0946Z disk handoff read: my laptop runs total ~17MB (largest r20260925-091229-073a 6.4MB), no big pulls; A100 inspected on pod only. A100 pod q7bv9o3wbj95j8 up (quota 13.6, driver 580); full line r20260925-095215-eaeb in setup (first launch 9eec died: --name).
CHECKPOINT none (09:38Z) [open] H100 done+terminated (~$2.5): clmad 8.4T/s art:7b941558; CPU union BF16 1.32s FP8 0.74s art:8b4c35bf; GPU unit+B3 BF16 0.75s FP8 0.33s art:876ab350; kernel floor BF16 0.137 FP8 0.071 art:b6148b4a,art:83f2d55d. A100 next.
CHECKPOINT 15f74f3 (09:27Z) [open] H100 done: CPU16T unit+BLAKE3 union 4096VU BF16 1.32s FP8 0.74s art:8b4c35bf; Flock-CUDA sm_90 BLAKE3 m33 0.30s m32 0.098s; GPU unit (flock-bench port) m32 0.45s incl 0.28s H2D art:876ab350; xcheck+clmad run r20260925-092702-cc5a; A100 next
CHECKPOINT 10996616 (09:13Z) [open] H100 pod up (17-CPU quota, driver 570 + cuda-compat-13-3); clmad sm_90 8.33 TCLMAD/s, GF128 690 GMul/s; unit-circuit Flock harness bit-exact, proves+verifies; H100 CPU sweep + Flock-CUDA sm_90 running r20260925-091229-073a

# flock-bench-80gb: Flock (pure binary-field backend) on the H100 80GB and A100 80GB lines

Goal (coordinator launch): the 80 GB half of "binary backend vs link": clmad / GF(2^128) peak, Flock CPU prover on the census
unit circuit and on the BLAKE3 row-leaf table (64 / 1024 / 4096 VUs), the GPU port if it builds on sm_90 / sm_80, and a
projection per Table 2 line against B-Ligero bare (A100 BF16 0.2374 s, H100 BF16 0.1131 s, H100 FP8 0.0706 s at 4096 VUs).
No repo worktree (pods only).

Handoffs received: `20260925T0904Z-handoff-from-flock-bench.md` (flock-bench already had a unit harness; it reached me after
mine was written and running, so I keep mine, which adds the unit + BLAKE3 union mode, and cross-check the two harnesses at one
point on the H100 instead of switching).

Also received:
- `20260925T0955Z-handoff-from-flock-bench.md`: their 5090 unit numbers, which the projection reading and the numbers
  handoff cite.
- `20260925T0946Z-handoff-from-coordinator.md`: laptop disk. I pulled A100 evidence only as pruned trees of about 1 MB
  each (no inputs, telemetry or netlists), preserved them, and deleted the local copies. The full runs are in R2 custody.

## Harness (pod-scripts)

- `export_unit.py`: census `unit.py` (bit-exact vs verity.ml.tc) -> Flock canonical R1CS netlist (row i = committed bit z_i,
  (A_i z)(B_i z) = z_i, C = I; const wire last, pinned). Finiteness assertions folded into input rows (A_j = {j} xor L), so
  committed bits = census count + const: ampere_bf16 7,654, hopper_bf16 7,272, hopper_e4m3 6,938 (2^13 slot each).
  Plus 512 verity.ml.tc test vectors + 64 non-finite negatives per pipeline.
- `verity_unit.rs` (into flock-prover `r1cs_hashes/`), `unit_shape.rs` bench: unit table alone, or unit + BLAKE3 row-leaf
  table in ONE Flock union proof (the relation + standard-hash leaves a binary backend proves; chain glue and relation-hash
  region equality NOT modelled, as in flock-bench's verity_shape). Witness = chained VUs (c_in(0) = +0), every row checked.
- `verity_shape.rs` = flock-bench's BLAKE3/SHA-256 row-leaf harness, unchanged.

## Results

### H100 80GB HBM3 (pod gyw0w7e79jak4n, Xeon 8468 host, cgroup quota 17 CPU -> 16 threads, driver 570 + cuda-compat-13-3, CUDA 13.3)

- clmad / GF(2^128) sm_90 (art:7b941558): 8.33-8.40 TCLMAD/s (5090: 1.00); GF(2^128) mul best 690-695 GMul/s (binius+clmad),
  karatsuba ~370, schoolbook ~420, software 10.8.
- Flock CPU, 16 threads, 4096 VUs, every proof verifies, tampered witness rejected (art:8b4c35bf):

  | table | prove s | unit witness s | verify ms | proof KiB | peak heap GB |
  |---|---|---|---|---|---|
  | unit ampere_bf16 | 0.733 | 0.100 | 6.2 | 446 | 9.1 |
  | unit hopper_bf16 | 0.603 | 0.107 | - | 438 | - |
  | unit hopper_e4m3 | 0.429 | 0.045 | - | 420 | - |
  | union ampere_bf16 + BLAKE3 | 1.388 | 0.106 | 8.3 | 507 | 25.9 |
  | union hopper_bf16 + BLAKE3 | 1.317 | 0.112 | 9.1 | 503 | 25.6 |
  | union hopper_e4m3 + BLAKE3 | 0.741 | 0.044 | 8.5 | 488 | 15.1 |
  | BLAKE3 BF16 (96 compr/VU) | 1.135 | - | 8.0 | 423 | 16.4 |
  | BLAKE3 FP8 (48 compr/VU) | 0.567 | - | 7.2 | 408 | 8.0 |

  1024 VUs: union ampere 0.417, unit ampere 0.222, BLAKE3 BF16 0.298 s. 64 VUs: unit 0.032, union 0.067, BLAKE3 0.054 s.
  Union is ~26% cheaper than the two tables proved separately. flock-bench's harness on the same host (art:7b941558):
  ampere_bf16 4096 prove 1.136 s incl. 0.61 s naive witness; hopper_e4m3 0.573 s incl. 0.27 s: consistent.
- Flock-CUDA on sm_90 (build.rs sed sm_120 -> sm_90; steady prove incl. host glue, 3 reps, all verified; art:876ab350):
  BLAKE3 m32 (FP8 4096 VUs) 0.098 s, m33 (BF16 4096 VUs) 0.30 s; proof 404-534 KB, verify 16-23 ms, RSS 0.8 GB. Same
  wall as the 5090 despite 8.4x its CLMAD rate: host-bound, not CLMAD-bound.  Census unit via flock-bench's `flock_cuda_prove_host` port: hopper_bf16 m32 0.445 s (of which 0.25-0.29 s pageable H2D of
  the 2.15 GB witness), ampere_bf16 m32 0.44 s, hopper_e4m3 m31 0.232 s (0.126 s H2D). hopper_e4m3 m29 panics "no fast
  ligerito config for m=29" (Flock-CUDA config gap; not on the 4096 path).
- nsys kernel time per prove (art:b6148b4a, art:83f2d55d): BLAKE3 m32 0.047 s, m33 0.092 s (vs 0.31 s wall:
  cudaDeviceSynchronize 272 ms + cudaMemcpy 112 ms over 2 proves); unit hopper_bf16 m32 0.045 s; unit hopper_e4m3 m31
  0.024 s. Top kernels: zerocheck_first_round_cpu_structured, ring_switch_combine_basis, ring_switch_fold_rows_grouped.

### A100 80GB SXM4 (pod q7bv9o3wbj95j8, EPYC 7742 Zen2 host (no AVX-512 / VPCLMULQDQ), quota 13.6 CPU -> 13 threads, driver 580, CUDA 13.3; run r20260925-095215-eaeb, art:2a541cd8)

- clmad / GF(2^128) sm_80: 3.92 TCLMAD/s (0.47x H100); GF(2^128) mul best 369-399 GMul/s (binius+clmad), schoolbook
  ~242, karatsuba ~213, software 5.3-6.7; 884k chained 373 GMul/s.
- Flock CPU, 13 threads, ampere_bf16, all verified:

  | table | 64 VU s | 1024 VU s | 4096 VU prove s | unit witness s | verify ms | proof KiB | peak heap GB |
  |---|---|---|---|---|---|---|---|
  | unit ampere_bf16 | 0.053 | 0.511 | 2.043 | 0.179 | 5.0 | 446 | 9.1 |
  | union ampere_bf16 + BLAKE3 | 0.125 | 1.363 | 5.370 | 0.173 | 13.3 | 507 | 25.9 |
  | BLAKE3 BF16 | 0.114 | 0.960 | 3.591 | - | 9.1 | 423 | 16.4 |

  2.8-3.9x the H100 host: the CPU column is a property of the host (Zen2 without VPCLMULQDQ), not of the A100 line.
- Flock-CUDA builds and runs on sm_80 (same sed as sm_90). Steady prove incl. glue, 2 reps, all verified:
  BLAKE3 m27 0.072, m31 0.191, m33 (BF16 4096 VUs) 0.406 s, verify 19-24 ms. Census unit ampere_bf16 m26 0.036,
  m30 0.161-0.178, m32 0.339-0.341 s incl. 0.15-0.165 s H2D of 2.15 GB (excl ~0.18 s); verify 8.5 ms; NaN-operand witness
  tamper rejected (Lincheck ConsistencyFailed sumcheck-final).
- nsys per prove (run r20260925-100453-eb27, art:2428284b): BLAKE3 m33 kernels 0.162 s, unit m32 kernels 0.082 s
  (H2D 0.20 s per unit prove). A100 kernels are ~1.8x the H100's, yet the GPU wall matches the H100 (0.745 s): host-bound.

### Projection, binary backend = census unit table + BLAKE3 row leaves, 4096 VUs, vs B-Ligero bare

Not modelled: chain glue and relation-hash region equality (as in flock-bench), so these are lower bounds on the backend.
"GPU measured" = two separate Flock-CUDA proofs (no GPU union), witness built on host and uploaded (pageable).

| line | bare s | CPU union s (x) | GPU measured s (x) | GPU excl H2D s (x) | GPU kernel floor s (x) |
|---|---|---|---|---|---|
| H100 BF16 | 0.1131 | 1.317 (11.6x) | 0.445+0.30 = 0.745 (6.6x) | 0.17+0.30 = 0.47 (4.2x) | 0.045+0.092 = 0.137 (1.2x) |
| H100 FP8 | 0.0706 | 0.741 (10.5x) | 0.232+0.098 = 0.330 (4.7x) | 0.106+0.098 = 0.204 (2.9x) | 0.024+0.047 = 0.071 (1.0x) |
| A100 BF16 | 0.2374 | 5.370 (22.6x; 1.388 = 5.8x on the H100 host) | 0.339+0.406 = 0.745 (3.1x) | 0.18+0.406 = 0.59 (2.5x) | 0.082+0.162 = 0.244 (1.03x) |

Reading: the census "~1x bare" matches only the kernel floor, i.e. a Flock-CUDA with device-side unit witness gen and no
host glue, on every 80 GB line (1.0-1.2x). As shipped it is 3.1x (A100) and 4.7-6.6x (H100) bare, and the absolute GPU wall
is the same ~0.75 s for BF16 on A100, H100 and ~0.55 s on the 5090 (flock-bench): Flock-CUDA's host glue and pageable
witness upload, not CLMAD rate (8.4x / 3.9x the 5090's), set the time. Unlike flock-bench's 5090-vs-4090 cells, these
ratios are same-GPU (bare measured on the same SKU). Census rate assumption 38.7 G slot-bit/s vs 2^33 / wall at m33 =
28.6 G (H100) / 21.2 G (A100) measured end-to-end (kernel-only: 93 G / 53 G).

## FINAL

~~~text
tip: none (no repo worktree; pods only; harness in lanes/flock-bench-80gb/evidence/pod-scripts/)        merge-with: none
known-failures: Flock-CUDA has no fast Ligerito config at m29 (hopper_e4m3 1024-VU unit panics; not on the 4096 path)    pod: H100 gyw0w7e79jak4n terminated 09:38Z, A100 q7bv9o3wbj95j8 terminated 10:07Z; ~$3.2 (H100 ~0.7 h x $3.49, A100 ~0.5 h x $1.59)
artifacts: art:7b941558 art:8b4c35bf art:876ab350 art:b6148b4a art:83f2d55d art:2a541cd8 art:2428284b
~~~

Numbers handoff: `lanes/coordinator/20260925T1010Z-handoff-from-flock-bench-80gb.md`, with copies in flock-bench,
agkr-bound and b-ligero-standard-hash. At 4096 VUs, the binary backend as shipped (Flock-CUDA, two proofs, host-built
unit witness) against B-Ligero bare on the same SKU:
- A100 BF16: 0.745 s, 3.1x.
- H100 BF16: 0.745 s, 6.6x.
- H100 FP8: 0.330 s, 4.7x.

The GPU kernel floor is 1.03x, 1.2x and 1.0x on those lines. CPU union proofs run 10.5-22.6x bare, and the CPU numbers
depend on the host.

The gap is Flock-CUDA's host glue and pageable witness upload, not CLMAD rate: the H100 has 2.1x the A100's CLMAD rate
and the same BF16 wall. The census "~1x bare" therefore needs three things: device-side unit witness generation, no
host round-trips, and a GPU union prover.

kb updates:
- `kb/flock-prover.md`: H100 constants, the sm_90/sm_80 build, the host-bound finding.
- `kb/ops-tools.md`: rayon versus the cgroup quota, cuda-compat on driver 570, re-registering after an interrupted
  `pods create`, and `run --on --name` failing.

Two notes on the FINAL checks:
- `pushed: lane/flock-bench-80gb missing` is expected, because this lane had no worktree or branch.
- notes sync skipped the three `unit-*.netlist` files (over 1 MB). They are in the preserved H100 run inputs, and
  `export_unit.py` regenerates them in under a second.

Left undone: A100 FP8 (not a Table 2 line), flock-zorch on the 80 GB cards, and a pinned-memory upload variant.
