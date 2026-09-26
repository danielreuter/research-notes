---
lane: verify-flock-pure
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T10:03Z
---

# flock-l40s-101: six #101 C-Flock cells on an L40S (two GEMM, four elementwise frame cells) for non-producer replay and `independently_verified`

These are the first C-Flock cells on #101's served hardware. They count in the Workload headline only with a non-producer verification label, preserved proof files and a red-team `proof_class` (census-json's note in `lanes/flock-l40s-101/`).

| statement | cell | set | B (proofs) | e2e /s | prover run (run_files) | verifier run |
|---|---|---|---|---|---|---|
| `gemm-coordinate/k2048/sm80-mma-bf16` | art:df3d63e4 | art:123dc234 | 4,096 (1) | 4,113 | r20260926-091307-6e8e (art:59837c1c) | r20260926-091258-2ea6 |
| `gemm-coordinate/k8192/sm80-mma-bf16` | art:8bc3dba2 | art:927a4c3a | 1,024 (1) | 1,032 | r20260926-091717-661b (art:639cadc9) | r20260926-091707-1f82 |
| `rope-head/d64/neox-bf16` | art:dc9b92f6 | art:16825154 | 1,024 (1) | 1,136 | r20260926-092147-abed (art:1285baef) | r20260926-092141-73ff |
| `silu-mul/i8192/bf16` | art:6dc1f392 | art:d3e2d9b1 | 64 (2) | 10.2 | r20260926-092512-acec (art:dbb9a40c) | r20260926-092506-6e11 |
| `rmsnorm-fused-cuda/n2048-eps1e-05/bf16` | art:d1ae527d | art:a261c0c2 | 128 (1) | 19.5 | r20260926-093933-baf0 (art:e32c46a7) | r20260926-093927-1c91 |
| `rmsnorm-triton/n2048-eps1e-05/bf16` | art:1e7cdc41 | art:9582a734 | 256 (1) | 18.8 | r20260926-094831-b0d0 (art:e0a79895) | r20260926-094826-eb4b |

Every statement's scheme is `frame-v3/blake3-keyed`.

- **Code:** `cursor/flock-l40s-101-a420` @ 8aa12e20, pushed. It is flock-ir-lowering 2f55d2d3 (PR #54, IR6) plus pod-harness commits; it already contains main's `31-replay.sh` input-set / K options.
  - **GEMM:** `flock-pure-block/v2`, relation `bf16-ampere`, Chunk(4) and Chunk(16), sets art:123dc234 and art:927a4c3a with no y-model. It is the same statement as flock-backend's A100 cells art:149cdaf9 / art:673c1835, at the same K and on the same sets.
  - **Frame cells:** `flock-ir-frame/v2` at the IR6 pins (933c4ef8, 823415f4, e7b8dd88, 6490d5e8). Your r20260926-075751-1b20 replayed the c53d9148 pins, so re-verifying these needs a tree at 2f55d2d3 or later.
- **Proof files:** each prover run's `run_files` art holds `sweep/<point>/proofs-s*` and the session logs. Custody is on R2: `research data preserved` passes for every run.
- **Verifier runs:** they staged their own instance files. Each is named in the table.
