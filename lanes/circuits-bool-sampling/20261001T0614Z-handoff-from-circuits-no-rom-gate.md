---
id: 20261001T0614Z-handoff-from-circuits-no-rom-gate
campaign: verity
lane: circuits-bool-sampling
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: Daniel ruled at 11:11 PM PDT. No ROM or lookup gate family; every table read is a plain Boolean circuit

- Every table read in the Boolean conversion is built from AND/XOR/NOT and constant bits: attention's ex2/rcp, the MUFU tables
  (`MufuEx2Ftz`, `MufuSqrtFtz`, `RsqrtApprox`, `DivFullRcp`, `DivFullScaleA`), and any table a sampler reads (Gumbel's log or
  exp, for one). Use a constant-table multiplexer, or the hardware's arithmetic where that's smaller.
- MUFU Definitions are proofs'. Keep sub-Calling them by id. If yours needs a MUFU before proofs has its Boolean version, keep the word id
  in the sub-Call and report it; don't build your own copy unless circuits asks you to.
- **Sampling:** any table read inside the samplers is yours, and it becomes a plain Boolean circuit too.
- **Switch:** the purity check counts a word-id MUFU sub-Call as non-Boolean.
