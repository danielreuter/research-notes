---
lane: verify-flock-pure
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T14:40Z
---

# flock-ir-lowering: class cell c3 (T = 257..287) is ready to replay, art:4dd2069b

- **Cell:** `art:4dd2069b9c797223093b2e23461aad1dc54c62ade344187f02f50a7d457d6b56`, at 11f24da6.
  - Verifier run r20260926-140928-d05d (vy-flock-ir-lowering-b-ver): `out/verifier` has `class.json` (pin 365f1b5d), `net-t257..287.txt` and `p0-496/sessions-s0..30`.
  - Prover run r20260926-140931-b414.
- **Inputs:** set `art:74de7df5`, `TEMPLATE=attention-head`, `PER=16`. It is 31 sub-batches, so about 190 sessions.
- **Build:** 31d275ad or later: the replay script's class support, and a `flock-ir-frame` identical to 11f24da6's.
- **c2** (T 129..256) is re-running after a contention refusal and lands around 15:20Z.
