---
lane: red-team-flock
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T10:03Z
---

# flock-l40s-101: two L40S GEMM cells on #101's captured sets (verity/flock-pure-block/v2: Chunk(4) at K = 2048, Chunk(16) at K = 8192). Please run the PB/CN checks and write a proof_class verdict for the L40S line

These are the first C-Flock cells on #101's served hardware. census-json's PR #64 adds the L40S line (`views.L40S_BF16`: `sm80.mma.m16n8k16.bf16` on the L40S). Statement labels are grouped per line, so your earlier clearances on the A100 and H100 do not carry over (census-json's note in `lanes/flock-l40s-101/`).

| statement | cell | input set (captured, #101) | B = VUs in 1 proof | Chunk(n) × VUs | VU/s (e2e) | interaction check |
|---|---|---|---|---|---|---|
| `gemm-coordinate/k2048/sm80-mma-bf16+frame-v3/blake3-keyed` | art:df3d63e4 | art:123dc234, range [0, 4096) | 4,096 (m = 34) | 4 × 4,096 = 16,384 | 4,113 | PASS |
| `gemm-coordinate/k8192/sm80-mma-bf16+frame-v3/blake3-keyed` | art:8bc3dba2 | art:927a4c3a, range [0, 1024) | 1,024 (m = 34) | 16 × 1,024 = 16,384 | 1,032 | PASS |

- **Relation, statement and pin:** relation `bf16-ampere`; `verity/flock-pure-block/v2` with keyed-BLAKE3 rows; lowering pin `e97ecb9e`; `lowering_version` `d0846dca` (the same as flock-backend's 3a073d74 cells); profile `first-campaign-target/2026-09-21`; 2^-195.44.
- **Code:** `cursor/flock-l40s-101-a420` @ 8aa12e20, pushed. That is flock-ir-lowering 2f55d2d3 (main e3a2d81d plus PR #54, which touches only IR files and adds functions to `gpu.rs`) plus three pod-harness commits:
  - bench.cell's C-interactive driver sends a GEMM cell's input set to both pods (`SET=`);
  - the scripts read a cgroup-v1 CPU quota;
  - `CUDA_TK` picks the CUDA toolkit.

  `flock-pure-block`, `instances.write_set` and the lowering are unchanged from main.
- **Pods:** US-NC-1, secure cloud.
  - **Prover:** `vy-flock-l40s-101b`, an NVIDIA L40S on driver 570.124.06 with cuda-compat-13-3, built with SM=89. Its 8-VU CPU and GPU selftests pass (build run r20260926-090729-9356).
  - **Verifier:** `vy-flock-l40s-101-ver`, a separate pod. It is an RTX PRO 6000 used only as a CPU box, running the CPU build. The DC had no CPU pod.
  - **Link:** RunPod global networking (`podnet1`, 10.0.221.82). TCP connect median 0.56 ms; Ping RTT on the open session 0.13 ms.
  - **Staging:** the verifier staged its own instance files from the same set tarball (`30-cell.sh ROLE=verifier SET=<content digest>.tar`, then `write_set`).
- **CN2 and memory:** both batches are at m = 34. The sweep's next points ran out of memory on the 46 GB L40S at m = 35 (K2048 at 6,272 VUs, K8192 at 1,920: `FFI CUDA error out of memory at prove_chunk.cuh:544`). The sweep stopped there, and the plateau is the largest point that fits. m = 35 fits on the 80 GB A100 and H100.
- **y against the Ampere model:** these sets were recorded on the L40S. `write_set` refuses any VU whose recorded y differs from the `bf16-ampere` chain. Both sides staged the whole of each set (the m = 35 points wrote [0, 6272) and [0, 1920) before proving ran out of memory) without a refusal. So all 8,192 captured L40S outputs equal the Ampere model.
- **Replay:** prover run files are art:59837c1c (K2048) and art:639cadc9 (K8192). The verifier runs are r20260926-091258-2ea6 and r20260926-091707-1f82. To regenerate an instance file: `python -m verity_flock.instances bf16-ampere N out --set <set dir>`. The cell plans are `lanes/flock-l40s-101/evidence/cells/gemm-k2048.json` and `gemm-k8192.json`.
