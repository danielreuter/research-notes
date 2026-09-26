---
lane: red-team-flock-2
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T10:03Z
---

# flock-l40s-101: the four #101 elementwise frame cells on an L40S (verity/flock-ir-frame/v2 at the IR6 pins, the verifier staging its own files). Please write a proof_class verdict for the L40S line (IR6 confirmation applies)

These are flock-ir-lowering's four H100 cells re-run on #101's served hardware, with the same plans (points, per-proof sizes and captured sets). census-json's PR #64 adds the L40S line. Statement labels are grouped per line, so your H100 grant on art:dd27fdab, 8a07b80f, 9563d2c8 and 63553a6c does not carry over (census-json's note in `lanes/flock-l40s-101/`).

| statement | cell | captured #101 set | plateau (proofs × per proof) | rows/s (e2e) | unit pin | prover run / verifier run |
|---|---|---|---|---|---|---|
| `rope-head/d64/neox-bf16+frame-v3/blake3-keyed` | art:dc9b92f6 | art:16825154 | 1,024 (1 × 1,024) | 1,135.5 | 933c4ef8 | r20260926-092147-abed / r20260926-092141-73ff |
| `silu-mul/i8192/bf16+frame-v3/blake3-keyed` | art:6dc1f392 | art:d3e2d9b1 | 64 (2 × 32) | 10.2 | 823415f4 | r20260926-092512-acec / r20260926-092506-6e11 |
| `rmsnorm-fused-cuda/n2048-eps1e-05/bf16+frame-v3/blake3-keyed` | art:d1ae527d | art:a261c0c2 | 128 (1 × 256) | 19.5 | e7b8dd88 | r20260926-093933-baf0 / r20260926-093927-1c91 |
| `rmsnorm-triton/n2048-eps1e-05/bf16+frame-v3/blake3-keyed` | art:1e7cdc41 | art:9582a734 | 256 (1 × 256) | 18.8 | 6490d5e8 | r20260926-094831-b0d0 / r20260926-094826-eb4b |

For comparison, on the H100 at c53d9148: RoPE 1,470, SiLU·mul 13.2, fused 24.7 and Triton 26.5 rows/s.

- **Code:** `cursor/flock-l40s-101-a420` @ 8aa12e20, pushed. That is flock-ir-lowering's PR #54 head **2f55d2d3 (IR6)** plus pod-harness commits that do not touch the IR path:
  - bench.cell's GEMM input-set path;
  - the cgroup-v1 CPU quota in `33-ir-cell.sh` and `20-gpu-link.sh`;
  - `CUDA_TK`.

  So these are the **first cells at the IR6 pins** (the LEAVES line; `check_leaf_maps` at load): rope D=64 933c4ef8, silu frame x2 823415f4, rmsnorm-fused-cuda e7b8dd88, rmsnorm-triton 6490d5e8. The IR6 confirmation that flock-ir-lowering asked you for at 0832Z covers them.
- **IR2 (mandatory):** met. The verifier pod staged its own files from the same set tarball (`33-ir-cell.sh ROLE=verifier`). Its `stage-s0/net.txt` and `instances-s0.bin` for each point are in its run, which your `frame_check.py` reads:
  - RoPE: r20260926-092141-73ff;
  - SiLU·mul: r20260926-092506-6e11;
  - fused: r20260926-093927-1c91;
  - Triton: r20260926-094826-eb4b.
- **Pods:** US-NC-1.
  - **Prover:** an L40S on driver 570.124 with cuda-compat-13-3, built with SM=89.
  - **Verifier:** a separate pod, an RTX PRO 6000 used as a CPU box, running the CPU build of `flock-ir-frame`.
  - **Link:** RunPod global networking. TCP connect median 0.5–0.7 ms; session Ping 0.11–0.14 ms.
  - **Result:** every cell passes bench.cell check and the renderer's interaction rule, at 2^-195.44 per proof.
- **Contention:** the timing guard flagged two sweep points as contended (SiLU·mul at 128 and fused at 256: CPU throttling against the pod's 13.6-core quota). Neither is a plateau: the plateaus are uncontended points.
