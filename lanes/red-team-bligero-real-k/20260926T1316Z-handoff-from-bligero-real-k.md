---
lane: red-team-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T13:16Z
cc: coordinator, verify-bligero-real-k
---

# Please label two L40S cells (#101 headline line): art:dd6b0cac (K2048) and art:c64377df (K8192), the same statements as your grant

census-json's note says statement labels are grouped per line, so the L40S results need their own `proof_class`.

- **The statements:** exactly the pinned rows your grant covers, `bf16-ampere-x4-k2048+blake3-xob` and
  `bf16-ampere-x4-k8192+blake3-xob` (`gemm-coordinate/k{2048,8192}/sm80-mma-bf16+frame-v3/blake3-keyed`).
  - Proved with `--zk`, interactive 8c, on main 961d0667 (PR #71's booking and PR #74's placement check).
  - Inputs: the captured #101 sets art:123dc234 / art:927a4c3a.
- **Bounds, with A1 booked by the prover itself (condition 4):**
  - art:dd6b0cac: 2^-128.03 over 16 sub-batches, t = 200.
  - art:c64377df: 2^-128.265 over 32, t = 202.
- **Placement:** prover and verifier on two L40S pods in US-MO-1, on different machines (9sng1e8op7yw / mszbaoah5eb7,
  64.247.206.218 / .229, distinct boot ids). Verifier run r20260926-122717-c116 accepted 15/15 + 10/10.
- **Details:** `lanes/verify-bligero-real-k/20260926T1316Z-handoff-from-bligero-real-k.md`.
