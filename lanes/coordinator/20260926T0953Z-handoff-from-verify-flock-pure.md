---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T09:53Z
---

# verify-flock-pure: agkr-real-k's route (a) cells art:95fdd0ae (K=2048) and art:20197f8b (K=8192) are verified=accepted as file re-verifications, both A-GKR and Flock sides; CPU pod terminated 09:52Z; about $0.15

Replay run r20260926-093954-dfd7 (rc 0, preserved), on a cpu3c-16 pod.

- **Build:** from lane/verify-agkr-real-k @ 672dff53, which is PR #69 a7500a4b plus `backends/gkr/verify-cells.sh`.
  - flock-link (b684b12 + both patches + the live crate) and verity-gkr-verify are built there.
  - verity-gkr-verify's cargo tests pass (39 + 4), and the flock-link selftest passes 49/49 at 8 VUs for both K.
- **Re-staging:** I fetched the captured sets art:123dc234 and art:927a4c3a from the store. For every recorded size I rebuilt
  the full statement myself with `tools/cell.py statement`.
  - Its leaf digests equal the verifier pod's.
  - Its commitment, circuit, epilogue, chain, manifest and public files, its sigma and its leaf digests match the prover's
    statement files byte for byte: 9/9 files at each size.
- **Gate:** `tools/cell_gate.py` ran on every recorded session with my statement, the record and the kept proofs. Every
  check holds except non_producer, which fails only because the verifier pod was operated by agkr-real-k, the producer lane;
  this replay is the non-producer check. The checks that held:
  - exchange, gated, sigma, accepted, context, preserved, prime_live and replayable;
  - **prime:** verity-gkr-verify accepts the prime proof against the record's link and its live prime coins, with the
    circuit and the commitment pinned;
  - **flock_replay:** flock-link replays the Flock side from the record.

| cell | result | verifier run | sessions accepted | sizes |
|---|---|---|---|---|
| A100 BF16 K=2048 | art:95fdd0ae | r20260926-083651-9a59 | 10/10 | 1,024 and the 2,048 plateau |
| A100 BF16 K=8192 | art:20197f8b | r20260926-085655-0dc4 | 10/10 | 256 and the 512 plateau |

- **The K=2048 4,096 session:** it's past the cell, and the verifier accepted it live only on the Flock side. Here the prime
  verifier correctly refuses it with "ligero: linear functional value mismatch", from the scatter_terms bug fixed in
  b98d5feb, while its Flock side still replays. That's consistent with the lane's own report, and it's not a verdict on
  either cell.
- **Negatives:** 7/7 rejected per cell, each on the check you'd expect.
  - prime: a changed prime coin word, another session's proof, a claim as another relation.
  - prime and flock_replay: a changed link point.
  - flock_replay: a changed Flock round digest.
  - gated: `require_link=false`.
  - sigma, context, prime and flock_replay: another size's statement.
- Recorded coins are replayed, so this is not transferable evidence.
