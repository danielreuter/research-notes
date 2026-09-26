---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T10:52Z
---

# verify-flock-pure: the six L40S #101 cells and both sampling cells are verified=accepted as file re-verifications; A-GKR queue dropped as instructed; pods terminated 10:50Z; about $0.5

## L40S #101 (flock-l40s-101), replay run r20260926-101538-4dd1 (rc 0, preserved)

- **Build:** from lane/verify-flock-l40s @ b4eb302d, which is flock-ir-lowering 2f55d2d3 (IR6 pins) plus my flock-ir-frame
  replay subcommand. The cells ran 8aa12e20, which differs from 2f55d2d3 only in `verity_flock/bench.py` (harness). Its
  flock-pure-gpu equals main's verifier.
- **Re-staging:** I fetched the captured sets from the store and staged the instance files myself.
  - GEMM: `31-replay.sh SET=`. IR: `34-ir-replay.sh`, whose staged files pass IR6 check_leaf_maps at load.
  - Every file matches the verifier pod's by sha256, and the netlists are pinned and equal to the verifier pod's.
- **Proofs and negatives:** the prover's plateau proofs are the recorded ones, and all 12 tampered-record negatives behaved
  as expected on each cell.

| cell | result | sessions accepted | files |
|---|---|---|---|
| GEMM K2048 (flock-pure-block/v2, Chunk(4), art:123dc234) | art:df3d63e4 | 18/18 | 4/4 |
| GEMM K8192 (Chunk(16), art:927a4c3a) | art:8bc3dba2 | 18/18 | 4/4 |
| RoPE (flock-ir-frame/v2, pin 933c4ef8) | art:dc9b92f6 | 24/24 | 4/4 |
| SiLU·mul (823415f4) | art:6dc1f392 | 96/96 | 16/16 |
| RMSNorm fused (e7b8dd88) | art:d1ae527d | 30/30 | 5/5 |
| RMSNorm Triton (6490d5e8) | art:1e7cdc41 | 30/30 | 5/5 |

- **GEMM last points:** the last point of each GEMM sweep (6,272 and 1,920) has no proofs, because the prover stopped, and
  the verifier refused those sessions live ("R7: no proof"). There's nothing to replay there, and it's not part of either
  cell.

## Sampling (flock-ir-sampling), replay run r20260926-102147-4684 (rc 0, preserved)

- **Build:** from lane/verify-flock-sampling @ 38eff1c4, which is f70c6c77 (the cells' commit) plus the replay subcommand.
- **S1:** `replay` refuses a sampling file without `--native-checked`. For every staged file the script runs
  `ir_sampling.check_native` before any replay, and a replay without the attestation is refused, as a 13th negative.
- **Sessions:** art:a330c568 (L40S) 48/48 and art:26b5f7d8 (H100) 48/48, from 4 to 32 rows including the 8-row plateau.
  Staged files match the verifier pod's (8/8 each), the plateau proofs are the recorded ones, and 13/13 negatives behaved as
  expected.
- **Scope:** per red-team-flock-2, and in the labels' note. The proof covers the lane arithmetic and the commitment binding;
  the top-p keep word and the Gumbel noise are checked natively by the verifier, not proven.

## Other

- **A-GKR:** dropped per your 10:48Z change. Run r20260926-104635-3ee0 was stopped at build (rc 143), and nothing was labelled
  from it. The tool is `backends/gkr/verify-afs.sh` on lane/verify-agkr-real-k @ f1ccec97, unused.
- Recorded coins are replayed, so this is not transferable evidence.
