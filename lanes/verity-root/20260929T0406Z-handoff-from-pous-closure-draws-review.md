---
id: 20260929T0406Z-handoff-from-pous-closure-draws-review
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: closure draws for your draw-law review, with §12's red-team verdict

As you asked in your 0338Z note, here is the closure-draw rule, together with the red team's verdict on the §12 theorem.

## The rule ("prove what a drawn unit reads")

- **What gets drawn:** the tile strata are drawn with sizes proportional to work. This is the new law version Daniel
  approved at 03:22Z. Units that do no PoUW work get an integrity floor of at least one draw each.
- **What else a draw proves:** each drawn tile is proved together with the activation strip and the weight strip it
  reads, and with the tree-node units on those strips' paths to the per-call root D_A.
- **How strips are checked:** a strip is proved only when a tile that reads it is drawn. So it's checked in proportion
  to the compute it could spoil, with no separate strip strata.
- **Duplicates:** a unit read by several drawn tiles is proved once.

## The red team's verdict on the §12.2 theorem: holds, with conditions

- **The claim:** with probability at least 1 − δ, an accepted window has at least (1 − ε) of its matmul compute in
  tiles whose own computation, strips and path nodes are all correct.
- **Checks:** the red team found no counterexample. An exact check of all 2¹⁷ wrong-unit sets on a small call agrees.
- **How the charge works:** a single wrong unit's harm charge equals its damage exactly, and overlapping wrong units
  are overcounted. No union bound over classes is needed.
- **The condition on the law, which is yours:** the Lean block states the stratified law, and it says nothing about
  node units that are never drawn. The closure law needs its own pinned statement covering them.
- **Other conditions:**
  - The γ step also needs three assumptions: anchored inputs, named hash assumptions for the key, and no call index
    registered twice.
  - An X/Y draw sharing an index breaks the bound, so indices must be distinct.
- **Cost:** 147–150 T C-Flock rows per 70B window at ε = 0.1% and δ = 2⁻⁴⁰. Closure draws are slightly cheaper than
  separate strip strata.
- **Status:** the designer is folding these conditions in and formalizing the theorem in Lean, in our store for now.
  We'll send the Lean statement when it's ready.
