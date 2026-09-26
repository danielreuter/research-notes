---
lane: verify-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T08:45Z
---

# The last five new-sender cells to verify: the 16-cell real-K matrix is complete

These cells use the same sender, protocol and dump layout as the 07:05Z and 07:58Z handoffs. `reverify()` reads
`meta.artifacts[0]` (`sweep/<point>/proofs`), rep 1 of the plateau. Every cell here carries its verifier-run session
counts in `validation.evidence.verifier_run`.

| art | cell | prover run | verifier run (sessions accepted) | input set | interaction |
|---|---|---|---|---|---|
| art:622c9737 | A100 bf16-ampere-x4-k8192+sha256, captured (new) | r20260926-075125-a608 | r20260926-072253-ca25 (10/10) | art:927a4c3a (1,920) | -17% |
| art:4b567c9c | H100 bf16-hopper-x4-k2048+sha256, spine wgmma (new) | r20260926-074816-11c0 | r20260926-073309-3956 (15/15) | art:4f27dc3d (4,096) | -21% |
| art:e8fb169d | H100 bf16-hopper-x4-k8192+sha256, spine wgmma (new) | r20260926-081620-1969 | r20260926-073309-3956 (15/15) | art:ee183a74 (4,096) | -20% |
| art:82587955 | H100 fp8-hopper-x4-k2048+sha256, spine FP8 (new) | r20260926-075526-f055 | r20260926-073309-3956 (15/15) | art:5f311851 (6,272) | -27% |
| art:9260a985 | H100 fp8-hopper-x4-k8192+sha256, spine FP8 (new) | r20260926-083140-322b | r20260926-073309-3956 (10/10) | art:d5578eff (1,920) | pass |

- **Interaction check:** "pass" means no problem at all. A negative percentage is the cell's only problem: measured
  time came in that far under the serial model. Each such cell carries a `note` label, per the root's ruling.
- **Full set of new-sender cells:** 16, one per fold × K × leaf:
  - 07:05Z: art:c56a09a8, art:664f3142.
  - 07:58Z: art:3bb4d03f, art:b1d710da, art:1dafbfd5, art:11208bf7, art:f1ac2db5, art:9fd5ec09, art:767b54db,
    art:c92a439a, art:f451dabc.
  - Here: art:622c9737, art:4b567c9c, art:e8fb169d, art:82587955, art:9260a985.
- **Pods:** all of this lane's pods are being terminated once `research pods drain` confirms every attempt is preserved.
  The proofs stay in each prover run's custody (R2).
