---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T12:32Z
---

# verify-flock-pure: all eight per-workload GEMM cells are verified=accepted as file re-verifications; pod terminated 12:31Z; about $0.25

- **Builds:** each cell's verifier was built from the commit it names, using its own replay subcommand and `31-replay.sh`
  staging.
  - Six cells ran e09c19a5: lane/verify-flock-workload, replay run r20260926-114049-edf0.
  - Two cells ran 581c3084: lane/verify-flock-workload-581 @ 2266e096 (581c3084 plus e09c19a5's `31-replay.sh`), replay run
    r20260926-122145-c586.
  - The first run's rc 1 comes only from those two 581c3084 cells: staged with e09c19a5's instance writer, the file header
    gains `content_digest` in its instance ref, which Σ binds, so their files didn't match the verifier's. Restaged with
    581c3084's writer, they match and replay.
- **Re-staging:** I fetched each bench-spine set from the store and staged the instance files myself with write_set. Every
  file matches the verifier pod's by sha256.
- **Each session's checks:** every recorded accepted session replays under main's admission, with Σ, the publics and
  link_sha256 recomputed here. The prover's plateau proofs are the recorded ones, and all 12 tampered-record negatives
  behaved as expected on every cell.

| workload / line | K / layout | result | set | verifier run | sessions accepted | files |
|---|---|---|---|---|---|---|
| #73 H100 wgmma | 4096 / Chunk(8) | art:d9a40cd4 | art:cdc7b5eb | r20260926-100228-ce99 | 18/18 | 3/3 |
| #73/#74 H100 wgmma | 2560 / Chunk(5) | art:8b5a0bf1 | art:01326d5b | r20260926-100445-34f4 | 18/18 | 3/3 |
| #73 H100 wgmma | 9728 / Chunk(19) | art:2e5ea606 | art:8ab7c2da | r20260926-101605-2948 | 30/30 | 5/5 |
| #39 L40S sm80 | 1536 / Chunk(3) | art:4e3f5048 | art:dbaacc6f | r20260926-105305-b3c4 | 18/18 | 3/3 |
| #57/#67 L40S sm80 | 2048 / Chunk(4) | art:aea553ae | art:69cb815c | r20260926-105650-3ef5 | 18/18 | 3/3 |
| #60 L40S sm80 | 4096 / Chunk(8) | art:86780ca6 | art:bfed1730 | r20260926-105908-8593 | 24/24 | 4/4 |
| #57 L40S sm80 | 9216 / Chunk(18) | art:4a319a65 | art:c6237f08 | r20260926-110129-2549 | 48/48 | 8/8 |
| #60 L40S sm80 | 14336 / Chunk(28) | art:89dab836 | art:762f5923 | r20260926-110559-1e87 | 48/48 | 8/8 |

- **L40S placement:** the labels note that the verifier pod shared a machine with the prover (separate pods, private
  network), as flock-backend reported. The replay verdict doesn't depend on it.
- **Set provenance:** the #73 wgmma sets' own header names their source as "synthetic" (bench-spine PR #68), not captured.
- Recorded coins are replayed, so this is not transferable evidence.
