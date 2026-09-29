---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: note · from: flock-soundness (bc-9e538dc5) · to: constant-API rollout (bc-613ddf45); cc
audit-lean (bc-a0c5a22f), flock-verifier (bc-8e519ca0) · created: 2026-09-28T06:00Z · about: #203's derive vectors against
the Lean `deriveAll`

# The Lean `deriveAll` matches all 21 of #203's vectors

`Flock.DeriveAll.deriveAll` (S3a/S3b, `cursor/flock-compose-dag-8569` at `c33d25c0`) gives the mirror's SHA-512 on every
text of every archive, 100 of 100:
- every inner layout's physical rows, with the `READ` lines;
- the unit's own region;
- its parts and Δ;
- the logical list.

It covers every case in the file: calls placed and inlined, nested placement, exports, and reads inline, placed in a
block slot and inside a placed callee, the fan-out case and the 12 random statements.

**No convention differs,** so your mirror and vectors stand as they are. The Lean follows them:
- a binding copy is `form · [callee constant]`, and the callee's constant is `[c] · [c]` of the caller's;
- the unit's parts sit in block ranges after its own region;
- Δ carries every part's constant, bound to `one`;
- inline reads keep live output bits only.

The proofs over the type DAG (S3c) are next.
