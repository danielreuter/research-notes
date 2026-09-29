---
id: 20260929T0442Z-handoff-from-pous-width-rule-ruling
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Daniel's width-rule ruling for PoUW under sampled proofs (Q10's second half)

**Ruling (Daniel, 04:35Z):** keep the strict partition, with the matmul result Z staying in the tile unit. Z is a
separator between every PoUW-only unit and the served output, and a separator's width caps the influence of every unit
behind it.

## Details

- **What crosses the cut:** the strips, noise, strip digests (D_s), tree-node units and the tiles' checked words reach
  the served output only through Z → y. Per tile, only its 256 Z values (8,192 bits) cross, and per call the m·n Z
  values at 32 bits.
- **The theorem:** it is Lemma 4.7 and Theorem 5.4 of Daniel's Notion "Draft 2: Computational integrity via
  zero-knowledge spot checks": the values at a cut K determine the delivered output, so |𝒪_C(E)| ≤ 2^(w(K)), with
  U = log₂ Σ 2^(w(K_E)).
  - Here "RU" means replay unit, so the RU outputs are the served tokens.
  - Neither the repo nor research-notes states this theorem. Flock's `compose_cone` is only its determination half.
  - A worker is extracting the draft's partition results, with draft Lean statements, for the sampled-proofs Lean.
    We'll send them.
- **Width exceptions:** no unit behind the separator needs one. The only departure from the Sep 26 32-bit rule is the
  tiles that produce Z, which add 8,192 bits each to U. The served output, about 17 bits per token, caps U anyway.
- **Condition:** word leaves and every other commitment count as committed, not delivered.
- **Recompute:** there is none. Daniel's standing default is a strict partition, with a recompute only for a compelling
  reason.
- **Cost:** 147–150 T C-Flock rows per 70B window at ε = 0.1% and δ = 2⁻⁴⁰, independent of the open `checkIdx`
  question.
- **Kept on file, not adopted:** computing Z once outside the tile, as an integrity upgrade for y (+0.65 T for
  1.0 × 10⁻³).

The closure-draw rule and the §12 verdict are in our 0406Z note, and the design snapshot is in the 0420Z note.
