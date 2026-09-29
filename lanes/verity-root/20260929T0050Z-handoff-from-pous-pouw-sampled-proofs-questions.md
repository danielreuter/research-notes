---
id: 20260929T0050Z-handoff-from-pous-pouw-sampled-proofs-questions
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# PoUW verified by sampled proofs (two-stage): six questions on `protocols/sampled_proofs` and `vllm-v1`

Daniel ruled at 00:15Z that PoUW composes with sampled proofs, with its own modeled circuit and no verification lottery:
sampled proofs' draw replaces PoUW's own audit draw. At 00:38Z he asked for the two-stage protocol, with no capture of
replay-unit interiors. We need the protocol owner's answers before we build it. The design so far, from bc-75d1b678:

- **Proof unit and replay unit:** PoUW's tile (16×16 outputs at full depth k). Each tile is one replay unit, and also its
  own single proof unit. Its outputs are y and one per-tile digest over the tile's checked words, hashed inside the kernel.
  The checked words stay interior: the verifier recomputes them, and the digest, when it replays a drawn tile.
- **Why the digest is committed at serving:** y comes out the same with or without PoUW's noised work. A digest committed
  only after the draw would let the prover do that work only for tiles it knows are drawn.
- **Draw:** stratified by tile template (depth k), with each template's draw rate proportional to its work; keyed from a
  beacon round published after the boundary root is registered. The sampling target is 0.1% of tiles.
- **What `vllm-v1` in #311 does today:** the two-stage law in its degenerate form. Every stratum is one replay unit at
  p = 1, with a single draw after the commit, and that draw is derived from the run root (`LEGACY = True`), so it can be
  ground. PoUW tiles need a replay-unit class drawn at p < 1, and a beacon-keyed draw.

## Questions

1. **A hash as a replay unit's output.** Can a replay unit's output be a hash that the Program computes? Here that would
   be a SHAKE256 Definition inside the tile Definition, evaluated when the verifier replays the tile.
   - The repo has no hash Definition today, and the Glossary puts leaf hashing in the instrumented program, "about which
     no proof claims anything".
   - If a Program-computed hash is not the right form, should the per-tile digest be a `vllm-v1` leaf kind over the
     tile's checked words? It would be hashed inside the kernel like the `fa2h` thread leaves and checked by
     recomputation on replay. The words would then formally be committed values, though never written to memory.
2. **An RU class at p < 1 inside `vllm-v1`.** Today `vllm-v1` makes every stratum one replay unit at p = 1 and makes a
   single proof-unit draw (`replay_key` is `vu_key`).
   - Can a row carry a second RU class, the tiles, drawn at p < 1 by `ru_key` from a beacon round published after the
     boundary root is registered?
   - When a tile RU's only proof unit is the whole tile (n_v = 1), may lifecycle steps 3 and 4 be skipped (commit the
     interiors, then the proof-unit draw)? Nothing would be committed after the RU draw.
3. **One δ across RU classes.** `TwoStageLaw.profile` returns one profile per class. PoUW needs one class per tile
   template, because tiles at different depths k do different work, with draw rates proportional to that work.
   - How should a consumer combine several classes' profiles under one δ: by a union bound, or through a joint profile
     over the classes?
   - Or may one class carry a rate per RU?
4. **An input derived from a serving-time root.** A tile's noise E₁ is derived from (salt, call index, root_A, weight
   id). root_A, the Merkle root of the call's A rows, is a commitment artifact, not a Program value. How does a
   two-stage RU take such an input?
   - (i) As a prescribed "noise" family that the verifier derives for each drawn RU and the prover never commits?
   - (ii) Committed by the prover, and checked against the derivation by a plan class?
   - (iii) Derived inside the Definition, with root_A as a Program value?

   `IntegrityProfile` lists "noise" among its prescribed families, which it says are checked exhaustively. Does that mean
   (ii) at p = 1?
5. **Opening boundary values.** A drawn tile RU reads A rows that serving committed as another RU's outputs. Must the
   prover retain every committed boundary value until the RU draw? Or may it regenerate one by replaying undrawn
   upstream RUs bit-exactly, and open it against the serving-time root? The answer decides §8's retention question.
6. **The pitfalls document.** `PROTOCOL.md` and `law.py` cite `docs/audit-protocols.md` (§2.9, §3.3, pitfalls 4 and 6),
   which is not in this checkout. Where is it? This design relies on pitfalls 4 and 6 only as `PROTOCOL.md` restates
   them.

Reply in `lanes/pous/`. We'll fold the answers into the design and ask Daniel only if one changes what he ruled.
