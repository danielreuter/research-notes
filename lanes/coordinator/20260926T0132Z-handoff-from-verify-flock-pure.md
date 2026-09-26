---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T01:32Z
---

# verify-flock-pure: all four SHA-256 Flock cells are verified=accepted as file re-verifications (728d8724, df857ea6, fd772057, 324888c5); pod terminated 01:31Z; lane total about $3.2

Replay run r20260926-011150-e4e9 (rc 0, preserved).

- **Verifier build:** from lane/verify-flock-pure @ 787ac154, which is flock-backend c058c33f plus my replay subcommand.
  - c058c33f and bab181d6, which the H100 E4M3 and 4090 verifiers ran, are identical in the verifier path. c058c33f only
    adds the fp4-nvf4 pin.
  - For the SHA row layouts, the replay rebuilds the honest publics from the rows, as the device prover does.
  - The instance files were regenerated here with `--scheme sha256`.

| cell | result | verifier run | sessions accepted | plateau proofs = recorded |
|---|---|---|---|---|
| H100 BF16 SHA-256 | art:728d8724 | r20260926-005512-3f15 | 60/60 | 24/24 |
| H100 E4M3 SHA-256 | art:df857ea6 | r20260926-004555-8c05 | 66/66 | 12/12 |
| RTX 4090 E4M3 SHA-256 | art:fd772057 | r20260926-004625-a5bb | 54/54 | 24/24 |
| A100 BF16 SHA-256 (frozen set, rebuilt and checked against the manifest) | art:324888c5 | r20260926-004955-6a4a | 18/18 | 12/12 |

- **Each cell's checks:** my instance files match the verifier pod's by sha256, and all 12 tampered-record negatives
  behaved as expected. Recorded coins are replayed, so this is not transferable evidence.
