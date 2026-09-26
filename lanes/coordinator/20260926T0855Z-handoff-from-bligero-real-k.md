---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T08:55Z
---

# B-Ligero real-K is complete: 16 new-sender cells; be42c41a, c8cc8514, 67fb03cb and db9f01bf are superseded

Every fold × K × leaf is now registered with the sender from PR #55 (merged 07:35Z):
{bf16-ampere, bf16-hopper, fp8-ada, fp8-hopper} × K ∈ {2048, 8192} × {keyed-BLAKE3 xob, SHA-256}. Each old cell carries
`superseded_by`: be42c41a → 3bb4d03f, c8cc8514 → b1d710da, 67fb03cb → c56a09a8, db9f01bf → 1dafbfd5.

| cell | art | plateau VU/s | interaction |
|---|---|---:|---|
| A100 BF16 K2048 xob / sha256 (captured #101) | art:3bb4d03f / art:1dafbfd5 | 1,886 / 1,294 | -13% / -33% |
| A100 BF16 K8192 xob / sha256 (captured #101) | art:b1d710da / art:622c9737 | 372 / 329 | pass / -17% |
| H100 BF16 K2048 xob / sha256 (spine wgmma) | art:c56a09a8 / art:4b567c9c | 2,672 / 1,849 | pass / -21% |
| H100 BF16 K8192 xob / sha256 (spine wgmma) | art:11208bf7 / art:e8fb169d | 464 / 458 | pass / -20% |
| RTX 4090 FP8 K2048 xob / sha256 (spine) | art:664f3142 / art:c92a439a | 3,779 / 2,183 | -44% / -41% |
| RTX 4090 FP8 K8192 xob / sha256 (spine) | art:767b54db / art:f451dabc | 674 / 534 | -36% / -37% |
| H100 FP8 K2048 xob / sha256 (spine) | art:f1ac2db5 / art:82587955 | 5,494 / 3,776 | -27% / -27% |
| H100 FP8 K8192 xob / sha256 (spine) | art:9fd5ec09 / art:9260a985 | 1,185 / 804 | -15% / pass |

- **Interaction check:** 4 of the 16 cells pass outright.
  - The other 12 have one problem only: measured time comes in 13-44% under the serial model. That happens because proofs
    now stream while the prover works, and the transfer tail is still counted.
  - Each of the 12 carries a `note` label. They count only if Daniel accepts the one-sided rule; your preview switch
    covers that.
- **Verification:** every cell's live verifier on a separate pod accepted all its sessions. verify-bligero-real-k has all
  16 in three handoffs: 07:05Z, 07:58Z and 08:45Z (`lanes/verify-bligero-real-k/`).
- **Pods and spend:** the RTX 4090, A100 and first verifier pods are terminated. The H100 pair terminates as soon as
  `research pods drain` confirms every attempt is preserved. Spend is about $47 of the $52.
