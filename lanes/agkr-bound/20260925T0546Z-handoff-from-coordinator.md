---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T05:46Z
---

# Commitment scheme must be NON-algebraic: SHA-256 or BLAKE3 (user decision 10:45 PM PT)

Amends 0507Z: the scheme that commits x, W, y and that the proof binds must be a non-algebraic hash (SHA-256 or BLAKE3, from
`verity.commitments`); no Poseidon / algebraic hashes. Include this in your revised estimate if it changes cost (binding a SHA-256 /
BLAKE3 commitment inside the circuit is expensive; a commitment checked by the verifier outside the circuit, bound to the proof's
committed columns, may be the realistic design: say which and why). Integration v2 (pins) is unaffected: send it as planned.
