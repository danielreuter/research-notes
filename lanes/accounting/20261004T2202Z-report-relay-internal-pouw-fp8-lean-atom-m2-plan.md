---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-lean-atom-m2-plan
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/lean-atom-m2-plan.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/lean-atom-m2-plan.md`, sha256 `4cc7b4854ca8482f60104ac73bf65910f9f2039ac0894f11cf344c363090891a`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# M2 plan: `DistinctLiveH1T` in Lean

Lean worker, 29 Sep 00:25Z, updated at 00:36Z for R1, at 01:00Z for X-H1T-S5 (§3), at 02:30Z when M2 landed (§0),
and at 04:10Z when M3 and M4a landed (§0.6), and at 06:05Z when M4b's column-aware `Hard` and `TTH1T` landed (§0.7),
and at 07:20Z when `TTH1T` got its domain and M4c narrowed `Hard` (§0.8).
The coordinator retargeted M2 to H-1T at 22:30Z (`genuine-fp8-interface.md`).
- **R1** (bc-1114588c, `lean-atom-r1-review.md`) passed M1 at 00:15Z, with one open condition (F1, §4).
- **R2** (Phase 19c, bc-89770364) accepted the statement with 9 changes (X-H1T-8), and M2 started at 01:19Z.

**Status (04:10Z): M2 is granted (Phase 19d, 03:27Z); M3 and M4a are in the package, pending a named statement
reviewer; M4b is the named `Prop` `H1TRunningWords` (§0.6).** §0 is what landed and what remains.
§1 to §6 are the 00:25Z plan, kept for their arguments. Where §0 differs, §0 governs: the §1.2 sketch and the §6 table
are superseded. Sources:
`docs/pouw/hardness-shaped-matrices.md` §3.1–3.3 and §5.3; `internal/pouw/hardness/h1_tagged.py` and `h1_kernel.py`;
`Pouw/Dimension/H100W.lean` (`DistinctOn`, `DistinctLiveAt`, `DistinctLiveMH100`); M1 (`lean-atom-m1.md`); red team
Phase 19c (`internal/pouw/new-crypto/red-team.md` §19c); the sampled-proofs circuit review
(`internal/pouw-fp8/redteam-sampled-proofs-circuit.md`, X-SPC-3).

## 0. M2 as landed (29 Sep 02:30Z)

The package is `lean/submissions/pouw` (Lean v4.34.0, Mathlib `5ed2965`). `STATEMENTS.md` §13 describes the statements
and `ASSUMPTIONS.md` the named `Prop`s. The `--update` printout for the statement reviewer is
`internal/pouw-fp8/lean-atom-m2-update.txt`.

### 0.1 The pins

16 new pins, all `Pouw.Fp8Atom.H1T.Proofs.*`. Every existing record is unchanged, as is every existing module's reads
digest. The package now has 310 pins.

| Group | Pins |
|---|---|
| Conformance (every vector kernel-checked, `decide +kernel`) | `h1tFormTable` (2,540 forming lanes), `h1tTagTable` (80), `h1tSaltConformance` (74 raw salts), `h1tChainConformance` (31 rows, 128 atoms, `T ≤ 3`) |
| The map's properties | `h1tReadsFields`, `h1tNotRawWord`, `h1tTupleInjective`, `h1tTupleWrap`, `h1tWrapDuplicate`, `h1tPosCard`, `h1tNonVacuous` |
| M1 lemmas for M3 and M4 | `rnErr` (half-ulp error of `rn`), `rnAddMovesHalf` (L5), `halfOfInvolution` (L8) |
| Target A to γ | `h1tUnitsDistinct`, `h1tGamma` (both take `DistinctLiveH1T` as a binder, so their records list it) |

New files:
- trusted: `Pouw/Fp8Atom/{H1T,H1TVec,H1TAssumptions,H1TPinned,H1TGamma}.lean` and the generated `H1TVectors.lean`;
- proofs: `H1TProofs.lean`, `H1TGammaProofs.lean` and the generated `H1TChecks.lean`;
- `scripts/h1t_vectors.py` (the generator, byte-reproducible) and `Pouw/Fp8Atom/H1TCoverage.json`.

`lean-audit.json` gains the assumptions module `Pouw.Fp8Atom.H1TAssumptions` and six layers. `H1TGamma` may import
only Mathlib, `Pouw.Dimension.H100W` and the assumptions module.

### 0.2 The 9 changes of X-H1T-8, in Lean

| # | Change | Where |
|---|---|---|
| 1 | The salt is the kernel's fields of 18 raw XOF words per (row, slice) | `RawSlice := Fin 18 → Fin 2^32`; `extract` reads bits 15 and 31 of `r0..r14` (the 29 real lanes) and the sign and 3 mantissa bits per tag lane from `r16` and `r17`. `h1tReadsFields`: equal fields give equal words. `h1tSaltConformance` checks it against the kernel's masks |
| 2 | The credited words are the `4T − 3`: `I_1..I_2T` and `R_2..R_(2T−2)` (1-based) | `Pos T := Fin (2T) ⊕ {p // 1 ≤ p ∧ p + 3 ≤ 2T}` (0-based). `h1tPosCard`: `4T − 3` for `T ≥ 2` |
| 3 | B′ is the real codes plus the fixed tag table | `Unit.b` is real codes only; `colLanes` appends `tuple j` (`A0`, `A1`). `h1tTupleInjective` and `h1tTagTable` |
| 4 | `n ≤ 88,412` per unit, and the unit id is bound in the salt | `Legal` has `n ≤ 88,412`. Each unit has its own `Salt`, and families of units take the product `MSalt Us` (independent coordinates). `h1tWrapDuplicate` shows the bound is needed; `h1tUnitsDistinct` is the multi-unit form |
| 5 | LegalXq is finite codes (no `\|x\| ≤ 416`) | `Legal`: every code of `xq` and `b` finite. §1.1's 416 clause is dropped |
| 6 | `T = ⌈k/29⌉` with zero padding | `Unit.T := (k + 28)/29`; `row` and `col` pad with code 0 |
| 7 | The target is Target A; the half-salt clause is separate | `DistinctLiveH1T` is Target A; `HalfApartH1T` is stated beside it and used by no pin (§0.3) |
| 8 | The obligations list | §0.4 |
| 9 | Non-vacuity at `k = 32,768` and `n = 88,412` | `h1tNonVacuous`: a legal unit there with `m = 1`, `T = 1,130` and 4,517 credited words per output (every code 1.0) |

### 0.3 Which form is proved (X-H1T-7)

- **The target is Target A, at function level, per unit:** `DistinctLiveH1T := ∀ U, U.Legal → Function.Injective
  U.word ∧ ∀ c, U.word c ∉ U.free`. That is one separating salt per pair and per free value, which is what
  `distinctLiveMH100` at `ε = 0, S = univ` needs, and so what `h1tGamma` uses.
- **The half-salt clause is not the target.** `HalfApartH1T` is stated separately: per row, two distinct credited
  words agree on at most half of the row's salts, and a word takes one value on at most half of them. It is Derived
  for `I` words (one flip) and Simulated for `R` words (red team pair frequencies at most 0.375). `census` does not
  measure it: it counts equality on every salt. It is the input to the per-tile count (§0.5) and to any branching
  argument, and no pin reads it yet.
- **What is proved of Target A today:** the raw-XOF half of "not free" (`h1tNotRawWord`: no read bit is below bit 7),
  unconditionally. Everything else in `DistinctLiveH1T` is Assumed, as a binder of `h1tUnitsDistinct` and `h1tGamma`.

### 0.4 The obligations (X-H1T-8 change 8, and the reviews), with a route for each

| Obligation | Source | Route | Milestone |
|---|---|---|---|
| **O1: cross-column `R` words** (`R_p` against `R_p′` or `I_p′`, different columns, same block-1 position) | X-H1T-S5, M2-1 (§3), X-H1T-6 | No single flip works: at `F = 1/4` a flip moves the difference by `2·\|v\|·\|Δt\|`, which can be 64 (128 for a `t₀`-only pair), against `ulp(R) = 512`. The route is function level first, across several slices: salts aligned on the loud slices, L9's window, and a rounding lemma (a gap that is a nonzero multiple of the ulp survives a rounding except at a tie or a binade change), with salts chosen to avoid ties. Half-salts after, as the strike's lattice walk | M4b |
| **O2: block-2 `R` words against every other word** (the chain keeps moving) | X-H1T-5, M2-1 (§3) | A chain-keeps-moving lemma for `R_(T+τ)`: the tag dependence enters at block-1 slices `σ > τ` and passes `T − σ + τ` roundings. Same tools as O1: L9 with aligned salts, and the tie-avoiding rounding lemma. The end of block 2 (`R_(2T−2)`) is the thinnest case | M4b |
| **`I_τ` against `R_τ`** (same slice) | X-H1T-5 | Flip slice `τ − 1`. `R_τ = I_τ` means `R_(τ−1)` is absorbed, so `2·\|R_(τ−1)\| ≤ ulp(I_τ) ≤ 1` by `rnAddMovesHalf`; the flip moves `R_(τ−1)` by at least 448. Needs L1 to L3 and the word-grid lemma | M4a |
| **Absorption** (`R_(p−1)` against `R_p`) | X-H1T-3 | **The strict half-ulp lemma has landed** (`rnAddMovesHalf`, with `rnErr`), so the doc's argument stands: an absorbed summand has `\|I\| ≤ 256`, and a flip moves `I` by at least 960. The alternative, A0's floor raised to 72 (Track H's call), would make the pinned `rnAddMoves` enough; the Lean does not depend on the choice | M4a (the lemma is done) |
| **The legal inputs are all finite codes** | X-H1T-4 | Done in `Legal`. What remains is the range lemma that makes it safe: `\|I\| ≤ 6,881,280` per slice and `\|R\| < 1,130·6,881,280 ≈ 7.78·10⁹ < 2^33` at `x = ±448`, so `ulp(R) ≤ 512`, with no overflow and no subnormal case (R1 F3) | M3 (L4) |
| **Per-unit salts past 88,412 columns** | change 4, X-H1T-S7 | Done: `Legal`'s `n ≤ 88,412`, `h1tWrapDuplicate`, and `MSalt` in `h1tUnitsDistinct` and `h1tGamma`. X-H1T-S7 can be struck | landed |

The other one-flip clauses of §2 (`I` against `I`, block 1 against block 2, block-1 `R` against later words, and
"not a constant" for `I` and block-1 `R`) are M4a, with L1 to L4, L7 and `halfOfInvolution` (L8).

### 0.5 Target after `DistinctLiveH1T`: the per-tile count statement (X-SPC-3; plan only)

- **Why.** `distinctLiveMH100` and `h1tGamma` bound a program that computes one fixed word set, on one fixed salt set
  `S`. The sampled-proofs audit sees a set of correct tiles that depends on the salt, and a union over subsets of
  tiles is vacuous. Theorem 3.1 needs the count form, as NCP-INT has in `TTNCP_U`.
- **The statement (a named `Prop`, `TTH1T pr γ η`, sketch):** for legal units `Us` with independent salts, a tiling
  of their credited words (a tile is a unit or a sub-block of one; tiles of one unit share its rows' salts), and
  every well-formed straight-line `MH100w` program on free inputs with a fixed output slot per credited word:

  ```lean
  Pr_{G : MSalt Us}[ (1 − γ) · Σ_{c right at G} W c > cost100 pr P ] ≤ η
  ```

  Here tile `c` is right at `G` when every one of its credited words equals its output slot's value at `G`, and
  `W c = 32·|credited words of c|`. For equal tiles this is X-SPC-3's form: except with probability η, the number of
  right tiles is at most `cost/((1 − γ)·W_tile)`.
- **Fixed output slots, not "some register".** At a single salt, "some register equals the word" would count
  coincidences, which makes the statement stronger than the audit needs. The verifier reads fixed slots.
- **Z is outside it** (the coordinator's 03:30Z question). "Right" reads only credited words, and the useful output
  `R_(2T−1)` is not credited, nor is `R_(2T−2)` (change 2, `Pos`). So `TTH1T` counts tiles by their checked words
  alone as sketched, and certifying Z in narrow width-rule units needs no change to it. That certification is a
  statement of its own, and `TTH1T` neither needs it nor provides it. NCP-INT is different: `TTNCP_U` counts
  `checkedSet`, whose `checkIdx` includes the last block, and that block's value is Z (`checkedU_final`). Dropping it
  means restating `checkIdx` (a changed definition, so a statement reviewer). The unit's credit `3·m·k·n` includes
  the last block's share of the work (at most `d/(3k)`), which the restatement must then drop or justify. The NCP lower-bound
  chain (A2, `A1_cost`, the lifting) is already stated on the non-final words only (`nonFinal`, P9B-1).
- **Its input is `HalfApartH1T`,** not Target A. Independent row salts give the tail over rows. That lifting (from
  pointwise-right tiles to a cost bound) is the FP8 analogue of `LiftMinRank`, and it is research. Until it is proved,
  `TTH1T` is Assumed, with `HalfApartH1T` and the simulation evidence.
- **Sanity pin (M5):** for a program right on every tile at every salt, `TTH1T`'s event fails at `γ = η = 0`. That
  follows from `h1tGamma`, so the two statements are consistent. A witness pin shows that `TTH1T` is satisfiable.
- **Branching is outside it.** `MH100w` is straight-line. The budgeted P2′ does not bound branching (X-H1T-2), so the
  branching gap stays a named gap, and nothing here cites the budget as covering it.

### 0.6 M3 and M4a as landed (29 Sep 04:10Z), and what remains

The 16 M2 records were granted by Phase 19d (bc-89770364, 03:27Z), with no change asked. M3 and M4a added **11 pins**
(321 in the package; no existing record or reads digest changed). `STATEMENTS.md` §14 describes them, and the
`--update` printout for the statement reviewer is `internal/pouw-fp8/lean-atom-m3-update.txt`.

- **M3, proved:**
  - `h1tAtomValue`: on finite codes, the step from `+0` is two truncations toward zero, `trunc14 (preSum a b)`. This
    settles F4 for H-1T's steps.
  - `trunc14Mono` (L7) and `trunc14Cell` (L3).
  - `h1tSlice`: L1 to L3 on one slice, with block sums at most 6,142,976 and 738,304, and exact `∓2·v·t` moves.
  - `h1tChainMono` (L7 for the chain).
  - `h1tRange`: L4 at `x = ±448`, `|R| < 2^33` and so `ulp ≤ 512` (F3). The block sums are smaller than §0.4's
    6,881,280 bound.
  - `h1tFormCover`: X-M2-4 (a).
- **M4a, proved:** `h1tOneFlip`, both half-salt clauses for every pair that is not `Hard` and every word that is not a
  block-2 running word. `I_τ` against `R_τ` is among them: it flips slice `τ − 1` and uses `RN(y) = w`,
  `|w| < 2^23 ⇒ |y − w| ≤ 1/4`. Absorption (`R_(q−1)` against `R_q`) flips slice `q`, which moves `R_q` by at least
  `960 − 2·256 = 448` and leaves `R_(q−1)`. No M4a proof uses `rnAddMovesHalf`: L4's rounding error of at most 256
  does its work. It stays pinned.
- **M4b, carried as the named `Prop` `H1TRunningWords`** (`Pouw/Fp8Atom/H1TRunningAssumptions.lean`): on every legal
  unit and row, two distinct credited words at `Hard` positions are distinct functions of the salt, and no block-2
  running word is constant. `Hard` is O1 (two columns' block-1 `R` words at one position; narrower than §0.4's O1,
  since `R` against `I` and different positions fall to one flip) and O2 (a block-2 `R` word against every word
  except a later fresh-step word).
  - O1: a flip moves the pair's difference by `2·|v|·|Δt| = 256F` (64 at `F = 1/4`) against up to `512F` of cell and
    rounding error.
  - O2: a several-slice monotone argument (all three lanes of every block-1 slice after `m`) gains at least 3,264
    per slice and loses up to 512 per later rounding. It proves `R_(T+m)` non-constant only for `m` below about
    `0.86·T`, and nothing near the end of block 2.
  - Closing either needs the tie- and binade-avoiding rounding lemma with salts chosen across about `T` roundings.
    That is research, so the `Prop` stays Assumed with the simulation evidence.
- **M5's first half, proved under it:** `h1tDistinctLive` (`H1TRunningWords ⇒ DistinctLiveH1T`), `h1tRunningOfDistinct`
  (the converse), and `h1tGammaRunning` (`H1TGamma` under `H1TRunningWords`). So `h1tGamma`'s statement is now proved
  conditional on O1 and O2 only, as M5 aimed. `HalfApartH1T` stays open for the `Hard` pairs and `Run2` words, since
  `H1TRunningWords` is function level only.
- **Remains:** `H1TRunningWords` itself (M4b); `TTH1T` (§0.5); X-M2-2 (widen `free` and `mfree` at the next change of
  `DistinctLiveH1T`); lanes 29–31 of `X_q` being zero is a layout condition no pin checks (X-M2-4 (b)).
- **Silicon (R1 F1): closed** by Round 11 (04:02Z): all 4,915,200 captured words match `verity.ml.tc`. The forming is
  still checked against a float16 simulation of `h1t_form_xq`, not a GPU, and the chain vectors have `T ≤ 3`.
- **`check.sh`:** ALL CHECKS PASSED on the final state in 582 s (warm build; audit 513.6 s, of which replay 144.8 s
  and `--fresh` 362.6 s), against 557 s at M2. The audit covers 5,479 declarations in 132 modules, with 321 pins.
- **For Track H:** the doc's line 213 ("`x + s·mu` computed in f16 (exact for every code)") and `h1_kernel.py`'s
  line 28 ("exact in f16 for every E4M3 code while F <= 4") are slightly too strong. In the generator's float16
  simulation of `h1t_form_xq`, 16 of the 2,236 reachable forming lanes have an inexact f16 intermediate
  (`H1TCoverage.json`, `f16_intermediate_inexact_reachable`). Every one still encodes to the same codes
  (`kernel_f16_codes_differ: 0`), so the map and the statement are unaffected; only the comments need "the codes are
  exact".

### 0.7 M4b's column-aware `Hard`, and `TTH1T` (29 Sep 06:05Z)

Phase 19f (bc-89770364, 05:17Z) granted §0.6's 11 records and `H1TRunningWords`'s statement. Its notes X-M3-1 to X-M3-3
are applied in `STATEMENTS.md` §12 to §14 and `ASSUMPTIONS.md`. On X-M3-3 the text keeps `T ≤ 14`, with the accounting
written out: `m + 1` block-2 roundings against `T − m − 1` flipped slices. The `T ≤ 22` comes from §3's first
inequality, which counted one slice too many and one rounding too few, and §3 is corrected.

- **M4b, `Hard` by column** (X-M3-1; `STATEMENTS.md` §15). No pin was added and no pin record changed. The definitions
  `Hard`, `H1TOneFlip` and `H1TRunningWords` changed, and `FarTags` and `OppLater` are new. So `h1tOneFlip`,
  `h1tDistinctLive`, `h1tRunningOfDistinct` and `h1tGammaRunning` read changed definitions, and bc-89770364 is their
  named statement reviewer. The printout is `internal/pouw-fp8/lean-atom-m4b-update.txt`.
  - O1 loses the `FarTags` pairs (some lane `|Δt| ≥ 72`). Flip that lane of slice `q`: both `R_(q−1)` stay, and the
    two sums' moves differ by `≥ 4608F` minus four strict cells (`< 512F`), against at most 1,024 of rounding
    (`sep_run_columns`).
  - O2 loses the `OppLater` pairs: a block-2 `R_p` against a block-1 `I_q` or `R_q` of another column with
    `p − T < q < T`, in a lane of opposite signs, with `|t′| ≥ 36` for `R_q`. `R_p` moves weakly one way (L7), and
    the other word strictly the other (`sep_opp_fresh`, `sep_opp_run`). `R_q` needs `|t′| ≥ 36`: `I_q` then moves
    by more than `2304F − 256F ≥ 512`, and at `|t′| = 32` a rounding can absorb its move.
  - What stays in `H1TRunningWords`: nearby columns' block-1 `R` at one position, and a block-2 `R_p` against every
    block-2 word except later fresh-step words, every block-1 word of slices up to `p − T`, and later-slice block-1
    words without an opposite-signed lane (every pair within one column among them). Its equivalence with
    `DistinctLiveH1T` is unchanged.
- **`TTH1T`, stated as a named assumption** (§0.5; `STATEMENTS.md` §16; 2 new pins, 323 in the package). The printout
  is `internal/pouw-fp8/lean-atom-tth1t-update.txt`.
  - `Pouw/Fp8Atom/H1TTile.lean`: `Tiling` (every tile nonempty, in one unit, a block of its rows and columns),
    `slotVal`, `TileRight`, `rightWords`, and the sanity statement `TTH1TAllRight`.
    `H1TTileAssumptions.lean`: `TTH1T γ η`, the probability over the joint salt that
    `(1 − γ)·32·rightWords > cost` is at most `η (tile count)`.
  - Pins: `tth1tAllRight` (under `H1TRunningWords`, the all-right program is never in the event at `γ = 0`; from
    `h1tGammaRunning`) and `tth1tSat` (`TTH1T 1 0`).
- **Remains:** `H1TRunningWords` on what is left of `Hard`; `HalfApartH1T` there; the lifting that would prove `TTH1T`;
  X-M2-2; X-M2-4 (b).

### 0.8 `TTH1T`'s domain, and M4c (29 Sep 07:20Z)

Phase 19h (bc-89770364, 06:42Z) granted §0.7's four changed statements, the narrowed `H1TRunningWords`, `tth1tAllRight`
and `tth1tSat`, confirmed the 36 threshold and X-M3-3's `T ≤ 14`, and did not grant `TTH1T` as stated (X-M4-4).
`STATEMENTS.md` §17 has the detail; the printout is `internal/pouw-fp8/lean-atom-m4c-update.txt`, and bc-89770364 is
the named statement reviewer again.
- **`TTH1T r c γ η`** reads only tilings with `Tiling.AtLeast r c` (every tile holds an `r × c` block of one unit's
  outputs); layout A is `r = c = 16`. Of the three fixes, this one states what layout A fixes before the salt, as
  `TTNCP_U`'s `D` does. Rows are what bound a lucky guess (independent row salts; columns share a row's), so `η`
  reading the tile's credited-word count would not fix it, and `η` reading rows and `T` would still claim one `η` for
  every shape. A slack would need a tail bound of its own.
  - `tth1tSat` is now `∀ r c, TTH1T r c 1 0` (the one changed record). `tth1tAllRight` is unchanged, over every tiling.
  - No witness at `γ < 1` with `η < 1`: that is the lifting. §0.5's promised witness is met only at `γ = 1` (X-M4-5).
- **M4c, `Hard` narrowed further** (both optional, both cheap given M4b's lemmas):
  - X-M4-1: O1 excludes `OppLater` either way round (`sep_opp_run` at `p = q`): 591,000 fewer pairs.
  - X-M4-2: `Early` block-2 running words (a lane `≥ 32·(p − T + 2) + 4`) separate from every word that skips slice
    `T − 1`, and are not constant. A flip of slice `T − 1` reaches `R_p` through `p − T + 2` roundings
    (`run_last_chain`). `Stuck` (`Run2` and not `Early`) replaces `Run2` in both non-constancy clauses. It covers 6.98
    positions per column on average: most of block 2 at small `T`, 2.5% at `k = 8,192`.
  - §14's "up to `2T − 3` roundings" now says it is the worst case (slice 0), and `p − T + 2` from the last slice.
- **Remains:** as §0.7, less X-M4-1 and X-M4-2's pairs.

## Summary

- **The statement** is the doc's §5.3 restated with Lean quantifiers (§1). It has three clauses per row: any two
  credited positions are unequal on at least half of the row's salts; no credited word takes one value on more than half
  of them; and no credited word is a raw XOF word. The γ corollary needs only the function-level consequence,
  `DistinctLiveAt 0 univ F ts`, which feeds the pinned `distinctLiveMH100`.
- **What the doc's one-flip argument proves** (§2): every pair of fresh-step words. It also proves every pair of a
  block-1 running word (R_2..R_T) with a fresh-step word, or with another block-1 running word at a different
  position. Beyond that, it proves absorption and the non-freeness of those words. The Lean route for these is clear.
  It needs a sharp movement lemma from M1 (a summand of more than half an ulp moves the sum), exactness of the tag
  products on the alignment grid, a cell bound, monotonicity, and an involution count.
- **Finding M2-1: the open obligation is larger than §3.2 says** (§3). Besides the named case (running words of
  different columns at the same position, O1), no single salt flip reaches the **block-2 running words**
  R_(T+1)..R_(2T−2) (O2). Every salt of a slice ≤ s enters R_(T+s) through both blocks and cancels. Every salt of a
  later slice enters only through block 1, followed by further FP32 roundings that can absorb the move.
  - So without O1 and O2, only the 2T fresh-step words are provably distinct, and ε ≈ 1/2.
  - O1 and O2 together cover essentially every running word, and the γ bound's 4T − 3 credit needs them.
  - Simulation finds 0 violations (the doc's §5.2 and `h1_tagged_rcheck.py`), so this is a proof gap, not a
    counterexample.
  - The H-1T strike found the cross-column case independently (X-H1T-S5, `red-team-h1-strike.md`, bc-8954d550): no
    single flip separates adjacent columns at quiet slices, so the proof needs an argument across several slices (§3).
- **Recommendation:** state O1 and O2 as named clauses. Prove everything else. If they don't fall, carry them as a named
  assumption Prop, with the simulation evidence, as §5.3 already does for the whole statement.

## 1. The statement

### 1.1 New trusted definitions (`Pouw/Fp8Atom/H1T.lean`, a new layer over `Atom` and `Fp32`)

- **Salt:** `SliceSalt := Fin 18 → Fin (2^32)` (raw XOF words r0..r17), and `RowSalt T := Fin T → SliceSalt`.
  - Bit extraction follows §3.1 and the kernel (`h1_kernel.py` docstring). The sign of real lane `ℓ ≤ 28` is bit 15
    (ℓ even) or bit 31 (ℓ odd) of `r_(ℓ/2)`; a set bit gives s = +1, so x2 = −μ.
  - Tag lane 29 takes its sign and m from r17 bits 31 and 25..23. Tag lanes 30 and 31 take theirs from r16 bits 15,
    9..7 and 31, 25..23. On tag lanes a set bit makes v negative.
- **Instance:** `Unit` with `m k n`, `xq : Fin m → Fin k → Code`, `b : Fin k → Fin n → Code`, and
  `T := ⌈k/29⌉`. `Legal U`: k ≤ 32,768, n ≤ 88,412, every code finite, and |x| ≤ 416 on X_q.
- **Forming (§3.1):**
  - the layout: real lanes 0..28 of each slice, zero-padded to 29·T;
  - per slice, `M`, `F = max(2^(e(M)−6), 2^−2)`, `p`, `μ = max(p/8, F)`;
  - `x1 = rneSatfinite (x + s·μ)` and `x2 = −s·μ`. x + s·μ is taken exactly over ℚ; §3.1 says the f16 intermediate
    is exact;
  - tag values `v = ±32F(1 + m/8)`, which are exact E4M3 codes for F ∈ [1/4, 4];
  - tag rows `t0 = A0[j mod 23]`, `t1 = A1[(j / 23) mod 62]` and `t2 = A1[(j / 1426) mod 62]` on lanes 29, 30 and 31.
  - `rneSatfinite : ℚ → Code` is a new trusted E4M3 encoder.
- **Chain:**
  - `I p := hopperStep 0 (x1 or x2 of slice p) (B′ column of slice p)`, where positions 1..T are block 1 and
    T+1..2T are block 2;
  - `R 1 := I 1` and `R (p+1) := rnAdd (R p) (I (p+1))`.
  - Words are taken as **values in ℚ**. That is conservative: two words that are equal as values count as equal, which
    covers +0 against −0.
- **Credited positions:** `Pos T n`, meaning `I j p` for p ∈ 1..2T and `R j p` for p ∈ 2..2T−2. That is 4T − 3 per
  column for **T ≥ 2**; at T = 1 the count is 2, not 1 (a small flag on §3.1's formula).

### 1.2 The statement (sketch; superseded by §0.3)

The half-salt form below is no longer the target. The landed target is Target A (§0.3), and the half-salt clause is
`HalfApartH1T`.

```lean
def HalfApart {G} [Fintype G] (w w' : G → ℚ) : Prop :=
  2 * (Finset.univ.filter fun g => w g = w' g).card ≤ Fintype.card G

def xofWord (τ : Fin T) (ℓ : Fin 18) : RowSalt T → ℚ := fun σ => (σ τ ℓ : ℚ)

/-- §5.3 clause 2, per row. `word U i a` is the credited word at position `a` of row `i`. -/
def DistinctLiveH1T : Prop :=
  ∀ U : Unit, Legal U → 2 ≤ U.T → ∀ i : Fin U.m,
    (∀ a b : Pos U.T U.n, a ≠ b → HalfApart (word U i a) (word U i b)) ∧
    (∀ (a : Pos U.T U.n) (q : ℚ), HalfApart (word U i a) (fun _ => q)) ∧
    (∀ a τ ℓ, word U i a ≠ xofWord τ ℓ)
```

- **The free set** for the unit is the constants plus every raw XOF word of every row and slice. Bit-extracted signs are
  not free: extraction is a priced instruction. The last clause is immediate, because bit 0 of every word is unread.
- **The unit corollary** (`distinctLiveH1T_unit`): over `G = Fin m → RowSalt T`, `DistinctLiveAt 0 Set.univ freeUnit
  unitWords`.
  - Within a row, it follows from `HalfApart` at `a ≠ b`, since `RowSalt T` is nonempty.
  - Across rows, the words are functions of disjoint coordinates, so two equal ones would both be constant. The second
    clause excludes that.
- **The γ corollary (M5):** `distinctLiveMH100` at ε = 0 gives a cost of at least 32·m·n·(4T − 3). The honest cost
  `32·2T + p_FADD·(2T − 1) + f_a·k/n` per output is a parameter, so the §5.3 bound follows. The attainment, in the style
  of `splitK` and `C2FirstRunCopy` (with `WordsRepresentable`), is reused.
- **For R2 to decide:**
  - Should the pinned target be the half-salts form above, or only the function-level form that γ uses? If O1 and O2
    fall only at function level, the split is `DistinctLiveH1T` (function level) and `HalfApartH1T` (the per-row copy
    bound of §3.2's last bullet).
  - Is constants ∪ raw XOF words the right free set?
  - Are values, rather than bit patterns, the right comparison?

### 1.3 Conformance and non-vacuity

- **Conformance of the forming and the chain** is new vectors, kernel-checked like M1:
  - exhaustively, the per-lane forming table: every legal x code × s × F ∈ {2^−2..2^2}, about 2,500 cases, with no
    atom;
  - a few hundred full rows at T ≤ 8 through the forming, the atoms and the chain, against `h1_tagged.chain`.
  - `h1t_ref` draws its signs from an RNG and has no raw-word interface. So the oracle is a short wrapper in
    `scripts/`, reusing `_floor` and `enc`, with signs decoded from r_i as above.
  - Round 11's `h1t_form_xq` against `h1t_ref` check covers the kernel side.
- **Non-vacuity:**
  - a legal unit exists (X_q = 0, B′ = 0, k = 58, n = 2), and it has 5 credited words per output;
  - the hypotheses of the γ corollary hold together at the nominal prices (as `pipeChainConsistent` does for NCP);
  - a sanity lemma shows the tags are load-bearing: without tag rows, two identical real columns give duplicate words.

## 2. The proof plan (M3/M4), by clause

Notation: positions p ≤ T are block 1 (slice p) and p = T + s is block 2 (slice s). "Flip lane i of slice σ" means
flipping that tag's sign bit, which is an involution on the row's salts.

**Lemmas (all from M1 and the new definitions):**

| # | Lemma | How |
|---|---|---|
| L1 | Flipping a product's sign keeps every magnitude and exponent, so `maxExp` is unchanged. Truncation toward zero is odd, so `alignedSum` changes by exactly 2·`aligned` of the term | structural, `Atom` |
| L2 | **Tag products are exact on the alignment grid.** The grid is 2^(E−13) ≤ 4F, since every product is below 2^16·F. A tag product is a multiple of 16F (v a multiple of 4F, and \|t\| ≥ 32 a multiple of 4) | a finite `decide` table over the v codes, the 85 tag codes and the exponent gap, plus the bound on E |
| L3 | **Cell:** every aligned sum is below 2^21·F (at most 144F·29·448 + 3·60F·448). So a word's cell is at most 128F, and two equal words have sums within 128F | `normalize` |
| L4 | **Range:** on legal inputs no word or running sum overflows: \|I\| < 6.9·10⁶, and \|R\| < 2^33 for T ≤ 1,130, so ulp(R) ≤ 512. No subnormal case is needed, since `rnAdd` is binary32 on finite words short of overflow (R1 F3). The saturation in `groupStepTotal` and the `mag = 0` exit in `normalize` are unreachable, and nothing reads the −139 floor (R1 F4) | the forming bounds and L3 |
| L5 | **Sharp movement (new M1 pin):** for representable r ≠ 0, ulp(r) < 2·\|i\| gives `rnAdd r i ≠ r`. It holds at powers of two too; I checked both binade boundaries by hand. The pinned `RnAddMoves` (\|i\| ≥ ulp) is too weak for absorption at F = 1/4 with 2^32 ≤ \|R\| < 2^33 (§4; R1 F6 reads it otherwise) | `Fp32Proofs`, `roundEven_near` |
| L6 | **Separation:** \|y − y′\| > 512 and \|y\|, \|y′\| < 2^33 give `rn y ≠ rn y′` | `roundEven_near` |
| L7 | **Monotonicity:** `hopperStep` is monotone in one product term (`AlignedMono` and monotone `normalize`, M3's key lemma), and the chain is monotone in each I (`RnAddMono`). E is salt-invariant, since salt signs and tag mantissa bits don't move product exponents, and the atom is symmetric in its 32 pairs (R1 F6) | M1 and M3 |
| L8 | **Involution count:** if ψ is an involution and `w g = w' g` gives `w (ψ g) ≠ w' (ψ g)`, then `HalfApart w w'` | Finset |
| L9 | **Window:** in one column, for p < q, R_q − R_p lies within (q − p)·256 of Σ_(p<t≤q) I_t | L4 and `roundEven_near` |

**Clauses and their status** (Derived on paper; for R2 to check):

| Pair or clause | Argument | Status |
|---|---|---|
| I_p against I_q, different slices | flip lane 0 of one word's slice: by L1–L3 the word moves by more than 3,840F ≥ 960, and the other doesn't depend on it | one flip |
| I_p against I_p′, same slice and block, different columns | the tuples differ in some lane i by \|Δt\| ≥ 4. By L1 and L2 the sum difference moves by exactly 2\|v_i\|·\|Δt\| ≥ 256F, and by L3 equal words need it below 128F both before and after. **The margin is exactly tight;** it holds only because of L2 | one flip |
| block 1 against block 2, same slice, any columns | lane 0 moves the difference by 2\|v0\|(t0 + t0′) ≥ 8,192F | one flip |
| R_p (p ≤ T) against I_q, q ≠ p, any columns; R_p against R_q, p < q ≤ T, any columns | flip the slice at the later word's last position. That word moves strictly (for a block-1 R, by L6: 960 > 512), and the other does not depend on it. When a block-2 I_(T+s) shares slice s with R_p (s ≤ p), they move in opposite directions (L7) | one flip |
| I_p against R_p, same column (2 ≤ p ≤ T+1) | R_p = I_p forces \|R_(p−1)\| ≤ ulp(I_p)/2 ≤ 1/4 (L5). Flipping slice p − 1 (slice T when p = T + 1) moves R_(p−1) by ≥ 448 and leaves I_p alone | one flip |
| **Absorption**, R_(p−1) against R_p, same column, every p | equality means \|I_p\| ≤ 256 (L5, with ulp ≤ 512). A lane-0 flip of I_p's slice moves I_p by ≥ 960 | one flip |
| R_(T+s) against I_(T+s′), s′ > s, any columns | lane 0 of slice s′: R moves weakly (through block 1) and I strictly, in opposite directions (L7) | one flip |
| no free word, for I and block-1 R | as above, against every constant; bit 0 against the XOF words | one flip |
| **O1:** R_p against R_p′ and R_p against I_p′, different columns, same block-1 position | the flip moves both words the same way. Their difference is 2v_iΔt_i ≥ 256F ≥ 64 (128 for a t₀-only pair), below ulp(R) at quiet slices | **open** (the doc's named obligation; confirmed by X-H1T-S5) |
| **O2:** every other pair involving a block-2 R_(T+s) (1 ≤ s ≤ T−2), and its non-freeness | no single flip moves R_(T+s) strictly (§3) | **open** (new) |

## 3. Finding M2-1: the block-2 running words (O2), and ways to close O1 and O2

**Why one flip fails for R_(T+s).**
- A slice σ ≤ s enters R_(T+s) at position σ (block 1, +v) and at T + σ (block 2, −v). Flipping it moves the two
  contributions in opposite directions, with roundings in between, so the net move has no controlled sign or size.
- A slice σ in (s, T] enters only at position σ, followed by T + s − σ further `rnAdd`s. By L7 the move is weak and in
  one direction, but a later rounding can absorb it (with ulp 512, a gap of 448 can merge).
- So §3.2's "flip a tag sign of the later slice changes only the later word" doesn't hold for these words. For
  example, R_(T+1) against I_T is not reached by any flip.
- These are T − 2 of the 4T − 3 credited words per output, and O1 adds cross-column pairs among the other T − 1
  running words. Without both, the provable D is the 2T fresh-step words, giving ε ≈ 1/2.

**Independent confirmation of O1 (X-H1T-S5, `red-team-h1-strike.md`, the H-1T strike, bc-8954d550).**
- The strike's `e4` construction (k = 32,768, 48 salts) takes column pairs whose tag tuples differ in one lane by the
  smallest step, with identical real columns: t₀ only (j, j + 1), with Δt₀ = 8, and t₁ or t₂ only, with Δt = 4.
- Adjacent columns differ only in t₀, and they are the most common pair. At a quiet slice (F = 1/4, v = 8) a flip moves
  their difference by 2·8·8 = 128, under ulp(R) = 512. So no single flip separates them.
- §6's fallback of four positive A0 tags gives the same 128. A one-flip proof would need Δt ≥ 64 at v = 8, and no set
  of 23 or more E4M3 codes is spaced that widely.
- **So O1 needs an argument across several slices.** The strike's sketch: after the loud slices the pair's difference
  is a lattice walk whose every step a flip moves by at least 2 ulp, and the proof bounds how often the quiet suffix's
  roundings merge it back to 0. That is route 2 below.
- **Simulation:** function level 0 (no credited R position equal on every salt, for any pair). No pair and position is
  equal on more than half the salts; the worst quiet position is 0.19, and the means are at most 0.9%.

**Ways to close them**, in the order I would try them:
1. **Function level first.** γ needs only `DistinctLiveAt 0 univ`, meaning one salt per pair where the words differ.
   - For same-column pairs, L9 with salts aligned on every singly covered slice should work. Each such slice moves
     Σ I by ≥ 3,776 against a window of 512 per position.
   - That proves R_(T+s)'s non-freeness at function level whenever (T − s − 1)·3,264 > (s + 1)·512
     (s ≲ 0.86·T − 1). The aligned slices are s + 1 to T − 1, and each adds at least 3,776 − 512 net of its own
     rounding. The s + 1 block-2 roundings after them erode at most 512 each. (Corrected at 05:30Z, X-M3-3: this
     first read (T − s)·3,264 > s·512, one slice too many and one rounding too few.) The tail and most cross-column pairs
     need a finer rounding lemma: a gap that is a nonzero multiple of the ulp survives a rounding except at a tie or a
     binade change. With that lemma, choose salts that avoid ties.
2. **Half-salts.** One flip moves Σ I by only ≥ 960 against L9's window of (q − p)·512. So it reaches only adjacent
   positions, which absorption already covers. Beyond that it needs an anti-concentration argument over several
   slices, which is research. For O1 this is X-H1T-S5's lattice walk above.
3. **Named-assumption fallback.** `H1TRunningWords` in a new `Pouw/Fp8Atom/H1TAssumptions.lean`, taken as a hypothesis
   of the γ corollary, with the simulation evidence. It states O1 and O2 in the same clause form, and the rest is
   proved. This matches §5.3, which already carries the whole statement as Assumed.
4. **Construction (Track H's call).** The trouble comes from per-slice tag cancellation between the blocks. Any
   repair is Track H's; I only note where the proof needs strict single-flip movement.

## 4. What M2 needs from M1, and the R1 dependency

- **New M1 pins:** L5 (sharp movement) and L6 (separation), both in `Fp32Proofs` and both small; plus M3's `normalize`
  monotonicity. The existing records are unchanged.
- **M2's definitions build on M1's `hopperStep` and `rnAdd`.** R1 found no discrepancy (00:15Z), so M2 can build on
  them as they are.
- **R1's open condition, F1:** the instruction form H-1T issues has not been compared with the model on silicon. That
  form is m64n128k32, scale-d = 0, both operands from shared-memory descriptors, then `add.rn.f32`.
  - Round 11's C1 and C4 close it, and then M1 adds `HopperCaptures` and `ChainCaptures`.
  - Until then `DistinctLiveH1T` is a statement about the model, and no ledger should say it is about H-1T's silicon.
- **R1's rules, taken up here:**
  - L4 needs only "no overflow" (F3). M1 adds the no-overflow and word-grid lemmas: word values are multiples of
    2^−149, and H-1T's atom words and running sums are multiples of 2^−25.
  - The two unreachable branches are proved unreachable as range lemmas, and no statement depends on the −139
    floor (F4).
- **The 22:30Z `rnAddAbsorb` note:** H-1T's absorption uses L5's contrapositive ("absorbed means 2·|i| ≤ ulp r"), which
  holds at ±2^k in both directions. So the boundary clause doesn't bite here, and the ≥ 960 against ≤ 512 argument
  stands with L5.
- **Where I differ from R1 (F6):** R1 reads `RnAddMoves` (|i| ≥ ulp r moves r) as covering "≥ 960 against ulp ≤ 512"
  directly. It doesn't in one case: F = 1/4, where a lane-0 flip moves I by at least 960, with 2^32 ≤ |R| < 2^33,
  where ulp(R) = 512.
  - Take the absorption row, R_(p−1) = R_p. `RnAddMoves` only says that |I_p| < 512 at the equal salt. After the flip,
    |I_p| > 960 − 512 = 448, which is below 512, so `RnAddMoves` can't show the flipped salt moves R. The band it
    leaves, |i| < 512, is 1,024 wide, more than the 960 a flip guarantees.
  - L5 narrows the band to |i| ≤ 256. After the flip |I_p| ≥ 704, so 2·|I_p| > 512 and R moves, whatever the flip
    does to R_(p−1), since ulp stays at most 512 (L4).
  - So L5 stays a new, small M1 pin. For F ≥ 1/2 a flip moves I by at least 1,920 > 1,024, and `RnAddMoves` would do.

## 5. Flags for Track H and the doc

1. **M2-1** (§3): §3.2's one-flip argument does not cover the block-2 running words, and §5.3's "proof obligation
   left" should also name O2.
2. **The `h1_tagged.py` module docstring** (line 9) still says `v_i = s_i · 64F`. The code's default (`TAG_MANT = 1`)
   and doc §3.1 use 32F(1 + m/8).
3. **r15 is unread by the map,** and so is bit 31 of r14 (its lane 29 is a tag, signed from r17). `h1_kernel.py` says
   the real-lane salt words are r0..r15. That is harmless for the statement, since XOF words are free anyway, but
   Track H should confirm it is intended.
4. **The same-block cross-column margin is exactly tight:** 2·32F·4 = 256F against two cells of 128F. It holds only
   because tag products are exact on the grid (L2). A change to the tag magnitudes, to A1's minimum |t| = 32, or to
   the 14-bit width must keep 2·v_min·Δt_min ≥ 2·cell_max.
5. **The credit formula 4T − 3 holds for T ≥ 2** (k ≥ 30). At T = 1 the count is 2.

## 6. Effort and order (after R1 and R2; superseded by §0.6)

M2 has landed. L5 is pinned as `rnAddMovesHalf` and L8 as `halfOfInvolution`, and §0.6 lists what remains.

| Step | Content | Size |
|---|---|---|
| M2 | `H1T.lean` definitions, the statement, the unit and γ corollaries as statements, the forming and chain conformance, non-vacuity | ~500–700 lines plus generated vectors; 1–2 passes |
| M3 | L1–L4, L7 (`normalize` monotone), and as M1 additions L5, L6, and R1's no-overflow, word-grid and unreachability lemmas (F3, F4) | ~1,000–1,500 lines; 2 passes |
| M4a | the one-flip clauses of §2, L8, and the unit corollary | ~800–1,200 lines; 1–2 passes |
| M4b | O1 and O2: function level via L9 and the rounding lemma first, half-salts after | research; timeboxed, with the §3 item 3 fallback |
| M5 | the γ corollary at ε = 0 (under `H1TRunningWords` if M4b doesn't close), pins, `audit.py --update`, R3 | ~200 lines; 1 pass |

Kernel-checked conformance adds to `check.sh`, so the M2 vectors go wherever the check-cost decision puts the
conformance (`lean-atom-check-cost.md`).
