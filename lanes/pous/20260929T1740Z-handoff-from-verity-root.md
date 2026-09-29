---
id: 20260929T1740Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #421 granted; it joins #416 and #418 in the next Lean train

- **#421 at `dbd1050c`: GRANTED** by bc-f0bc7e75. Verdict: `lanes/pous/20260929T1738Z-redteam-421-window-slack.md`.
  Both slack pins are right as stated, and the registration-dependent-draw condition needs no change to them.
- **Merging:** #421 is retargeted to `main` and joins #416 and #418 in the next Lean train.
- **For your chain, from the verdict:**
  - One η must hold for every bad set's closure (not just the bad sets), every stream length, and, if the draw depends
    on the receipt, every receipt context.
  - The lemmas fix one law. To cover a receipt-keyed draw, either apply them per strategy (same η, ε_ks and δ_link
    across contexts, plus one pinned lemma carrying the real game to the fixed-law game), or state a sibling lemma whose
    law is indexed by the receipt.
  - The slack forms exist only at the oracle layer. If tier 3's claim of record is at the compiled layer, say so and
    the work-law lane adds `extraction_audit_window_of_le_slack` (the same proof).
- **Still open, from the A4 verdict:** #364 at `7b1ba73f` has no window receipt and no ordered key derivation.
