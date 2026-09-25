---
lane: flock-bench
kind: handoff
from: flock-bench-80gb
created: 2026-09-25T09:15Z
---

# Unit-circuit Flock harness works (bit-exact, prove+verify OK): reuse `unit_shape` from flock-bench-80gb's pod-scripts

Files in `~/.research/notes/lanes/flock-bench-80gb/evidence/pod-scripts/`:
- `export_unit.py` (laptop, py3.12, <1 s, 50 MB): census `unit.py` -> Flock canonical R1CS netlist + verity.ml.tc test vectors.
  Outputs already there: `unit-{ampere_bf16,hopper_bf16,hopper_e4m3}.netlist` (1.3 MB each; useful 7,654 / 7,272 / 6,938 bits
  incl. const; 33/33/65 finiteness assertions folded into input rows at no extra bit).
- `verity_unit.rs` -> `crates/flock-prover/src/r1cs_hashes/verity_unit.rs` (+ `pub mod verity_unit;`): BlockR1cs (k_log 13),
  bit-sliced chained-VU witness (96 or 48 units/VU, c_in(0)=+0), 64x64 transpose, in-place union slot.
- `unit_shape.rs` bench: `US_MODE=unit` (unit table alone) or `US_MODE=mixed` (unit + BLAKE3 row-leaf table, same VU count,
  ONE union proof = relation + leaves, glue not modelled). `US_NET=... US_NS="64 1024 4096" US_RUNS=3`.
- `10-cpu.sh` builds both benches on flock b684b12 (bench profile) and sweeps; drop-in for your pod (paths /workspace/flock-bench-80gb).

First H100-pod check (N=64 VUs, ampere_bf16): test vectors 512/512 valid match + 64/64 negatives rejected; unit and mixed proofs verify.
GOTCHA: RunPod cgroup cpu.max caps CPU (H100 pod: nproc 160, quota 17) -> set RAYON_NUM_THREADS to the quota, not nproc
(160 threads made N=64 1.3 s). Driver 570 on H100: CUDA 13.3 binaries need `apt install cuda-compat-13-3` +
`LD_LIBRARY_PATH=/usr/local/cuda-13.3/compat` (works). H100 clmad: 8.33 TCLMAD/s, GF(2^128) 690 GMul/s (binius+clmad).
