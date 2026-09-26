---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T06:40Z
---

# verify-flock-pure: all eight current real-K Flock cells are verified=accepted as file re-verifications; the four superseded fp8 cells are also accepted (noted superseded); pod terminated 06:38Z; lane total about $3.9

- **Verifier build:** from main c0460349, the integration; its flock-pure-gpu already carries the replay subcommand.
  - For the bench-spine fp8 re-runs I merged flock-backend 3a073d74, whose write_set reads 8-bit sets; the verifier path is
    unchanged from main.
  - Branch lane/verify-flock-pure-realk @ 9bad7c7b, which adds `31-replay.sh` SET / YMODEL / K. It regenerates the instance
    files through `bench.write_instances`, the same function the verifier pod uses.
  - I fetched the spine sets from the store myself and staged them.
- **Each cell's checks:** my instance files match the verifier pod's by sha256, and every recorded session replays under
  main's admission (CN2/CN3/NV1–NV5). The prover's plateau proofs are the recorded ones, and all 12 tampered-record
  negatives behaved as expected.

| cell | result | inputs | verifier run | sessions accepted | replay run |
|---|---|---|---|---|---|
| 4090 fp8-ada K2048 | art:5d2a91a7 | spine art:c0999789 | r20260926-054446-33b0 | 48/48 | r20260926-061059-c818 |
| 4090 fp8-ada K8192 | art:ab115376 | spine art:6ffda100 | r20260926-055342-3115 | 48/48 | r20260926-061059-c818 |
| A100 bf16-ampere K2048 | art:149cdaf9 | captured art:123dc234 | r20260926-042144-6b19 | 24/24 | r20260926-051537-fde5 |
| A100 bf16-ampere K8192 | art:673c1835 | captured art:927a4c3a | r20260926-044447-5e21 | 24/24 | r20260926-051537-fde5 |
| H100 wgmma K2048 | art:c767e092 | art:123dc234, y from the Hopper model | r20260926-042144-f7db | 24/24 | r20260926-051537-fde5 |
| H100 wgmma K8192 | art:bbb95342 | art:927a4c3a, y from the Hopper model | r20260926-042613-b02c | 24/24 | r20260926-051537-fde5 |
| H100 fp8-hopper K2048 | art:66d2412c | spine art:5f311851 | r20260926-054446-1eba | 24/24 | r20260926-061059-c818 |
| H100 fp8-hopper K8192 | art:1c520240 | spine art:d5578eff | r20260926-055227-daa5 | 24/24 | r20260926-061059-c818 |

- **Superseded, labelled accepted:** art:43986c5d (54/54), c0999f7f (102/102), c200eef3 (30/30) and c4d03dd5 (54/54),
  all from synthetic backend inputs. Each carries a note saying it's superseded by the spine re-run.
- Recorded coins are replayed, so this is not transferable evidence.
