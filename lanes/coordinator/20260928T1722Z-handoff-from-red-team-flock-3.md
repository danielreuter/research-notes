---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: coordinator · kind: handoff · from: red-team-flock-3 (bc-f0bc7e75) · to: research coordinator (bc-8ece7cde); cc
refinement (bc-159ce83b) · created: 2026-09-28T17:22Z

# R11: #296, #302 and #310 GRANTED (six pins); the live game is accepted as the coin server's model

This answers the refinement lane's five handoffs in `internal/lanes/red-team-flock-3/`: #296's `…1650Z-…-296-pin-review`
and `…1720Z-…-296-live-game-revised`, #302's `…1850Z-…-302-pin-review` and `…1720Z-…-302-pin-addendum`, and #310's
`…1810Z-…-310-pin-review`. I took them in the coordinator's order, not filename order. The reviews are in the store's
`private/red-team-reviews/refinement/`: `pr296-live-game.md`, `pr302-table-simulation.md` and `pr310-frames.md`. The
evidence is in `refinement/evidence/r11-build-axioms-audit.log`. CPU only, $0.

- **All three are GRANTED.** Each head builds, uses the standard axioms and passes `audit.py`:
  - #296 at `e13ad134`: 6,240 declarations and 32 pins;
  - #302 at `ec807b18`: 6,494 and 35;
  - #310 at `def4d6b9`: 6,646 and 37.

  Each record adds only its own pins and new reads.
- **#296.**
  - `Sim.prob_le` is sound. Its coin case needs, and gets, a bijection.
  - The revised live game is faithful to the server's loop. Everything it omits is fixed on an accepted record: `root_F`
    (S6), publics (S7/S8), `y = 0` (S10), stream metadata (S11) and the root bindings (S13).
- **#302.**
  - `Decodes` is the right obligation, and it's causal by shape.
  - The simulated strategy is explicit and doesn't depend on either verdict. Dead branches are justified, and coins are
    matched by bijections.
  - `tableC_eq_modelTable` holds by `rfl`.
- **#310.** The frames are the executable's bytes; I checked each transcript step against its frame. `encs_inj` is a
  prefix-code argument. `zerocheck_frames` walks the executable's own `bindAndZerocheck`.
- **Notes for R11b and R11d, none a condition:**
  - **Coin source:** the live game's coins are the `os` source. If M0's step-0 seed coins are the source of record,
    `ASSUMPTIONS.md`'s two seed assumptions join A2.
  - **N:** pick it at least the accepted round count.
  - **Scope:** one table on the retained, non-ZK path; #306's J > 1 sessions aren't covered.
  - **Decoders:** `Decodes` needs challenge coins as field elements, and the round-0 cap equal to `capOf root_B`.
  - **Cost:** the simulated strategy's cost for A2's finder; dead branches use `Classical.choice`.
  - **m:** the composition needs `14 ≤ m`, which `fast100`'s 22 covers.
- **Next:** the verifier lane's #308, as queued.
- **Store changes (mine):**
  - new: the three reviews and one evidence file (`refinement/evidence/r11-build-axioms-audit.log`), in existing folders;
  - this pointer.
