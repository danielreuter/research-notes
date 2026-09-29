---
id: 20260929T0521Z-handoff-from-pous-circuit-pr364
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: PoUW sampled-proofs circuit is up as draft #364

Follow-up to 0442Z (width ruling) and 0420Z (draw-law design pointer).

- **Draft PR [#364](https://github.com/danielreuter/verity/pull/364):** the NCP-INT circuit in `protocols/pouw/verity_pouw/circuit`.
  - At small shapes the whole call passes `validate_unit_cut` with no value computed in two units: 484,967 computing gates at 32 × 64 × 32. It evaluates bit for bit to a native reference, and 86 `protocols/pouw` tests pass.
  - The recorded `check` hasn't run yet. A layout-A red-team review of the build is under way.
- **For your draw law:** the closure-draw plan sits behind a seam. `CountLaw` is today's law on `main`, and `WorkLaw` waits for your work-sized law in `Flock/Draw.lean`, which we didn't touch.
- **For the IR:** the pinned separator port (the tile's Z) is enforced in `partition.width_rule` for now. Its permanent home is the `Q_nested_instances` v0 spec, evaluator and Lean port. That's yours to schedule.
- **What the build changed in the design:**
  - D_s gets its own digest unit, because one IR call can't both write D_s and read D_A.
  - A per-call key unit feeds E₁ and F₁. Otherwise every X unit repeats round 1, and the recompute check rejects it.
  - c₀ moves to the Y unit.
  - The index binding travels as anchored inputs, because `Q_template_instances` allows no constant nodes at the root.
- **For #311:** it stays unchanged and merge-ready. The wiring that makes "PoUW + sampled proofs" of record for `ncp-v2` will be a separate draft PR stacked on #311 and #364.
