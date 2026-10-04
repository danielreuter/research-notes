---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: M3, RowSeed (P2, per-row seeds)

1 Oct 2026 UTC (30 Sep, 6:05 PM PDT). The statement reviewer (bc-22298e90), for compute-accounting (bc-e90634dd), the
coordinator since Daniel's 5:52 PM PDT ruling. It reviews bc-5382063c's staging `internal/pouw-fp8/rowseed-staging/` on the
basis Daniel set: the per-row draw condition becomes a named `Prop` in the PoUW Lean assumptions module, taken as a
hypothesis.

## Verdict

- **GO on 27 of the 28 proposed pins as stated.** That covers P2's main line (the reduction to rev1's TT_OUT), the γ
  carry-over, the `-h3` bridge and the fragment count.
- **`ttOutRowSeed_skipClass`: GO on condition.** Its hypothesis `FragDraw` has to be restated as a named `Prop` in
  `Pouw.PearlC.Assumptions`, per the ruling.
  - The statement's content (the quantifiers below) is right as written.
  - The move changes where `FragDraw` lives and how the audit records it, not what it says.
  - I'll re-GO the diff.

## The snapshot and checks

- **The snapshot** was taken at 6:01 PM PDT. The staging is unchanged since 10:50 AM PDT:
  - `TTOutRowSeed.lean` `e13a63b0…`, `RowSeedGamma.lean` `521e995b…`, `RowSeedCode.lean` `94db066b…`,
    `RowSeedFragment.lean` `aed6eaa6…` and `RowSeedSkip.lean` `e7de8395…`;
  - `rowseed-pins.json` `d0101158…`, with 28 records.
- **The build:** on my post-M1 tree (rev2 + add-on + the `SaltDead` delta, with `DeviceSm120Gamma`), the four modules
  built cleanly (2,126 jobs).
- **Axioms:** `#print axioms` on all 28 gives standard axioms only, with no `sorry`.
- **The audit:** bc-5382063c's run on the post-M1 store passed with kernel replay (482 pins). The store's 454 records and
  their read digests are unchanged, and 11 of the 28 read M1's `SaltDead` at `a37bdcc5…`.

## The trusted definitions (`TTOutRowSeed.lean`)

- **C0, `PearlCDevice.RowLocal`:** the ticket, flags and U at word (i, j) are the one-row matrix's. It holds at every
  `devAt` by `rfl` (`devAt_rowLocal`), so it is discharged at the sm_120 records.
- **C1, `RowSeedNoise sem sem'`:** row i's E_A is row 0 of the one-row split unit's at `rowIdx L u i`. The per-job
  F_A, F_B and E_B are that unit's, so they must agree across a unit's rows; that is right for per-job draws. The chain,
  scales and floor are `sem`'s.
- **C2, the per-row cap.** It implies rev1's aggregate cap (`rowCap_agg`), so it only removes credit, and it is needed:
  without it, a row over its own cap would be credited row-seeded while excluded split.
- **C3, `CostModel.SplitClosed`:** the split program and its activations are chosen before the oracle, the state and the
  salt, and its transcript is the original's relabelled row by row, at no more cost or calls. It is a property of W1,
  which charges instructions, not unit grouping. It is fine as a hypothesis.
- **The target forms.** `TTOutRowSeed` and `TTOutTileRowSeed` are `TTOut` and `TTOutTile` with `rowsOf ≤ 2^64` added and
  the error read at R rows, (q + R)/2^128. They are proved, not assumed.
- **The `-h3` bridge.**
  - C1-h3 (`CodeSeedNoise`) makes the code's noise `sem'` at `H ∘ π L`, with π a fixed permutation per layout.
  - C5 (`RelabelClosed`) relabels a program's oracle at no more cost or calls.
  - `pr_comp_equiv` is the uniform-oracle fact the bridge needs.
- **The fragment side.**
  - `chainOmitP`, `SkipSetU`, `undebitedSkippable` and `fragCount` say what the count needs.
  - `SkipProgram.out` keeps a patched word's atom. As the docstring explains, free patched values would break the count.
- **C6, `PearlCSem.RowDrawn`:** the per-job noise reads only `H xJ`, and row i's E_A reads only `H (key i w)` and
  `H xJ`, with `key` injective and never `xJ`.
- **`FragDraw`:** for every oracle (every per-job B̃ and every other answer), every activation input and every in-domain
  row, the chance over the row's own answer that its `fragCount` exceeds Λ is at most 2⁻¹²⁸.
  - The update at `key i w` changes only row i's A′, by C6.
  - The adversary's freedom to choose w is paid for by `qtree_union_bound`'s (q + m) union.

## The theorems

- **`ttOutRowSeed_of_ttOut` (and its tile twin)** takes these hypotheses:
  - rev1's TT_OUT at `sem`, which is per unit;
  - C1, C3 and C0;
  - ρ ≤ 1, add ≥ 0 and bf16 ≥ 0.

  It gives `TTOutRowSeed` at the per-row-cap protocol on `sem'`, on the same domain, at γ₀ = 1/400. P2 rests on this
  alone.
- **The carry-over** (`ttOut_of_ttOutRowSeed` and its tile twin) restates it as `TTOut` on the one-shape domain with
  `rowsOf ≤ 2^64`, at error `εPearlC q (N·s.m)`. So the γ theorems apply unchanged.
- **The sm_120 corollaries' γ is rev1's pinned γ:**
  - 216793/59950000 at v2 with cap 1/1,000, 8,192³, the same numeral as the store's `pearlCGammaSm120v2Cap1000_8192`;
  - 16223/3177500 at v1 with cap 1/400, the same as `pearlCGammaSm120v1Rev1_8192`.

  The protocol is the per-row-cap one at `sem'`, and the error is (q + N·m)/2^128. The row-count bound costs units:
  N ≤ 2⁵¹ at m = 8,192.
- **One-row admission:** `pearlCDomainDev_split`, `devSm120v1_domain_row` and `devSm120v2_domain_row` show the split
  layouts are in the records' domains.
- **`fragSkip_count_le`** has complete hypotheses:
  - each slot lies in the unit and patches at most 5 words;
  - every word's omitted atoms are a skip set;
  - every slot's atom is unflagged in its unpatched words.

  Its conclusion, 11·#slots ≤ Σ_i fragCount i, is what the fragment argument needs.

## The condition: `FragDraw` as a named `Prop` (Daniel, 5:52 PM PDT)

- **Where it is now.** `FragDraw` is a plain definition in `Pouw.PearlC` (`TTOutRowSeed.lean`), taken as a hypothesis of
  `ttOutRowSeed_skipClass`. The README says "no new named assumption" and "no `assumptions` entry".
- **What the restage needs:**
  - `FragDraw`, with the same body, in `Pouw.PearlC.Assumptions`, in an assumptions module importing `TTOutRowSeed` for
    `fragCount`;
  - an `assumptions` entry and a `layers` rule for that module;
  - `ttOutRowSeed_skipClass` taking it as its hypothesis, as now.
  - The README's "No new named assumption" has to change to say P2's main line still has none, and the skip class's
    supporting line has one.
- **What doesn't change:** the other 27 pins don't read `FragDraw`. Only `ttOutRowSeed_skipClass`'s record moves.

## Notes for the assessor and the table (not conditions)

- **One-row units.** P2's main line applies rev1's TT_OUT to the split workload, whose units are single rows, (1, n, k),
  up to 2⁶⁴ of them. That is inside the statement's domain (proved in-domain above). Whether the TT_OUT evidence covers
  one-row units is the assessor's rating to give, not a statement question.
- **C6 idealizes the row leaf.** Its key injectivity stands in for the row leaf's collision resistance. The ruling names
  only the draw condition, so C6 stays a hypothesis, but the table should cite the hash's collision resistance beside the
  skip-class line.
- **The skip class's stated gap.** Partly flagged slots are outside the class (save 4,096 units, debited about 40 a
  flagged word). The README says so, and it is theory's call. It doesn't affect P2's main line.

No label was requested.

## Re-GO, 30 Sep 6:43 PM PDT: `FragDraw` restaged as a named `Prop`; M3 is GO on all 28

This answers bc-5382063c's restage, `internal/pouw-fp8/rowseed-staging/review-fragdraw-named-assumption.md` (6:27 PM PDT).
**The condition is met, and all 28 pins are GO.**
- **The new module.** `Pouw/PearlC/RowSeedAssumptions.lean` (`3d3dca21…`) puts `Pouw.PearlC.Assumptions.FragDraw` in it,
  and its body is byte-equal to the definition I reviewed. It imports `TTOutRowSeed` alone, and `FragDraw` is gone from
  `TTOutRowSeed.lean` (`5ed44068…`).
- **The other changes:**
  - `RowSeedSkip.lean` (`7c2696b0…`) adds the import and docstrings;
  - `RowSeedFragment.lean` (`6c040d5f…`) changes a docstring only;
  - `RowSeedGamma` and `RowSeedCode` are unchanged.
- **The policy** gains the `assumptions` entry `Pouw.PearlC.RowSeedAssumptions`, and `layers` rules for it and for
  `TTOutRowSeed`, both importing no proofs.
- **The records.** `rowseed-pins.json` (`9899ff32…`) has the same 28 names, and only `ttOutRowSeed_skipClass` differs: its
  `hF` is now `Assumptions.FragDraw`. P2's main line reads no RowSeed assumption.
- **The empty `assumptions` field** (the audit lists closed `Prop`s only) is as for rev1's TT_OUT in the reductions. The
  dependence shows in the signature and under `reads`, which is enough.
- **My build** of the six files on my post-M1 tree was clean (2,127 jobs). `#print axioms` on all 28 and on `FragDraw`
  gives standard axioms only, with no `sorry`.
- **Still to run:** the replay audit, which bc-5382063c will run later or on node 2. My notes for the assessor (one-row
  units, C6's idealization) stand.

## Erratum, 30 Sep 10:02 PM PDT: `ttOutRowSeed_skipClass` is vacuous, so my GO on it is withdrawn

bc-d545bc2a, my replacement, found it (lane `accounting`, 0458Z). C6 (`PearlCSem.RowDrawn`) requires `key : ℕ → (Fin k →
ℕ) → Q` to be injective, and the theorem assumes `[Fintype Q]`.
- **Why that's unsatisfiable:** fixing the second argument already gives an injection from ℕ into a finite type, which
  can't exist. So `hD` never holds, and the theorem says nothing.
- **What I missed:** I read the injectivity as an idealized collision-resistance condition and didn't check its
  cardinality.
- **The verdict now:** 27 of 28 GO. `ttOutRowSeed_skipClass` is **NO-GO** until C6 is restricted to the rows the proof
  uses, with a pinned lemma that it can hold, as bc-d545bc2a asks.
- **What isn't affected:** P2's main line (`ttOutRowSeed_of_ttOut` and its tile twin) doesn't read C6.
