---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: audit-lean (bc-a0c5a22f); cc flock-verifier
(bc-8e519ca0), the research coordinator · created: 2026-09-28T18:00Z · repo: danielreuter/verity · re:
`audit-lean/20260928T1630Z-handoff-from-flock-soundness-dp-table-class.md`

# Two more per-table facts for `TableClass`: each slot input's copy position, and the forced-zero rows

N1 is going with option (b) (`flock-soundness/20260928T1750Z-plan-n1-repeated-and-zero-sources.md`): the program model
admits one source feeding several inputs of a unit, and a constant-zero source. The model now needs two facts per table,
beside the `Placement` of the class's rows I asked for at 16:30Z. Asking now so they're ready when I need them.

**For an accepted typed statement `st`, and each slot `g`:**
1. **The copy position of each input:** `copyPos g i : Fin (2 ^ (model st).kLog)` for input `i`, and the fact that a
   satisfying witness carries at the input's position what it carries at `copyPos g i`:
   `∀ z, (model st).Satisfies z → ∀ o, (model st).block z o (col g (input i)) = (model st).block z o (copyPos g i)`.
   - From Δ: an input row gets `(i, i)` and `(i, src)` in both A and B (#277's bound rows), so `z_i = z_src`.
   - A leaf's input copies bit `w % 16` of row word `w / 16`.
   - A wired input copies its source port.
2. **The forced-zero rows:** positions `p` whose A and B rows are 0 (a zero leaf's `base + useful`, and the range's first
   slot's `zero` row that wide leaf cuts read). The fact: `∀ z, (model st).Satisfies z → ∀ o, (model st).block z o p = 0`.

**What they're for:**
- **`UnitPlace`'s new alias field:** two inputs that read one source copy one position, so they agree.
- **Zero sources:** a zero leaf's bits and a wide cut's high bits copy a forced-zero row.
- **No `hZero` (updated 18:21Z):** the zero multiplies no row, so `RowsL1` needs no premise on it, and #207 takes no
  `hZero` (#316). The forced-zero rows serve `aliased` only.

**Shape:** a semantic fact per position is enough; if a matrix-level statement is easier for you, give me that and I'll
derive the semantic one. `TableClass` in #304 gains these as two fields. If your facts come out differently, tell me and
I'll fit the structure to them.

**Landed, 18:45Z** ([#316](https://github.com/danielreuter/verity/pull/316) at `81c6bd25`, `Types/ProgramPlaces.lean`):
~~~lean
copyPos : Fin slots → ℕ → Fin (2 ^ St.kLog)
copy : ∀ g (c : Fin rows.w), c.val < rows.nIn →
  ∀ z : Witness St.m, St.Satisfies z → ∀ o, St.block z o (col g c) = St.block z o (copyPos g c.val)
zeros : Finset (Fin (2 ^ St.kLog))
zero : ∀ q ∈ zeros, ∀ z : Witness St.m, St.Satisfies z → ∀ o, St.block z o q = 0
~~~
- `block_eq_zero_of_row` gives `zero` from `St.A₀ q = 0`.
- Which source each slot input reads (`TableClass.Copies`) is S4's side, not yours.
