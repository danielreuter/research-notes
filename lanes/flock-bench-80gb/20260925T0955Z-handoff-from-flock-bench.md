---
lane: flock-bench-80gb
kind: handoff
from: flock-bench
created: 2026-09-25T09:55Z
---

# The census unit now runs on Flock-CUDA (5090, verified): `22-gpu-unit.sh` in my pod-scripts. Reuse it if you get cuda-ghash building for sm_80/90

`lanes/flock-bench/evidence/pod-scripts/22-gpu-unit.sh` patches `cuda-ghash/prove_ffi.cu`:
- `flock_cuda_prove_host` uploads a host-built RowMajor witness;
- `n_blocks_log = m - k_log` replaces the hard-coded `m - 14`.

It generates `tests/gpu_unit.rs`, which Rust `verify_ligerito` checks, and a NaN-operand witness tamper is rejected.

5090 results at N=4096:
- unit ampere_bf16 m32 0.257 s, of which 0.133 s is upload;
- hopper_bf16 0.29 s;
- ada_e4m3 m31 0.295 s;
- device high-water 8.0 GB (m32).

There is no Ligerito config at m29. Numbers and the B-Ligero/census comparison are in my coordinator handoff
`lanes/coordinator/20260925T0945Z-handoff-from-flock-bench.md`. Both my pods are terminated. Your A100/H100 numbers are
the missing column there, so cite that handoff when you report.
