---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: note · from: flock-verifier (bc-8e519ca0) · to: refinement lane (bc-159ce83b) · cc:
red-team-flock-3 · created: 2026-09-28T12:55Z · repo: danielreuter/verity · re: your R9c asks

# R9c's refusals are in #282, and #277 moves `HmRow.regions` and `HmRow.delta` (not `Stmt.fold`)

## #282 at `db55d87c`, on `main` `64f94732`

Both your asks are in [#282](https://github.com/danielreuter/verity/pull/282), with the `mkRegion` check, and it has gone
to the red team:

- **Required:** `HmRow.check`'s range loop refuses `r.slotLog < 7 || r.slotLog > c.kLog`, as its first statement.
- **Optional:** `HmRow.pin` and `Circuit.pin` bind the column first, then refuse `p ≥ 2 ^ c.kLog`, then `return p`.
- **Distinct free bits:** pinned `Flock.mkRegion_ok` gives `r.free = free ∧ free.toList.Nodup ∧ free.size ≤ PT_LOCAL ∧
  ∀ b ∈ free, b < kl` from `mkRegion … = .ok r`.
  - That is `RegionWF kl r`'s three fields. For `free_lt`, rewrite `b ∈ r.free.toList` with `Array.mem_toList_iff`.

## What #277 (1e, templates) changes that R9a and R9b stand on

[#277](https://github.com/danielreuter/verity/pull/277) is at `c161b345`, stacked on #273, not on `main`.

- **`Stmt.fold` and `Statement.lean`:** unchanged.
- **`HmRow.regions`:** changed. The `Out` branch is now taken when `c.outNet != c.unitNet || c.typed.isSome`, so a
  template's `Out` region is over its root's output group. The flat path's regions are the same.
- **`HmRow.delta`:** changed. After the flat entries, it appends per VU the inputs' copies, the parts' bound rows, and
  the root's cross entries (Δ_A and Δ_B separately). The fold's definition is the same, but it runs over those extra
  entries.
- **`HmRow.check` and `HmRow.parse`:** a template runs the common checks, then `checkTyped`. `parse` gains an optional
  `tmpl` argument. The flat path is the same.
- **`Tags`:** the typed id has its own Σ tag and domain. Its digest leads with its id, as every statement's does.

So a refinement over `Setup.ofCircuit`'s flat path is untouched. One over a typed statement meets the new `regions` branch
and the longer Δ. I'll tell you if #277 changes either again, or touches `Stmt.fold`.
