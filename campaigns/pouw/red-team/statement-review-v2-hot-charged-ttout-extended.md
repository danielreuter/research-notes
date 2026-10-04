---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: v2-hot's charged TT_OUT beyond 8,192 deep and wide

30 Sep 2026, 2:36 PM PDT. The statement reviewer (bc-22298e90), through the pous root, for bc-b58c6093 and
bc-824e54a2. It answers `internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/review-request-2135.md`, and follows my
review of the 8,192³ charged forms, `statement-review-v2-hot-charged-ttout.md` beside this file.

## Verdict: GO on the extension, with two conditions

- **GO:** Δ's table to 65,536 deep and wide, its lemmas, and the pins.
- **The existing 8,192³ GO stands unchanged,** with the same cell (0.8012), the same Δ (0.8012/256) and the same figures.
- **Condition 1 (new): the width caveat.** For units wider than 8,192, Δ = 0.9885 rests on clause (b) at a block no
  measurement has tested. The docstrings state the depth caveat but not this one; see below.
- **Condition 2 (carried): the block tables are provisional.** Both tables, and the 640 × 10,726 block, are rebuilt on
  bc-d9842080's audited floors with every contraction factor up to 2L, and re-pinned.

## What I checked

- **The snapshot** (my copy of 2:33 PM PDT), at the request's hashes:
  - `TTOutV2HotCharged.lean` `12243894…`, `V2HotCharged.lean` `27834b2f…` and `NoAlignedExactRegionHot.lean`
    `4c1d3bd6…`;
  - the other seven Lean files, byte-identical to the GO'd ones.
- **The diffs:**
  - the four forms' definitions are unchanged;
  - the region file changes in its docstring only;
  - the table gains the wide row, and the lemmas cover it.
- **The build and axioms:** on my post-M1 tree the build was clean (3,137 jobs), and `#print axioms` on all 16 theorems
  gives `propext`, `Classical.choice` and `Quot.sound` only. There is no `sorry`, `axiom`, `opaque`, `native_decide` or
  `set_option`.
- **Every pinned file,** 21 of them, hashes to its pin in the store: the table, the four runs, `deepbands`, the ten
  scripts, both block tables, the free-shape log, the audited catalogue's stats and the region file.

## Δ's table against its source

- **The source's rule.** `delta_by_n_k_p8.0_copy.json` (`5d9c2b0d…`) tables n and k at 8,192, 16,384, 32,768 and
  65,536. Its rule is to use the least tabled n′ ≥ n and k′ ≥ k, and it says each entry bounds every smaller unit.
- **Every Lean cell is an upper bound:**
  - n ≤ 8,192 gets 0.8012, and the exact value at every k is 0.80115344;
  - 8,192 < n ≤ 65,536 gets 0.9885, and the exact value at every k and at each of 16,384, 32,768 and 65,536 is
    0.98842478. The source's 0.9884 rounds down, and the Lean's 0.9885 rounds up.
  - k below 8,192 is covered by the least tabled k′ ≥ k, which is 8,192.
- **Depth.** The four runs (`deltadeep_p8.0_n*.json`) use `lmax = 2048`, which covers k = 2¹⁶'s windows. `delta_by_k` is
  flat, and `new_max` is empty, so no window longer than 8 atoms raises the maximum.
- **Rows:** "rows otherwise uncapped, which bounds any m".
- **The lemmas:** `deltaHotAtoms_mono` (both dimensions), `deltaHotAtoms_nonneg`, `deltaHot_of_le`, `deltaHot_of_wide`
  and `deltaHot_eq_none` state what the request says.
- **Checked in scratch:**
  - 8,192³ gets 0.8012/256;
  - 16,384³ gets 0.9885/512;
  - 8,192 wide × 16,384 deep gets 0.8012/512;
  - 65,536³ gets 0.9885/2,048;
  - one past 65,536 in either dimension gets `none`.
- **The credit condition** (Δ is a share of the credit only while credit per word is at least one chain) is unchanged
  by width. Its tightest case is already the wide-unit limit, about 70 W1 to spare at k = 2¹⁶ and ρ = 1/1,000.

## Condition 1: clause (b) is unmeasured on wider units, too

- **Where 0.9885 comes from.** At 16,384 and 65,536 columns the runs' maximum is the 8-atom window from atom 0 at 10,725
  columns (`start: [8, 0, null, 10725]`). That is one column short of the 4-atom tail's block 640 × 10,726, which clause
  (b) rules out from atom 4. Without that exclusion, the full-width window at 16,384 columns is unbounded by this table.
- **No measurement reaches it.** The block "can't fit 8,192 columns", as the region file's docstring says. GPU 3's
  support for (b) is on 8,192³ units, so it can't have tested this block, or any block wider than 8,192.
- **What the docstrings say now.** `TTOutV2HotCharged` states "Clause (b) is unmeasured on deeper units", and the region
  file states that tails over 256 atoms aren't measured. Neither says the same about width.
- **The fix:** add it beside the depth caveat in both docstrings. For n > 8,192, the bound uses clause (b) on blocks
  wider than 8,192 columns (the 640 × 10,726 block at 4 atoms sets Δ = 0.9885), and GPU 3's support for (b) is on
  8,192-wide units only.
  - This is docstring only, and no record moves.
  - A grant for n > 8,192 should cite it, or wait for a measurement on a wider unit.

## The figures beyond 8,192³

These are from my scratch compositions, standard axioms, at the provisional Δ, per tile, FADD 8.376, cast 8.
- **Forming credited, 16,384³:** `GγSampled` at 1 − (1 − (1/400 + 0.9885/512))·(1 − gammaHot)/(1 − 1/400), which is
  **0.54890%** and matches bc-3006c44a's 0.549%. It comes from `hotTileAccounting_sm120v2hot` and
  `pearlCSampledHotAtγ₀`, with the twins' value `140663893/39508150000`.
- **Chain-only, 16,384³:** 0.78889%.
- **Both caveats apply.** The 16,384³ figures rest on clause (b) at tails over 256 atoms and at widths over 8,192, and
  neither is measured.

**No label** was requested.

**Condition 1: met (checked 2:39 PM PDT).** At `TTOutV2HotCharged.lean` `c3d15402…` and `NoAlignedExactRegionHot.lean` `5805f44e…` (`V2HotCharged.lean` unchanged at `27834b2f…`), both docstrings now say clause (b) is unmeasured on wider units, with the reason: the 10,725-column window, one short of 640 × 10,726. The diff is docstring text plus the updated pin, which matches the region file. The build is clean, and all 16 theorems use only the standard axioms. Condition 2, the block tables, stays open.
