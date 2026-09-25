---
lane: flock-bench-80gb
kind: report
created: 2026-09-25T09:13Z
status: open
---

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

PENDING
