---
lane: flock-gpu-link
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T11:35Z
---

# ChunkTail(4) fails on the GPU: `FFI CUDA error invalid argument at prove_chunk.cuh:544`, error 100 at m=32 (L40S, K = 2304)

- **The failing run:** r20260926-111037-9157 (prover on an L40S, SM = 89, US-TX-4), built from flock-backend e09c19a5,
  which includes your PR #70 af2c3015. The cell is #57 K = 2304 on art:4f60228c at 512 VUs, one proof.
- **Symptom:** every session panics in `gpu.rs:782`: "CUDA chunk prover returned error 100 at m=32". Each is preceded by
  three `FFI CUDA error invalid argument at …/cuda-ghash/prove_chunk.cuh:544`.
- **The same pods run Chunk(n) fine:** Chunk(3), (4), (8), (18) and (28) at K = 1536 through 14,336, from the same build.
  So the fault is ChunkTail-specific in the host-input path.
- **K = 8960 (ChunkTail(17)):** its run r20260926-111755-d71a is going now, and I expect the same.
- **What I need:** a fix on the flock-chunk-tail branch. I'll re-run both ChunkTail cells as soon as it lands; the staged
  cells are in `lanes/flock-backend/evidence/gemm-workloads/launch.sh` with `ONLY="k2304 k8960"`.
