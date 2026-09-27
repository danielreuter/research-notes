---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-27T05:20Z
---

# verify-flock-pure: all 9 total-unit L40S cells (verity/flock-pure-block-total) are verified=accepted as file re-verifications; replayed on the lane VM's CPU, no pod, $0

- **Run:** replay run r20260927-045439-2525, rc 0 and preserved. It's a local `research run` on the cloud VM (4 vCPU), because
  the replay fit without a pod.
  - An earlier local attempt, r20260927-045401-a92b, failed in about a second on a wrong working directory. It did nothing,
    and nothing was labelled from it.
- **Build:** lane/verify-flock-total @ 4e38e9f1, which is flock-backend 852816d6 (every cell's verifier commit) plus
  `31-replay.sh` BINPATH / WORKDIR.
- **Staging:** for each cell I fetched its bench-spine set from the store; each content digest equals the verifier's SET. I
  staged the files myself with `write_set(relation=bf16-ampere-total)`, and every file matches the verifier pod's by sha256.
- **Sessions:** relation bf16-ampere-total, pin fef256df, domain total. Every recorded accepted session replays with the
  recorded coins, with Σ, the publics and link_sha256 recomputed here. The prover's plateau proofs are the recorded ones, and
  all 12 tampered-record negatives behaved as expected on every cell.

| cell | result | verifier run | sessions accepted | files | plateau proofs |
|---|---|---|---|---|---|
| #39 K1536 | art:199bccee | r20260927-042424-8a73 | 18/18 | 3/3 | 12/12 |
| #57/#67 K2048 | art:c6b96f7e | r20260927-033129-d6c6 | 18/18 | 3/3 | 12/12 |
| #60 K4096 | art:c3a3d2c7 | r20260927-033421-b9c3 | 24/24 | 4/4 | 12/12 |
| #57 K9216 | art:3e1bf074 | r20260927-042818-747f | 48/48 | 8/8 | 24/24 |
| #60 K14336 | art:5bdcd1d1 | r20260927-034454-b761 | 48/48 | 8/8 | 12/12 |
| #101 K2048 | art:216143fd | r20260927-035116-3923 | 30/30 | 5/5 | 12/12 |
| #101 K8192 | art:3367e633 | r20260927-035531-779d | 30/30 | 5/5 | 12/12 |
| #57 K2304 ChunkTail(4) | art:b1e5fed5 | r20260927-040322-8b30 | 18/18 | 3/3 | 12/12 |
| #39 K8960 ChunkTail(17) | art:062f4951 | r20260927-040715-ff8e | 48/48 | 8/8 | 24/24 |

- **Placement:** the shared-NAT record (`cell.placement`) is red-team-flock-3's call; the replay verdict doesn't depend on it.
- Recorded coins are replayed, so this is not transferable evidence.
