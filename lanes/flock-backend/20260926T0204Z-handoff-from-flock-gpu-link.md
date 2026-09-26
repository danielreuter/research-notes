---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:02Z
---

# gemm_coordinate K = 2048 on the A100 (bf16-ampere), captured #101 set: layout Chunk(4). Selftests pass; all 6,272 VUs in 2.77–2.83 s

- **Layout:** `Chunk(4)` (see my 01:58Z note). A 16-bit K = 2048 row is 4,096 bytes: 4 chunks and 128 units. The Y region
  is the verifier's `out[v]` at chunk 3.
- **Binary:** `cursor/flock-gpu-link-797a` @ 758a8edf, SM = 80. Netlist e97ecb9e (your bf16-ampere pin), unchanged.
- **Inputs: the captured set** `gemm-coordinate-ampere-bf16-k2048`, art:123dc234 (#101, Llama-3.2-1B on an L40S).
  - `inst_k.py captured` reads its x.u16 / w.u16 rows and chains them with `tc_dot` (AMPERE_BF16_M16N8K16).
  - It asserts that f32_to_bf16 of every VU's final accumulator equals the set's recorded y.u16. All 6,272 match.
  - It then calls your `instances.statement` with K = 2048. The instance ref names the set and its content digest
    (49d7658f…) as the manifest.
- **Evidence:** A100-SXM4-80GB, loopback verifier, run r20260926-014936-28eb, art:0f5e418a (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m25) and 64 VUs (m28).
  - 2,048 VUs (m33): 0.91–1.11 s.
  - 4,096 VUs (m34): 1.48–1.67 s.
  - **All 6,272 VUs in one proof (m35): 2.77–2.83 s**, about 2.25 k VU/s. The two reps prove in 1.27 s and 0.73 s. The
    rest, about 0.8 s, is host time: row digests and publics, on this pod's CPU.
- **For the cell:** the whole captured set fits one proof at m35 on the A100. The same file layout works on the H100
  once wgmma-bf16's lowering lands (see step 3 of the plan).
