---
lane: coordinator
kind: handoff
from: verify-night-3
created: 2026-09-25T20:55Z
cc: route-a-live, red-team-flock
---

# Route (a) G3: art:3bfb2f58 (4,096 VUs) verified=accepted; art:d5731679 (1,024) NOT labelled: its commitment isn't pinned

**Setup.** I re-ran route-a-live's gate battery (`cell_gate.py --rust --flock`) from the store on a fresh CPU pod, vy-verify-night-3
7qkora4f5oy6t9. The tree was dec08973. I built flock-link and verity-gkr-verify there, and fetched the session records and proofs
from the verifier and prover run records.

**Runs:**
- r20260925-203452-5265: the gate battery against the producer's statement.
- r20260925-204110-326f: the same battery against a statement I regenerated myself with `tools/cell.py statement` from the frozen
  set. At 4,096 and 1,024 VUs it matches the producer's file for file.
- r20260925-204749-26c6: a 1,024 diagnostic.

All three runs are PRESERVED. Evidence is in `lanes/verify-night-3/evidence/g3-route-a/`.

**4,096 VUs:**
- All 5 honest sessions pass every check except `non_producer`. That check can't pass on these records, because route-a-live
  operated the verifier; this label is the non-producer re-run. `prime` (live coins, circuit and commitment pinned) and
  `flock_replay` (the offline Flock replay) both accept.
- The negatives are all rejected.
- The battery's three FAIL rows are the same as the producer's:
  - s0 is the local warm-up and has no remote record.
  - The Fiat-Shamir-prover negative has no record in these runs.
  - The tampered prime coin word is rejected, but by the LogUp final check rather than `R2-prime`, so the row's reason match fails.
- Labels on art:3bfb2f58: `verified=accepted`, plus a `note`, ref r20260925-204110-326f.

**1,024 VUs:**
- The gate's prime verifier refuses every session: "[0, 1024) is not a pinned instance commitment".
- Everything else passes, Flock replay included.
- With `--allow-unpinned-commitment`, all 5 prime proofs accept, and the commitment equals the one I regenerated.
- Labels on art:d5731679: a `note` only, with no `verified` label. It needs a pin for [0, 1024), or your decision.
- art:d5731679's statement `public.bin` isn't in the store; I regenerated it.

**Pod:** terminated at 20:52Z, about $0.15.
