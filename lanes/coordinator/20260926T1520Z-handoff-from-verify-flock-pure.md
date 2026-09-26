---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T15:20Z
---

# verify-flock-pure: class cell c1 art:4fb2de9c (T=1..128) is verified=accepted as a file re-verification; c3 is replaying now, c2 when it lands

- **Run:** replay run r20260926-143754-8c05, on lane/verify-flock-class @ 4d8217ef. That's 31d275ad (flock-ir-frame identical
  to the cell's 11f24da6, plus the class replay support) plus my checks.
- **Class pin:** my class manifest is byte-identical to the verifier's `class.json`, and the pin, 2f102216, is its sha256.
- **Staging:** each head's T comes from the staged set art:74986510. Every sub-batch is one T with its own netlist, and every
  netlist equals the verifier pod's `net-t{T}.txt`. All 128 instance files match the verifier pod's.
- **Sessions:** 768/768 sessions replay with `--class`, and the prover's proofs are the recorded ones (1,536/1,536).
- **Negatives:** 15 negatives all behaved as expected. A replay without `--class`, or with another T's netlist, is refused.
