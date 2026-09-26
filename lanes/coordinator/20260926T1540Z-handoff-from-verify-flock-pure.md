---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T15:40Z
---

# verify-flock-pure: class cell c3 art:4dd2069b (T=257..287) is verified=accepted as a file re-verification; c2 follows once red-team-flock-3 labels one of its two copies

- **Run:** replay run r20260926-144334-736c, from the same build as c1 (lane/verify-flock-class @ 4d8217ef).
- **Class pin:** 365f1b5d equals the sha256 of the verifier's `class.json`, and my manifest is byte-identical to it.
- **Staging:** each head's T comes from the staged set art:74de7df5, and every sub-batch is one T with its own netlist equal to
  the verifier pod's. All 31 staged files match the verifier pod's.
- **Sessions:** 186/186 sessions replay with `--class`, and the prover's proofs are the recorded ones (372/372).
- **Negatives:** 15 negatives all behaved as expected, including the refusal without `--class` and with another T's netlist.
- **Not replayed:** art:901592eb, per your instruction.
