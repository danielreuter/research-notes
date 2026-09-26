---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T10:08Z
---

# verify-flock-pure: both NVFP4 Flock cells are verified=accepted as file re-verifications (art:2753a371 Fp4, art:db7f48de ShaFp4); pod terminated 10:07Z; about $0.12

Replay run r20260926-095555-fdcb (rc 0, preserved), on a cpu3c-16 pod.

- **Build:** from lane/verify-flock-pure-realk @ db908649, which is main c0460349 plus flock-backend 51743c71 (the NVFP4
  write_set) plus `31-replay.sh`. The cells' verifier (51743c71) is identical to main in the verifier path.
- **Re-staging:** I fetched bench-spine's set art:160a53a0 from the store and staged the instance files myself with
  write_set, which re-chains every VU under BLACKWELL_SM120_NVF4 against the set's y. Every file matches the verifier pod's
  by sha256.
- **Each session's checks:** main's admission (CN2/CN3/NV1–NV5), with Σ, the publics and link_sha256 recomputed here under
  the fp4-nvf4 pin fb52a87c. The prover's plateau proofs are the recorded ones, and all 12 tampered-record negatives behaved
  as expected on each cell.

| cell | result | row leaf | verifier run | sessions accepted | files = verifier's | plateau proofs = recorded |
|---|---|---|---|---|---|---|
| Fp4 | art:2753a371 | blake3-keyed/row-nvfp4/v1 | r20260926-092136-85d8 | 30/30 | 5/5 | 12/12 |
| ShaFp4 | art:db7f48de | sha256/row-nvfp4/v1 | r20260926-093034-8f26 | 54/54 | 9/9 | 48/48 |

- **Placement:** the live verifier was in EU-SE-1 while the prover was a COMMUNITY 5090 in Sweden. That's red-team-flock's
  call, and the replay verdict doesn't depend on it; the labels' note says so.
- Recorded coins are replayed, so this is not transferable evidence.
- I'm ready for the per-workload GEMM cells and the sampling cells when they're assigned.
