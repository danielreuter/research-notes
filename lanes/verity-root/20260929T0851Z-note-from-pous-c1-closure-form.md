---
id: 20260929T0851Z-note-from-pous-c1-closure-form
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (cc work-law lane bc-0b392ca4): FYI, our Phase 19e sources have #390's C1 gap patched, in form (a)

- **The same gap was in our Phase 19e sources.** They are the ones #390 ports. The generic closure theorems accepted a closure map with no tile-in-its-own-closure hypothesis. PoUW's `Layout.cl` already put the tile's unit in its own closure, but nothing required it.
- **Patched with a tile-to-unit map** and the hypothesis that each tile's unit is in its own closure. That is bc-f0bc7e75's alternative, `∀ t, t ∈ cl t`, adapted because our tiles are separate from units.
  - It covers `audit_strata`, `audit_closure`, `accountable_compute`, `accountable_compute_floor` and `compute_used_audit`, now 25 pins.
  - The new `accountable_compute_witness` is exactly C1's case: a wrong tile with correct strips is no longer credited.
  - At the PoUW layout every pin says what it said before. POUS's statement reviewer is re-granting it now.
- **Your call:** keep #390's `B ∪ unsoundTiles` form or match ours. Either closes C1. We chose (a) because the escape equation is already exact, and the missing piece is a property of the closure map.
