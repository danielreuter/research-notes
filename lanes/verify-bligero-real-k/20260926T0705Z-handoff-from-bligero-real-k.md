---
lane: verify-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T07:05Z
---

# New-sender cells to verify (first two): art:c56a09a8 (re-run of 67fb03cb) and art:664f3142 (4090 FP8, new); more follow

The sender now streams proofs on 4 parallel data connections (root's ruling 2026-09-26). The protocol, the statements and
the proof bytes are unchanged, and the dump layout is the same (`sweep/<point>/proofs`). `reverify()` now tries
`meta.artifacts[0]` (29c04001).

| art | cell | prover run | verifier run | input set |
|---|---|---|---|---|
| art:c56a09a8 | H100 bf16-hopper-x4-k2048+blake3-xob, spine wgmma (supersedes art:67fb03cb) | r20260926-065344-8c18 | r20260926-065319-bf61 | art:4f27dc3d (4,096) |
| art:664f3142 | RTX 4090 fp8-ada-x4-k2048+blake3-xob, spine FP8 (new) | r20260926-064526-48cb | r20260926-064458-327b | art:c063de3a (6,272) |

- **E4M3 input sets:** `relchain.set_instances` compares the u32 `y` as the FP32 accumulator (9ef1d11f). The FP8 set
  templates come from PR #57's branch, which is merged into mine.
- **The verifier runs:** they record verdict JSON only (`--drop-files`). The proofs to re-verify are the prover's plateau
  dump, rep 1.
- **Next:** I'll write a follow-up handoff as each re-run lands (be42c41a, c8cc8514 and db9f01bf on the A100), then the FP8
  cells on the H100 and 4090.
