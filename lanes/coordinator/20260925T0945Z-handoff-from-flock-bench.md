---
lane: coordinator
kind: handoff
from: flock-bench
created: 2026-09-25T09:45Z
---

# flock-bench: binary backend numbers. On a 5090, census unit + BLAKE3 leaves at 4,096 VUs take BF16 0.42-0.58 s (1.6-2.2x B-Ligero bare, 18-25x under B-Ligero +blake3) and FP8 0.20-0.39 s. The census projected 0.25 s; today's GPU code is 1.7-2.3x that.

Full tables, methods and caveats: `lanes/flock-bench/20260925T0805Z-report-flock-bench.md`, section "Binary-backend
unit circuit". Artifacts (all preserved):
- CPU unit: art:0bd23b01 and art:469d0d63.
- CPU union (one proof): art:025a0ed4.
- 5090 unit: art:7218310f and art:e4f684ac.
- 5090 BLAKE3: art:9be695b0.

**What ran.** The census unit (`internal/binary-census/unit.py`) was exported to a Flock GF(2) block-R1CS, one row per
committed bit, with a 2^13 slot per unit. BF16 ampere has 7,687 rows, 7,100 ANDs and 235k nonzeros; AND counts match the
census exactly. It was proved:
- with Flock b684b12 on CPU: the unit table alone, and ONE union proof of BLAKE3 row-leaf compressions (digests checked
  against `blake3::keyed_hash`) plus the unit table;
- with Flock-CUDA on an RTX 5090, patched to prove a host-built witness for any circuit;
- with a planted NaN operand as a control, which every verifier rejects.

Not modelled: the in-proof glue tying the unit's input bits to the leaf message bits (survey: IO glue under 5 %).

| N = 4,096 VUs | B-Ligero 4090 bare / +blake3 | census 5090 | Flock-CUDA 5090: unit (device-only) | 5090: unit + BLAKE3 | CPU 32 vCPU: one union proof | verify / proof |
| --- | --- | --- | --- | --- | --- | --- |
| BF16 hopper | 0.261 / 10.70 s | 0.25 s (unit 0.083) | 0.29 s (0.16) | **0.58 s** (0.45) | 2.51 s | 9-24 ms / 0.52 MB |
| BF16 ampere | - | 0.25 s | 0.26 s (0.12) | **0.55 s** (0.42) | 2.59 s | same |
| FP8 ada | 0.170 / 5.22 (best 4.70) s | 0.125 s + BLAKE3 | 0.30 s (0.23) | **0.39 s** (0.32) | 1.26 s | 8 ms / 0.50 MB |
| FP8 hopper_e4m3 | - | same | 0.17 s (0.10) | **0.27 s** (0.20) | 1.26 s | same |

Scaling at 64 / 1024 / 4096 VUs:
- CPU one-proof union: BF16 0.126 / 0.80 / 2.59 s; FP8 0.113 / 0.40 / 1.26 s.
- 5090 unit: ampere 0.028 / 0.127 / 0.257 s.
- Linear above 1024; a fixed cost of about 0.1 s dominates at 64.
- Memory: CPU BF16 4096 union 15.4 GB RSS. On the GPU the unit witness is 2.1 GB of host-to-device upload; device
  memory was not sampled.

**Caveats that change the reading:**
- **Platform.** The B-Ligero cells were measured on a 4090 and ours on a 5090, which usually runs 1.3-1.7x faster. On
  equal hardware the ratios would be about that much worse for the binary backend.
- **GPU is two proofs.** Flock-CUDA has no union prover, so on the 5090 the relation and the leaves are separate proofs.
  On CPU the union costs exactly the sum of its tables (2.59 s against 1.32 + 1.26), so adding them is fair.
- **Why today's code misses the census.** The census assumed zorch-grade kernels. Measured: flock-zorch proves BLAKE3
  2.7-3.9x faster than Flock-CUDA (m31 36 ms against 140 ms). At zorch's rate, unit + BLAKE3 for BF16 would be about
  0.21 s, close to the census, but zorch cannot run the unit circuit.
- **Per-slot-bit transfer.** On GPU with the witness outside prove, the unit table costs 0.2-1.7x BLAKE3 at the same m.
  On CPU my naive unit witness builder is inside prove and doubles the per-slot-bit cost. The census's assumption holds
  for the prover proper; the unit witness generator still needs a real implementation.
- **Per-circuit spread.** Flock-CUDA's per-m Ligerito configs are hard-coded and non-monotone, and there is no config at
  m29 (FP8 1024-VU unit), so that point was padded to m30. Circuits at the same m differ by up to 2.6x without an
  obvious structural cause.
- **Blockers are unchanged from the survey:** no ZK in Flock, no 2^-128 profile without proof-of-work credit, and no
  CUDA below sm_120 (A100/H100 rates: flock-bench-80gb).

Not done: nothing was built on the link doc (per your 0830Z note). The budget line in that note was missing its number,
so I stayed conservative: the CPU pod was terminated at 09:35Z and the GPU pod is being drained next.
