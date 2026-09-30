---
id: 20260930T2329Z-handoff-from-proofs-daniel-priorities
campaign: verity
lane: proofs-arch
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Daniel's priorities (4:27 PM PDT): stay interactive, drop no-ops, try uniform copies first, then lookups and hashes; everything sound under SHA-512 CR only

These supersede your brief's scope where they differ.

1. **Drop** the no-op audit and idea (e) for now. Stop that work, and don't write `noop-audit.md` unless it's already done.
2. **Keep the protocol interactive:** no Fiat–Shamir. Batching coin rounds is acceptable only with a security proof. A separate
   security worker (lane `proofs-security`) is finding and checking the existing batching proof, so don't duplicate it.
3. **Uniform copies is first, and Daniel wants it tried.** The plan:
   - **Profile first.** For one K=2048 m=35 statement (M0's #20 tree), split the prover's ~1.02 s and the loopback verifier's
     ~6.5–6.85 s per statement into phases. How much is circuit-structure work (wiring or copy constraints, selector and
     structure evaluation) that a uniform-copies form would shrink? Identical k16 steps × 128 per coordinate × 8,192
     coordinates per statement: the verifier may be evaluating structure it could get from one template.
   - **A standalone prototype** (your branch, not production): the zerocheck/sumcheck for N copies of one small template
     circuit over Flock's field against the same circuit flattened, on CPU then GPU. Measure prover s, verifier s and proof
     bytes as N grows.
   - **The soundness argument** in one paragraph: the flat circuit equals template ⊗ copies, so the same relation is proved.
     What would the Lean verifier of record need?
4. **Then first-class lookups:** mantissa products, alignment and normalization, replacing Boolean multiplier and carry
   chains.
5. **Then hashes:** measure the hash share of today's statement cost (rows' SHA-512 compressions against arithmetic), and
   list the hillclimb levers.
6. **Security constraint for every idea:** it must stay provable in the interactive model with **SHA-512 collision resistance
   (A2) as the only hardness assumption**, plus A3 (the verifier's own uniform randomness). Say, per idea, which hash it
   relies on and why. Anything needing SHA-256, BLAKE3 or another assumption is out, or needs a migration named.

Deliver: the study doc as briefed, with uniform copies' profile and prototype results first. Checkpoint when the profile
is done.
