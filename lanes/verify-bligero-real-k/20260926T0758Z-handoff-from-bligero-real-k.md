---
lane: verify-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T07:58Z
---

# Nine more new-sender cells to verify, including the re-runs of be42c41a, c8cc8514 and db9f01bf

These cells use the same sender, protocol and dump layout as the 07:05Z handoff. `reverify()` reads `meta.artifacts[0]`
(`sweep/<point>/proofs`), rep 1 of the plateau. All four registered cells are now replaced: 67fb03cb by art:c56a09a8
(07:05Z), and be42c41a, c8cc8514 and db9f01bf by the rows marked below. Each old art carries `superseded_by`.

| art | cell | prover run | verifier run (sessions accepted) | input set | interaction |
|---|---|---|---|---|---|
| art:3bb4d03f | A100 bf16-ampere-x4-k2048+blake3-xob, captured (supersedes art:be42c41a) | r20260926-072307-515a | r20260926-072253-ca25 (20/20) | art:123dc234 (6,272) | -13% |
| art:b1d710da | A100 bf16-ampere-x4-k8192+blake3-xob, captured (supersedes art:c8cc8514) | r20260926-070015-c005 | r20260926-064431-4043 (10/10) | art:927a4c3a (1,920) | pass |
| art:1dafbfd5 | A100 bf16-ampere-x4-k2048+sha256, captured (supersedes art:db9f01bf) | r20260926-073644-7e26 | r20260926-072253-ca25 (20/20) | art:123dc234 (6,272) | -33% |
| art:11208bf7 | H100 bf16-hopper-x4-k8192+blake3-xob, spine wgmma (new) | r20260926-070231-a993 | r20260926-065319-bf61 (15/15) | art:ee183a74 (4,096) | pass |
| art:f1ac2db5 | H100 fp8-hopper-x4-k2048+blake3-xob, spine FP8 (new) | r20260926-073325-f56a | r20260926-073309-3956 (20/20) | art:5f311851 (6,272) | -27% |
| art:9fd5ec09 | H100 fp8-hopper-x4-k8192+blake3-xob, spine FP8 (new) | r20260926-074057-2043 | r20260926-073309-3956 (10/10) | art:d5578eff (1,920) | -15% |
| art:767b54db | RTX 4090 fp8-ada-x4-k8192+blake3-xob, spine FP8 (new) | r20260926-065446-551f | r20260926-064458-327b (10/10) | art:cdb0e90d (1,920) | -36% |
| art:c92a439a | RTX 4090 fp8-ada-x4-k2048+sha256, spine FP8 (new) | r20260926-071013-8db8 | r20260926-070945-4ad5 (20/20) | art:c063de3a (6,272) | -41% |
| art:f451dabc | RTX 4090 fp8-ada-x4-k8192+sha256, spine FP8 (new) | r20260926-072427-b5a6 | r20260926-070945-4ad5 (10/10) | art:cdb0e90d (1,920) | -37% |

- **Interaction check:** "pass" means no problem at all; this also holds for art:c56a09a8 (07:05Z). A negative percentage
  is the cell's only problem: measured time came in that far under the serial model. That happens because proofs now
  stream during proving, while the transfer tail is still counted. Each such cell carries a `note` label, per the root's
  ruling, and the one-sided rule is Daniel's decision. art:664f3142 (07:05Z) is -44%.
- **Verifier evidence:** registrations from 07:33Z on pass `--verifier-run`, so the session counts are in
  `validation.evidence.verifier_run`. The earlier ones (art:c56a09a8, art:664f3142, art:767b54db, art:b1d710da) carry the
  same count in a `note` label instead. The verifier runs were stopped by process group before each relaunch or at the
  end of a pod's queue (rc 143). Their `sessions/index.jsonl` is intact, but the proofs themselves are not kept there
  (`--drop-files`).
- **Next:** the A100 SHA-256 at K=8192 is running, and so is the H100 BF16 SHA-256 at K=2048; the H100 FP8 SHA-256 at
  K=2048 is queued. The RTX 4090 pair is being terminated: its queue is done.
