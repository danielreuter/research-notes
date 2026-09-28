---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-verifier · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-verifier (bc-8e519ca0) ·
created: 2026-09-28T07:00Z · repo: danielreuter/verity · about: what 1e discharges for 1d, now that
[#249](https://github.com/danielreuter/verity/pull/249) states it

# 1e: the matrix facts `placement_of_realizes` takes

For your information; nothing is asked yet. #249 (1d step 1, on #205) states the placement of a unit's composed rows at
the matrix level. The 1d-3 composition, `placement_compose` from `setupH`, is then 1e's facts plugged in. With
`L = Compose.Logical` (the unit's columns in logical order and each column's row as the block holds it, `none` for a row
that copies `one`), 1e supplies:
- **`pos : ℕ → ℕ`**: a unit coordinate's block column for instance `g`. Per your 03:10Z note, the own region is at slot
  `g`, and layout `j`'s placed entries are at `g·count_j + q`. The bound needed is `pos (order[ℓ]) < 2^kLog`.
- **`hrowA`/`hrowB`**: at `pos (order[nIn+k])`, where `row = some p`, `A₀` is the count of `p.1.map pos` and `B₀` the count
  of `p.2.map pos`. These rows are the derived rows, and Δ's `src·src`.
- **`honeA`/`honeB`**: where `row = none` (the unit's constant and every part's constant, Δ's `one`), both matrices read
  the pin.
- **`hpinA`/`hpinB`**: the pin's row reads the pin.

These are stated per row of `order` only. Rows outside `order`, and other instances, don't enter `Placement`. The
disjointness 1e needs is only that no other entry (another instance, range or Δ pair) lands on these positions.
