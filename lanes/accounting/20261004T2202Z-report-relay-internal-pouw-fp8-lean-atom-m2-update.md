---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-lean-atom-m2-update
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/lean-atom-m2-update.txt
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/lean-atom-m2-update.txt`, sha256 `74932a2723b57a358c00480cb86a06874768a777b80fc25ba84eb5f970495571`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store. It is a `.txt` file; the body below is its bytes.

# audit.py --update review printout: H-1T M2 (lean/submissions/pouw; 310 pins, 16 new, none changed)

Named statement reviewer: to be named by the coordinator (proposed: R2, bc-89770364, who reviewed DistinctLiveH1T in
Phase 19c). The audit requires one for the 16 new pins before the merge.
Change: internal/pouw-fp8/lean-atom-m2-plan.md, section 0 (M2 as landed, 29 Sep 02:30Z); STATEMENTS.md section 13.
Run: 29 Sep 02:25Z on /home/ubuntu/pouw, `python3 tools/lean/audit.py --update .`, from lean-audit.json with the 16 new
pin names added with empty records. Result: AUDIT PASS; 5,064 declarations in 126 modules; axioms propext,
Classical.choice, Quot.sound; 310 pinned theorems.

What changed:
- 16 new pin records, all in Pouw.Fp8Atom.H1T.Proofs: h1tFormTable, h1tTagTable, h1tSaltConformance,
  h1tChainConformance, h1tReadsFields, h1tNotRawWord, h1tTupleInjective, h1tTupleWrap, h1tWrapDuplicate, h1tPosCard,
  h1tNonVacuous, rnErr, rnAddMovesHalf, halfOfInvolution, h1tUnitsDistinct, h1tGamma.
- h1tUnitsDistinct and h1tGamma take the named assumption DistinctLiveH1T as a binder (hD), so their records list it
  under `assumptions`. The other 14 take none.
- No existing pin record changed: all 294 signatures, named assumptions and type hashes are as before.
- No existing module's `reads` digest or definition digests changed. Seven existing modules' `reads.pins` lists gained
  new pin names, because the new statements read definitions there that existing pins already read:
  Pouw.Dimension.{Embed, H100, H100Assumptions, H100W} (h1tGamma) and Pouw.Fp8Atom.{Atom, E4M3, Fp32}.
- New `reads` modules: Pouw.Fp8Atom.H1T (44 definitions), H1TVec (35), H1TVectors (40), H1TPinned (14),
  H1TGamma (6), H1TAssumptions (1: DistinctLiveH1T).
- Policy: `assumptions` gains Pouw.Fp8Atom.H1TAssumptions; `layers` gains Pouw.Fp8Atom.H1T, H1TVec, H1TVectors,
  H1TAssumptions, H1TPinned and H1TGamma. Nothing else in the policy changed.

The audit's printout follows, verbatim.

audit: ./lean-audit.json: pins and reads rewritten from the build; a named statement reviewer must read these changes before the merge:
  pin Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance : Pouw.Fp8Atom.H1T.H1TChainConformance
  pin Pouw.Fp8Atom.H1T.Proofs.h1tFormTable: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tFormTable : Pouw.Fp8Atom.H1T.H1TFormTable
  pin Pouw.Fp8Atom.H1T.Proofs.h1tGamma: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tGamma (hD : Pouw.Fp8Atom.H1T.DistinctLiveH1T) : Pouw.Fp8Atom.H1T.H1TGamma
  pin Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous : Pouw.Fp8Atom.H1T.H1TNonVacuous
  pin Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord : Pouw.Fp8Atom.H1T.H1TNotRawWord
  pin Pouw.Fp8Atom.H1T.Proofs.h1tPosCard: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tPosCard : Pouw.Fp8Atom.H1T.H1TPosCard
  pin Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields : Pouw.Fp8Atom.H1T.H1TReadsFields
  pin Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance : Pouw.Fp8Atom.H1T.H1TSaltConformance
  pin Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tTagTable : Pouw.Fp8Atom.H1T.H1TTagTable
  pin Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective : Pouw.Fp8Atom.H1T.H1TTupleInjective
  pin Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap : Pouw.Fp8Atom.H1T.H1TTupleWrap
  pin Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct (hD : Pouw.Fp8Atom.H1T.DistinctLiveH1T) : Pouw.Fp8Atom.H1T.H1TUnitsDistinct
  pin Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate : Pouw.Fp8Atom.H1T.H1TWrapDuplicate
  pin Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution : Pouw.Fp8Atom.H1T.HalfOfInvolution
  pin Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf : Pouw.Fp8Atom.H1T.RnAddMovesHalf
  pin Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    after:
      Pouw.Fp8Atom.H1T.Proofs.rnErr : Pouw.Fp8Atom.H1T.RnErr
  definition Pouw.Fp8Atom.H1T.A0 (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:125-126):
      /-- `A0`: the 23 positive codes `0x68..0x7E` (64 to 448). -/
      def A0 (i : Fin 23) : Code := ⟨0x68 + i.val, by have := i.isLt; omega⟩
  definition Pouw.Fp8Atom.H1T.A1 (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:128-130):
      /-- `A1`: the 62 codes `0x60..0x7E` (32 to 448) and `0xE0..0xFE` (their negations). -/
      def A1 (i : Fin 62) : Code :=
        ⟨if i.val < 31 then 0x60 + i.val else 0xE0 + (i.val - 31), by have := i.isLt; split <;> omega⟩
  definition Pouw.Fp8Atom.H1T.Pos (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:165-167):
      /-- The credited positions of one output (0-based): `I_p` for `p < 2T` (`inl`) and `R_p` for `1 ≤ p ≤ 2T − 3`
      (`inr`). -/
      abbrev Pos (T : ℕ) := Fin (2 * T) ⊕ {p : Fin (2 * T) // 1 ≤ p.val ∧ p.val + 3 ≤ 2 * T}
  definition Pouw.Fp8Atom.H1T.RawSlice (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:62-63):
      /-- One (row, slice)'s 18 raw XOF words `r0..r17`. -/
      abbrev RawSlice := Fin 18 → Fin (2 ^ 32)
  definition Pouw.Fp8Atom.H1T.SliceSalt (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:68-75):
      /-- The fields of one (row, slice)'s salt that the map reads. -/
      structure SliceSalt where
        /-- Real lane `ℓ`'s sign bit: set means `s = +1` (`x1 = x + μ`, `x2 = −μ`). -/
        pos : Fin 29 → Bool
        /-- Tag lane `29 + i`'s sign bit: set means `v` is negative. -/
        neg : Fin 3 → Bool
        /-- Tag lane `29 + i`'s three mantissa bits `m`. -/
        man : Fin 3 → Fin 8
  definition Pouw.Fp8Atom.H1T.SliceSalt.man (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:75-75):
        man : Fin 3 → Fin 8
  definition Pouw.Fp8Atom.H1T.SliceSalt.neg (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:73-73):
        neg : Fin 3 → Bool
  definition Pouw.Fp8Atom.H1T.SliceSalt.pos (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:71-71):
        pos : Fin 29 → Bool
  definition Pouw.Fp8Atom.H1T.Unit (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:169-175):
      /-- A unit: `m` rows of `X_q` (`xq`, E4M3 codes) against `n` columns of B′'s registered real codes (`b`) over `k`. -/
      structure Unit where
        m : ℕ
        k : ℕ
        n : ℕ
        xq : Fin m → Fin k → Code
        b : Fin k → Fin n → Code
  definition Pouw.Fp8Atom.H1T.Unit.Legal (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:206-208):
      /-- **Legal inputs**: `k ≤ 32,768`, `n ≤ 88,412` columns per unit, and every code of `X_q` and of B′ finite. -/
      def Legal (U : Unit) : Prop :=
        U.k ≤ 32768 ∧ U.n ≤ 88412 ∧ (∀ i l, (U.xq i l).isNaN = false) ∧ ∀ l j, (U.b l j).isNaN = false
  definition Pouw.Fp8Atom.H1T.Unit.Salt (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:188-189):
      /-- The unit's salt: 18 raw XOF words per (row, slice). -/
      abbrev Salt (U : Unit) := Fin U.m → Fin U.T → RawSlice
  definition Pouw.Fp8Atom.H1T.Unit.T (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:179-180):
      /-- The number of slices, `⌈k/29⌉`. -/
      def T (U : Unit) : ℕ := (U.k + 28) / 29
  definition Pouw.Fp8Atom.H1T.Unit.b (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:175-175):
        b : Fin k → Fin n → Code
  definition Pouw.Fp8Atom.H1T.Unit.col (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:185-186):
      /-- Column `j` of B′'s real codes, zero-padded. -/
      def col (U : Unit) (j : Fin U.n) : ℕ → Code := fun r => if h : r < U.k then U.b ⟨r, h⟩ j else ⟨0, by norm_num⟩
  definition Pouw.Fp8Atom.H1T.Unit.free (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:201-204):
      /-- The free values on the unit's salt (W1): the constants, which include every salt-independent function of the
      committed input, and the raw XOF words. -/
      def free (U : Unit) : Set (U.Salt → ℚ) :=
        {f | (∃ q : ℚ, f = fun _ => q) ∨ ∃ (i : Fin U.m) (τ : Fin U.T) (ℓ : Fin 18), f = fun g => ((g i τ ℓ : ℕ) : ℚ)}
  definition Pouw.Fp8Atom.H1T.Unit.k (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:172-172):
        k : ℕ
  definition Pouw.Fp8Atom.H1T.Unit.m (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:171-171):
        m : ℕ
  definition Pouw.Fp8Atom.H1T.Unit.n (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:173-173):
        n : ℕ
  definition Pouw.Fp8Atom.H1T.Unit.row (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:182-183):
      /-- Row `i` of `X_q`, zero-padded. -/
      def row (U : Unit) (i : Fin U.m) : ℕ → Code := fun r => if h : r < U.k then U.xq i ⟨r, h⟩ else ⟨0, by norm_num⟩
  definition Pouw.Fp8Atom.H1T.Unit.rowSalt (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:191-193):
      /-- Row `i`'s salt fields per slice. -/
      def rowSalt (U : Unit) (g : U.Salt) (i : Fin U.m) : ℕ → SliceSalt :=
        fun τ => if h : τ < U.T then extract (g i ⟨τ, h⟩) else extract rawZero
  definition Pouw.Fp8Atom.H1T.Unit.word (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:195-199):
      /-- The credited word of row `i`, column `j`, position `a`, as a function of the unit's salt. -/
      def word (U : Unit) (c : Fin U.m × Fin U.n × Pos U.T) (g : U.Salt) : ℚ :=
        match c.2.2 with
        | .inl p => freshVal U.T (U.row c.1) (U.col c.2.1) c.2.1.val (U.rowSalt g c.1) p.val
        | .inr p => runVal U.T (U.row c.1) (U.col c.2.1) c.2.1.val (U.rowSalt g c.1) p.val.val
  definition Pouw.Fp8Atom.H1T.Unit.xq (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:174-174):
        xq : Fin m → Fin k → Code
  definition Pouw.Fp8Atom.H1T.bitAt (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:80-81):
      /-- Bit `b` of `w`. -/
      def bitAt (w b : ℕ) : Bool := (w >>> b) % 2 == 1
  definition Pouw.Fp8Atom.H1T.bits3 (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:83-84):
      /-- Bits `b + 2 .. b` of `w`. -/
      def bits3 (w b : ℕ) : Fin 8 := ⟨(w >>> b) % 8, Nat.mod_lt _ (by norm_num)⟩
  definition Pouw.Fp8Atom.H1T.colLanes (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:142-144):
      /-- Column `j`'s 32 lanes in slice `τ`: its zero-padded real codes `b` on lanes 0..28, its tuple on 29..31. -/
      def colLanes (b : ℕ → Code) (j τ : ℕ) : Fin 32 → Code :=
        fun l => if h : l.val < 29 then b (29 * τ + l.val) else tuple j ⟨l.val - 29, by have := l.isLt; omega⟩
  definition Pouw.Fp8Atom.H1T.enc (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:54-58):
      /-- `cvt.rn.satfinite.e4m3`: round to nearest even on the E4M3 grid, and clamp to ±448. Zero is `+0`. -/
      def enc (y : ℚ) : Code :=
        if y = 0 then ⟨0, by norm_num⟩
        else if 0 < y then ⟨encPos y, by have := encPos_le y; omega⟩
        else ⟨128 + encPos (-y), by have := encPos_le (-y); omega⟩
  definition Pouw.Fp8Atom.H1T.encPos (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:45-50):
      /-- The code nearest a positive rational `y`, ties to the even code, saturating at `0x7E` (448). With
      `e = max (binade y) (−6)` the grid step is `2^(e − 3)`, and the code is `8·(e + 6)` plus the rounded multiple of the
      step (a subnormal for `e = −6`; a carry into the next binade is the next code). -/
      def encPos (y : ℚ) : ℕ :=
        let e := max (binade y) (-6)
        min 126 (8 * (e + 6) + roundEven (y / 2 ^ (e - 3))).toNat
  definition Pouw.Fp8Atom.H1T.extract (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:86-91):
      /-- The fields `h1t_form_xq` reads (`h1_kernel.py`): real lanes `2i` and `2i + 1` from bits 15 and 31 of `r_i`; tag
      lane 29 from bits 31 and 25..23 of `r17`; tag lanes 30 and 31 from bits 15, 9..7 and 31, 25..23 of `r16`. -/
      def extract (r : RawSlice) : SliceSalt where
        pos l := bitAt (r ⟨l.val / 2, by have := l.isLt; omega⟩) (if l.val % 2 = 0 then 15 else 31)
        neg := pick3 (bitAt (r 17) 31) (bitAt (r 16) 15) (bitAt (r 16) 31)
        man := pick3 (bits3 (r 17) 23) (bits3 (r 16) 7) (bits3 (r 16) 23)
  definition Pouw.Fp8Atom.H1T.floorF (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:98-99):
      /-- `F = max(2^(e(M) − 6), 2^−2)` (`c0 = 6`, `c1 = 10`); `2^−2` at `M = 0`. -/
      def floorF (M : ℚ) : ℚ := if M = 0 then 1 / 4 else max (2 ^ (binade M - 6)) (1 / 4)
  definition Pouw.Fp8Atom.H1T.formReal (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:107-110):
      /-- A real lane with floor `F`, code `x` and sign bit `pos`: `(x1, x2) = (RNE_satfinite(x + s·μ), −s·μ)`. -/
      def formReal (F : ℚ) (x : Code) (pos : Bool) : Code × Code :=
        let s : ℚ := if pos then 1 else -1
        (enc (val x + s * mu F (val x)), enc (-(s * mu F (val x))))
  definition Pouw.Fp8Atom.H1T.formSlice (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:115-121):
      /-- One slice's operands `(x1, x2)`: the real lanes formed with the slice's `F`, and the tag lanes `v` and `−v`. -/
      def formSlice (xs : Fin 29 → Code) (σ : SliceSalt) : (Fin 32 → Code) × (Fin 32 → Code) :=
        let F := floorF (sliceMax xs)
        (fun l => if h : l.val < 29 then (formReal F (xs ⟨l.val, h⟩) (σ.pos ⟨l.val, h⟩)).1
          else enc (tagVal F (σ.neg ⟨l.val - 29, by have := l.isLt; omega⟩) (σ.man ⟨l.val - 29, by have := l.isLt; omega⟩)),
         fun l => if h : l.val < 29 then (formReal F (xs ⟨l.val, h⟩) (σ.pos ⟨l.val, h⟩)).2
          else enc (-tagVal F (σ.neg ⟨l.val - 29, by have := l.isLt; omega⟩) (σ.man ⟨l.val - 29, by have := l.isLt; omega⟩)))
  definition Pouw.Fp8Atom.H1T.freshVal (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:155-156):
      /-- `I_p` as a value. -/
      def freshVal (T : ℕ) (x b : ℕ → Code) (j : ℕ) (σ : ℕ → SliceSalt) (p : ℕ) : ℚ := wordVal (freshWord T x b j σ p)
  definition Pouw.Fp8Atom.H1T.freshWord (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:146-150):
      /-- The fresh-step word at position `p` of a row `x` and a column (`b`, `j`) under the slices' salts `σ`: block 1
      (`x1`) of slice `p` for `p < T`, block 2 (`x2`) of slice `p − T` otherwise. -/
      def freshWord (T : ℕ) (x b : ℕ → Code) (j : ℕ) (σ : ℕ → SliceSalt) (p : ℕ) : ℕ :=
        if p < T then hopperStep 0 (formSlice (realLanes x p) (σ p)).1 (colLanes b j p)
        else hopperStep 0 (formSlice (realLanes x (p - T)) (σ (p - T))).2 (colLanes b j (p - T))
  definition Pouw.Fp8Atom.H1T.mu (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:104-105):
      /-- `μ = max(p/8, F)`. -/
      def mu (F x : ℚ) : ℚ := max (pow2Floor x / 8) F
  definition Pouw.Fp8Atom.H1T.pick3 (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:77-78):
      /-- `a`, `b` or `c` at index 0, 1 or 2. -/
      def pick3 {α : Type} (a b c : α) (i : Fin 3) : α := if i.val = 0 then a else if i.val = 1 then b else c
  definition Pouw.Fp8Atom.H1T.pow2Floor (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:101-102):
      /-- `p = 2^⌊log₂ |x|⌋`, `0` at `x = 0`. -/
      def pow2Floor (x : ℚ) : ℚ := if x = 0 then 0 else 2 ^ binade |x|
  definition Pouw.Fp8Atom.H1T.rawZero (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:65-66):
      /-- The raw words all zero. -/
      def rawZero : RawSlice := fun _ => ⟨0, by norm_num⟩
  definition Pouw.Fp8Atom.H1T.realLanes (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:139-140):
      /-- Real lane `ℓ` of slice `τ` of a zero-padded row: element `29τ + ℓ`. -/
      def realLanes (x : ℕ → Code) (τ : ℕ) : Fin 29 → Code := fun l => x (29 * τ + l.val)
  definition Pouw.Fp8Atom.H1T.runVal (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:158-161):
      /-- The running words: `R_0 = I_0` and `R_(p+1) = RN_f32(R_p + I_(p+1))`. -/
      def runVal (T : ℕ) (x b : ℕ → Code) (j : ℕ) (σ : ℕ → SliceSalt) : ℕ → ℚ
        | 0 => freshVal T x b j σ 0
        | p + 1 => rnAdd (runVal T x b j σ p) (freshVal T x b j σ (p + 1))
  definition Pouw.Fp8Atom.H1T.sliceMax (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:95-96):
      /-- The slice maximum `M`: the largest magnitude over the 29 real lanes. -/
      def sliceMax (xs : Fin 29 → Code) : ℚ := (List.ofFn fun l => |val (xs l)|).foldl max 0
  definition Pouw.Fp8Atom.H1T.tagVal (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:112-113):
      /-- A tag lane's value `v = ±32F·(1 + m/8)`, negative when the sign bit is set. -/
      def tagVal (F : ℚ) (neg : Bool) (m : Fin 8) : ℚ := (if neg then -1 else 1) * (32 * F) * (1 + (m : ℚ) / 8)
  definition Pouw.Fp8Atom.H1T.tuple (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:132-135):
      /-- Column `j`'s tag tuple `(t0, t1, t2)`, on lanes 29, 30 and 31. -/
      def tuple (j : ℕ) : Fin 3 → Code :=
        pick3 (A0 ⟨j % 23, Nat.mod_lt _ (by norm_num)⟩) (A1 ⟨j / 23 % 62, Nat.mod_lt _ (by norm_num)⟩)
          (A1 ⟨j / 1426 % 62, Nat.mod_lt _ (by norm_num)⟩)
  definition Pouw.Fp8Atom.H1T.val (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:42-43):
      /-- A code's value (`0` for the two NaNs, which legal inputs exclude). -/
      def val (c : Code) : ℚ := (decode c).getD 0
  definition Pouw.Fp8Atom.H1T.wordVal (Pouw.Fp8Atom.H1T), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate: new
    now (Pouw/Fp8Atom/H1T.lean:152-153):
      /-- A word's value (`0` if it is not finite, which on legal inputs no H-1T word is). -/
      def wordVal (w : ℕ) : ℚ := (wordQ w).getD 0
  definition Pouw.Fp8Atom.H1T.DistinctLiveH1T (Pouw.Fp8Atom.H1TAssumptions), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TAssumptions.lean:25-28):
      /-- **`DistinctLiveH1T`** (Target A per unit): on every legal unit, the credited words are pairwise distinct functions
      of the unit's salt, and none of them is free. -/
      def DistinctLiveH1T : Prop :=
        ∀ U : Unit, U.Legal → Function.Injective U.word ∧ ∀ c, U.word c ∉ U.free
  definition Pouw.Fp8Atom.H1T.H1TGamma (Pouw.Fp8Atom.H1TGamma), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TGamma.lean:44-51):
      /-- **γ for H-1T** (under `DistinctLiveH1T`; `MH100w` is draft semantics): under `H32`, an `MH100w` program on free
      inputs whose registers include every credited word of legal units costs at least 32 per credited word. -/
      def H1TGamma : Prop :=
        ∀ pr : Prices100, H32 pr → ∀ (N : ℕ) (Us : Fin N → Unit), (∀ u, (Us u).Legal) →
          ∀ (fpSem : ℕ → ℚ → ℚ → ℚ → ℚ) (L : List (MSalt Us → ℚ)) (P : List (Op100 (MSalt Us))),
            (∀ f ∈ L, f ∈ mfree Us) → (∀ o ∈ P, o.WFw pr (mfree Us)) →
            (∀ x : Idx Us, ∃ r ∈ regs100 fpSem P L, ∀ G, r G = mword Us x G) →
            32 * ((∑ u, (Us u).m * (Us u).n * Fintype.card (Pos (Us u).T) : ℕ) : ℚ) ≤ (cost100 pr P : ℚ)
  definition Pouw.Fp8Atom.H1T.H1TUnitsDistinct (Pouw.Fp8Atom.H1TGamma), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TGamma.lean:39-42):
      /-- **Several units** (under `DistinctLiveH1T`): on legal units, the credited words are pairwise distinct functions of
      the joint salt, and none is free. -/
      def H1TUnitsDistinct : Prop :=
        ∀ (N : ℕ) (Us : Fin N → Unit), (∀ u, (Us u).Legal) → Function.Injective (mword Us) ∧ ∀ x, mword Us x ∉ mfree Us
  definition Pouw.Fp8Atom.H1T.Idx (Pouw.Fp8Atom.H1TGamma), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TGamma.lean:28-29):
      /-- A credited word of units `Us`: a unit, and a row, column and position of it. -/
      abbrev Idx {N : ℕ} (Us : Fin N → Unit) : Type := Σ u : Fin N, Fin (Us u).m × Fin (Us u).n × Pos (Us u).T
  definition Pouw.Fp8Atom.H1T.MSalt (Pouw.Fp8Atom.H1TGamma), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TGamma.lean:25-26):
      /-- The joint salt of units `Us`: unit `u`'s salt is coordinate `u`. -/
      abbrev MSalt {N : ℕ} (Us : Fin N → Unit) : Type := (u : Fin N) → (Us u).Salt
  definition Pouw.Fp8Atom.H1T.mfree (Pouw.Fp8Atom.H1TGamma), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TGamma.lean:34-37):
      /-- The free values on the joint salt: the constants and every unit's raw XOF words. -/
      def mfree {N : ℕ} (Us : Fin N → Unit) : Set (MSalt Us → ℚ) :=
        {f | (∃ q : ℚ, f = fun _ => q) ∨
          ∃ (u : Fin N) (i : Fin (Us u).m) (τ : Fin (Us u).T) (ℓ : Fin 18), f = fun G => ((G u i τ ℓ : ℕ) : ℚ)}
  definition Pouw.Fp8Atom.H1T.mword (Pouw.Fp8Atom.H1TGamma), read by Pouw.Fp8Atom.H1T.Proofs.h1tGamma, Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct: new
    now (Pouw/Fp8Atom/H1TGamma.lean:31-32):
      /-- The credited word `x` as a function of the joint salt: unit `x.1`'s word on its own coordinate. -/
      def mword {N : ℕ} (Us : Fin N → Unit) (x : Idx Us) : MSalt Us → ℚ := fun G => (Us x.1).word x.2 (G x.1)
  definition Pouw.Fp8Atom.H1T.H1TChainConformance (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:72-76):
      /-- **The chain**: on at least 31 rows and columns, at every position `p < 2T`, `freshWord` writes the expected
      fresh-step word and `runVal` is the value of the expected running word. -/
      def H1TChainConformance : Prop :=
        31 ≤ rowVectors.length ∧ ∀ v ∈ rowVectors, ∀ p < 2 * v.T,
          freshWord v.T v.xs v.bs v.j v.σ p = v.I.getD p 0 ∧ wordQ (v.R.getD p 0) = some (runVal v.T v.xs v.bs v.j v.σ p)
  definition Pouw.Fp8Atom.H1T.H1TFormTable (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:55-59):
      /-- **The real-lane table**: its keys are every finite code, both signs and every `F` index, and on each of them
      `formReal` gives the expected codes. -/
      def H1TFormTable : Prop :=
        formTable.map (fun v => (v.x, v.pos, v.fi)) = formKeys ∧ ∀ v ∈ formTable,
          (formReal (fOf v.fi) (codeOf v.x) v.pos).1.val = v.x1 ∧ (formReal (fOf v.fi) (codeOf v.x) v.pos).2.val = v.x2
  definition Pouw.Fp8Atom.H1T.H1TNonVacuous (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:102-105):
      /-- **Non-vacuity**: a legal unit with `k = 32,768` and `n = 88,412` exists; it has `T = 1,130` and 4,517 credited
      words per output. -/
      def H1TNonVacuous : Prop :=
        ∃ U : Unit, U.Legal ∧ U.m = 1 ∧ U.k = 32768 ∧ U.n = 88412 ∧ U.T = 1130 ∧ Fintype.card (Pos U.T) = 4517
  definition Pouw.Fp8Atom.H1T.H1TNotRawWord (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:82-85):
      /-- **No credited word is a raw XOF word.** -/
      def H1TNotRawWord : Prop :=
        ∀ (U : Unit) (c : Fin U.m × Fin U.n × Pos U.T) (i : Fin U.m) (τ : Fin U.T) (ℓ : Fin 18),
          U.word c ≠ fun g => ((g i τ ℓ : ℕ) : ℚ)
  definition Pouw.Fp8Atom.H1T.H1TPosCard (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:99-100):
      /-- **`4T − 3` credited words per output**, for `T ≥ 2`. -/
      def H1TPosCard : Prop := ∀ T : ℕ, 2 ≤ T → Fintype.card (Pos T) = 4 * T - 3
  definition Pouw.Fp8Atom.H1T.H1TReadsFields (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:78-80):
      /-- **The words read only the fields**: two salts with the same fields give every credited word the same value. -/
      def H1TReadsFields : Prop :=
        ∀ (U : Unit) (g g' : U.Salt), (∀ i τ, extract (g i τ) = extract (g' i τ)) → ∀ c, U.word c g = U.word c g'
  definition Pouw.Fp8Atom.H1T.H1TSaltConformance (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:68-70):
      /-- **The salt fields**: on at least 74 raw salts, `extract` reads the expected fields. -/
      def H1TSaltConformance : Prop :=
        74 ≤ saltVectors.length ∧ ∀ v ∈ saltVectors, packSalt (extract (rawOf v.r)) = (v.pos, v.neg, v.man)
  definition Pouw.Fp8Atom.H1T.H1TTagTable (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:61-66):
      /-- **The tag table**: its keys are every `F` index, sign and mantissa, and each tag value and its negation encode
      exactly to the expected codes. -/
      def H1TTagTable : Prop :=
        tagTable.map (fun v => (v.fi, v.neg, v.m)) = tagKeys ∧ ∀ v ∈ tagTable,
          (enc (tagVal (fOf v.fi) v.neg (fin8 v.m))).val = v.c1 ∧ (enc (-tagVal (fOf v.fi) v.neg (fin8 v.m))).val = v.c2 ∧
          val (codeOf v.c1) = tagVal (fOf v.fi) v.neg (fin8 v.m) ∧ val (codeOf v.c2) = -tagVal (fOf v.fi) v.neg (fin8 v.m)
  definition Pouw.Fp8Atom.H1T.H1TTupleInjective (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:87-88):
      /-- **The tuples are distinct** on the 88,412 columns of a unit. -/
      def H1TTupleInjective : Prop := ∀ j j' : ℕ, j < 88412 → j' < 88412 → tuple j = tuple j' → j = j'
  definition Pouw.Fp8Atom.H1T.H1TTupleWrap (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:90-91):
      /-- **The tuples repeat** after 88,412 columns. -/
      def H1TTupleWrap : Prop := ∀ j : ℕ, tuple (j + 88412) = tuple j
  definition Pouw.Fp8Atom.H1T.H1TWrapDuplicate (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:93-97):
      /-- **Columns 88,412 apart collide**: in one unit, two columns 88,412 apart with the same real codes have the same
      credited words on every salt. -/
      def H1TWrapDuplicate : Prop :=
        ∀ (U : Unit) (j j' : Fin U.n), j'.val = j.val + 88412 → (∀ r, U.b r j = U.b r j') →
          ∀ (i : Fin U.m) (a : Pos U.T), U.word (i, j, a) = U.word (i, j', a)
  definition Pouw.Fp8Atom.H1T.HalfOfInvolution (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:113-117):
      /-- **Half of a finite set**: if an involution `ψ` maps every point where `P` holds to one where it fails, `P` holds on
      at most half of the points. -/
      def HalfOfInvolution : Prop :=
        ∀ (α : Type) [Fintype α] (ψ : α → α) (P : α → Bool), Function.Involutive ψ → (∀ a, P a = true → P (ψ a) = false) →
          2 * (Finset.univ.filter fun a => P a = true).card ≤ Fintype.card α
  definition Pouw.Fp8Atom.H1T.RnAddMovesHalf (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:110-111):
      /-- **Movement past half an ulp**: a summand of more than half an ulp of a nonzero representable `r` changes `r`. -/
      def RnAddMovesHalf : Prop := ∀ r i : ℚ, Representable r → r ≠ 0 → ulp r < 2 * |i| → rnAdd r i ≠ r
  definition Pouw.Fp8Atom.H1T.RnErr (Pouw.Fp8Atom.H1TPinned), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous, Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord, Pouw.Fp8Atom.H1T.Proofs.h1tPosCard, Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable, Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective, Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap, Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate, Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution, Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf, Pouw.Fp8Atom.H1T.Proofs.rnErr: new
    now (Pouw/Fp8Atom/H1TPinned.lean:107-108):
      /-- **Rounding error**: `rn y` is within half an ulp of `y`. -/
      def RnErr : Prop := ∀ y : ℚ, |rn y - y| ≤ ulp y / 2
  definition Pouw.Fp8Atom.H1T.FormVec (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:39-45):
      /-- A real-lane vector. -/
      structure FormVec where
        x : ℕ
        pos : Bool
        fi : ℕ
        x1 : ℕ
        x2 : ℕ
  definition Pouw.Fp8Atom.H1T.FormVec.fi (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:43-43):
        fi : ℕ
  definition Pouw.Fp8Atom.H1T.FormVec.pos (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:42-42):
        pos : Bool
  definition Pouw.Fp8Atom.H1T.FormVec.x (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:41-41):
        x : ℕ
  definition Pouw.Fp8Atom.H1T.FormVec.x1 (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:44-44):
        x1 : ℕ
  definition Pouw.Fp8Atom.H1T.FormVec.x2 (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:45-45):
        x2 : ℕ
  definition Pouw.Fp8Atom.H1T.RowVec (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:90-98):
      /-- A full-row vector. -/
      structure RowVec where
        T : ℕ
        j : ℕ
        x : ℕ
        b : ℕ
        r : List ℕ
        I : List ℕ
        R : List ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.I (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:97-97):
        I : List ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.R (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:98-98):
        R : List ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.T (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:92-92):
        T : ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.b (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:95-95):
        b : ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.bs (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:103-104):
      /-- The column's real codes. -/
      def RowVec.bs (v : RowVec) : ℕ → Code := fun i => codeOf (v.b >>> (8 * i))
  definition Pouw.Fp8Atom.H1T.RowVec.j (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:93-93):
        j : ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.r (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:96-96):
        r : List ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.x (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:94-94):
        x : ℕ
  definition Pouw.Fp8Atom.H1T.RowVec.xs (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:100-101):
      /-- The row. -/
      def RowVec.xs (v : RowVec) : ℕ → Code := fun i => codeOf (v.x >>> (8 * i))
  definition Pouw.Fp8Atom.H1T.RowVec.σ (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:106-107):
      /-- The salt fields per slice. -/
      def RowVec.σ (v : RowVec) : ℕ → SliceSalt := fun τ => extract (rawOf (v.r.getD τ 0))
  definition Pouw.Fp8Atom.H1T.SaltVec (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:74-79):
      /-- A salt vector. -/
      structure SaltVec where
        r : ℕ
        pos : ℕ
        neg : ℕ
        man : ℕ
  definition Pouw.Fp8Atom.H1T.SaltVec.man (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:79-79):
        man : ℕ
  definition Pouw.Fp8Atom.H1T.SaltVec.neg (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:78-78):
        neg : ℕ
  definition Pouw.Fp8Atom.H1T.SaltVec.pos (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:77-77):
        pos : ℕ
  definition Pouw.Fp8Atom.H1T.SaltVec.r (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:76-76):
        r : ℕ
  definition Pouw.Fp8Atom.H1T.TagVec (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:57-63):
      /-- A tag vector. -/
      structure TagVec where
        fi : ℕ
        neg : Bool
        m : ℕ
        c1 : ℕ
        c2 : ℕ
  definition Pouw.Fp8Atom.H1T.TagVec.c1 (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:62-62):
        c1 : ℕ
  definition Pouw.Fp8Atom.H1T.TagVec.c2 (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:63-63):
        c2 : ℕ
  definition Pouw.Fp8Atom.H1T.TagVec.fi (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:59-59):
        fi : ℕ
  definition Pouw.Fp8Atom.H1T.TagVec.m (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:61-61):
        m : ℕ
  definition Pouw.Fp8Atom.H1T.TagVec.neg (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:60-60):
        neg : Bool
  definition Pouw.Fp8Atom.H1T.codeOf (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:27-28):
      /-- A natural number as a code, modulo 256. -/
      def codeOf (c : ℕ) : Code := ⟨c % 256, Nat.mod_lt _ (by norm_num)⟩
  definition Pouw.Fp8Atom.H1T.fOf (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:30-31):
      /-- `F = 2^(fi − 2)`. -/
      def fOf (fi : ℕ) : ℚ := 2 ^ ((fi : ℤ) - 2)
  definition Pouw.Fp8Atom.H1T.fin8 (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:33-34):
      /-- A natural number as a mantissa field, modulo 8. -/
      def fin8 (m : ℕ) : Fin 8 := ⟨m % 8, Nat.mod_lt _ (by norm_num)⟩
  definition Pouw.Fp8Atom.H1T.formKeys (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:52-55):
      /-- Every finite code, both signs and every `F` index `0..4`. -/
      def formKeys : List (ℕ × Bool × ℕ) :=
        ((List.range 256).filter fun c => (codeOf c).isNaN == false).flatMap fun x =>
          [false, true].flatMap fun pos => (List.range 5).map fun fi => (x, pos, fi)
  definition Pouw.Fp8Atom.H1T.packSalt (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:81-85):
      /-- The fields as three numbers: real-lane signs (bit `ℓ`), tag signs (bit `i`), tag mantissas (`8^i · m_i`). -/
      def packSalt (σ : SliceSalt) : ℕ × ℕ × ℕ :=
        ((List.finRange 29).foldr (fun l s => (if σ.pos l then 2 ^ l.val else 0) + s) 0,
         (List.finRange 3).foldr (fun i s => (if σ.neg i then 2 ^ i.val else 0) + s) 0,
         (List.finRange 3).foldr (fun i s => (σ.man i).val * 8 ^ i.val + s) 0)
  definition Pouw.Fp8Atom.H1T.rawOf (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:36-37):
      /-- 18 raw XOF words packed in `r` (word `ℓ` is bits `32ℓ..32ℓ+31`). -/
      def rawOf (r : ℕ) : RawSlice := fun ℓ => ⟨(r >>> (32 * ℓ.val)) % 2 ^ 32, Nat.mod_lt _ (by norm_num)⟩
  definition Pouw.Fp8Atom.H1T.tagKeys (Pouw.Fp8Atom.H1TVec), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVec.lean:70-72):
      /-- Every `F` index `0..4`, sign and mantissa. -/
      def tagKeys : List (ℕ × Bool × ℕ) :=
        (List.range 5).flatMap fun fi => [false, true].flatMap fun neg => (List.range 8).map fun m => (fi, neg, m)
  definition Pouw.Fp8Atom.H1T.Vectors.form0 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:7-108):
      /-- `formReal` on every finite code, both signs and every `F`, part 0. -/
      def form0 : List FormVec := [
        ⟨0, false, 0, 168, 40⟩,
        ⟨0, false, 1, 176, 48⟩,
        ⟨0, false, 2, 184, 56⟩,
        ⟨0, false, 3, 192, 64⟩,
        ⟨0, false, 4, 200, 72⟩,
        ⟨0, true, 0, 40, 168⟩,
        ⟨0, true, 1, 48, 176⟩,
        ⟨0, true, 2, 56, 184⟩,
        ⟨0, true, 3, 64, 192⟩,
        ⟨0, true, 4, 72, 200⟩,
        ⟨1, false, 0, 168, 40⟩,
        ⟨1, false, 1, 176, 48⟩,
        ⟨1, false, 2, 184, 56⟩,
        ⟨1, false, 3, 192, 64⟩,
        ⟨1, false, 4, 200, 72⟩,
        ⟨1, true, 0, 40, 168⟩,
        ⟨1, true, 1, 48, 176⟩,
        ⟨1, true, 2, 56, 184⟩,
        ⟨1, true, 3, 64, 192⟩,
        ⟨1, true, 4, 72, 200⟩,
        ⟨2, false, 0, 168, 40⟩,
        ⟨2, false, 1, 176, 48⟩,
        ⟨2, false, 2, 184, 56⟩,
        ⟨2, false, 3, 192, 64⟩,
        ⟨2, false, 4, 200, 72⟩,
        ⟨2, true, 0, 40, 168⟩,
        ⟨2, true, 1, 48, 176⟩,
        ⟨2, true, 2, 56, 184⟩,
        ⟨2, true, 3, 64, 192⟩,
        ⟨2, true, 4, 72, 200⟩,
        ⟨3, false, 0, 168, 40⟩,
        ⟨3, false, 1, 176, 48⟩,
        ⟨3, false, 2, 184, 56⟩,
        ⟨3, false, 3, 192, 64⟩,
        ⟨3, false, 4, 200, 72⟩,
        ⟨3, true, 0, 40, 168⟩,
        ⟨3, true, 1, 48, 176⟩,
        ⟨3, true, 2, 56, 184⟩,
        ⟨3, true, 3, 64, 192⟩,
        ⟨3, true, 4, 72, 200⟩,
        ⟨4, false, 0, 168, 40⟩,
        ⟨4, false, 1, 176, 48⟩,
        ⟨4, false, 2, 184, 56⟩,
        ⟨4, false, 3, 192, 64⟩,
        ⟨4, false, 4, 200, 72⟩,
        ⟨4, true, 0, 40, 168⟩,
        ⟨4, true, 1, 48, 176⟩,
        ⟨4, true, 2, 56, 184⟩,
        ⟨4, true, 3, 64, 192⟩,
        ⟨4, true, 4, 72, 200⟩,
        ⟨5, false, 0, 167, 40⟩,
        ⟨5, false, 1, 176, 48⟩,
        ⟨5, false, 2, 184, 56⟩,
        ⟨5, false, 3, 192, 64⟩,
        ⟨5, false, 4, 200, 72⟩,
        ⟨5, true, 0, 40, 168⟩,
        ⟨5, true, 1, 48, 176⟩,
        ⟨5, true, 2, 56, 184⟩,
        ⟨5, true, 3, 64, 192⟩,
        ⟨5, true, 4, 72, 200⟩,
        ⟨6, false, 0, 167, 40⟩,
        ⟨6, false, 1, 176, 48⟩,
        ⟨6, false, 2, 184, 56⟩,
        ⟨6, false, 3, 192, 64⟩,
        ⟨6, false, 4, 200, 72⟩,
        ⟨6, true, 0, 40, 168⟩,
        ⟨6, true, 1, 48, 176⟩,
        ⟨6, true, 2, 56, 184⟩,
        ⟨6, true, 3, 64, 192⟩,
        ⟨6, true, 4, 72, 200⟩,
        ⟨7, false, 0, 167, 40⟩,
        ⟨7, false, 1, 176, 48⟩,
        ⟨7, false, 2, 184, 56⟩,
        ⟨7, false, 3, 192, 64⟩,
        ⟨7, false, 4, 200, 72⟩,
        ⟨7, true, 0, 40, 168⟩,
        ⟨7, true, 1, 48, 176⟩,
        ⟨7, true, 2, 56, 184⟩,
        ⟨7, true, 3, 64, 192⟩,
        ⟨7, true, 4, 72, 200⟩,
        ⟨8, false, 0, 167, 40⟩,
        ⟨8, false, 1, 176, 48⟩,
        ⟨8, false, 2, 184, 56⟩,
        ⟨8, false, 3, 192, 64⟩,
        ⟨8, false, 4, 200, 72⟩,
        ⟨8, true, 0, 40, 168⟩,
        ⟨8, true, 1, 48, 176⟩,
        ⟨8, true, 2, 56, 184⟩,
        ⟨8, true, 3, 64, 192⟩,
        ⟨8, true, 4, 72, 200⟩,
        ⟨9, false, 0, 167, 40⟩,
        ⟨9, false, 1, 175, 48⟩,
        ⟨9, false, 2, 184, 56⟩,
        ⟨9, false, 3, 192, 64⟩,
        ⟨9, false, 4, 200, 72⟩,
        ⟨9, true, 0, 41, 168⟩,
        ⟨9, true, 1, 48, 176⟩,
        ⟨9, true, 2, 56, 184⟩,
        ⟨9, true, 3, 64, 192⟩,
        ⟨9, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form1 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:110-211):
      /-- `formReal` on every finite code, both signs and every `F`, part 1. -/
      def form1 : List FormVec := [
        ⟨10, false, 0, 167, 40⟩,
        ⟨10, false, 1, 175, 48⟩,
        ⟨10, false, 2, 184, 56⟩,
        ⟨10, false, 3, 192, 64⟩,
        ⟨10, false, 4, 200, 72⟩,
        ⟨10, true, 0, 41, 168⟩,
        ⟨10, true, 1, 48, 176⟩,
        ⟨10, true, 2, 56, 184⟩,
        ⟨10, true, 3, 64, 192⟩,
        ⟨10, true, 4, 72, 200⟩,
        ⟨11, false, 0, 167, 40⟩,
        ⟨11, false, 1, 175, 48⟩,
        ⟨11, false, 2, 184, 56⟩,
        ⟨11, false, 3, 192, 64⟩,
        ⟨11, false, 4, 200, 72⟩,
        ⟨11, true, 0, 41, 168⟩,
        ⟨11, true, 1, 48, 176⟩,
        ⟨11, true, 2, 56, 184⟩,
        ⟨11, true, 3, 64, 192⟩,
        ⟨11, true, 4, 72, 200⟩,
        ⟨12, false, 0, 166, 40⟩,
        ⟨12, false, 1, 175, 48⟩,
        ⟨12, false, 2, 184, 56⟩,
        ⟨12, false, 3, 192, 64⟩,
        ⟨12, false, 4, 200, 72⟩,
        ⟨12, true, 0, 41, 168⟩,
        ⟨12, true, 1, 48, 176⟩,
        ⟨12, true, 2, 56, 184⟩,
        ⟨12, true, 3, 64, 192⟩,
        ⟨12, true, 4, 72, 200⟩,
        ⟨13, false, 0, 166, 40⟩,
        ⟨13, false, 1, 175, 48⟩,
        ⟨13, false, 2, 184, 56⟩,
        ⟨13, false, 3, 192, 64⟩,
        ⟨13, false, 4, 200, 72⟩,
        ⟨13, true, 0, 41, 168⟩,
        ⟨13, true, 1, 48, 176⟩,
        ⟨13, true, 2, 56, 184⟩,
        ⟨13, true, 3, 64, 192⟩,
        ⟨13, true, 4, 72, 200⟩,
        ⟨14, false, 0, 166, 40⟩,
        ⟨14, false, 1, 175, 48⟩,
        ⟨14, false, 2, 184, 56⟩,
        ⟨14, false, 3, 192, 64⟩,
        ⟨14, false, 4, 200, 72⟩,
        ⟨14, true, 0, 41, 168⟩,
        ⟨14, true, 1, 48, 176⟩,
        ⟨14, true, 2, 56, 184⟩,
        ⟨14, true, 3, 64, 192⟩,
        ⟨14, true, 4, 72, 200⟩,
        ⟨15, false, 0, 166, 40⟩,
        ⟨15, false, 1, 175, 48⟩,
        ⟨15, false, 2, 184, 56⟩,
        ⟨15, false, 3, 192, 64⟩,
        ⟨15, false, 4, 200, 72⟩,
        ⟨15, true, 0, 41, 168⟩,
        ⟨15, true, 1, 48, 176⟩,
        ⟨15, true, 2, 56, 184⟩,
        ⟨15, true, 3, 64, 192⟩,
        ⟨15, true, 4, 72, 200⟩,
        ⟨16, false, 0, 166, 40⟩,
        ⟨16, false, 1, 175, 48⟩,
        ⟨16, false, 2, 184, 56⟩,
        ⟨16, false, 3, 192, 64⟩,
        ⟨16, false, 4, 200, 72⟩,
        ⟨16, true, 0, 41, 168⟩,
        ⟨16, true, 1, 48, 176⟩,
        ⟨16, true, 2, 56, 184⟩,
        ⟨16, true, 3, 64, 192⟩,
        ⟨16, true, 4, 72, 200⟩,
        ⟨17, false, 0, 166, 40⟩,
        ⟨17, false, 1, 175, 48⟩,
        ⟨17, false, 2, 183, 56⟩,
        ⟨17, false, 3, 192, 64⟩,
        ⟨17, false, 4, 200, 72⟩,
        ⟨17, true, 0, 41, 168⟩,
        ⟨17, true, 1, 49, 176⟩,
        ⟨17, true, 2, 56, 184⟩,
        ⟨17, true, 3, 64, 192⟩,
        ⟨17, true, 4, 72, 200⟩,
        ⟨18, false, 0, 166, 40⟩,
        ⟨18, false, 1, 175, 48⟩,
        ⟨18, false, 2, 183, 56⟩,
        ⟨18, false, 3, 192, 64⟩,
        ⟨18, false, 4, 200, 72⟩,
        ⟨18, true, 0, 41, 168⟩,
        ⟨18, true, 1, 49, 176⟩,
        ⟨18, true, 2, 56, 184⟩,
        ⟨18, true, 3, 64, 192⟩,
        ⟨18, true, 4, 72, 200⟩,
        ⟨19, false, 0, 165, 40⟩,
        ⟨19, false, 1, 175, 48⟩,
        ⟨19, false, 2, 183, 56⟩,
        ⟨19, false, 3, 192, 64⟩,
        ⟨19, false, 4, 200, 72⟩,
        ⟨19, true, 0, 41, 168⟩,
        ⟨19, true, 1, 49, 176⟩,
        ⟨19, true, 2, 56, 184⟩,
        ⟨19, true, 3, 64, 192⟩,
        ⟨19, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form10 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1037-1138):
      /-- `formReal` on every finite code, both signs and every `F`, part 10. -/
      def form10 : List FormVec := [
        ⟨100, false, 0, 99, 72⟩,
        ⟨100, false, 1, 99, 72⟩,
        ⟨100, false, 2, 99, 72⟩,
        ⟨100, false, 3, 99, 72⟩,
        ⟨100, false, 4, 99, 72⟩,
        ⟨100, true, 0, 101, 200⟩,
        ⟨100, true, 1, 101, 200⟩,
        ⟨100, true, 2, 101, 200⟩,
        ⟨100, true, 3, 101, 200⟩,
        ⟨100, true, 4, 101, 200⟩,
        ⟨101, false, 0, 100, 72⟩,
        ⟨101, false, 1, 100, 72⟩,
        ⟨101, false, 2, 100, 72⟩,
        ⟨101, false, 3, 100, 72⟩,
        ⟨101, false, 4, 100, 72⟩,
        ⟨101, true, 0, 102, 200⟩,
        ⟨101, true, 1, 102, 200⟩,
        ⟨101, true, 2, 102, 200⟩,
        ⟨101, true, 3, 102, 200⟩,
        ⟨101, true, 4, 102, 200⟩,
        ⟨102, false, 0, 101, 72⟩,
        ⟨102, false, 1, 101, 72⟩,
        ⟨102, false, 2, 101, 72⟩,
        ⟨102, false, 3, 101, 72⟩,
        ⟨102, false, 4, 101, 72⟩,
        ⟨102, true, 0, 103, 200⟩,
        ⟨102, true, 1, 103, 200⟩,
        ⟨102, true, 2, 103, 200⟩,
        ⟨102, true, 3, 103, 200⟩,
        ⟨102, true, 4, 103, 200⟩,
        ⟨103, false, 0, 102, 72⟩,
        ⟨103, false, 1, 102, 72⟩,
        ⟨103, false, 2, 102, 72⟩,
        ⟨103, false, 3, 102, 72⟩,
        ⟨103, false, 4, 102, 72⟩,
        ⟨103, true, 0, 104, 200⟩,
        ⟨103, true, 1, 104, 200⟩,
        ⟨103, true, 2, 104, 200⟩,
        ⟨103, true, 3, 104, 200⟩,
        ⟨103, true, 4, 104, 200⟩,
        ⟨104, false, 0, 102, 80⟩,
        ⟨104, false, 1, 102, 80⟩,
        ⟨104, false, 2, 102, 80⟩,
        ⟨104, false, 3, 102, 80⟩,
        ⟨104, false, 4, 102, 80⟩,
        ⟨104, true, 0, 105, 208⟩,
        ⟨104, true, 1, 105, 208⟩,
        ⟨104, true, 2, 105, 208⟩,
        ⟨104, true, 3, 105, 208⟩,
        ⟨104, true, 4, 105, 208⟩,
        ⟨105, false, 0, 104, 80⟩,
        ⟨105, false, 1, 104, 80⟩,
        ⟨105, false, 2, 104, 80⟩,
        ⟨105, false, 3, 104, 80⟩,
        ⟨105, false, 4, 104, 80⟩,
        ⟨105, true, 0, 106, 208⟩,
        ⟨105, true, 1, 106, 208⟩,
        ⟨105, true, 2, 106, 208⟩,
        ⟨105, true, 3, 106, 208⟩,
        ⟨105, true, 4, 106, 208⟩,
        ⟨106, false, 0, 105, 80⟩,
        ⟨106, false, 1, 105, 80⟩,
        ⟨106, false, 2, 105, 80⟩,
        ⟨106, false, 3, 105, 80⟩,
        ⟨106, false, 4, 105, 80⟩,
        ⟨106, true, 0, 107, 208⟩,
        ⟨106, true, 1, 107, 208⟩,
        ⟨106, true, 2, 107, 208⟩,
        ⟨106, true, 3, 107, 208⟩,
        ⟨106, true, 4, 107, 208⟩,
        ⟨107, false, 0, 106, 80⟩,
        ⟨107, false, 1, 106, 80⟩,
        ⟨107, false, 2, 106, 80⟩,
        ⟨107, false, 3, 106, 80⟩,
        ⟨107, false, 4, 106, 80⟩,
        ⟨107, true, 0, 108, 208⟩,
        ⟨107, true, 1, 108, 208⟩,
        ⟨107, true, 2, 108, 208⟩,
        ⟨107, true, 3, 108, 208⟩,
        ⟨107, true, 4, 108, 208⟩,
        ⟨108, false, 0, 107, 80⟩,
        ⟨108, false, 1, 107, 80⟩,
        ⟨108, false, 2, 107, 80⟩,
        ⟨108, false, 3, 107, 80⟩,
        ⟨108, false, 4, 107, 80⟩,
        ⟨108, true, 0, 109, 208⟩,
        ⟨108, true, 1, 109, 208⟩,
        ⟨108, true, 2, 109, 208⟩,
        ⟨108, true, 3, 109, 208⟩,
        ⟨108, true, 4, 109, 208⟩,
        ⟨109, false, 0, 108, 80⟩,
        ⟨109, false, 1, 108, 80⟩,
        ⟨109, false, 2, 108, 80⟩,
        ⟨109, false, 3, 108, 80⟩,
        ⟨109, false, 4, 108, 80⟩,
        ⟨109, true, 0, 110, 208⟩,
        ⟨109, true, 1, 110, 208⟩,
        ⟨109, true, 2, 110, 208⟩,
        ⟨109, true, 3, 110, 208⟩,
        ⟨109, true, 4, 110, 208⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form11 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1140-1241):
      /-- `formReal` on every finite code, both signs and every `F`, part 11. -/
      def form11 : List FormVec := [
        ⟨110, false, 0, 109, 80⟩,
        ⟨110, false, 1, 109, 80⟩,
        ⟨110, false, 2, 109, 80⟩,
        ⟨110, false, 3, 109, 80⟩,
        ⟨110, false, 4, 109, 80⟩,
        ⟨110, true, 0, 111, 208⟩,
        ⟨110, true, 1, 111, 208⟩,
        ⟨110, true, 2, 111, 208⟩,
        ⟨110, true, 3, 111, 208⟩,
        ⟨110, true, 4, 111, 208⟩,
        ⟨111, false, 0, 110, 80⟩,
        ⟨111, false, 1, 110, 80⟩,
        ⟨111, false, 2, 110, 80⟩,
        ⟨111, false, 3, 110, 80⟩,
        ⟨111, false, 4, 110, 80⟩,
        ⟨111, true, 0, 112, 208⟩,
        ⟨111, true, 1, 112, 208⟩,
        ⟨111, true, 2, 112, 208⟩,
        ⟨111, true, 3, 112, 208⟩,
        ⟨111, true, 4, 112, 208⟩,
        ⟨112, false, 0, 110, 88⟩,
        ⟨112, false, 1, 110, 88⟩,
        ⟨112, false, 2, 110, 88⟩,
        ⟨112, false, 3, 110, 88⟩,
        ⟨112, false, 4, 110, 88⟩,
        ⟨112, true, 0, 113, 216⟩,
        ⟨112, true, 1, 113, 216⟩,
        ⟨112, true, 2, 113, 216⟩,
        ⟨112, true, 3, 113, 216⟩,
        ⟨112, true, 4, 113, 216⟩,
        ⟨113, false, 0, 112, 88⟩,
        ⟨113, false, 1, 112, 88⟩,
        ⟨113, false, 2, 112, 88⟩,
        ⟨113, false, 3, 112, 88⟩,
        ⟨113, false, 4, 112, 88⟩,
        ⟨113, true, 0, 114, 216⟩,
        ⟨113, true, 1, 114, 216⟩,
        ⟨113, true, 2, 114, 216⟩,
        ⟨113, true, 3, 114, 216⟩,
        ⟨113, true, 4, 114, 216⟩,
        ⟨114, false, 0, 113, 88⟩,
        ⟨114, false, 1, 113, 88⟩,
        ⟨114, false, 2, 113, 88⟩,
        ⟨114, false, 3, 113, 88⟩,
        ⟨114, false, 4, 113, 88⟩,
        ⟨114, true, 0, 115, 216⟩,
        ⟨114, true, 1, 115, 216⟩,
        ⟨114, true, 2, 115, 216⟩,
        ⟨114, true, 3, 115, 216⟩,
        ⟨114, true, 4, 115, 216⟩,
        ⟨115, false, 0, 114, 88⟩,
        ⟨115, false, 1, 114, 88⟩,
        ⟨115, false, 2, 114, 88⟩,
        ⟨115, false, 3, 114, 88⟩,
        ⟨115, false, 4, 114, 88⟩,
        ⟨115, true, 0, 116, 216⟩,
        ⟨115, true, 1, 116, 216⟩,
        ⟨115, true, 2, 116, 216⟩,
        ⟨115, true, 3, 116, 216⟩,
        ⟨115, true, 4, 116, 216⟩,
        ⟨116, false, 0, 115, 88⟩,
        ⟨116, false, 1, 115, 88⟩,
        ⟨116, false, 2, 115, 88⟩,
        ⟨116, false, 3, 115, 88⟩,
        ⟨116, false, 4, 115, 88⟩,
        ⟨116, true, 0, 117, 216⟩,
        ⟨116, true, 1, 117, 216⟩,
        ⟨116, true, 2, 117, 216⟩,
        ⟨116, true, 3, 117, 216⟩,
        ⟨116, true, 4, 117, 216⟩,
        ⟨117, false, 0, 116, 88⟩,
        ⟨117, false, 1, 116, 88⟩,
        ⟨117, false, 2, 116, 88⟩,
        ⟨117, false, 3, 116, 88⟩,
        ⟨117, false, 4, 116, 88⟩,
        ⟨117, true, 0, 118, 216⟩,
        ⟨117, true, 1, 118, 216⟩,
        ⟨117, true, 2, 118, 216⟩,
        ⟨117, true, 3, 118, 216⟩,
        ⟨117, true, 4, 118, 216⟩,
        ⟨118, false, 0, 117, 88⟩,
        ⟨118, false, 1, 117, 88⟩,
        ⟨118, false, 2, 117, 88⟩,
        ⟨118, false, 3, 117, 88⟩,
        ⟨118, false, 4, 117, 88⟩,
        ⟨118, true, 0, 119, 216⟩,
        ⟨118, true, 1, 119, 216⟩,
        ⟨118, true, 2, 119, 216⟩,
        ⟨118, true, 3, 119, 216⟩,
        ⟨118, true, 4, 119, 216⟩,
        ⟨119, false, 0, 118, 88⟩,
        ⟨119, false, 1, 118, 88⟩,
        ⟨119, false, 2, 118, 88⟩,
        ⟨119, false, 3, 118, 88⟩,
        ⟨119, false, 4, 118, 88⟩,
        ⟨119, true, 0, 120, 216⟩,
        ⟨119, true, 1, 120, 216⟩,
        ⟨119, true, 2, 120, 216⟩,
        ⟨119, true, 3, 120, 216⟩,
        ⟨119, true, 4, 120, 216⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form12 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1243-1344):
      /-- `formReal` on every finite code, both signs and every `F`, part 12. -/
      def form12 : List FormVec := [
        ⟨120, false, 0, 118, 96⟩,
        ⟨120, false, 1, 118, 96⟩,
        ⟨120, false, 2, 118, 96⟩,
        ⟨120, false, 3, 118, 96⟩,
        ⟨120, false, 4, 118, 96⟩,
        ⟨120, true, 0, 121, 224⟩,
        ⟨120, true, 1, 121, 224⟩,
        ⟨120, true, 2, 121, 224⟩,
        ⟨120, true, 3, 121, 224⟩,
        ⟨120, true, 4, 121, 224⟩,
        ⟨121, false, 0, 120, 96⟩,
        ⟨121, false, 1, 120, 96⟩,
        ⟨121, false, 2, 120, 96⟩,
        ⟨121, false, 3, 120, 96⟩,
        ⟨121, false, 4, 120, 96⟩,
        ⟨121, true, 0, 122, 224⟩,
        ⟨121, true, 1, 122, 224⟩,
        ⟨121, true, 2, 122, 224⟩,
        ⟨121, true, 3, 122, 224⟩,
        ⟨121, true, 4, 122, 224⟩,
        ⟨122, false, 0, 121, 96⟩,
        ⟨122, false, 1, 121, 96⟩,
        ⟨122, false, 2, 121, 96⟩,
        ⟨122, false, 3, 121, 96⟩,
        ⟨122, false, 4, 121, 96⟩,
        ⟨122, true, 0, 123, 224⟩,
        ⟨122, true, 1, 123, 224⟩,
        ⟨122, true, 2, 123, 224⟩,
        ⟨122, true, 3, 123, 224⟩,
        ⟨122, true, 4, 123, 224⟩,
        ⟨123, false, 0, 122, 96⟩,
        ⟨123, false, 1, 122, 96⟩,
        ⟨123, false, 2, 122, 96⟩,
        ⟨123, false, 3, 122, 96⟩,
        ⟨123, false, 4, 122, 96⟩,
        ⟨123, true, 0, 124, 224⟩,
        ⟨123, true, 1, 124, 224⟩,
        ⟨123, true, 2, 124, 224⟩,
        ⟨123, true, 3, 124, 224⟩,
        ⟨123, true, 4, 124, 224⟩,
        ⟨124, false, 0, 123, 96⟩,
        ⟨124, false, 1, 123, 96⟩,
        ⟨124, false, 2, 123, 96⟩,
        ⟨124, false, 3, 123, 96⟩,
        ⟨124, false, 4, 123, 96⟩,
        ⟨124, true, 0, 125, 224⟩,
        ⟨124, true, 1, 125, 224⟩,
        ⟨124, true, 2, 125, 224⟩,
        ⟨124, true, 3, 125, 224⟩,
        ⟨124, true, 4, 125, 224⟩,
        ⟨125, false, 0, 124, 96⟩,
        ⟨125, false, 1, 124, 96⟩,
        ⟨125, false, 2, 124, 96⟩,
        ⟨125, false, 3, 124, 96⟩,
        ⟨125, false, 4, 124, 96⟩,
        ⟨125, true, 0, 126, 224⟩,
        ⟨125, true, 1, 126, 224⟩,
        ⟨125, true, 2, 126, 224⟩,
        ⟨125, true, 3, 126, 224⟩,
        ⟨125, true, 4, 126, 224⟩,
        ⟨126, false, 0, 125, 96⟩,
        ⟨126, false, 1, 125, 96⟩,
        ⟨126, false, 2, 125, 96⟩,
        ⟨126, false, 3, 125, 96⟩,
        ⟨126, false, 4, 125, 96⟩,
        ⟨126, true, 0, 126, 224⟩,
        ⟨126, true, 1, 126, 224⟩,
        ⟨126, true, 2, 126, 224⟩,
        ⟨126, true, 3, 126, 224⟩,
        ⟨126, true, 4, 126, 224⟩,
        ⟨128, false, 0, 168, 40⟩,
        ⟨128, false, 1, 176, 48⟩,
        ⟨128, false, 2, 184, 56⟩,
        ⟨128, false, 3, 192, 64⟩,
        ⟨128, false, 4, 200, 72⟩,
        ⟨128, true, 0, 40, 168⟩,
        ⟨128, true, 1, 48, 176⟩,
        ⟨128, true, 2, 56, 184⟩,
        ⟨128, true, 3, 64, 192⟩,
        ⟨128, true, 4, 72, 200⟩,
        ⟨129, false, 0, 168, 40⟩,
        ⟨129, false, 1, 176, 48⟩,
        ⟨129, false, 2, 184, 56⟩,
        ⟨129, false, 3, 192, 64⟩,
        ⟨129, false, 4, 200, 72⟩,
        ⟨129, true, 0, 40, 168⟩,
        ⟨129, true, 1, 48, 176⟩,
        ⟨129, true, 2, 56, 184⟩,
        ⟨129, true, 3, 64, 192⟩,
        ⟨129, true, 4, 72, 200⟩,
        ⟨130, false, 0, 168, 40⟩,
        ⟨130, false, 1, 176, 48⟩,
        ⟨130, false, 2, 184, 56⟩,
        ⟨130, false, 3, 192, 64⟩,
        ⟨130, false, 4, 200, 72⟩,
        ⟨130, true, 0, 40, 168⟩,
        ⟨130, true, 1, 48, 176⟩,
        ⟨130, true, 2, 56, 184⟩,
        ⟨130, true, 3, 64, 192⟩,
        ⟨130, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form13 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1346-1447):
      /-- `formReal` on every finite code, both signs and every `F`, part 13. -/
      def form13 : List FormVec := [
        ⟨131, false, 0, 168, 40⟩,
        ⟨131, false, 1, 176, 48⟩,
        ⟨131, false, 2, 184, 56⟩,
        ⟨131, false, 3, 192, 64⟩,
        ⟨131, false, 4, 200, 72⟩,
        ⟨131, true, 0, 40, 168⟩,
        ⟨131, true, 1, 48, 176⟩,
        ⟨131, true, 2, 56, 184⟩,
        ⟨131, true, 3, 64, 192⟩,
        ⟨131, true, 4, 72, 200⟩,
        ⟨132, false, 0, 168, 40⟩,
        ⟨132, false, 1, 176, 48⟩,
        ⟨132, false, 2, 184, 56⟩,
        ⟨132, false, 3, 192, 64⟩,
        ⟨132, false, 4, 200, 72⟩,
        ⟨132, true, 0, 40, 168⟩,
        ⟨132, true, 1, 48, 176⟩,
        ⟨132, true, 2, 56, 184⟩,
        ⟨132, true, 3, 64, 192⟩,
        ⟨132, true, 4, 72, 200⟩,
        ⟨133, false, 0, 168, 40⟩,
        ⟨133, false, 1, 176, 48⟩,
        ⟨133, false, 2, 184, 56⟩,
        ⟨133, false, 3, 192, 64⟩,
        ⟨133, false, 4, 200, 72⟩,
        ⟨133, true, 0, 39, 168⟩,
        ⟨133, true, 1, 48, 176⟩,
        ⟨133, true, 2, 56, 184⟩,
        ⟨133, true, 3, 64, 192⟩,
        ⟨133, true, 4, 72, 200⟩,
        ⟨134, false, 0, 168, 40⟩,
        ⟨134, false, 1, 176, 48⟩,
        ⟨134, false, 2, 184, 56⟩,
        ⟨134, false, 3, 192, 64⟩,
        ⟨134, false, 4, 200, 72⟩,
        ⟨134, true, 0, 39, 168⟩,
        ⟨134, true, 1, 48, 176⟩,
        ⟨134, true, 2, 56, 184⟩,
        ⟨134, true, 3, 64, 192⟩,
        ⟨134, true, 4, 72, 200⟩,
        ⟨135, false, 0, 168, 40⟩,
        ⟨135, false, 1, 176, 48⟩,
        ⟨135, false, 2, 184, 56⟩,
        ⟨135, false, 3, 192, 64⟩,
        ⟨135, false, 4, 200, 72⟩,
        ⟨135, true, 0, 39, 168⟩,
        ⟨135, true, 1, 48, 176⟩,
        ⟨135, true, 2, 56, 184⟩,
        ⟨135, true, 3, 64, 192⟩,
        ⟨135, true, 4, 72, 200⟩,
        ⟨136, false, 0, 168, 40⟩,
        ⟨136, false, 1, 176, 48⟩,
        ⟨136, false, 2, 184, 56⟩,
        ⟨136, false, 3, 192, 64⟩,
        ⟨136, false, 4, 200, 72⟩,
        ⟨136, true, 0, 39, 168⟩,
        ⟨136, true, 1, 48, 176⟩,
        ⟨136, true, 2, 56, 184⟩,
        ⟨136, true, 3, 64, 192⟩,
        ⟨136, true, 4, 72, 200⟩,
        ⟨137, false, 0, 169, 40⟩,
        ⟨137, false, 1, 176, 48⟩,
        ⟨137, false, 2, 184, 56⟩,
        ⟨137, false, 3, 192, 64⟩,
        ⟨137, false, 4, 200, 72⟩,
        ⟨137, true, 0, 39, 168⟩,
        ⟨137, true, 1, 47, 176⟩,
        ⟨137, true, 2, 56, 184⟩,
        ⟨137, true, 3, 64, 192⟩,
        ⟨137, true, 4, 72, 200⟩,
        ⟨138, false, 0, 169, 40⟩,
        ⟨138, false, 1, 176, 48⟩,
        ⟨138, false, 2, 184, 56⟩,
        ⟨138, false, 3, 192, 64⟩,
        ⟨138, false, 4, 200, 72⟩,
        ⟨138, true, 0, 39, 168⟩,
        ⟨138, true, 1, 47, 176⟩,
        ⟨138, true, 2, 56, 184⟩,
        ⟨138, true, 3, 64, 192⟩,
        ⟨138, true, 4, 72, 200⟩,
        ⟨139, false, 0, 169, 40⟩,
        ⟨139, false, 1, 176, 48⟩,
        ⟨139, false, 2, 184, 56⟩,
        ⟨139, false, 3, 192, 64⟩,
        ⟨139, false, 4, 200, 72⟩,
        ⟨139, true, 0, 39, 168⟩,
        ⟨139, true, 1, 47, 176⟩,
        ⟨139, true, 2, 56, 184⟩,
        ⟨139, true, 3, 64, 192⟩,
        ⟨139, true, 4, 72, 200⟩,
        ⟨140, false, 0, 169, 40⟩,
        ⟨140, false, 1, 176, 48⟩,
        ⟨140, false, 2, 184, 56⟩,
        ⟨140, false, 3, 192, 64⟩,
        ⟨140, false, 4, 200, 72⟩,
        ⟨140, true, 0, 38, 168⟩,
        ⟨140, true, 1, 47, 176⟩,
        ⟨140, true, 2, 56, 184⟩,
        ⟨140, true, 3, 64, 192⟩,
        ⟨140, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form14 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1449-1550):
      /-- `formReal` on every finite code, both signs and every `F`, part 14. -/
      def form14 : List FormVec := [
        ⟨141, false, 0, 169, 40⟩,
        ⟨141, false, 1, 176, 48⟩,
        ⟨141, false, 2, 184, 56⟩,
        ⟨141, false, 3, 192, 64⟩,
        ⟨141, false, 4, 200, 72⟩,
        ⟨141, true, 0, 38, 168⟩,
        ⟨141, true, 1, 47, 176⟩,
        ⟨141, true, 2, 56, 184⟩,
        ⟨141, true, 3, 64, 192⟩,
        ⟨141, true, 4, 72, 200⟩,
        ⟨142, false, 0, 169, 40⟩,
        ⟨142, false, 1, 176, 48⟩,
        ⟨142, false, 2, 184, 56⟩,
        ⟨142, false, 3, 192, 64⟩,
        ⟨142, false, 4, 200, 72⟩,
        ⟨142, true, 0, 38, 168⟩,
        ⟨142, true, 1, 47, 176⟩,
        ⟨142, true, 2, 56, 184⟩,
        ⟨142, true, 3, 64, 192⟩,
        ⟨142, true, 4, 72, 200⟩,
        ⟨143, false, 0, 169, 40⟩,
        ⟨143, false, 1, 176, 48⟩,
        ⟨143, false, 2, 184, 56⟩,
        ⟨143, false, 3, 192, 64⟩,
        ⟨143, false, 4, 200, 72⟩,
        ⟨143, true, 0, 38, 168⟩,
        ⟨143, true, 1, 47, 176⟩,
        ⟨143, true, 2, 56, 184⟩,
        ⟨143, true, 3, 64, 192⟩,
        ⟨143, true, 4, 72, 200⟩,
        ⟨144, false, 0, 169, 40⟩,
        ⟨144, false, 1, 176, 48⟩,
        ⟨144, false, 2, 184, 56⟩,
        ⟨144, false, 3, 192, 64⟩,
        ⟨144, false, 4, 200, 72⟩,
        ⟨144, true, 0, 38, 168⟩,
        ⟨144, true, 1, 47, 176⟩,
        ⟨144, true, 2, 56, 184⟩,
        ⟨144, true, 3, 64, 192⟩,
        ⟨144, true, 4, 72, 200⟩,
        ⟨145, false, 0, 169, 40⟩,
        ⟨145, false, 1, 177, 48⟩,
        ⟨145, false, 2, 184, 56⟩,
        ⟨145, false, 3, 192, 64⟩,
        ⟨145, false, 4, 200, 72⟩,
        ⟨145, true, 0, 38, 168⟩,
        ⟨145, true, 1, 47, 176⟩,
        ⟨145, true, 2, 55, 184⟩,
        ⟨145, true, 3, 64, 192⟩,
        ⟨145, true, 4, 72, 200⟩,
        ⟨146, false, 0, 169, 40⟩,
        ⟨146, false, 1, 177, 48⟩,
        ⟨146, false, 2, 184, 56⟩,
        ⟨146, false, 3, 192, 64⟩,
        ⟨146, false, 4, 200, 72⟩,
        ⟨146, true, 0, 38, 168⟩,
        ⟨146, true, 1, 47, 176⟩,
        ⟨146, true, 2, 55, 184⟩,
        ⟨146, true, 3, 64, 192⟩,
        ⟨146, true, 4, 72, 200⟩,
        ⟨147, false, 0, 169, 40⟩,
        ⟨147, false, 1, 177, 48⟩,
        ⟨147, false, 2, 184, 56⟩,
        ⟨147, false, 3, 192, 64⟩,
        ⟨147, false, 4, 200, 72⟩,
        ⟨147, true, 0, 37, 168⟩,
        ⟨147, true, 1, 47, 176⟩,
        ⟨147, true, 2, 55, 184⟩,
        ⟨147, true, 3, 64, 192⟩,
        ⟨147, true, 4, 72, 200⟩,
        ⟨148, false, 0, 170, 40⟩,
        ⟨148, false, 1, 177, 48⟩,
        ⟨148, false, 2, 184, 56⟩,
        ⟨148, false, 3, 192, 64⟩,
        ⟨148, false, 4, 200, 72⟩,
        ⟨148, true, 0, 37, 168⟩,
        ⟨148, true, 1, 46, 176⟩,
        ⟨148, true, 2, 55, 184⟩,
        ⟨148, true, 3, 64, 192⟩,
        ⟨148, true, 4, 72, 200⟩,
        ⟨149, false, 0, 170, 40⟩,
        ⟨149, false, 1, 177, 48⟩,
        ⟨149, false, 2, 184, 56⟩,
        ⟨149, false, 3, 192, 64⟩,
        ⟨149, false, 4, 200, 72⟩,
        ⟨149, true, 0, 37, 168⟩,
        ⟨149, true, 1, 46, 176⟩,
        ⟨149, true, 2, 55, 184⟩,
        ⟨149, true, 3, 64, 192⟩,
        ⟨149, true, 4, 72, 200⟩,
        ⟨150, false, 0, 170, 40⟩,
        ⟨150, false, 1, 177, 48⟩,
        ⟨150, false, 2, 184, 56⟩,
        ⟨150, false, 3, 192, 64⟩,
        ⟨150, false, 4, 200, 72⟩,
        ⟨150, true, 0, 36, 168⟩,
        ⟨150, true, 1, 46, 176⟩,
        ⟨150, true, 2, 55, 184⟩,
        ⟨150, true, 3, 64, 192⟩,
        ⟨150, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form15 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1552-1653):
      /-- `formReal` on every finite code, both signs and every `F`, part 15. -/
      def form15 : List FormVec := [
        ⟨151, false, 0, 170, 40⟩,
        ⟨151, false, 1, 177, 48⟩,
        ⟨151, false, 2, 184, 56⟩,
        ⟨151, false, 3, 192, 64⟩,
        ⟨151, false, 4, 200, 72⟩,
        ⟨151, true, 0, 36, 168⟩,
        ⟨151, true, 1, 46, 176⟩,
        ⟨151, true, 2, 55, 184⟩,
        ⟨151, true, 3, 64, 192⟩,
        ⟨151, true, 4, 72, 200⟩,
        ⟨152, false, 0, 170, 40⟩,
        ⟨152, false, 1, 177, 48⟩,
        ⟨152, false, 2, 184, 56⟩,
        ⟨152, false, 3, 192, 64⟩,
        ⟨152, false, 4, 200, 72⟩,
        ⟨152, true, 0, 36, 168⟩,
        ⟨152, true, 1, 46, 176⟩,
        ⟨152, true, 2, 55, 184⟩,
        ⟨152, true, 3, 64, 192⟩,
        ⟨152, true, 4, 72, 200⟩,
        ⟨153, false, 0, 170, 40⟩,
        ⟨153, false, 1, 177, 48⟩,
        ⟨153, false, 2, 185, 56⟩,
        ⟨153, false, 3, 192, 64⟩,
        ⟨153, false, 4, 200, 72⟩,
        ⟨153, true, 0, 36, 168⟩,
        ⟨153, true, 1, 46, 176⟩,
        ⟨153, true, 2, 55, 184⟩,
        ⟨153, true, 3, 63, 192⟩,
        ⟨153, true, 4, 72, 200⟩,
        ⟨154, false, 0, 170, 40⟩,
        ⟨154, false, 1, 177, 48⟩,
        ⟨154, false, 2, 185, 56⟩,
        ⟨154, false, 3, 192, 64⟩,
        ⟨154, false, 4, 200, 72⟩,
        ⟨154, true, 0, 35, 168⟩,
        ⟨154, true, 1, 46, 176⟩,
        ⟨154, true, 2, 55, 184⟩,
        ⟨154, true, 3, 63, 192⟩,
        ⟨154, true, 4, 72, 200⟩,
        ⟨155, false, 0, 171, 40⟩,
        ⟨155, false, 1, 177, 48⟩,
        ⟨155, false, 2, 185, 56⟩,
        ⟨155, false, 3, 192, 64⟩,
        ⟨155, false, 4, 200, 72⟩,
        ⟨155, true, 0, 34, 168⟩,
        ⟨155, true, 1, 45, 176⟩,
        ⟨155, true, 2, 55, 184⟩,
        ⟨155, true, 3, 63, 192⟩,
        ⟨155, true, 4, 72, 200⟩,
        ⟨156, false, 0, 171, 40⟩,
        ⟨156, false, 1, 178, 48⟩,
        ⟨156, false, 2, 185, 56⟩,
        ⟨156, false, 3, 192, 64⟩,
        ⟨156, false, 4, 200, 72⟩,
        ⟨156, true, 0, 34, 168⟩,
        ⟨156, true, 1, 45, 176⟩,
        ⟨156, true, 2, 54, 184⟩,
        ⟨156, true, 3, 63, 192⟩,
        ⟨156, true, 4, 72, 200⟩,
        ⟨157, false, 0, 171, 40⟩,
        ⟨157, false, 1, 178, 48⟩,
        ⟨157, false, 2, 185, 56⟩,
        ⟨157, false, 3, 192, 64⟩,
        ⟨157, false, 4, 200, 72⟩,
        ⟨157, true, 0, 34, 168⟩,
        ⟨157, true, 1, 45, 176⟩,
        ⟨157, true, 2, 54, 184⟩,
        ⟨157, true, 3, 63, 192⟩,
        ⟨157, true, 4, 72, 200⟩,
        ⟨158, false, 0, 172, 40⟩,
        ⟨158, false, 1, 178, 48⟩,
        ⟨158, false, 2, 185, 56⟩,
        ⟨158, false, 3, 192, 64⟩,
        ⟨158, false, 4, 200, 72⟩,
        ⟨158, true, 0, 33, 168⟩,
        ⟨158, true, 1, 44, 176⟩,
        ⟨158, true, 2, 54, 184⟩,
        ⟨158, true, 3, 63, 192⟩,
        ⟨158, true, 4, 72, 200⟩,
        ⟨159, false, 0, 172, 40⟩,
        ⟨159, false, 1, 178, 48⟩,
        ⟨159, false, 2, 185, 56⟩,
        ⟨159, false, 3, 192, 64⟩,
        ⟨159, false, 4, 200, 72⟩,
        ⟨159, true, 0, 32, 168⟩,
        ⟨159, true, 1, 44, 176⟩,
        ⟨159, true, 2, 54, 184⟩,
        ⟨159, true, 3, 63, 192⟩,
        ⟨159, true, 4, 72, 200⟩,
        ⟨160, false, 0, 172, 40⟩,
        ⟨160, false, 1, 178, 48⟩,
        ⟨160, false, 2, 185, 56⟩,
        ⟨160, false, 3, 192, 64⟩,
        ⟨160, false, 4, 200, 72⟩,
        ⟨160, true, 0, 32, 168⟩,
        ⟨160, true, 1, 44, 176⟩,
        ⟨160, true, 2, 54, 184⟩,
        ⟨160, true, 3, 63, 192⟩,
        ⟨160, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form16 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1655-1756):
      /-- `formReal` on every finite code, both signs and every `F`, part 16. -/
      def form16 : List FormVec := [
        ⟨161, false, 0, 172, 40⟩,
        ⟨161, false, 1, 178, 48⟩,
        ⟨161, false, 2, 185, 56⟩,
        ⟨161, false, 3, 193, 64⟩,
        ⟨161, false, 4, 200, 72⟩,
        ⟨161, true, 0, 30, 168⟩,
        ⟨161, true, 1, 44, 176⟩,
        ⟨161, true, 2, 54, 184⟩,
        ⟨161, true, 3, 63, 192⟩,
        ⟨161, true, 4, 71, 200⟩,
        ⟨162, false, 0, 173, 40⟩,
        ⟨162, false, 1, 178, 48⟩,
        ⟨162, false, 2, 185, 56⟩,
        ⟨162, false, 3, 193, 64⟩,
        ⟨162, false, 4, 200, 72⟩,
        ⟨162, true, 0, 28, 168⟩,
        ⟨162, true, 1, 43, 176⟩,
        ⟨162, true, 2, 54, 184⟩,
        ⟨162, true, 3, 63, 192⟩,
        ⟨162, true, 4, 71, 200⟩,
        ⟨163, false, 0, 174, 40⟩,
        ⟨163, false, 1, 179, 48⟩,
        ⟨163, false, 2, 185, 56⟩,
        ⟨163, false, 3, 193, 64⟩,
        ⟨163, false, 4, 200, 72⟩,
        ⟨163, true, 0, 26, 168⟩,
        ⟨163, true, 1, 42, 176⟩,
        ⟨163, true, 2, 53, 184⟩,
        ⟨163, true, 3, 63, 192⟩,
        ⟨163, true, 4, 71, 200⟩,
        ⟨164, false, 0, 174, 40⟩,
        ⟨164, false, 1, 179, 48⟩,
        ⟨164, false, 2, 186, 56⟩,
        ⟨164, false, 3, 193, 64⟩,
        ⟨164, false, 4, 200, 72⟩,
        ⟨164, true, 0, 24, 168⟩,
        ⟨164, true, 1, 42, 176⟩,
        ⟨164, true, 2, 53, 184⟩,
        ⟨164, true, 3, 62, 192⟩,
        ⟨164, true, 4, 71, 200⟩,
        ⟨165, false, 0, 174, 40⟩,
        ⟨165, false, 1, 179, 48⟩,
        ⟨165, false, 2, 186, 56⟩,
        ⟨165, false, 3, 193, 64⟩,
        ⟨165, false, 4, 200, 72⟩,
        ⟨165, true, 0, 20, 168⟩,
        ⟨165, true, 1, 42, 176⟩,
        ⟨165, true, 2, 53, 184⟩,
        ⟨165, true, 3, 62, 192⟩,
        ⟨165, true, 4, 71, 200⟩,
        ⟨166, false, 0, 175, 40⟩,
        ⟨166, false, 1, 180, 48⟩,
        ⟨166, false, 2, 186, 56⟩,
        ⟨166, false, 3, 193, 64⟩,
        ⟨166, false, 4, 200, 72⟩,
        ⟨166, true, 0, 16, 168⟩,
        ⟨166, true, 1, 41, 176⟩,
        ⟨166, true, 2, 52, 184⟩,
        ⟨166, true, 3, 62, 192⟩,
        ⟨166, true, 4, 71, 200⟩,
        ⟨167, false, 0, 176, 40⟩,
        ⟨167, false, 1, 180, 48⟩,
        ⟨167, false, 2, 186, 56⟩,
        ⟨167, false, 3, 193, 64⟩,
        ⟨167, false, 4, 200, 72⟩,
        ⟨167, true, 0, 8, 168⟩,
        ⟨167, true, 1, 40, 176⟩,
        ⟨167, true, 2, 52, 184⟩,
        ⟨167, true, 3, 62, 192⟩,
        ⟨167, true, 4, 71, 200⟩,
        ⟨168, false, 0, 176, 40⟩,
        ⟨168, false, 1, 180, 48⟩,
        ⟨168, false, 2, 186, 56⟩,
        ⟨168, false, 3, 193, 64⟩,
        ⟨168, false, 4, 200, 72⟩,
        ⟨168, true, 0, 0, 168⟩,
        ⟨168, true, 1, 40, 176⟩,
        ⟨168, true, 2, 52, 184⟩,
        ⟨168, true, 3, 62, 192⟩,
        ⟨168, true, 4, 71, 200⟩,
        ⟨169, false, 0, 176, 40⟩,
        ⟨169, false, 1, 180, 48⟩,
        ⟨169, false, 2, 186, 56⟩,
        ⟨169, false, 3, 193, 64⟩,
        ⟨169, false, 4, 201, 72⟩,
        ⟨169, true, 0, 144, 168⟩,
        ⟨169, true, 1, 38, 176⟩,
        ⟨169, true, 2, 52, 184⟩,
        ⟨169, true, 3, 62, 192⟩,
        ⟨169, true, 4, 71, 200⟩,
        ⟨170, false, 0, 177, 40⟩,
        ⟨170, false, 1, 181, 48⟩,
        ⟨170, false, 2, 186, 56⟩,
        ⟨170, false, 3, 193, 64⟩,
        ⟨170, false, 4, 201, 72⟩,
        ⟨170, true, 0, 152, 168⟩,
        ⟨170, true, 1, 36, 176⟩,
        ⟨170, true, 2, 51, 184⟩,
        ⟨170, true, 3, 62, 192⟩,
        ⟨170, true, 4, 71, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form17 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1758-1859):
      /-- `formReal` on every finite code, both signs and every `F`, part 17. -/
      def form17 : List FormVec := [
        ⟨171, false, 0, 178, 40⟩,
        ⟨171, false, 1, 182, 48⟩,
        ⟨171, false, 2, 187, 56⟩,
        ⟨171, false, 3, 193, 64⟩,
        ⟨171, false, 4, 201, 72⟩,
        ⟨171, true, 0, 156, 168⟩,
        ⟨171, true, 1, 34, 176⟩,
        ⟨171, true, 2, 50, 184⟩,
        ⟨171, true, 3, 61, 192⟩,
        ⟨171, true, 4, 71, 200⟩,
        ⟨172, false, 0, 178, 40⟩,
        ⟨172, false, 1, 182, 48⟩,
        ⟨172, false, 2, 187, 56⟩,
        ⟨172, false, 3, 194, 64⟩,
        ⟨172, false, 4, 201, 72⟩,
        ⟨172, true, 0, 160, 168⟩,
        ⟨172, true, 1, 32, 176⟩,
        ⟨172, true, 2, 50, 184⟩,
        ⟨172, true, 3, 61, 192⟩,
        ⟨172, true, 4, 70, 200⟩,
        ⟨173, false, 0, 178, 40⟩,
        ⟨173, false, 1, 182, 48⟩,
        ⟨173, false, 2, 187, 56⟩,
        ⟨173, false, 3, 194, 64⟩,
        ⟨173, false, 4, 201, 72⟩,
        ⟨173, true, 0, 162, 168⟩,
        ⟨173, true, 1, 28, 176⟩,
        ⟨173, true, 2, 50, 184⟩,
        ⟨173, true, 3, 61, 192⟩,
        ⟨173, true, 4, 70, 200⟩,
        ⟨174, false, 0, 179, 40⟩,
        ⟨174, false, 1, 183, 48⟩,
        ⟨174, false, 2, 188, 56⟩,
        ⟨174, false, 3, 194, 64⟩,
        ⟨174, false, 4, 201, 72⟩,
        ⟨174, true, 0, 164, 168⟩,
        ⟨174, true, 1, 24, 176⟩,
        ⟨174, true, 2, 49, 184⟩,
        ⟨174, true, 3, 60, 192⟩,
        ⟨174, true, 4, 70, 200⟩,
        ⟨175, false, 0, 180, 40⟩,
        ⟨175, false, 1, 184, 48⟩,
        ⟨175, false, 2, 188, 56⟩,
        ⟨175, false, 3, 194, 64⟩,
        ⟨175, false, 4, 201, 72⟩,
        ⟨175, true, 0, 166, 168⟩,
        ⟨175, true, 1, 16, 176⟩,
        ⟨175, true, 2, 48, 184⟩,
        ⟨175, true, 3, 60, 192⟩,
        ⟨175, true, 4, 70, 200⟩,
        ⟨176, false, 0, 180, 40⟩,
        ⟨176, false, 1, 184, 48⟩,
        ⟨176, false, 2, 188, 56⟩,
        ⟨176, false, 3, 194, 64⟩,
        ⟨176, false, 4, 201, 72⟩,
        ⟨176, true, 0, 168, 168⟩,
        ⟨176, true, 1, 0, 176⟩,
        ⟨176, true, 2, 48, 184⟩,
        ⟨176, true, 3, 60, 192⟩,
        ⟨176, true, 4, 70, 200⟩,
        ⟨177, false, 0, 181, 40⟩,
        ⟨177, false, 1, 184, 48⟩,
        ⟨177, false, 2, 188, 56⟩,
        ⟨177, false, 3, 194, 64⟩,
        ⟨177, false, 4, 201, 72⟩,
        ⟨177, true, 0, 170, 168⟩,
        ⟨177, true, 1, 152, 176⟩,
        ⟨177, true, 2, 46, 184⟩,
        ⟨177, true, 3, 60, 192⟩,
        ⟨177, true, 4, 70, 200⟩,
        ⟨178, false, 0, 182, 40⟩,
        ⟨178, false, 1, 185, 48⟩,
        ⟨178, false, 2, 189, 56⟩,
        ⟨178, false, 3, 194, 64⟩,
        ⟨178, false, 4, 201, 72⟩,
        ⟨178, true, 0, 172, 168⟩,
        ⟨178, true, 1, 160, 176⟩,
        ⟨178, true, 2, 44, 184⟩,
        ⟨178, true, 3, 59, 192⟩,
        ⟨178, true, 4, 70, 200⟩,
        ⟨179, false, 0, 183, 40⟩,
        ⟨179, false, 1, 186, 48⟩,
        ⟨179, false, 2, 190, 56⟩,
        ⟨179, false, 3, 195, 64⟩,
        ⟨179, false, 4, 201, 72⟩,
        ⟨179, true, 0, 174, 168⟩,
        ⟨179, true, 1, 164, 176⟩,
        ⟨179, true, 2, 42, 184⟩,
        ⟨179, true, 3, 58, 192⟩,
        ⟨179, true, 4, 69, 200⟩,
        ⟨180, false, 0, 184, 40⟩,
        ⟨180, false, 1, 186, 48⟩,
        ⟨180, false, 2, 190, 56⟩,
        ⟨180, false, 3, 195, 64⟩,
        ⟨180, false, 4, 202, 72⟩,
        ⟨180, true, 0, 176, 168⟩,
        ⟨180, true, 1, 168, 176⟩,
        ⟨180, true, 2, 40, 184⟩,
        ⟨180, true, 3, 58, 192⟩,
        ⟨180, true, 4, 69, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form18 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1861-1962):
      /-- `formReal` on every finite code, both signs and every `F`, part 18. -/
      def form18 : List FormVec := [
        ⟨181, false, 0, 184, 40⟩,
        ⟨181, false, 1, 186, 48⟩,
        ⟨181, false, 2, 190, 56⟩,
        ⟨181, false, 3, 195, 64⟩,
        ⟨181, false, 4, 202, 72⟩,
        ⟨181, true, 0, 177, 168⟩,
        ⟨181, true, 1, 170, 176⟩,
        ⟨181, true, 2, 36, 184⟩,
        ⟨181, true, 3, 58, 192⟩,
        ⟨181, true, 4, 69, 200⟩,
        ⟨182, false, 0, 185, 40⟩,
        ⟨182, false, 1, 187, 48⟩,
        ⟨182, false, 2, 191, 56⟩,
        ⟨182, false, 3, 196, 64⟩,
        ⟨182, false, 4, 202, 72⟩,
        ⟨182, true, 0, 178, 168⟩,
        ⟨182, true, 1, 172, 176⟩,
        ⟨182, true, 2, 32, 184⟩,
        ⟨182, true, 3, 57, 192⟩,
        ⟨182, true, 4, 68, 200⟩,
        ⟨183, false, 0, 186, 40⟩,
        ⟨183, false, 1, 188, 48⟩,
        ⟨183, false, 2, 192, 56⟩,
        ⟨183, false, 3, 196, 64⟩,
        ⟨183, false, 4, 202, 72⟩,
        ⟨183, true, 0, 179, 168⟩,
        ⟨183, true, 1, 174, 176⟩,
        ⟨183, true, 2, 24, 184⟩,
        ⟨183, true, 3, 56, 192⟩,
        ⟨183, true, 4, 68, 200⟩,
        ⟨184, false, 0, 186, 40⟩,
        ⟨184, false, 1, 188, 48⟩,
        ⟨184, false, 2, 192, 56⟩,
        ⟨184, false, 3, 196, 64⟩,
        ⟨184, false, 4, 202, 72⟩,
        ⟨184, true, 0, 180, 168⟩,
        ⟨184, true, 1, 176, 176⟩,
        ⟨184, true, 2, 0, 184⟩,
        ⟨184, true, 3, 56, 192⟩,
        ⟨184, true, 4, 68, 200⟩,
        ⟨185, false, 0, 187, 40⟩,
        ⟨185, false, 1, 189, 48⟩,
        ⟨185, false, 2, 192, 56⟩,
        ⟨185, false, 3, 196, 64⟩,
        ⟨185, false, 4, 202, 72⟩,
        ⟨185, true, 0, 182, 168⟩,
        ⟨185, true, 1, 178, 176⟩,
        ⟨185, true, 2, 160, 184⟩,
        ⟨185, true, 3, 54, 192⟩,
        ⟨185, true, 4, 68, 200⟩,
        ⟨186, false, 0, 188, 40⟩,
        ⟨186, false, 1, 190, 48⟩,
        ⟨186, false, 2, 193, 56⟩,
        ⟨186, false, 3, 197, 64⟩,
        ⟨186, false, 4, 202, 72⟩,
        ⟨186, true, 0, 184, 168⟩,
        ⟨186, true, 1, 180, 176⟩,
        ⟨186, true, 2, 168, 184⟩,
        ⟨186, true, 3, 52, 192⟩,
        ⟨186, true, 4, 67, 200⟩,
        ⟨187, false, 0, 189, 40⟩,
        ⟨187, false, 1, 191, 48⟩,
        ⟨187, false, 2, 194, 56⟩,
        ⟨187, false, 3, 198, 64⟩,
        ⟨187, false, 4, 203, 72⟩,
        ⟨187, true, 0, 185, 168⟩,
        ⟨187, true, 1, 182, 176⟩,
        ⟨187, true, 2, 172, 184⟩,
        ⟨187, true, 3, 50, 192⟩,
        ⟨187, true, 4, 66, 200⟩,
        ⟨188, false, 0, 190, 40⟩,
        ⟨188, false, 1, 192, 48⟩,
        ⟨188, false, 2, 194, 56⟩,
        ⟨188, false, 3, 198, 64⟩,
        ⟨188, false, 4, 203, 72⟩,
        ⟨188, true, 0, 186, 168⟩,
        ⟨188, true, 1, 184, 176⟩,
        ⟨188, true, 2, 176, 184⟩,
        ⟨188, true, 3, 48, 192⟩,
        ⟨188, true, 4, 66, 200⟩,
        ⟨189, false, 0, 191, 40⟩,
        ⟨189, false, 1, 192, 48⟩,
        ⟨189, false, 2, 194, 56⟩,
        ⟨189, false, 3, 198, 64⟩,
        ⟨189, false, 4, 203, 72⟩,
        ⟨189, true, 0, 187, 168⟩,
        ⟨189, true, 1, 185, 176⟩,
        ⟨189, true, 2, 178, 184⟩,
        ⟨189, true, 3, 44, 192⟩,
        ⟨189, true, 4, 66, 200⟩,
        ⟨190, false, 0, 192, 40⟩,
        ⟨190, false, 1, 193, 48⟩,
        ⟨190, false, 2, 195, 56⟩,
        ⟨190, false, 3, 199, 64⟩,
        ⟨190, false, 4, 204, 72⟩,
        ⟨190, true, 0, 188, 168⟩,
        ⟨190, true, 1, 186, 176⟩,
        ⟨190, true, 2, 180, 184⟩,
        ⟨190, true, 3, 40, 192⟩,
        ⟨190, true, 4, 65, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form19 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:1964-2065):
      /-- `formReal` on every finite code, both signs and every `F`, part 19. -/
      def form19 : List FormVec := [
        ⟨191, false, 0, 192, 40⟩,
        ⟨191, false, 1, 194, 48⟩,
        ⟨191, false, 2, 196, 56⟩,
        ⟨191, false, 3, 200, 64⟩,
        ⟨191, false, 4, 204, 72⟩,
        ⟨191, true, 0, 189, 168⟩,
        ⟨191, true, 1, 187, 176⟩,
        ⟨191, true, 2, 182, 184⟩,
        ⟨191, true, 3, 32, 192⟩,
        ⟨191, true, 4, 64, 200⟩,
        ⟨192, false, 0, 193, 40⟩,
        ⟨192, false, 1, 194, 48⟩,
        ⟨192, false, 2, 196, 56⟩,
        ⟨192, false, 3, 200, 64⟩,
        ⟨192, false, 4, 204, 72⟩,
        ⟨192, true, 0, 190, 168⟩,
        ⟨192, true, 1, 188, 176⟩,
        ⟨192, true, 2, 184, 184⟩,
        ⟨192, true, 3, 0, 192⟩,
        ⟨192, true, 4, 64, 200⟩,
        ⟨193, false, 0, 194, 40⟩,
        ⟨193, false, 1, 195, 48⟩,
        ⟨193, false, 2, 197, 56⟩,
        ⟨193, false, 3, 200, 64⟩,
        ⟨193, false, 4, 204, 72⟩,
        ⟨193, true, 0, 192, 168⟩,
        ⟨193, true, 1, 190, 176⟩,
        ⟨193, true, 2, 186, 184⟩,
        ⟨193, true, 3, 168, 192⟩,
        ⟨193, true, 4, 62, 200⟩,
        ⟨194, false, 0, 195, 40⟩,
        ⟨194, false, 1, 196, 48⟩,
        ⟨194, false, 2, 198, 56⟩,
        ⟨194, false, 3, 201, 64⟩,
        ⟨194, false, 4, 205, 72⟩,
        ⟨194, true, 0, 193, 168⟩,
        ⟨194, true, 1, 192, 176⟩,
        ⟨194, true, 2, 188, 184⟩,
        ⟨194, true, 3, 176, 192⟩,
        ⟨194, true, 4, 60, 200⟩,
        ⟨195, false, 0, 196, 40⟩,
        ⟨195, false, 1, 197, 48⟩,
        ⟨195, false, 2, 199, 56⟩,
        ⟨195, false, 3, 202, 64⟩,
        ⟨195, false, 4, 206, 72⟩,
        ⟨195, true, 0, 194, 168⟩,
        ⟨195, true, 1, 193, 176⟩,
        ⟨195, true, 2, 190, 184⟩,
        ⟨195, true, 3, 180, 192⟩,
        ⟨195, true, 4, 58, 200⟩,
        ⟨196, false, 0, 197, 40⟩,
        ⟨196, false, 1, 198, 48⟩,
        ⟨196, false, 2, 200, 56⟩,
        ⟨196, false, 3, 202, 64⟩,
        ⟨196, false, 4, 206, 72⟩,
        ⟨196, true, 0, 195, 168⟩,
        ⟨196, true, 1, 194, 176⟩,
        ⟨196, true, 2, 192, 184⟩,
        ⟨196, true, 3, 184, 192⟩,
        ⟨196, true, 4, 56, 200⟩,
        ⟨197, false, 0, 198, 40⟩,
        ⟨197, false, 1, 199, 48⟩,
        ⟨197, false, 2, 200, 56⟩,
        ⟨197, false, 3, 202, 64⟩,
        ⟨197, false, 4, 206, 72⟩,
        ⟨197, true, 0, 196, 168⟩,
        ⟨197, true, 1, 195, 176⟩,
        ⟨197, true, 2, 193, 184⟩,
        ⟨197, true, 3, 186, 192⟩,
        ⟨197, true, 4, 52, 200⟩,
        ⟨198, false, 0, 199, 40⟩,
        ⟨198, false, 1, 200, 48⟩,
        ⟨198, false, 2, 201, 56⟩,
        ⟨198, false, 3, 203, 64⟩,
        ⟨198, false, 4, 207, 72⟩,
        ⟨198, true, 0, 197, 168⟩,
        ⟨198, true, 1, 196, 176⟩,
        ⟨198, true, 2, 194, 184⟩,
        ⟨198, true, 3, 188, 192⟩,
        ⟨198, true, 4, 48, 200⟩,
        ⟨199, false, 0, 200, 40⟩,
        ⟨199, false, 1, 200, 48⟩,
        ⟨199, false, 2, 202, 56⟩,
        ⟨199, false, 3, 204, 64⟩,
        ⟨199, false, 4, 208, 72⟩,
        ⟨199, true, 0, 198, 168⟩,
        ⟨199, true, 1, 197, 176⟩,
        ⟨199, true, 2, 195, 184⟩,
        ⟨199, true, 3, 190, 192⟩,
        ⟨199, true, 4, 40, 200⟩,
        ⟨200, false, 0, 201, 48⟩,
        ⟨200, false, 1, 201, 48⟩,
        ⟨200, false, 2, 202, 56⟩,
        ⟨200, false, 3, 204, 64⟩,
        ⟨200, false, 4, 208, 72⟩,
        ⟨200, true, 0, 198, 176⟩,
        ⟨200, true, 1, 198, 176⟩,
        ⟨200, true, 2, 196, 184⟩,
        ⟨200, true, 3, 192, 192⟩,
        ⟨200, true, 4, 0, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form2 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:213-314):
      /-- `formReal` on every finite code, both signs and every `F`, part 2. -/
      def form2 : List FormVec := [
        ⟨20, false, 0, 165, 40⟩,
        ⟨20, false, 1, 174, 48⟩,
        ⟨20, false, 2, 183, 56⟩,
        ⟨20, false, 3, 192, 64⟩,
        ⟨20, false, 4, 200, 72⟩,
        ⟨20, true, 0, 42, 168⟩,
        ⟨20, true, 1, 49, 176⟩,
        ⟨20, true, 2, 56, 184⟩,
        ⟨20, true, 3, 64, 192⟩,
        ⟨20, true, 4, 72, 200⟩,
        ⟨21, false, 0, 165, 40⟩,
        ⟨21, false, 1, 174, 48⟩,
        ⟨21, false, 2, 183, 56⟩,
        ⟨21, false, 3, 192, 64⟩,
        ⟨21, false, 4, 200, 72⟩,
        ⟨21, true, 0, 42, 168⟩,
        ⟨21, true, 1, 49, 176⟩,
        ⟨21, true, 2, 56, 184⟩,
        ⟨21, true, 3, 64, 192⟩,
        ⟨21, true, 4, 72, 200⟩,
        ⟨22, false, 0, 164, 40⟩,
        ⟨22, false, 1, 174, 48⟩,
        ⟨22, false, 2, 183, 56⟩,
        ⟨22, false, 3, 192, 64⟩,
        ⟨22, false, 4, 200, 72⟩,
        ⟨22, true, 0, 42, 168⟩,
        ⟨22, true, 1, 49, 176⟩,
        ⟨22, true, 2, 56, 184⟩,
        ⟨22, true, 3, 64, 192⟩,
        ⟨22, true, 4, 72, 200⟩,
        ⟨23, false, 0, 164, 40⟩,
        ⟨23, false, 1, 174, 48⟩,
        ⟨23, false, 2, 183, 56⟩,
        ⟨23, false, 3, 192, 64⟩,
        ⟨23, false, 4, 200, 72⟩,
        ⟨23, true, 0, 42, 168⟩,
        ⟨23, true, 1, 49, 176⟩,
        ⟨23, true, 2, 56, 184⟩,
        ⟨23, true, 3, 64, 192⟩,
        ⟨23, true, 4, 72, 200⟩,
        ⟨24, false, 0, 164, 40⟩,
        ⟨24, false, 1, 174, 48⟩,
        ⟨24, false, 2, 183, 56⟩,
        ⟨24, false, 3, 192, 64⟩,
        ⟨24, false, 4, 200, 72⟩,
        ⟨24, true, 0, 42, 168⟩,
        ⟨24, true, 1, 49, 176⟩,
        ⟨24, true, 2, 56, 184⟩,
        ⟨24, true, 3, 64, 192⟩,
        ⟨24, true, 4, 72, 200⟩,
        ⟨25, false, 0, 164, 40⟩,
        ⟨25, false, 1, 174, 48⟩,
        ⟨25, false, 2, 183, 56⟩,
        ⟨25, false, 3, 191, 64⟩,
        ⟨25, false, 4, 200, 72⟩,
        ⟨25, true, 0, 42, 168⟩,
        ⟨25, true, 1, 49, 176⟩,
        ⟨25, true, 2, 57, 184⟩,
        ⟨25, true, 3, 64, 192⟩,
        ⟨25, true, 4, 72, 200⟩,
        ⟨26, false, 0, 163, 40⟩,
        ⟨26, false, 1, 174, 48⟩,
        ⟨26, false, 2, 183, 56⟩,
        ⟨26, false, 3, 191, 64⟩,
        ⟨26, false, 4, 200, 72⟩,
        ⟨26, true, 0, 42, 168⟩,
        ⟨26, true, 1, 49, 176⟩,
        ⟨26, true, 2, 57, 184⟩,
        ⟨26, true, 3, 64, 192⟩,
        ⟨26, true, 4, 72, 200⟩,
        ⟨27, false, 0, 162, 40⟩,
        ⟨27, false, 1, 173, 48⟩,
        ⟨27, false, 2, 183, 56⟩,
        ⟨27, false, 3, 191, 64⟩,
        ⟨27, false, 4, 200, 72⟩,
        ⟨27, true, 0, 43, 168⟩,
        ⟨27, true, 1, 49, 176⟩,
        ⟨27, true, 2, 57, 184⟩,
        ⟨27, true, 3, 64, 192⟩,
        ⟨27, true, 4, 72, 200⟩,
        ⟨28, false, 0, 162, 40⟩,
        ⟨28, false, 1, 173, 48⟩,
        ⟨28, false, 2, 182, 56⟩,
        ⟨28, false, 3, 191, 64⟩,
        ⟨28, false, 4, 200, 72⟩,
        ⟨28, true, 0, 43, 168⟩,
        ⟨28, true, 1, 50, 176⟩,
        ⟨28, true, 2, 57, 184⟩,
        ⟨28, true, 3, 64, 192⟩,
        ⟨28, true, 4, 72, 200⟩,
        ⟨29, false, 0, 162, 40⟩,
        ⟨29, false, 1, 173, 48⟩,
        ⟨29, false, 2, 182, 56⟩,
        ⟨29, false, 3, 191, 64⟩,
        ⟨29, false, 4, 200, 72⟩,
        ⟨29, true, 0, 43, 168⟩,
        ⟨29, true, 1, 50, 176⟩,
        ⟨29, true, 2, 57, 184⟩,
        ⟨29, true, 3, 64, 192⟩,
        ⟨29, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form20 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2067-2168):
      /-- `formReal` on every finite code, both signs and every `F`, part 20. -/
      def form20 : List FormVec := [
        ⟨201, false, 0, 202, 48⟩,
        ⟨201, false, 1, 202, 48⟩,
        ⟨201, false, 2, 203, 56⟩,
        ⟨201, false, 3, 205, 64⟩,
        ⟨201, false, 4, 208, 72⟩,
        ⟨201, true, 0, 200, 176⟩,
        ⟨201, true, 1, 200, 176⟩,
        ⟨201, true, 2, 198, 184⟩,
        ⟨201, true, 3, 194, 192⟩,
        ⟨201, true, 4, 176, 200⟩,
        ⟨202, false, 0, 203, 48⟩,
        ⟨202, false, 1, 203, 48⟩,
        ⟨202, false, 2, 204, 56⟩,
        ⟨202, false, 3, 206, 64⟩,
        ⟨202, false, 4, 209, 72⟩,
        ⟨202, true, 0, 201, 176⟩,
        ⟨202, true, 1, 201, 176⟩,
        ⟨202, true, 2, 200, 184⟩,
        ⟨202, true, 3, 196, 192⟩,
        ⟨202, true, 4, 184, 200⟩,
        ⟨203, false, 0, 204, 48⟩,
        ⟨203, false, 1, 204, 48⟩,
        ⟨203, false, 2, 205, 56⟩,
        ⟨203, false, 3, 207, 64⟩,
        ⟨203, false, 4, 210, 72⟩,
        ⟨203, true, 0, 202, 176⟩,
        ⟨203, true, 1, 202, 176⟩,
        ⟨203, true, 2, 201, 184⟩,
        ⟨203, true, 3, 198, 192⟩,
        ⟨203, true, 4, 188, 200⟩,
        ⟨204, false, 0, 205, 48⟩,
        ⟨204, false, 1, 205, 48⟩,
        ⟨204, false, 2, 206, 56⟩,
        ⟨204, false, 3, 208, 64⟩,
        ⟨204, false, 4, 210, 72⟩,
        ⟨204, true, 0, 203, 176⟩,
        ⟨204, true, 1, 203, 176⟩,
        ⟨204, true, 2, 202, 184⟩,
        ⟨204, true, 3, 200, 192⟩,
        ⟨204, true, 4, 192, 200⟩,
        ⟨205, false, 0, 206, 48⟩,
        ⟨205, false, 1, 206, 48⟩,
        ⟨205, false, 2, 207, 56⟩,
        ⟨205, false, 3, 208, 64⟩,
        ⟨205, false, 4, 210, 72⟩,
        ⟨205, true, 0, 204, 176⟩,
        ⟨205, true, 1, 204, 176⟩,
        ⟨205, true, 2, 203, 184⟩,
        ⟨205, true, 3, 201, 192⟩,
        ⟨205, true, 4, 194, 200⟩,
        ⟨206, false, 0, 207, 48⟩,
        ⟨206, false, 1, 207, 48⟩,
        ⟨206, false, 2, 208, 56⟩,
        ⟨206, false, 3, 209, 64⟩,
        ⟨206, false, 4, 211, 72⟩,
        ⟨206, true, 0, 205, 176⟩,
        ⟨206, true, 1, 205, 176⟩,
        ⟨206, true, 2, 204, 184⟩,
        ⟨206, true, 3, 202, 192⟩,
        ⟨206, true, 4, 196, 200⟩,
        ⟨207, false, 0, 208, 48⟩,
        ⟨207, false, 1, 208, 48⟩,
        ⟨207, false, 2, 208, 56⟩,
        ⟨207, false, 3, 210, 64⟩,
        ⟨207, false, 4, 212, 72⟩,
        ⟨207, true, 0, 206, 176⟩,
        ⟨207, true, 1, 206, 176⟩,
        ⟨207, true, 2, 205, 184⟩,
        ⟨207, true, 3, 203, 192⟩,
        ⟨207, true, 4, 198, 200⟩,
        ⟨208, false, 0, 209, 56⟩,
        ⟨208, false, 1, 209, 56⟩,
        ⟨208, false, 2, 209, 56⟩,
        ⟨208, false, 3, 210, 64⟩,
        ⟨208, false, 4, 212, 72⟩,
        ⟨208, true, 0, 206, 184⟩,
        ⟨208, true, 1, 206, 184⟩,
        ⟨208, true, 2, 206, 184⟩,
        ⟨208, true, 3, 204, 192⟩,
        ⟨208, true, 4, 200, 200⟩,
        ⟨209, false, 0, 210, 56⟩,
        ⟨209, false, 1, 210, 56⟩,
        ⟨209, false, 2, 210, 56⟩,
        ⟨209, false, 3, 211, 64⟩,
        ⟨209, false, 4, 213, 72⟩,
        ⟨209, true, 0, 208, 184⟩,
        ⟨209, true, 1, 208, 184⟩,
        ⟨209, true, 2, 208, 184⟩,
        ⟨209, true, 3, 206, 192⟩,
        ⟨209, true, 4, 202, 200⟩,
        ⟨210, false, 0, 211, 56⟩,
        ⟨210, false, 1, 211, 56⟩,
        ⟨210, false, 2, 211, 56⟩,
        ⟨210, false, 3, 212, 64⟩,
        ⟨210, false, 4, 214, 72⟩,
        ⟨210, true, 0, 209, 184⟩,
        ⟨210, true, 1, 209, 184⟩,
        ⟨210, true, 2, 209, 184⟩,
        ⟨210, true, 3, 208, 192⟩,
        ⟨210, true, 4, 204, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form21 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2170-2271):
      /-- `formReal` on every finite code, both signs and every `F`, part 21. -/
      def form21 : List FormVec := [
        ⟨211, false, 0, 212, 56⟩,
        ⟨211, false, 1, 212, 56⟩,
        ⟨211, false, 2, 212, 56⟩,
        ⟨211, false, 3, 213, 64⟩,
        ⟨211, false, 4, 215, 72⟩,
        ⟨211, true, 0, 210, 184⟩,
        ⟨211, true, 1, 210, 184⟩,
        ⟨211, true, 2, 210, 184⟩,
        ⟨211, true, 3, 209, 192⟩,
        ⟨211, true, 4, 206, 200⟩,
        ⟨212, false, 0, 213, 56⟩,
        ⟨212, false, 1, 213, 56⟩,
        ⟨212, false, 2, 213, 56⟩,
        ⟨212, false, 3, 214, 64⟩,
        ⟨212, false, 4, 216, 72⟩,
        ⟨212, true, 0, 211, 184⟩,
        ⟨212, true, 1, 211, 184⟩,
        ⟨212, true, 2, 211, 184⟩,
        ⟨212, true, 3, 210, 192⟩,
        ⟨212, true, 4, 208, 200⟩,
        ⟨213, false, 0, 214, 56⟩,
        ⟨213, false, 1, 214, 56⟩,
        ⟨213, false, 2, 214, 56⟩,
        ⟨213, false, 3, 215, 64⟩,
        ⟨213, false, 4, 216, 72⟩,
        ⟨213, true, 0, 212, 184⟩,
        ⟨213, true, 1, 212, 184⟩,
        ⟨213, true, 2, 212, 184⟩,
        ⟨213, true, 3, 211, 192⟩,
        ⟨213, true, 4, 209, 200⟩,
        ⟨214, false, 0, 215, 56⟩,
        ⟨214, false, 1, 215, 56⟩,
        ⟨214, false, 2, 215, 56⟩,
        ⟨214, false, 3, 216, 64⟩,
        ⟨214, false, 4, 217, 72⟩,
        ⟨214, true, 0, 213, 184⟩,
        ⟨214, true, 1, 213, 184⟩,
        ⟨214, true, 2, 213, 184⟩,
        ⟨214, true, 3, 212, 192⟩,
        ⟨214, true, 4, 210, 200⟩,
        ⟨215, false, 0, 216, 56⟩,
        ⟨215, false, 1, 216, 56⟩,
        ⟨215, false, 2, 216, 56⟩,
        ⟨215, false, 3, 216, 64⟩,
        ⟨215, false, 4, 218, 72⟩,
        ⟨215, true, 0, 214, 184⟩,
        ⟨215, true, 1, 214, 184⟩,
        ⟨215, true, 2, 214, 184⟩,
        ⟨215, true, 3, 213, 192⟩,
        ⟨215, true, 4, 211, 200⟩,
        ⟨216, false, 0, 217, 64⟩,
        ⟨216, false, 1, 217, 64⟩,
        ⟨216, false, 2, 217, 64⟩,
        ⟨216, false, 3, 217, 64⟩,
        ⟨216, false, 4, 218, 72⟩,
        ⟨216, true, 0, 214, 192⟩,
        ⟨216, true, 1, 214, 192⟩,
        ⟨216, true, 2, 214, 192⟩,
        ⟨216, true, 3, 214, 192⟩,
        ⟨216, true, 4, 212, 200⟩,
        ⟨217, false, 0, 218, 64⟩,
        ⟨217, false, 1, 218, 64⟩,
        ⟨217, false, 2, 218, 64⟩,
        ⟨217, false, 3, 218, 64⟩,
        ⟨217, false, 4, 219, 72⟩,
        ⟨217, true, 0, 216, 192⟩,
        ⟨217, true, 1, 216, 192⟩,
        ⟨217, true, 2, 216, 192⟩,
        ⟨217, true, 3, 216, 192⟩,
        ⟨217, true, 4, 214, 200⟩,
        ⟨218, false, 0, 219, 64⟩,
        ⟨218, false, 1, 219, 64⟩,
        ⟨218, false, 2, 219, 64⟩,
        ⟨218, false, 3, 219, 64⟩,
        ⟨218, false, 4, 220, 72⟩,
        ⟨218, true, 0, 217, 192⟩,
        ⟨218, true, 1, 217, 192⟩,
        ⟨218, true, 2, 217, 192⟩,
        ⟨218, true, 3, 217, 192⟩,
        ⟨218, true, 4, 216, 200⟩,
        ⟨219, false, 0, 220, 64⟩,
        ⟨219, false, 1, 220, 64⟩,
        ⟨219, false, 2, 220, 64⟩,
        ⟨219, false, 3, 220, 64⟩,
        ⟨219, false, 4, 221, 72⟩,
        ⟨219, true, 0, 218, 192⟩,
        ⟨219, true, 1, 218, 192⟩,
        ⟨219, true, 2, 218, 192⟩,
        ⟨219, true, 3, 218, 192⟩,
        ⟨219, true, 4, 217, 200⟩,
        ⟨220, false, 0, 221, 64⟩,
        ⟨220, false, 1, 221, 64⟩,
        ⟨220, false, 2, 221, 64⟩,
        ⟨220, false, 3, 221, 64⟩,
        ⟨220, false, 4, 222, 72⟩,
        ⟨220, true, 0, 219, 192⟩,
        ⟨220, true, 1, 219, 192⟩,
        ⟨220, true, 2, 219, 192⟩,
        ⟨220, true, 3, 219, 192⟩,
        ⟨220, true, 4, 218, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form22 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2273-2374):
      /-- `formReal` on every finite code, both signs and every `F`, part 22. -/
      def form22 : List FormVec := [
        ⟨221, false, 0, 222, 64⟩,
        ⟨221, false, 1, 222, 64⟩,
        ⟨221, false, 2, 222, 64⟩,
        ⟨221, false, 3, 222, 64⟩,
        ⟨221, false, 4, 223, 72⟩,
        ⟨221, true, 0, 220, 192⟩,
        ⟨221, true, 1, 220, 192⟩,
        ⟨221, true, 2, 220, 192⟩,
        ⟨221, true, 3, 220, 192⟩,
        ⟨221, true, 4, 219, 200⟩,
        ⟨222, false, 0, 223, 64⟩,
        ⟨222, false, 1, 223, 64⟩,
        ⟨222, false, 2, 223, 64⟩,
        ⟨222, false, 3, 223, 64⟩,
        ⟨222, false, 4, 224, 72⟩,
        ⟨222, true, 0, 221, 192⟩,
        ⟨222, true, 1, 221, 192⟩,
        ⟨222, true, 2, 221, 192⟩,
        ⟨222, true, 3, 221, 192⟩,
        ⟨222, true, 4, 220, 200⟩,
        ⟨223, false, 0, 224, 64⟩,
        ⟨223, false, 1, 224, 64⟩,
        ⟨223, false, 2, 224, 64⟩,
        ⟨223, false, 3, 224, 64⟩,
        ⟨223, false, 4, 224, 72⟩,
        ⟨223, true, 0, 222, 192⟩,
        ⟨223, true, 1, 222, 192⟩,
        ⟨223, true, 2, 222, 192⟩,
        ⟨223, true, 3, 222, 192⟩,
        ⟨223, true, 4, 221, 200⟩,
        ⟨224, false, 0, 225, 72⟩,
        ⟨224, false, 1, 225, 72⟩,
        ⟨224, false, 2, 225, 72⟩,
        ⟨224, false, 3, 225, 72⟩,
        ⟨224, false, 4, 225, 72⟩,
        ⟨224, true, 0, 222, 200⟩,
        ⟨224, true, 1, 222, 200⟩,
        ⟨224, true, 2, 222, 200⟩,
        ⟨224, true, 3, 222, 200⟩,
        ⟨224, true, 4, 222, 200⟩,
        ⟨225, false, 0, 226, 72⟩,
        ⟨225, false, 1, 226, 72⟩,
        ⟨225, false, 2, 226, 72⟩,
        ⟨225, false, 3, 226, 72⟩,
        ⟨225, false, 4, 226, 72⟩,
        ⟨225, true, 0, 224, 200⟩,
        ⟨225, true, 1, 224, 200⟩,
        ⟨225, true, 2, 224, 200⟩,
        ⟨225, true, 3, 224, 200⟩,
        ⟨225, true, 4, 224, 200⟩,
        ⟨226, false, 0, 227, 72⟩,
        ⟨226, false, 1, 227, 72⟩,
        ⟨226, false, 2, 227, 72⟩,
        ⟨226, false, 3, 227, 72⟩,
        ⟨226, false, 4, 227, 72⟩,
        ⟨226, true, 0, 225, 200⟩,
        ⟨226, true, 1, 225, 200⟩,
        ⟨226, true, 2, 225, 200⟩,
        ⟨226, true, 3, 225, 200⟩,
        ⟨226, true, 4, 225, 200⟩,
        ⟨227, false, 0, 228, 72⟩,
        ⟨227, false, 1, 228, 72⟩,
        ⟨227, false, 2, 228, 72⟩,
        ⟨227, false, 3, 228, 72⟩,
        ⟨227, false, 4, 228, 72⟩,
        ⟨227, true, 0, 226, 200⟩,
        ⟨227, true, 1, 226, 200⟩,
        ⟨227, true, 2, 226, 200⟩,
        ⟨227, true, 3, 226, 200⟩,
        ⟨227, true, 4, 226, 200⟩,
        ⟨228, false, 0, 229, 72⟩,
        ⟨228, false, 1, 229, 72⟩,
        ⟨228, false, 2, 229, 72⟩,
        ⟨228, false, 3, 229, 72⟩,
        ⟨228, false, 4, 229, 72⟩,
        ⟨228, true, 0, 227, 200⟩,
        ⟨228, true, 1, 227, 200⟩,
        ⟨228, true, 2, 227, 200⟩,
        ⟨228, true, 3, 227, 200⟩,
        ⟨228, true, 4, 227, 200⟩,
        ⟨229, false, 0, 230, 72⟩,
        ⟨229, false, 1, 230, 72⟩,
        ⟨229, false, 2, 230, 72⟩,
        ⟨229, false, 3, 230, 72⟩,
        ⟨229, false, 4, 230, 72⟩,
        ⟨229, true, 0, 228, 200⟩,
        ⟨229, true, 1, 228, 200⟩,
        ⟨229, true, 2, 228, 200⟩,
        ⟨229, true, 3, 228, 200⟩,
        ⟨229, true, 4, 228, 200⟩,
        ⟨230, false, 0, 231, 72⟩,
        ⟨230, false, 1, 231, 72⟩,
        ⟨230, false, 2, 231, 72⟩,
        ⟨230, false, 3, 231, 72⟩,
        ⟨230, false, 4, 231, 72⟩,
        ⟨230, true, 0, 229, 200⟩,
        ⟨230, true, 1, 229, 200⟩,
        ⟨230, true, 2, 229, 200⟩,
        ⟨230, true, 3, 229, 200⟩,
        ⟨230, true, 4, 229, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form23 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2376-2477):
      /-- `formReal` on every finite code, both signs and every `F`, part 23. -/
      def form23 : List FormVec := [
        ⟨231, false, 0, 232, 72⟩,
        ⟨231, false, 1, 232, 72⟩,
        ⟨231, false, 2, 232, 72⟩,
        ⟨231, false, 3, 232, 72⟩,
        ⟨231, false, 4, 232, 72⟩,
        ⟨231, true, 0, 230, 200⟩,
        ⟨231, true, 1, 230, 200⟩,
        ⟨231, true, 2, 230, 200⟩,
        ⟨231, true, 3, 230, 200⟩,
        ⟨231, true, 4, 230, 200⟩,
        ⟨232, false, 0, 233, 80⟩,
        ⟨232, false, 1, 233, 80⟩,
        ⟨232, false, 2, 233, 80⟩,
        ⟨232, false, 3, 233, 80⟩,
        ⟨232, false, 4, 233, 80⟩,
        ⟨232, true, 0, 230, 208⟩,
        ⟨232, true, 1, 230, 208⟩,
        ⟨232, true, 2, 230, 208⟩,
        ⟨232, true, 3, 230, 208⟩,
        ⟨232, true, 4, 230, 208⟩,
        ⟨233, false, 0, 234, 80⟩,
        ⟨233, false, 1, 234, 80⟩,
        ⟨233, false, 2, 234, 80⟩,
        ⟨233, false, 3, 234, 80⟩,
        ⟨233, false, 4, 234, 80⟩,
        ⟨233, true, 0, 232, 208⟩,
        ⟨233, true, 1, 232, 208⟩,
        ⟨233, true, 2, 232, 208⟩,
        ⟨233, true, 3, 232, 208⟩,
        ⟨233, true, 4, 232, 208⟩,
        ⟨234, false, 0, 235, 80⟩,
        ⟨234, false, 1, 235, 80⟩,
        ⟨234, false, 2, 235, 80⟩,
        ⟨234, false, 3, 235, 80⟩,
        ⟨234, false, 4, 235, 80⟩,
        ⟨234, true, 0, 233, 208⟩,
        ⟨234, true, 1, 233, 208⟩,
        ⟨234, true, 2, 233, 208⟩,
        ⟨234, true, 3, 233, 208⟩,
        ⟨234, true, 4, 233, 208⟩,
        ⟨235, false, 0, 236, 80⟩,
        ⟨235, false, 1, 236, 80⟩,
        ⟨235, false, 2, 236, 80⟩,
        ⟨235, false, 3, 236, 80⟩,
        ⟨235, false, 4, 236, 80⟩,
        ⟨235, true, 0, 234, 208⟩,
        ⟨235, true, 1, 234, 208⟩,
        ⟨235, true, 2, 234, 208⟩,
        ⟨235, true, 3, 234, 208⟩,
        ⟨235, true, 4, 234, 208⟩,
        ⟨236, false, 0, 237, 80⟩,
        ⟨236, false, 1, 237, 80⟩,
        ⟨236, false, 2, 237, 80⟩,
        ⟨236, false, 3, 237, 80⟩,
        ⟨236, false, 4, 237, 80⟩,
        ⟨236, true, 0, 235, 208⟩,
        ⟨236, true, 1, 235, 208⟩,
        ⟨236, true, 2, 235, 208⟩,
        ⟨236, true, 3, 235, 208⟩,
        ⟨236, true, 4, 235, 208⟩,
        ⟨237, false, 0, 238, 80⟩,
        ⟨237, false, 1, 238, 80⟩,
        ⟨237, false, 2, 238, 80⟩,
        ⟨237, false, 3, 238, 80⟩,
        ⟨237, false, 4, 238, 80⟩,
        ⟨237, true, 0, 236, 208⟩,
        ⟨237, true, 1, 236, 208⟩,
        ⟨237, true, 2, 236, 208⟩,
        ⟨237, true, 3, 236, 208⟩,
        ⟨237, true, 4, 236, 208⟩,
        ⟨238, false, 0, 239, 80⟩,
        ⟨238, false, 1, 239, 80⟩,
        ⟨238, false, 2, 239, 80⟩,
        ⟨238, false, 3, 239, 80⟩,
        ⟨238, false, 4, 239, 80⟩,
        ⟨238, true, 0, 237, 208⟩,
        ⟨238, true, 1, 237, 208⟩,
        ⟨238, true, 2, 237, 208⟩,
        ⟨238, true, 3, 237, 208⟩,
        ⟨238, true, 4, 237, 208⟩,
        ⟨239, false, 0, 240, 80⟩,
        ⟨239, false, 1, 240, 80⟩,
        ⟨239, false, 2, 240, 80⟩,
        ⟨239, false, 3, 240, 80⟩,
        ⟨239, false, 4, 240, 80⟩,
        ⟨239, true, 0, 238, 208⟩,
        ⟨239, true, 1, 238, 208⟩,
        ⟨239, true, 2, 238, 208⟩,
        ⟨239, true, 3, 238, 208⟩,
        ⟨239, true, 4, 238, 208⟩,
        ⟨240, false, 0, 241, 88⟩,
        ⟨240, false, 1, 241, 88⟩,
        ⟨240, false, 2, 241, 88⟩,
        ⟨240, false, 3, 241, 88⟩,
        ⟨240, false, 4, 241, 88⟩,
        ⟨240, true, 0, 238, 216⟩,
        ⟨240, true, 1, 238, 216⟩,
        ⟨240, true, 2, 238, 216⟩,
        ⟨240, true, 3, 238, 216⟩,
        ⟨240, true, 4, 238, 216⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form24 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2479-2580):
      /-- `formReal` on every finite code, both signs and every `F`, part 24. -/
      def form24 : List FormVec := [
        ⟨241, false, 0, 242, 88⟩,
        ⟨241, false, 1, 242, 88⟩,
        ⟨241, false, 2, 242, 88⟩,
        ⟨241, false, 3, 242, 88⟩,
        ⟨241, false, 4, 242, 88⟩,
        ⟨241, true, 0, 240, 216⟩,
        ⟨241, true, 1, 240, 216⟩,
        ⟨241, true, 2, 240, 216⟩,
        ⟨241, true, 3, 240, 216⟩,
        ⟨241, true, 4, 240, 216⟩,
        ⟨242, false, 0, 243, 88⟩,
        ⟨242, false, 1, 243, 88⟩,
        ⟨242, false, 2, 243, 88⟩,
        ⟨242, false, 3, 243, 88⟩,
        ⟨242, false, 4, 243, 88⟩,
        ⟨242, true, 0, 241, 216⟩,
        ⟨242, true, 1, 241, 216⟩,
        ⟨242, true, 2, 241, 216⟩,
        ⟨242, true, 3, 241, 216⟩,
        ⟨242, true, 4, 241, 216⟩,
        ⟨243, false, 0, 244, 88⟩,
        ⟨243, false, 1, 244, 88⟩,
        ⟨243, false, 2, 244, 88⟩,
        ⟨243, false, 3, 244, 88⟩,
        ⟨243, false, 4, 244, 88⟩,
        ⟨243, true, 0, 242, 216⟩,
        ⟨243, true, 1, 242, 216⟩,
        ⟨243, true, 2, 242, 216⟩,
        ⟨243, true, 3, 242, 216⟩,
        ⟨243, true, 4, 242, 216⟩,
        ⟨244, false, 0, 245, 88⟩,
        ⟨244, false, 1, 245, 88⟩,
        ⟨244, false, 2, 245, 88⟩,
        ⟨244, false, 3, 245, 88⟩,
        ⟨244, false, 4, 245, 88⟩,
        ⟨244, true, 0, 243, 216⟩,
        ⟨244, true, 1, 243, 216⟩,
        ⟨244, true, 2, 243, 216⟩,
        ⟨244, true, 3, 243, 216⟩,
        ⟨244, true, 4, 243, 216⟩,
        ⟨245, false, 0, 246, 88⟩,
        ⟨245, false, 1, 246, 88⟩,
        ⟨245, false, 2, 246, 88⟩,
        ⟨245, false, 3, 246, 88⟩,
        ⟨245, false, 4, 246, 88⟩,
        ⟨245, true, 0, 244, 216⟩,
        ⟨245, true, 1, 244, 216⟩,
        ⟨245, true, 2, 244, 216⟩,
        ⟨245, true, 3, 244, 216⟩,
        ⟨245, true, 4, 244, 216⟩,
        ⟨246, false, 0, 247, 88⟩,
        ⟨246, false, 1, 247, 88⟩,
        ⟨246, false, 2, 247, 88⟩,
        ⟨246, false, 3, 247, 88⟩,
        ⟨246, false, 4, 247, 88⟩,
        ⟨246, true, 0, 245, 216⟩,
        ⟨246, true, 1, 245, 216⟩,
        ⟨246, true, 2, 245, 216⟩,
        ⟨246, true, 3, 245, 216⟩,
        ⟨246, true, 4, 245, 216⟩,
        ⟨247, false, 0, 248, 88⟩,
        ⟨247, false, 1, 248, 88⟩,
        ⟨247, false, 2, 248, 88⟩,
        ⟨247, false, 3, 248, 88⟩,
        ⟨247, false, 4, 248, 88⟩,
        ⟨247, true, 0, 246, 216⟩,
        ⟨247, true, 1, 246, 216⟩,
        ⟨247, true, 2, 246, 216⟩,
        ⟨247, true, 3, 246, 216⟩,
        ⟨247, true, 4, 246, 216⟩,
        ⟨248, false, 0, 249, 96⟩,
        ⟨248, false, 1, 249, 96⟩,
        ⟨248, false, 2, 249, 96⟩,
        ⟨248, false, 3, 249, 96⟩,
        ⟨248, false, 4, 249, 96⟩,
        ⟨248, true, 0, 246, 224⟩,
        ⟨248, true, 1, 246, 224⟩,
        ⟨248, true, 2, 246, 224⟩,
        ⟨248, true, 3, 246, 224⟩,
        ⟨248, true, 4, 246, 224⟩,
        ⟨249, false, 0, 250, 96⟩,
        ⟨249, false, 1, 250, 96⟩,
        ⟨249, false, 2, 250, 96⟩,
        ⟨249, false, 3, 250, 96⟩,
        ⟨249, false, 4, 250, 96⟩,
        ⟨249, true, 0, 248, 224⟩,
        ⟨249, true, 1, 248, 224⟩,
        ⟨249, true, 2, 248, 224⟩,
        ⟨249, true, 3, 248, 224⟩,
        ⟨249, true, 4, 248, 224⟩,
        ⟨250, false, 0, 251, 96⟩,
        ⟨250, false, 1, 251, 96⟩,
        ⟨250, false, 2, 251, 96⟩,
        ⟨250, false, 3, 251, 96⟩,
        ⟨250, false, 4, 251, 96⟩,
        ⟨250, true, 0, 249, 224⟩,
        ⟨250, true, 1, 249, 224⟩,
        ⟨250, true, 2, 249, 224⟩,
        ⟨250, true, 3, 249, 224⟩,
        ⟨250, true, 4, 249, 224⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form25 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2582-2623):
      /-- `formReal` on every finite code, both signs and every `F`, part 25. -/
      def form25 : List FormVec := [
        ⟨251, false, 0, 252, 96⟩,
        ⟨251, false, 1, 252, 96⟩,
        ⟨251, false, 2, 252, 96⟩,
        ⟨251, false, 3, 252, 96⟩,
        ⟨251, false, 4, 252, 96⟩,
        ⟨251, true, 0, 250, 224⟩,
        ⟨251, true, 1, 250, 224⟩,
        ⟨251, true, 2, 250, 224⟩,
        ⟨251, true, 3, 250, 224⟩,
        ⟨251, true, 4, 250, 224⟩,
        ⟨252, false, 0, 253, 96⟩,
        ⟨252, false, 1, 253, 96⟩,
        ⟨252, false, 2, 253, 96⟩,
        ⟨252, false, 3, 253, 96⟩,
        ⟨252, false, 4, 253, 96⟩,
        ⟨252, true, 0, 251, 224⟩,
        ⟨252, true, 1, 251, 224⟩,
        ⟨252, true, 2, 251, 224⟩,
        ⟨252, true, 3, 251, 224⟩,
        ⟨252, true, 4, 251, 224⟩,
        ⟨253, false, 0, 254, 96⟩,
        ⟨253, false, 1, 254, 96⟩,
        ⟨253, false, 2, 254, 96⟩,
        ⟨253, false, 3, 254, 96⟩,
        ⟨253, false, 4, 254, 96⟩,
        ⟨253, true, 0, 252, 224⟩,
        ⟨253, true, 1, 252, 224⟩,
        ⟨253, true, 2, 252, 224⟩,
        ⟨253, true, 3, 252, 224⟩,
        ⟨253, true, 4, 252, 224⟩,
        ⟨254, false, 0, 254, 96⟩,
        ⟨254, false, 1, 254, 96⟩,
        ⟨254, false, 2, 254, 96⟩,
        ⟨254, false, 3, 254, 96⟩,
        ⟨254, false, 4, 254, 96⟩,
        ⟨254, true, 0, 253, 224⟩,
        ⟨254, true, 1, 253, 224⟩,
        ⟨254, true, 2, 253, 224⟩,
        ⟨254, true, 3, 253, 224⟩,
        ⟨254, true, 4, 253, 224⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form3 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:316-417):
      /-- `formReal` on every finite code, both signs and every `F`, part 3. -/
      def form3 : List FormVec := [
        ⟨30, false, 0, 161, 40⟩,
        ⟨30, false, 1, 172, 48⟩,
        ⟨30, false, 2, 182, 56⟩,
        ⟨30, false, 3, 191, 64⟩,
        ⟨30, false, 4, 200, 72⟩,
        ⟨30, true, 0, 44, 168⟩,
        ⟨30, true, 1, 50, 176⟩,
        ⟨30, true, 2, 57, 184⟩,
        ⟨30, true, 3, 64, 192⟩,
        ⟨30, true, 4, 72, 200⟩,
        ⟨31, false, 0, 160, 40⟩,
        ⟨31, false, 1, 172, 48⟩,
        ⟨31, false, 2, 182, 56⟩,
        ⟨31, false, 3, 191, 64⟩,
        ⟨31, false, 4, 200, 72⟩,
        ⟨31, true, 0, 44, 168⟩,
        ⟨31, true, 1, 50, 176⟩,
        ⟨31, true, 2, 57, 184⟩,
        ⟨31, true, 3, 64, 192⟩,
        ⟨31, true, 4, 72, 200⟩,
        ⟨32, false, 0, 160, 40⟩,
        ⟨32, false, 1, 172, 48⟩,
        ⟨32, false, 2, 182, 56⟩,
        ⟨32, false, 3, 191, 64⟩,
        ⟨32, false, 4, 200, 72⟩,
        ⟨32, true, 0, 44, 168⟩,
        ⟨32, true, 1, 50, 176⟩,
        ⟨32, true, 2, 57, 184⟩,
        ⟨32, true, 3, 64, 192⟩,
        ⟨32, true, 4, 72, 200⟩,
        ⟨33, false, 0, 158, 40⟩,
        ⟨33, false, 1, 172, 48⟩,
        ⟨33, false, 2, 182, 56⟩,
        ⟨33, false, 3, 191, 64⟩,
        ⟨33, false, 4, 199, 72⟩,
        ⟨33, true, 0, 44, 168⟩,
        ⟨33, true, 1, 50, 176⟩,
        ⟨33, true, 2, 57, 184⟩,
        ⟨33, true, 3, 65, 192⟩,
        ⟨33, true, 4, 72, 200⟩,
        ⟨34, false, 0, 156, 40⟩,
        ⟨34, false, 1, 171, 48⟩,
        ⟨34, false, 2, 182, 56⟩,
        ⟨34, false, 3, 191, 64⟩,
        ⟨34, false, 4, 199, 72⟩,
        ⟨34, true, 0, 45, 168⟩,
        ⟨34, true, 1, 50, 176⟩,
        ⟨34, true, 2, 57, 184⟩,
        ⟨34, true, 3, 65, 192⟩,
        ⟨34, true, 4, 72, 200⟩,
        ⟨35, false, 0, 154, 40⟩,
        ⟨35, false, 1, 170, 48⟩,
        ⟨35, false, 2, 181, 56⟩,
        ⟨35, false, 3, 191, 64⟩,
        ⟨35, false, 4, 199, 72⟩,
        ⟨35, true, 0, 46, 168⟩,
        ⟨35, true, 1, 51, 176⟩,
        ⟨35, true, 2, 57, 184⟩,
        ⟨35, true, 3, 65, 192⟩,
        ⟨35, true, 4, 72, 200⟩,
        ⟨36, false, 0, 152, 40⟩,
        ⟨36, false, 1, 170, 48⟩,
        ⟨36, false, 2, 181, 56⟩,
        ⟨36, false, 3, 190, 64⟩,
        ⟨36, false, 4, 199, 72⟩,
        ⟨36, true, 0, 46, 168⟩,
        ⟨36, true, 1, 51, 176⟩,
        ⟨36, true, 2, 58, 184⟩,
        ⟨36, true, 3, 65, 192⟩,
        ⟨36, true, 4, 72, 200⟩,
        ⟨37, false, 0, 148, 40⟩,
        ⟨37, false, 1, 170, 48⟩,
        ⟨37, false, 2, 181, 56⟩,
        ⟨37, false, 3, 190, 64⟩,
        ⟨37, false, 4, 199, 72⟩,
        ⟨37, true, 0, 46, 168⟩,
        ⟨37, true, 1, 51, 176⟩,
        ⟨37, true, 2, 58, 184⟩,
        ⟨37, true, 3, 65, 192⟩,
        ⟨37, true, 4, 72, 200⟩,
        ⟨38, false, 0, 144, 40⟩,
        ⟨38, false, 1, 169, 48⟩,
        ⟨38, false, 2, 180, 56⟩,
        ⟨38, false, 3, 190, 64⟩,
        ⟨38, false, 4, 199, 72⟩,
        ⟨38, true, 0, 47, 168⟩,
        ⟨38, true, 1, 52, 176⟩,
        ⟨38, true, 2, 58, 184⟩,
        ⟨38, true, 3, 65, 192⟩,
        ⟨38, true, 4, 72, 200⟩,
        ⟨39, false, 0, 136, 40⟩,
        ⟨39, false, 1, 168, 48⟩,
        ⟨39, false, 2, 180, 56⟩,
        ⟨39, false, 3, 190, 64⟩,
        ⟨39, false, 4, 199, 72⟩,
        ⟨39, true, 0, 48, 168⟩,
        ⟨39, true, 1, 52, 176⟩,
        ⟨39, true, 2, 58, 184⟩,
        ⟨39, true, 3, 65, 192⟩,
        ⟨39, true, 4, 72, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form4 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:419-520):
      /-- `formReal` on every finite code, both signs and every `F`, part 4. -/
      def form4 : List FormVec := [
        ⟨40, false, 0, 0, 40⟩,
        ⟨40, false, 1, 168, 48⟩,
        ⟨40, false, 2, 180, 56⟩,
        ⟨40, false, 3, 190, 64⟩,
        ⟨40, false, 4, 199, 72⟩,
        ⟨40, true, 0, 48, 168⟩,
        ⟨40, true, 1, 52, 176⟩,
        ⟨40, true, 2, 58, 184⟩,
        ⟨40, true, 3, 65, 192⟩,
        ⟨40, true, 4, 72, 200⟩,
        ⟨41, false, 0, 16, 40⟩,
        ⟨41, false, 1, 166, 48⟩,
        ⟨41, false, 2, 180, 56⟩,
        ⟨41, false, 3, 190, 64⟩,
        ⟨41, false, 4, 199, 72⟩,
        ⟨41, true, 0, 48, 168⟩,
        ⟨41, true, 1, 52, 176⟩,
        ⟨41, true, 2, 58, 184⟩,
        ⟨41, true, 3, 65, 192⟩,
        ⟨41, true, 4, 73, 200⟩,
        ⟨42, false, 0, 24, 40⟩,
        ⟨42, false, 1, 164, 48⟩,
        ⟨42, false, 2, 179, 56⟩,
        ⟨42, false, 3, 190, 64⟩,
        ⟨42, false, 4, 199, 72⟩,
        ⟨42, true, 0, 49, 168⟩,
        ⟨42, true, 1, 53, 176⟩,
        ⟨42, true, 2, 58, 184⟩,
        ⟨42, true, 3, 65, 192⟩,
        ⟨42, true, 4, 73, 200⟩,
        ⟨43, false, 0, 28, 40⟩,
        ⟨43, false, 1, 162, 48⟩,
        ⟨43, false, 2, 178, 56⟩,
        ⟨43, false, 3, 189, 64⟩,
        ⟨43, false, 4, 199, 72⟩,
        ⟨43, true, 0, 50, 168⟩,
        ⟨43, true, 1, 54, 176⟩,
        ⟨43, true, 2, 59, 184⟩,
        ⟨43, true, 3, 65, 192⟩,
        ⟨43, true, 4, 73, 200⟩,
        ⟨44, false, 0, 32, 40⟩,
        ⟨44, false, 1, 160, 48⟩,
        ⟨44, false, 2, 178, 56⟩,
        ⟨44, false, 3, 189, 64⟩,
        ⟨44, false, 4, 198, 72⟩,
        ⟨44, true, 0, 50, 168⟩,
        ⟨44, true, 1, 54, 176⟩,
        ⟨44, true, 2, 59, 184⟩,
        ⟨44, true, 3, 66, 192⟩,
        ⟨44, true, 4, 73, 200⟩,
        ⟨45, false, 0, 34, 40⟩,
        ⟨45, false, 1, 156, 48⟩,
        ⟨45, false, 2, 178, 56⟩,
        ⟨45, false, 3, 189, 64⟩,
        ⟨45, false, 4, 198, 72⟩,
        ⟨45, true, 0, 50, 168⟩,
        ⟨45, true, 1, 54, 176⟩,
        ⟨45, true, 2, 59, 184⟩,
        ⟨45, true, 3, 66, 192⟩,
        ⟨45, true, 4, 73, 200⟩,
        ⟨46, false, 0, 36, 40⟩,
        ⟨46, false, 1, 152, 48⟩,
        ⟨46, false, 2, 177, 56⟩,
        ⟨46, false, 3, 188, 64⟩,
        ⟨46, false, 4, 198, 72⟩,
        ⟨46, true, 0, 51, 168⟩,
        ⟨46, true, 1, 55, 176⟩,
        ⟨46, true, 2, 60, 184⟩,
        ⟨46, true, 3, 66, 192⟩,
        ⟨46, true, 4, 73, 200⟩,
        ⟨47, false, 0, 38, 40⟩,
        ⟨47, false, 1, 144, 48⟩,
        ⟨47, false, 2, 176, 56⟩,
        ⟨47, false, 3, 188, 64⟩,
        ⟨47, false, 4, 198, 72⟩,
        ⟨47, true, 0, 52, 168⟩,
        ⟨47, true, 1, 56, 176⟩,
        ⟨47, true, 2, 60, 184⟩,
        ⟨47, true, 3, 66, 192⟩,
        ⟨47, true, 4, 73, 200⟩,
        ⟨48, false, 0, 40, 40⟩,
        ⟨48, false, 1, 0, 48⟩,
        ⟨48, false, 2, 176, 56⟩,
        ⟨48, false, 3, 188, 64⟩,
        ⟨48, false, 4, 198, 72⟩,
        ⟨48, true, 0, 52, 168⟩,
        ⟨48, true, 1, 56, 176⟩,
        ⟨48, true, 2, 60, 184⟩,
        ⟨48, true, 3, 66, 192⟩,
        ⟨48, true, 4, 73, 200⟩,
        ⟨49, false, 0, 42, 40⟩,
        ⟨49, false, 1, 24, 48⟩,
        ⟨49, false, 2, 174, 56⟩,
        ⟨49, false, 3, 188, 64⟩,
        ⟨49, false, 4, 198, 72⟩,
        ⟨49, true, 0, 53, 168⟩,
        ⟨49, true, 1, 56, 176⟩,
        ⟨49, true, 2, 60, 184⟩,
        ⟨49, true, 3, 66, 192⟩,
        ⟨49, true, 4, 73, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form5 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:522-623):
      /-- `formReal` on every finite code, both signs and every `F`, part 5. -/
      def form5 : List FormVec := [
        ⟨50, false, 0, 44, 40⟩,
        ⟨50, false, 1, 32, 48⟩,
        ⟨50, false, 2, 172, 56⟩,
        ⟨50, false, 3, 187, 64⟩,
        ⟨50, false, 4, 198, 72⟩,
        ⟨50, true, 0, 54, 168⟩,
        ⟨50, true, 1, 57, 176⟩,
        ⟨50, true, 2, 61, 184⟩,
        ⟨50, true, 3, 66, 192⟩,
        ⟨50, true, 4, 73, 200⟩,
        ⟨51, false, 0, 46, 40⟩,
        ⟨51, false, 1, 36, 48⟩,
        ⟨51, false, 2, 170, 56⟩,
        ⟨51, false, 3, 186, 64⟩,
        ⟨51, false, 4, 197, 72⟩,
        ⟨51, true, 0, 55, 168⟩,
        ⟨51, true, 1, 58, 176⟩,
        ⟨51, true, 2, 62, 184⟩,
        ⟨51, true, 3, 67, 192⟩,
        ⟨51, true, 4, 73, 200⟩,
        ⟨52, false, 0, 48, 40⟩,
        ⟨52, false, 1, 40, 48⟩,
        ⟨52, false, 2, 168, 56⟩,
        ⟨52, false, 3, 186, 64⟩,
        ⟨52, false, 4, 197, 72⟩,
        ⟨52, true, 0, 56, 168⟩,
        ⟨52, true, 1, 58, 176⟩,
        ⟨52, true, 2, 62, 184⟩,
        ⟨52, true, 3, 67, 192⟩,
        ⟨52, true, 4, 74, 200⟩,
        ⟨53, false, 0, 49, 40⟩,
        ⟨53, false, 1, 42, 48⟩,
        ⟨53, false, 2, 164, 56⟩,
        ⟨53, false, 3, 186, 64⟩,
        ⟨53, false, 4, 197, 72⟩,
        ⟨53, true, 0, 56, 168⟩,
        ⟨53, true, 1, 58, 176⟩,
        ⟨53, true, 2, 62, 184⟩,
        ⟨53, true, 3, 67, 192⟩,
        ⟨53, true, 4, 74, 200⟩,
        ⟨54, false, 0, 50, 40⟩,
        ⟨54, false, 1, 44, 48⟩,
        ⟨54, false, 2, 160, 56⟩,
        ⟨54, false, 3, 185, 64⟩,
        ⟨54, false, 4, 196, 72⟩,
        ⟨54, true, 0, 57, 168⟩,
        ⟨54, true, 1, 59, 176⟩,
        ⟨54, true, 2, 63, 184⟩,
        ⟨54, true, 3, 68, 192⟩,
        ⟨54, true, 4, 74, 200⟩,
        ⟨55, false, 0, 51, 40⟩,
        ⟨55, false, 1, 46, 48⟩,
        ⟨55, false, 2, 152, 56⟩,
        ⟨55, false, 3, 184, 64⟩,
        ⟨55, false, 4, 196, 72⟩,
        ⟨55, true, 0, 58, 168⟩,
        ⟨55, true, 1, 60, 176⟩,
        ⟨55, true, 2, 64, 184⟩,
        ⟨55, true, 3, 68, 192⟩,
        ⟨55, true, 4, 74, 200⟩,
        ⟨56, false, 0, 52, 40⟩,
        ⟨56, false, 1, 48, 48⟩,
        ⟨56, false, 2, 0, 56⟩,
        ⟨56, false, 3, 184, 64⟩,
        ⟨56, false, 4, 196, 72⟩,
        ⟨56, true, 0, 58, 168⟩,
        ⟨56, true, 1, 60, 176⟩,
        ⟨56, true, 2, 64, 184⟩,
        ⟨56, true, 3, 68, 192⟩,
        ⟨56, true, 4, 74, 200⟩,
        ⟨57, false, 0, 54, 40⟩,
        ⟨57, false, 1, 50, 48⟩,
        ⟨57, false, 2, 32, 56⟩,
        ⟨57, false, 3, 182, 64⟩,
        ⟨57, false, 4, 196, 72⟩,
        ⟨57, true, 0, 59, 168⟩,
        ⟨57, true, 1, 61, 176⟩,
        ⟨57, true, 2, 64, 184⟩,
        ⟨57, true, 3, 68, 192⟩,
        ⟨57, true, 4, 74, 200⟩,
        ⟨58, false, 0, 56, 40⟩,
        ⟨58, false, 1, 52, 48⟩,
        ⟨58, false, 2, 40, 56⟩,
        ⟨58, false, 3, 180, 64⟩,
        ⟨58, false, 4, 195, 72⟩,
        ⟨58, true, 0, 60, 168⟩,
        ⟨58, true, 1, 62, 176⟩,
        ⟨58, true, 2, 65, 184⟩,
        ⟨58, true, 3, 69, 192⟩,
        ⟨58, true, 4, 74, 200⟩,
        ⟨59, false, 0, 57, 40⟩,
        ⟨59, false, 1, 54, 48⟩,
        ⟨59, false, 2, 44, 56⟩,
        ⟨59, false, 3, 178, 64⟩,
        ⟨59, false, 4, 194, 72⟩,
        ⟨59, true, 0, 61, 168⟩,
        ⟨59, true, 1, 63, 176⟩,
        ⟨59, true, 2, 66, 184⟩,
        ⟨59, true, 3, 70, 192⟩,
        ⟨59, true, 4, 75, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form6 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:625-726):
      /-- `formReal` on every finite code, both signs and every `F`, part 6. -/
      def form6 : List FormVec := [
        ⟨60, false, 0, 58, 40⟩,
        ⟨60, false, 1, 56, 48⟩,
        ⟨60, false, 2, 48, 56⟩,
        ⟨60, false, 3, 176, 64⟩,
        ⟨60, false, 4, 194, 72⟩,
        ⟨60, true, 0, 62, 168⟩,
        ⟨60, true, 1, 64, 176⟩,
        ⟨60, true, 2, 66, 184⟩,
        ⟨60, true, 3, 70, 192⟩,
        ⟨60, true, 4, 75, 200⟩,
        ⟨61, false, 0, 59, 40⟩,
        ⟨61, false, 1, 57, 48⟩,
        ⟨61, false, 2, 50, 56⟩,
        ⟨61, false, 3, 172, 64⟩,
        ⟨61, false, 4, 194, 72⟩,
        ⟨61, true, 0, 63, 168⟩,
        ⟨61, true, 1, 64, 176⟩,
        ⟨61, true, 2, 66, 184⟩,
        ⟨61, true, 3, 70, 192⟩,
        ⟨61, true, 4, 75, 200⟩,
        ⟨62, false, 0, 60, 40⟩,
        ⟨62, false, 1, 58, 48⟩,
        ⟨62, false, 2, 52, 56⟩,
        ⟨62, false, 3, 168, 64⟩,
        ⟨62, false, 4, 193, 72⟩,
        ⟨62, true, 0, 64, 168⟩,
        ⟨62, true, 1, 65, 176⟩,
        ⟨62, true, 2, 67, 184⟩,
        ⟨62, true, 3, 71, 192⟩,
        ⟨62, true, 4, 76, 200⟩,
        ⟨63, false, 0, 61, 40⟩,
        ⟨63, false, 1, 59, 48⟩,
        ⟨63, false, 2, 54, 56⟩,
        ⟨63, false, 3, 160, 64⟩,
        ⟨63, false, 4, 192, 72⟩,
        ⟨63, true, 0, 64, 168⟩,
        ⟨63, true, 1, 66, 176⟩,
        ⟨63, true, 2, 68, 184⟩,
        ⟨63, true, 3, 72, 192⟩,
        ⟨63, true, 4, 76, 200⟩,
        ⟨64, false, 0, 62, 40⟩,
        ⟨64, false, 1, 60, 48⟩,
        ⟨64, false, 2, 56, 56⟩,
        ⟨64, false, 3, 0, 64⟩,
        ⟨64, false, 4, 192, 72⟩,
        ⟨64, true, 0, 65, 168⟩,
        ⟨64, true, 1, 66, 176⟩,
        ⟨64, true, 2, 68, 184⟩,
        ⟨64, true, 3, 72, 192⟩,
        ⟨64, true, 4, 76, 200⟩,
        ⟨65, false, 0, 64, 40⟩,
        ⟨65, false, 1, 62, 48⟩,
        ⟨65, false, 2, 58, 56⟩,
        ⟨65, false, 3, 40, 64⟩,
        ⟨65, false, 4, 190, 72⟩,
        ⟨65, true, 0, 66, 168⟩,
        ⟨65, true, 1, 67, 176⟩,
        ⟨65, true, 2, 69, 184⟩,
        ⟨65, true, 3, 72, 192⟩,
        ⟨65, true, 4, 76, 200⟩,
        ⟨66, false, 0, 65, 40⟩,
        ⟨66, false, 1, 64, 48⟩,
        ⟨66, false, 2, 60, 56⟩,
        ⟨66, false, 3, 48, 64⟩,
        ⟨66, false, 4, 188, 72⟩,
        ⟨66, true, 0, 67, 168⟩,
        ⟨66, true, 1, 68, 176⟩,
        ⟨66, true, 2, 70, 184⟩,
        ⟨66, true, 3, 73, 192⟩,
        ⟨66, true, 4, 77, 200⟩,
        ⟨67, false, 0, 66, 40⟩,
        ⟨67, false, 1, 65, 48⟩,
        ⟨67, false, 2, 62, 56⟩,
        ⟨67, false, 3, 52, 64⟩,
        ⟨67, false, 4, 186, 72⟩,
        ⟨67, true, 0, 68, 168⟩,
        ⟨67, true, 1, 69, 176⟩,
        ⟨67, true, 2, 71, 184⟩,
        ⟨67, true, 3, 74, 192⟩,
        ⟨67, true, 4, 78, 200⟩,
        ⟨68, false, 0, 67, 40⟩,
        ⟨68, false, 1, 66, 48⟩,
        ⟨68, false, 2, 64, 56⟩,
        ⟨68, false, 3, 56, 64⟩,
        ⟨68, false, 4, 184, 72⟩,
        ⟨68, true, 0, 69, 168⟩,
        ⟨68, true, 1, 70, 176⟩,
        ⟨68, true, 2, 72, 184⟩,
        ⟨68, true, 3, 74, 192⟩,
        ⟨68, true, 4, 78, 200⟩,
        ⟨69, false, 0, 68, 40⟩,
        ⟨69, false, 1, 67, 48⟩,
        ⟨69, false, 2, 65, 56⟩,
        ⟨69, false, 3, 58, 64⟩,
        ⟨69, false, 4, 180, 72⟩,
        ⟨69, true, 0, 70, 168⟩,
        ⟨69, true, 1, 71, 176⟩,
        ⟨69, true, 2, 72, 184⟩,
        ⟨69, true, 3, 74, 192⟩,
        ⟨69, true, 4, 78, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form7 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:728-829):
      /-- `formReal` on every finite code, both signs and every `F`, part 7. -/
      def form7 : List FormVec := [
        ⟨70, false, 0, 69, 40⟩,
        ⟨70, false, 1, 68, 48⟩,
        ⟨70, false, 2, 66, 56⟩,
        ⟨70, false, 3, 60, 64⟩,
        ⟨70, false, 4, 176, 72⟩,
        ⟨70, true, 0, 71, 168⟩,
        ⟨70, true, 1, 72, 176⟩,
        ⟨70, true, 2, 73, 184⟩,
        ⟨70, true, 3, 75, 192⟩,
        ⟨70, true, 4, 79, 200⟩,
        ⟨71, false, 0, 70, 40⟩,
        ⟨71, false, 1, 69, 48⟩,
        ⟨71, false, 2, 67, 56⟩,
        ⟨71, false, 3, 62, 64⟩,
        ⟨71, false, 4, 168, 72⟩,
        ⟨71, true, 0, 72, 168⟩,
        ⟨71, true, 1, 72, 176⟩,
        ⟨71, true, 2, 74, 184⟩,
        ⟨71, true, 3, 76, 192⟩,
        ⟨71, true, 4, 80, 200⟩,
        ⟨72, false, 0, 70, 48⟩,
        ⟨72, false, 1, 70, 48⟩,
        ⟨72, false, 2, 68, 56⟩,
        ⟨72, false, 3, 64, 64⟩,
        ⟨72, false, 4, 0, 72⟩,
        ⟨72, true, 0, 73, 176⟩,
        ⟨72, true, 1, 73, 176⟩,
        ⟨72, true, 2, 74, 184⟩,
        ⟨72, true, 3, 76, 192⟩,
        ⟨72, true, 4, 80, 200⟩,
        ⟨73, false, 0, 72, 48⟩,
        ⟨73, false, 1, 72, 48⟩,
        ⟨73, false, 2, 70, 56⟩,
        ⟨73, false, 3, 66, 64⟩,
        ⟨73, false, 4, 48, 72⟩,
        ⟨73, true, 0, 74, 176⟩,
        ⟨73, true, 1, 74, 176⟩,
        ⟨73, true, 2, 75, 184⟩,
        ⟨73, true, 3, 77, 192⟩,
        ⟨73, true, 4, 80, 200⟩,
        ⟨74, false, 0, 73, 48⟩,
        ⟨74, false, 1, 73, 48⟩,
        ⟨74, false, 2, 72, 56⟩,
        ⟨74, false, 3, 68, 64⟩,
        ⟨74, false, 4, 56, 72⟩,
        ⟨74, true, 0, 75, 176⟩,
        ⟨74, true, 1, 75, 176⟩,
        ⟨74, true, 2, 76, 184⟩,
        ⟨74, true, 3, 78, 192⟩,
        ⟨74, true, 4, 81, 200⟩,
        ⟨75, false, 0, 74, 48⟩,
        ⟨75, false, 1, 74, 48⟩,
        ⟨75, false, 2, 73, 56⟩,
        ⟨75, false, 3, 70, 64⟩,
        ⟨75, false, 4, 60, 72⟩,
        ⟨75, true, 0, 76, 176⟩,
        ⟨75, true, 1, 76, 176⟩,
        ⟨75, true, 2, 77, 184⟩,
        ⟨75, true, 3, 79, 192⟩,
        ⟨75, true, 4, 82, 200⟩,
        ⟨76, false, 0, 75, 48⟩,
        ⟨76, false, 1, 75, 48⟩,
        ⟨76, false, 2, 74, 56⟩,
        ⟨76, false, 3, 72, 64⟩,
        ⟨76, false, 4, 64, 72⟩,
        ⟨76, true, 0, 77, 176⟩,
        ⟨76, true, 1, 77, 176⟩,
        ⟨76, true, 2, 78, 184⟩,
        ⟨76, true, 3, 80, 192⟩,
        ⟨76, true, 4, 82, 200⟩,
        ⟨77, false, 0, 76, 48⟩,
        ⟨77, false, 1, 76, 48⟩,
        ⟨77, false, 2, 75, 56⟩,
        ⟨77, false, 3, 73, 64⟩,
        ⟨77, false, 4, 66, 72⟩,
        ⟨77, true, 0, 78, 176⟩,
        ⟨77, true, 1, 78, 176⟩,
        ⟨77, true, 2, 79, 184⟩,
        ⟨77, true, 3, 80, 192⟩,
        ⟨77, true, 4, 82, 200⟩,
        ⟨78, false, 0, 77, 48⟩,
        ⟨78, false, 1, 77, 48⟩,
        ⟨78, false, 2, 76, 56⟩,
        ⟨78, false, 3, 74, 64⟩,
        ⟨78, false, 4, 68, 72⟩,
        ⟨78, true, 0, 79, 176⟩,
        ⟨78, true, 1, 79, 176⟩,
        ⟨78, true, 2, 80, 184⟩,
        ⟨78, true, 3, 81, 192⟩,
        ⟨78, true, 4, 83, 200⟩,
        ⟨79, false, 0, 78, 48⟩,
        ⟨79, false, 1, 78, 48⟩,
        ⟨79, false, 2, 77, 56⟩,
        ⟨79, false, 3, 75, 64⟩,
        ⟨79, false, 4, 70, 72⟩,
        ⟨79, true, 0, 80, 176⟩,
        ⟨79, true, 1, 80, 176⟩,
        ⟨79, true, 2, 80, 184⟩,
        ⟨79, true, 3, 82, 192⟩,
        ⟨79, true, 4, 84, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form8 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:831-932):
      /-- `formReal` on every finite code, both signs and every `F`, part 8. -/
      def form8 : List FormVec := [
        ⟨80, false, 0, 78, 56⟩,
        ⟨80, false, 1, 78, 56⟩,
        ⟨80, false, 2, 78, 56⟩,
        ⟨80, false, 3, 76, 64⟩,
        ⟨80, false, 4, 72, 72⟩,
        ⟨80, true, 0, 81, 184⟩,
        ⟨80, true, 1, 81, 184⟩,
        ⟨80, true, 2, 81, 184⟩,
        ⟨80, true, 3, 82, 192⟩,
        ⟨80, true, 4, 84, 200⟩,
        ⟨81, false, 0, 80, 56⟩,
        ⟨81, false, 1, 80, 56⟩,
        ⟨81, false, 2, 80, 56⟩,
        ⟨81, false, 3, 78, 64⟩,
        ⟨81, false, 4, 74, 72⟩,
        ⟨81, true, 0, 82, 184⟩,
        ⟨81, true, 1, 82, 184⟩,
        ⟨81, true, 2, 82, 184⟩,
        ⟨81, true, 3, 83, 192⟩,
        ⟨81, true, 4, 85, 200⟩,
        ⟨82, false, 0, 81, 56⟩,
        ⟨82, false, 1, 81, 56⟩,
        ⟨82, false, 2, 81, 56⟩,
        ⟨82, false, 3, 80, 64⟩,
        ⟨82, false, 4, 76, 72⟩,
        ⟨82, true, 0, 83, 184⟩,
        ⟨82, true, 1, 83, 184⟩,
        ⟨82, true, 2, 83, 184⟩,
        ⟨82, true, 3, 84, 192⟩,
        ⟨82, true, 4, 86, 200⟩,
        ⟨83, false, 0, 82, 56⟩,
        ⟨83, false, 1, 82, 56⟩,
        ⟨83, false, 2, 82, 56⟩,
        ⟨83, false, 3, 81, 64⟩,
        ⟨83, false, 4, 78, 72⟩,
        ⟨83, true, 0, 84, 184⟩,
        ⟨83, true, 1, 84, 184⟩,
        ⟨83, true, 2, 84, 184⟩,
        ⟨83, true, 3, 85, 192⟩,
        ⟨83, true, 4, 87, 200⟩,
        ⟨84, false, 0, 83, 56⟩,
        ⟨84, false, 1, 83, 56⟩,
        ⟨84, false, 2, 83, 56⟩,
        ⟨84, false, 3, 82, 64⟩,
        ⟨84, false, 4, 80, 72⟩,
        ⟨84, true, 0, 85, 184⟩,
        ⟨84, true, 1, 85, 184⟩,
        ⟨84, true, 2, 85, 184⟩,
        ⟨84, true, 3, 86, 192⟩,
        ⟨84, true, 4, 88, 200⟩,
        ⟨85, false, 0, 84, 56⟩,
        ⟨85, false, 1, 84, 56⟩,
        ⟨85, false, 2, 84, 56⟩,
        ⟨85, false, 3, 83, 64⟩,
        ⟨85, false, 4, 81, 72⟩,
        ⟨85, true, 0, 86, 184⟩,
        ⟨85, true, 1, 86, 184⟩,
        ⟨85, true, 2, 86, 184⟩,
        ⟨85, true, 3, 87, 192⟩,
        ⟨85, true, 4, 88, 200⟩,
        ⟨86, false, 0, 85, 56⟩,
        ⟨86, false, 1, 85, 56⟩,
        ⟨86, false, 2, 85, 56⟩,
        ⟨86, false, 3, 84, 64⟩,
        ⟨86, false, 4, 82, 72⟩,
        ⟨86, true, 0, 87, 184⟩,
        ⟨86, true, 1, 87, 184⟩,
        ⟨86, true, 2, 87, 184⟩,
        ⟨86, true, 3, 88, 192⟩,
        ⟨86, true, 4, 89, 200⟩,
        ⟨87, false, 0, 86, 56⟩,
        ⟨87, false, 1, 86, 56⟩,
        ⟨87, false, 2, 86, 56⟩,
        ⟨87, false, 3, 85, 64⟩,
        ⟨87, false, 4, 83, 72⟩,
        ⟨87, true, 0, 88, 184⟩,
        ⟨87, true, 1, 88, 184⟩,
        ⟨87, true, 2, 88, 184⟩,
        ⟨87, true, 3, 88, 192⟩,
        ⟨87, true, 4, 90, 200⟩,
        ⟨88, false, 0, 86, 64⟩,
        ⟨88, false, 1, 86, 64⟩,
        ⟨88, false, 2, 86, 64⟩,
        ⟨88, false, 3, 86, 64⟩,
        ⟨88, false, 4, 84, 72⟩,
        ⟨88, true, 0, 89, 192⟩,
        ⟨88, true, 1, 89, 192⟩,
        ⟨88, true, 2, 89, 192⟩,
        ⟨88, true, 3, 89, 192⟩,
        ⟨88, true, 4, 90, 200⟩,
        ⟨89, false, 0, 88, 64⟩,
        ⟨89, false, 1, 88, 64⟩,
        ⟨89, false, 2, 88, 64⟩,
        ⟨89, false, 3, 88, 64⟩,
        ⟨89, false, 4, 86, 72⟩,
        ⟨89, true, 0, 90, 192⟩,
        ⟨89, true, 1, 90, 192⟩,
        ⟨89, true, 2, 90, 192⟩,
        ⟨89, true, 3, 90, 192⟩,
        ⟨89, true, 4, 91, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.form9 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:934-1035):
      /-- `formReal` on every finite code, both signs and every `F`, part 9. -/
      def form9 : List FormVec := [
        ⟨90, false, 0, 89, 64⟩,
        ⟨90, false, 1, 89, 64⟩,
        ⟨90, false, 2, 89, 64⟩,
        ⟨90, false, 3, 89, 64⟩,
        ⟨90, false, 4, 88, 72⟩,
        ⟨90, true, 0, 91, 192⟩,
        ⟨90, true, 1, 91, 192⟩,
        ⟨90, true, 2, 91, 192⟩,
        ⟨90, true, 3, 91, 192⟩,
        ⟨90, true, 4, 92, 200⟩,
        ⟨91, false, 0, 90, 64⟩,
        ⟨91, false, 1, 90, 64⟩,
        ⟨91, false, 2, 90, 64⟩,
        ⟨91, false, 3, 90, 64⟩,
        ⟨91, false, 4, 89, 72⟩,
        ⟨91, true, 0, 92, 192⟩,
        ⟨91, true, 1, 92, 192⟩,
        ⟨91, true, 2, 92, 192⟩,
        ⟨91, true, 3, 92, 192⟩,
        ⟨91, true, 4, 93, 200⟩,
        ⟨92, false, 0, 91, 64⟩,
        ⟨92, false, 1, 91, 64⟩,
        ⟨92, false, 2, 91, 64⟩,
        ⟨92, false, 3, 91, 64⟩,
        ⟨92, false, 4, 90, 72⟩,
        ⟨92, true, 0, 93, 192⟩,
        ⟨92, true, 1, 93, 192⟩,
        ⟨92, true, 2, 93, 192⟩,
        ⟨92, true, 3, 93, 192⟩,
        ⟨92, true, 4, 94, 200⟩,
        ⟨93, false, 0, 92, 64⟩,
        ⟨93, false, 1, 92, 64⟩,
        ⟨93, false, 2, 92, 64⟩,
        ⟨93, false, 3, 92, 64⟩,
        ⟨93, false, 4, 91, 72⟩,
        ⟨93, true, 0, 94, 192⟩,
        ⟨93, true, 1, 94, 192⟩,
        ⟨93, true, 2, 94, 192⟩,
        ⟨93, true, 3, 94, 192⟩,
        ⟨93, true, 4, 95, 200⟩,
        ⟨94, false, 0, 93, 64⟩,
        ⟨94, false, 1, 93, 64⟩,
        ⟨94, false, 2, 93, 64⟩,
        ⟨94, false, 3, 93, 64⟩,
        ⟨94, false, 4, 92, 72⟩,
        ⟨94, true, 0, 95, 192⟩,
        ⟨94, true, 1, 95, 192⟩,
        ⟨94, true, 2, 95, 192⟩,
        ⟨94, true, 3, 95, 192⟩,
        ⟨94, true, 4, 96, 200⟩,
        ⟨95, false, 0, 94, 64⟩,
        ⟨95, false, 1, 94, 64⟩,
        ⟨95, false, 2, 94, 64⟩,
        ⟨95, false, 3, 94, 64⟩,
        ⟨95, false, 4, 93, 72⟩,
        ⟨95, true, 0, 96, 192⟩,
        ⟨95, true, 1, 96, 192⟩,
        ⟨95, true, 2, 96, 192⟩,
        ⟨95, true, 3, 96, 192⟩,
        ⟨95, true, 4, 96, 200⟩,
        ⟨96, false, 0, 94, 72⟩,
        ⟨96, false, 1, 94, 72⟩,
        ⟨96, false, 2, 94, 72⟩,
        ⟨96, false, 3, 94, 72⟩,
        ⟨96, false, 4, 94, 72⟩,
        ⟨96, true, 0, 97, 200⟩,
        ⟨96, true, 1, 97, 200⟩,
        ⟨96, true, 2, 97, 200⟩,
        ⟨96, true, 3, 97, 200⟩,
        ⟨96, true, 4, 97, 200⟩,
        ⟨97, false, 0, 96, 72⟩,
        ⟨97, false, 1, 96, 72⟩,
        ⟨97, false, 2, 96, 72⟩,
        ⟨97, false, 3, 96, 72⟩,
        ⟨97, false, 4, 96, 72⟩,
        ⟨97, true, 0, 98, 200⟩,
        ⟨97, true, 1, 98, 200⟩,
        ⟨97, true, 2, 98, 200⟩,
        ⟨97, true, 3, 98, 200⟩,
        ⟨97, true, 4, 98, 200⟩,
        ⟨98, false, 0, 97, 72⟩,
        ⟨98, false, 1, 97, 72⟩,
        ⟨98, false, 2, 97, 72⟩,
        ⟨98, false, 3, 97, 72⟩,
        ⟨98, false, 4, 97, 72⟩,
        ⟨98, true, 0, 99, 200⟩,
        ⟨98, true, 1, 99, 200⟩,
        ⟨98, true, 2, 99, 200⟩,
        ⟨98, true, 3, 99, 200⟩,
        ⟨98, true, 4, 99, 200⟩,
        ⟨99, false, 0, 98, 72⟩,
        ⟨99, false, 1, 98, 72⟩,
        ⟨99, false, 2, 98, 72⟩,
        ⟨99, false, 3, 98, 72⟩,
        ⟨99, false, 4, 98, 72⟩,
        ⟨99, true, 0, 100, 200⟩,
        ⟨99, true, 1, 100, 200⟩,
        ⟨99, true, 2, 100, 200⟩,
        ⟨99, true, 3, 100, 200⟩,
        ⟨99, true, 4, 100, 200⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row0 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2785-2790):
      /-- Full rows through the forming, the atoms and the chain, part 0. -/
      def row0 : List RowVec := [
        ⟨1, 14015, 0x5016BBEB98C08C5E769915B4DC4801F23AD218FA9BAC3D127BD96E49EC, 0xA6B441174C272366295B04073FDB3F2A4F1A2FE99AA7D65D765A7AC9C0, [0x1E8D6F61898DB147CDC786EAA403CD37EF1A4038DDFB70B354999965F3A7EAB12FE39786F7569FCCEF48B793A0A6F0BDE9C980AF012EDCB168B22208F0B218624169FC99DCEDC37A], [0x48313000, 0xC725EC00], [0x48313000, 0x4807B500]⟩,
        ⟨1, 34881, 0x4F17E5174003E60E21FD3DDE9E360A4B685C47E644FA403F1950FC370A, 0x5735C9A2568CA8D15DD17692694367291A4C6C7C8BFCFCABDCA96BCFEB, [0x2AF34FF207D202727EDC92CDE30D006A6AB46B7D8C3DD5E242FEEB8C1B6FE22035407B0E1CBE13E0F5B92C0D032ACA51491845A5B812B08385853CE6D686E25D4F712A109A237FCF], [0x48677400, 0xC8215C00], [0x48677400, 0x478C3000]⟩,
        ⟨1, 64534, 0xB867DC3AB89124EAAEED35C2F3EE69310DC5CC9F5955B93B2EFB198BF8, 0x0AC3786F5A3D37EF7B38623FE56C42EC5EEA8C601EB08503F78B3B0951, [0xB56E2BC3F62435DFC1DD281C29ECD714C1B102B5CCE20CDE01CCA5159B2C23D165548B59F20CA937BEE0C1A4F93B1B275B5EF486C7B5CA3D74A776622EF727FEBF3C9B787459D982], [0xC6785000, 0x46706000], [0xC6785000, 0xC3FE0000]⟩,
        ⟨2, 53757, 0xA4D3A3EDF20D90A7129D4C018B7DDC174B54CDF75A6B50DFF60E657AC1655992DA21433AB2D9E7B6D426FB3D3B4776A2CD874CB6F6D961C9E2DC, 0x378164DC03A2485685B2E33BDC47C0E10708E99DCCA3CD9FB607F76652C783E0112279373ED65B1FB342842FBCD4049F9236B46A4D6FEBFA57D1, [0x68F95095ADA2622659E092AB5F4CC7EDB175811BE077016CDFCC91E9AE324510554C8A3504D236808640C034D6F5D224623B7F7668123739AE5A300813B6499893473170C9C58685, 0x0B5A6C05299CE04DEF138D1C867921170E27634B7382374C985CB7F9F5D1C604D945C33473C703076BF123E1569BA556B72E6E6C9C25B69AB6B029D2F03C56A1CD92C58B21D5D9FA], [0x45041000, 0x47081800, 0xC6052000, 0xC6C44800], [0x45041000, 0x47105900, 0x46DE2200, 0x454ED000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row1 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2792-2797):
      /-- Full rows through the forming, the atoms and the chain, part 1. -/
      def row1 : List RowVec := [
        ⟨2, 1881, 0x962748809E17B94AF1ED4F8FD087A5CE9138752D2DD59A0B859C94205FD737D990A6D6E16D38AF1AB145E5C3F28A664DE7AE4DD3FE60229A085D, 0xB272A9A2AF1B711DA8130AAAAF503C16151C04C3071173779D12ED01748564F0B39C914C8F88FA3A2AFDC0251BCB21198203D7F2DC1710FE6E25, [0xEC67DF1F8BD704DA4E9BEAF3502B0CD86DB5BFFDFDA203D4026A18F256846AB07F4448E265224AFBCE7B8022AA16366EDD04DE751F3156BCE56F852E35EDE1F23A924B7A92D83360, 0x06DEFCF6EDAADC02D3C3E33D393E16034F6A7B3314043411A5FCCB6B0D7084D41B65F73EE2543A090430462DA817980891E5413EC08D2F64190B688B7933DBC623B334E58F45C274], [0xC5DB6000, 0x46BD3C00, 0x469A1800, 0xC690EC00], [0xC5DB6000, 0x46866400, 0x47103E00, 0x468F9000]⟩,
        ⟨2, 50851, 0x3FDDDB4495124F648EE81733F7F6212B6ED6CCAECAABDAFE3DE69F561BBA929DBB10920746D8367D78AFA6DD4F639104E7F9B8F41C6997B39506, 0x55E257685F03700A39025CB5140782120DC955DFF6D2104C67E2700510E1C53CE224DEFE88E44EFA90ECE8FA6EAF0DB37BB7D91A47284B40E0D3, [0x1E34E06DB059BF0DD81763FD7FF679F3C998A2C4275876E7F66AA7082870F6AA380AB605ACA515E904BECEE0753E01AC607F4050634FA61E3135A66BE451976058935E2E52C4BD68, 0x1DFC8A7E1D889EB7AB887C0F3E4818F8F32EE79F6E0CA9D15585B2DB8BCED9F219DCDDE0F602596F040E59DA8D4A1D849A2F690AD3B8651F14A4B14302255B98BE57ECF0256E43AE], [0xC75B8800, 0x47A35C00, 0xC7AB4400, 0xC79DB000], [0xC75B8800, 0x46D66000, 0xC76B5800, 0xC809AE00]⟩,
        ⟨3, 39283, 0x4052DC1F9718DAA4A80675C02D83D9D5B2630C01D4B59FD584A55DB73F0DBC63774D3883BD98A7D3679B8B5BE8C2C01ADDC2D34455B387BAC29D71C710DB822A6FD1A4AB4D2472C8AF74D81F99EF4F26778D664B765A12, 0xDC81E3EA30AE15C0EC67CF19A1294427CF733E567842933332E7B2D2688E878B7D0630B3EB09F4E004E9E1BC775CAB2ED3D3F8FE1ED8276E2644312A9E6A58D7DF9E204B47648193DFB53C3C0315E523AE2E61CD40AE58, [0xAAFE4A5DBBB7F635334744D5FE897449B1DA7477B6C64D7793D7B62A343E6F77E8E9A1CAFF2DE0478CF93E981FB2190012494E7018FBD337AF41D114EE98B6BB737D4C78F5CC1BCE, 0x4747CC5A2BF361F3935E606B15592DDABE8BEA988963CEC70BD6C9E469DE4DB81596A20FE2D182EBB13C7410B3E53C81B9BCEE51A66514FC25DF8280590928B78C1C863A821421DB, 0x123B31AC33B9DF0EA3978510657804112F6C9044094EE267CCBDD8783D8FA996E3C90E9FCE9768403D72E88AB5E14F2D8D9E1D389F5C6B2A86FA655A75F70B52C7B76C6811108D43], [0xC7ACD800, 0x4833D800, 0x47B85400, 0x47A5F800, 0xC7BE9000, 0xC7B01C00], [0xC7ACD800, 0x47BAD800, 0x48399600, 0x48864900, 0x482D4A00, 0x47AA7800]⟩,
        ⟨3, 59378, 0xCF02520F2A7B72902504E81B20A528B3C5351D6ECFB2FAE3CCD50A895689257B6659131A9961A18E8E86C63E2EE68ADBB6FB6CAA8B00D1064C3A60D5F3A355A7506231CB9AD2554E3D2723950D7AFCF1A02ED11DE69D54, 0x1E0716DEE7C3BC4F73796F03E5F12D26AA67595F102E2C963ACD21DC38B16DBA0FDC7D5CC1152AFDDC36FE9D130F19DC20F5715AB70E56B128F3792FCF6770A651939CF56B825E5A812E9DD5E6C53879CC3471138ABC2B, [0x73815F7B069B1D46EA16874378EE45975230A01035C57347FD7A532B28FA720DC1855AA775BCC698492914FD18ED0ABA92D11C66732F352ED8D6EF1B3A05D53455AF4D8A7B44AAF5, 0x98006FB10654D35A1BA99C38FF9631F35DF6E71F272FE2BBD6A91C433CE7171E1741F8F2A8328BC799A5032545C0D5446FC914EBFA22A0A2D809CA5898DB0E446BC0A33F64C4D6B9, 0xF9EDDDD1B7A540BDD447744940A6E787A918192AC155001546D74949415B0E01381D973DDE41C6693C82870948BB25103C2FCE17AADBF2345D74A0E86CBFEF3B95AB428F91910115], [0x45238000, 0x473A0800, 0xC714C800, 0xC7009400, 0x471DA800, 0x46FEC800], [0x45238000, 0x47444000, 0x463DE000, 0xC6A23800, 0x46991800, 0x474BF000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row2 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2799-2804):
      /-- Full rows through the forming, the atoms and the chain, part 2. -/
      def row2 : List RowVec := [
        ⟨3, 63678, 0xB615E61FD2FC216660C4776DC301B99903BDE94E02FEF91C0F0A40D87726C89517796379C99D4A24FE3336D0B01F194D7E3288893E9B70DBFE2B69BCE9E4951451679E84ED979F0B7AC8DF9B68BE74243BAA9DC73F2EC7, 0xFE11D5EE90C70457C7C89A3F24DE7ACEDA0A3E9A25686F3FAA1B9038694D1308A5758C5D8D0D4446B53BB01E9B9F9A474BE3D0D2BF00DB3C176166AE84296701B0DC0DB989119DB1E50951F52F3B60B4BC5B0F5ACABAF6, [0xBAC209307C8BF4BFCCE654AF2B376F7A95446C472CCCD44131BEBD47AB3F5D590E98406CCC41393A5871CAA6A5CFCF4453A7562F793AB45594ADD09E93F1AD6C628525A8692663E2, 0xAD908C21F08E9784D2FACBA9D52ED4807D2508BF79D8DF3302437D9ECFED7060612C79CC0BCC60D4B7D9B2D7546AAA4DB271979C3C701A3FBB3C68A719B6E67E9C9D1C1FC8784E88, 0x09A258BE4AD09698A5576C47094F7D9B73D23631E64BBFEEC5557D25C9C3214EEB8F542E9C4951ADF382A4D01CE776067C086B80EA47B97A6F05BD97EF91D2523C742A3736143503], [0xC7638000, 0x47800400, 0xC5968000, 0x4746B400, 0x44E0C000, 0xC70CB400], [0xC7638000, 0x45E44000, 0x451B8000, 0x47506C00, 0x47577200, 0x46957C00]⟩,
        ⟨2, 4467, 0x000000000000000000000000000000000000EC77D4D3A61FA8A016008712B0F09B04B0E9A3E343BACD5AB9B0BF50A869F57C5AC45BDA4331D960, 0x00000000000000000000000000000000000097ABF9432B11E62B0E22D9254E8DD347D7C56F7CD9F7D3BF0ABE452C381458EB60327C184B3BA69B, [0x943022ACAE49A19C592952E5DAC5228D91765C9FDD96DD54586EFF0CC2708292FF9FA85BBDBA4A3051AE8A22123EF865E5784967422CC5E958C2679A9B84C92C789EEC6FD87CB18A, 0x9B1E2A34C925FC2B1695ABB53EFA5FF0DF404325B5374386399124CF0D3AC0B3207E0C48509BDA88219F3A743483341158A7646F0BCB21D539EF3121E7148C20B7E32F8E35006199], [0xC798AC00, 0xC670A000, 0x4703CC00, 0x46929800], [0xC798AC00, 0xC7B6C000, 0xC769B400, 0xC7206800]⟩,
        ⟨3, 76251, 0x000000000000000000000000000000000000000000000000000000E40F3ECF189D461127519B4D82EDF59058294BD64FF46BE9E3A75CF637C285448C896317E68ED6935D509FF6C81D3E33EE851ECF03F560C6DE073620, 0x000000000000000000000000000000000000000000000000000000235CDB706DF0D06B8AEFC0DB1C4896187202ADE6BCC83907C521C63768454CD96CB3E9F3DCC8FB940D8D26074D6BC4E695F96678CD5609D6DF608478, [0xAEA796FE750BC42D42865DFDB4B1A1A80C9F12B086DC9E1A07AD59F6B0D44C0EE0F6FB2C3B2B2C7DC1A652F83B535FB980B3EC8EDCA87D2D6577C737D7CA670F465931B0A56F72E6, 0x7E95FD9250BE83E04FDDC4D764417BD99D5B5CD49023867EC7FDDB389724D9209E19159CB9082259A2E1D9CE8A62DBE9CAB046BB9BA4EC5603E679475249C8680D2FE6E1D4B17679, 0x4E491EEC132E9B402E46284328F676CE0D1EDB9833FBB575B6B30B51271FE042CED7923BE0D01DFF9BE0C96DCFCFFDA9E11F81B47E2EF70D4C6AB291FB45140B66FD93D96BFC6EF8], [0xC76A4C00, 0xC74EAC00, 0xC66E4C00, 0x47663400, 0x47547800, 0x466E3000], [0xC76A4C00, 0xC7DC7C00, 0xC7FA4580, 0xC7872B80, 0xC6677C00, 0x43D68000]⟩,
        ⟨1, 27594, 0x0000000000000000000000000000000000000000000000000000000080, 0x0000000000000000000000000000000000000000000000000000000034, [0xA4154A44BFC779869D55F263A01B9061BCF0E192DD89AE42A0740C83A33A01F71CD6277BED5808B9B678ED979904BADEAE6A1ED1CF2A85C218FF0FA72304DDC0BE2B4ECB2FC914F4], [0xC5260000, 0x45260000], [0xC5260000, 0x00000000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row3 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2806-2811):
      /-- Full rows through the forming, the atoms and the chain, part 3. -/
      def row3 : List RowVec := [
        ⟨2, 63600, 0x7EFE7E7EFEFE7E7EFE7EFE7E7E7E7EFEFE7EFEFE7EFE7EFE7E7E7E7EFEFE7E7E7EFEFEFEFEFEFE7EFE7E7EFE7EFEFE7E7EFEFE7EFE7E7EFE7E7E, 0x7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E, [0x0DB3D8179CFC0664B0CD1C681CCFCC6D044F96B994AC6582DAEF346936C9BF1E7E32C887D9F4282724D8716BD5C9BCBE49880592705E7A1256F1EC1EBAB297C35367E2A42B270877, 0x8FF88D002E2676BD64E565F839617DDCBD3ADD59796ACEC81601A270DDB476DC5AF5237CEEDEF87CE8CBB76C55168252ACB828FEF7B186F5D59D1717D50465E4D1D7D797E5D64E52], [0xC83C0000, 0x496AB000, 0x46A00000, 0xC72B0000], [0xC83C0000, 0x493BB000, 0x4940B000, 0x49360000]⟩,
        ⟨2, 82960, 0x7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D, 0xFEFEFE7E7E7E7E7EFEFE7EFEFE7EFEFEFE7EFEFEFE7E7EFE7EFEFEFE7EFE7E7EFEFE7EFEFEFEFE7EFE7E7EFE7EFEFEFEFE7EFEFE7E7EFE7E7EFE, [0x357A465A721ACB3B6630A1E6E943DBAD8025194A5689F63C1A2ADB9A556562CED93A169734C951ACE1251F1CFE30B85E3339BF4A321266816A506CD5F058213532B0F199DB0566DD, 0x6D540C2E60FAB6795450752E27437FAA0DAA3A5089BDE71FF4CDC98F84661624343524C203F9BC8F3F7F4849D6E3562D59B627772B3AD544E60EFE7325F0DBEE1F53F0EDE87D28BA], [0xC9556000, 0xC93BA000, 0xC7620000, 0xC81F8000], [0xC9556000, 0xC9C88000, 0xC9CF9000, 0xC9E38000]⟩,
        ⟨3, 26344, 0xFE7EFEFE7EFEFEFEFEFEFEFE7EFE7E7EFEFEFEFEFEFEFE7E7E7E7EFEFEFE7E7EFE7E7EFEFE7E7EFEFEFEFE7E7EFEFE7EFE7EFE7EFEFE7E7EFEFE7EFE7E7EFEFEFEFE7EFEFEFE7E7E7E7E7EFE7EFE7E7EFEFEFEFEFEFE7E, 0x7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E7E, [0xB9F0D6F1701A0179CEBA0DA17C81C6D7B2964DE910C823F10261EC70C9E4947DAD98693A8E04BE0568507E359B45913C89F6ABE84710458BBD6405707CDE4687BDE6AC5DD8A1F2BB, 0x8A4E36CFDCB5146B6D80F5697AFBB758D1DB044025369B5C8DDBE70087B4E6E38D66AD5CB62C34EF83208F02520FD18EA97A7F154325F7FC76C83F4FB3C9B2185E631F90376401C9, 0x868BB8723AE4BA30C7F1B71772150C643A53FDC01EF51DF2226E939E1B728AA28D4C9F40831D12068195AFA377AED062BF0F01344C9E932B03BC467EBB4A897F3053542B3A7E9841], [0xC8EBE000, 0xC9046000, 0xCA070C00, 0xC8024000, 0xC7910000, 0x47B18000], [0xC8EBE000, 0xC97A5000, 0xCA45A000, 0xCA4DC400, 0xCA524C00, 0xCA4CC000]⟩,
        ⟨3, 68293, 0x7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D7D, 0xFE7EFE7E7EFEFEFEFE7E7E7EFEFE7EFEFE7E7E7EFE7E7E7EFEFEFEFE7EFEFE7EFEFEFE7EFEFEFE7E7EFE7EFE7EFEFE7E7EFE7E7EFEFE7EFE7E7EFEFEFEFEFE7EFEFEFEFE7E7E7E7E7EFE7E7E7E7E7E7E7EFEFE7E7EFEFE, [0xE473CACD396BDBF5B8B511569A7D27F29E1CF4B25A689576E7D9A40D04489D14C44F57D02BAA3562FA12115474F8BF960039C8BB7E12DBDE5CE52AED5CB3B858755805FF8F4D4004, 0x2512E595AF23356A70BB3CADE930F4928E0CCB7D9011CC8D336FF5411DBF2220D5E60302AB734DCDE23D62B33C22F8311FCDFAA3D931082E9F3361F855281BDF93303BBB6F401ABA, 0xBA118F88AB3834BD97AE6050F4D3786C6FB11D205E42151D049FFC8401C3F115E42D92CBE5D43BD2DA2C7B85A27C121A308A90BFE77A0ADC2260E82F0C352E55EB493B3048925506], [0x47DC0000, 0xC8DD4000, 0xC8290000, 0x47900000, 0xC7CF0000, 0xC6500000], [0x47DC0000, 0xC8A64000, 0xC8FAC000, 0xC8D6C000, 0xC9054000, 0xC9088000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row4 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2813-2818):
      /-- Full rows through the forming, the atoms and the chain, part 4. -/
      def row4 : List RowVec := [
        ⟨2, 149, 0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x3C42B8FC2D1D1C165497D77201017761AA97473531B860BE7D0B3C1E87E00428BFB43FD73BD20A5F0A1FDAA532AF4F88252026284E1F17D1C373, [0x46EA7D687CA8D9E3E4EB7C1E7534526EFBE09459C8534BA98144E37862C241C1ECC10DDE25A28CC47F1F4807D33000D714744BFB259FF375112F2B823505C9BAC70B2B036232BAE3, 0xA462C506528E06769995BC7BE648C3E1BEECE7FFCA271DC41EEB6407BFD3BBEBCA2367591EC891ACCD386D57905D5339D389941686A85C64070F36531D021A3808667CCFA1B2FE53], [0x44FAF000, 0xC4189800, 0xC4FAF000, 0x44189800], [0x44FAF000, 0x44AEA400, 0xC4189800, 0x00000000]⟩,
        ⟨3, 2435, 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0xE0F343211DF3DF669E5CA784AC36F9684B57E9BD80B5B2A4B7D1DF132FCE083685FB555DD0EA6DA4A727BDEA096418AFAAA111BEE2C72777E78F6839108A019DCD63D1FCF0258930BEED3A41F4BEE7B80912B8E080DA1B, [0x0D4E103E0ABC8DD9EDB57C58B2328948EBF060C09A3C647F655A6D42CC98DC18BEA88113254C84034C53589B8482EDDAE56FE924D9021A71F24B8DBFC7303937F8A8173DBD029F02, 0xA32E9D4D8E8D2350CCDD684E6EFAA58D5E542A53140AC7E0C3ABB834BC5B8C9DFCFFAFC86BFBACAB33D7C9184589F33154E5C05640D14C8C093E0343FAAF849643EB25AD55109A52, 0x51A7AF349AAF355E5CF87BD45F89E53683F9D29EEDAFB24A4AF16549226C0069F0F59D1E599FC1EDE4773E11A684F89635AE2D43FCE9FBBE5E0A6EA508A4B712DA94D15A775B7F41], [0x45A23800, 0xC5E4F800, 0x45341800, 0xC5A23800, 0x45E4F800, 0xC5341800], [0x45A23800, 0xC5058000, 0x443A6000, 0xC58AEC00, 0x45341800, 0x00000000]⟩,
        ⟨2, 0, 0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, [0x5130FB7CBC917BE8CF6577BB566A917AF5BB2D8936392C10CED660BD7FF85FA187A5007E0C560F5FEB815E53498C269B18D7A9157C280BEDFA0EAAEF1BB4738643D64C5FC6E8B8E7, 0x703C86C2D6BD91477D5D73A75221B0D6A037C948411CDF48A7E8F84D8CCB2FDE599AB700E26F022BC9623C8518230081DBBD4D4A820A69C7D9B81F805081D304A1A9D890F106BEE7], [0x44500000, 0xC3600000, 0xC4500000, 0x43600000], [0x44500000, 0x44180000, 0xC3600000, 0x00000000]⟩,
        ⟨1, 53014, 0x0587030282878304840701030306060203030405078604018781810405, 0xF202D364A4C54DE882A1D8A01B300AF208FE6D5939A4F15F737AAD56A2, [0xB77CD0534A2FC02DFB55F364B909703AB2A26C9F48B11E681E05FEED587DBBBA4CC317CEBBC723DD129EA4BCFB27E66A889335DA4B3DF525BF5ABBA3082CC75912A8A38129989878], [0xC5F3C800, 0x45F3A000], [0xC5F3C800, 0xC0A00000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row5 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2820-2825):
      /-- Full rows through the forming, the atoms and the chain, part 5. -/
      def row5 : List RowVec := [
        ⟨2, 84607, 0x81860505870681050784818506848506870605070281048182860101060207860281070504068301028207040106828705860704820284840101, 0x3FBA12EF92DE0B57F3079339ADA08856ABF6B5C87D9DCB1D7161B37001771FADDD7658BE9A3B66190E153EC46F8F05E4D8B6C262BD7510018DBE, [0x17DD620F7CC5DA6D39D581F34876B031547D8969C692BB14A857F598D747F91A70526FDFE95E4D7AC09ED2DEDB181056FFE34D05110D57F534D685DD777297416D4B2D2E4D05004D, 0xADC4E763B9C0D4FD1E31703A9280140688D1E5804B6C6B5F8E461CB7F0635D1C6DECF8868252BE9F48A1043FCB7F0005D0EA6FDDD3D162EDC8919EE9393F368DE2BD66BB08F4F09A], [0xC5180400, 0x425D0000, 0x45180000, 0xC2730000], [0xC5180400, 0xC5149000, 0x425C0000, 0xC0B80000]⟩,
        ⟨2, 0, 0x6388402DD0AB90C2993645C1EEEBFEEFEFB7CFC055732BEAB5A2BBC3E9A4FC2A2614311F83FA9EFEAF0BD4DCB86258E8CD2730F7F5A5716B989F, 0xFCAEB5AEA450D258489D9F22D7582D401F3E72B3AB5B2AB4F8ECFABAAC0BEF1A714AF3C55EBB53D1ACDFFE2AFC1337C4F455ED725F872D25ED0B, [0xFB28FC757E386C1CB9AEFC07AFA564EE3E0F742D490E876A527BF1B675CE395400158BE74D94717ED185CF37695285928E30A43A16938331335DDBE801A4AEB4CB11D99E03305815, 0xDDB56950D75E23E332C1AB085A6999A44F41D755029E2593016469764AFA4971B392A75A6FA0374A34FE3E838B0557043F2A10C5AF6BD7C93A68FE492BAB8E36EB629BB95A69BFEF], [0x467AE800, 0xC6E88800, 0xC53F7000, 0x467ABC00], [0x467AE800, 0xC6562800, 0xC6830200, 0xC4348000]⟩,
        ⟨2, 22, 0xC9CA12FA91A7F2E18730A4CF12DAA2ADF7CF4B3F15811E5FBA15BE4995E4A66685416D602F6770D0C7083C42C9BCFA47B78B7CB0A083217E41E5, 0x0A6061F1F1BE16A3C0D1729D2376770218BBD806760F0DF02D0477BD53991086714EC0DD139E4084941880EB36AE591AC12C8DF83DC52EBCF45C, [0x5ADBAE4040206D9B337E6C3648FCD4D62A2C11FD34FA33C50CFA257F951826C92A4D45DA4FA0BA83BCB263D2245EAFDE87AD0FF2C8F90EA834A245A7DDB5A4F0E3A426C489583302, 0xE87EE5537E991851FD44F9D09442C2B8C3250FFF0F3AD2453DDA2CA852656906E6714CA91F3D5D8D71361139BE3CACA32C7CD100347444B091B7A17128F70127E414928F698A622E], [0x47B8B800, 0xC5EBE000, 0xC7CA2C00, 0x472E4C00], [0x47B8B800, 0x47A9FA00, 0xC680C800, 0x46DBD000]⟩,
        ⟨2, 23, 0x8C83044886F107476015738F9CC988E37793F396D3CDF45B9C8B0330D98D573B00C59D50680290BA6338F83BF6A4A04DBDF9D70B8D9AC2FD5858, 0x0F1E8B113CCBE62387099C60F7C32B1DE7C4ADD24AF7898545007016610B1E364BE6E7A9C10337959BB800A83E9EA21FFDB16B71E05E1044EDCD, [0xD65F92510B82EF871CEC91B5C1B9E43F23ABF91820E532E41E62871B44D9F358FFA871AC098B03F2F5F1C5B5950AD5AFCABE09B8C452CC6770555139D12D16AEA1AD136183B348E3, 0x190ED31844C42BE5285F3206B973FED2E3CCADB2BC2D06B2AFF4BC958D5E2094AEE3AAD2A09EB6C280CBD375538403DA98AAA5922A2D0F1ECE91F4FD4C43FA0B8652C05E88C7072C], [0xC69D0400, 0xC4592000, 0x467B6000, 0xC6382800], [0xC69D0400, 0xC6A3CD00, 0xC5987400, 0xC6823100]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row6 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2827-2832):
      /-- Full rows through the forming, the atoms and the chain, part 6. -/
      def row6 : List RowVec := [
        ⟨2, 1425, 0x6CBEBD1B794146B1CB1B6A7E32666506A4C9C9EF8A1E8D4E2782D2312BD99C93A99EE7E688C65766687638AF7E549B93D87E9193A72903C6AC81, 0xB023D1F9048C1533BB7E88794D60E7C644FD6052AB66F343EA19EACF48047E2704EA4CCE675EBAC8C8289D0BC960314010978E2A29F4ADA574A3, [0x524ED7D8BB61A0E1A3687F4B76606D449B20FCCC84C797C55854124E86C2774823FE4E29B3A7F1EF24348653FC72A7F8DA252A341431B6A92737DCD6F4A9DA9E5FFB26EF471D8D6C, 0x14E2B9161BF1E3B25E260A8B52C436E4AA03215D23370378DEDD8440942DE9675B598EF3615A43A22D7E7ED48AC9031E53CCB4589944363D409F2A7B05D771ABB81B8B65DF3C2410], [0x4809E000, 0x48930000, 0xC80C0800, 0xC8283800], [0x4809E000, 0x48D7F000, 0x4891EC00, 0x47F74000]⟩,
        ⟨2, 1426, 0x222CA5399754D355C190651E72981D1E710654D745D5737AF4F60250B4C918FAFE978C7819449B47EDC04CE947BBE5D57AE16ED6700FD9D472A4, 0x58E4E0A7449A152EB31B43760B194F7E1CCD97EFD9723887DE90DD514E37719A424F28810805F48CE5ADE3FB75C5DA8547ABF03DA95D70DAAAAD, [0xEBA22F7B35E9C6AB04806FDC558A198176BBC6520A2755943F5CCE67C40A181482F48C66F4FB7792E42D7E89065E249F397835825976C33CCBECEEF08C4817958A22916A0C0B65C3, 0xF8F0178FE550BD5D59EC130A6A5DB60B0C8E69826C48A5B61E921D841A3A3D6902DE34B6F38C34E166A45FDB71AA030F543E28E28A9952D68D078FB42AEF58C1861370AA51A7EB76], [0xC3E90000, 0xC660F000, 0x46809C00, 0x469AD400], [0xC3E90000, 0xC6683800, 0x44C80000, 0x46A75400]⟩,
        ⟨2, 88411, 0xC0EC664DEEAC23BCDA205C4A3064CAD657A78DD749FB4E5ECC9D904A9F4544575F8841CD96500BA6F08B84D9AD9FF88D34E62A2AFD92200F6C5F, 0x62DE5EA0EBF21699DF404D4E6A8F7449B839B7CAE35B2300EE87446FEE544CA82AC987BCCA445E607649C4BA5E578D9DF3B04BF79D5552EE1C04, [0x3939823482449D6CF664DCF75407029739B8443F95368D2541DFD4BA799D1146D6BD2F64C92CBCDAEF6524D10B5B91C7445ECC8C1D1C8134EF1F8D7EA42E6A22D196FF4DCDBA24AD, 0x662C6F414E9DD8454FD0CF4FAD59D21D60AC6FEB673ACDCDB36D8B126EB2212DC6C880A480E0846CB435C832FB52FA0C846BAE1D6C2251DD9C184913E6F349D237EF8A20A7FB99DF], [0x48469C00, 0x4766D800, 0xC862AC00, 0xC74A4400], [0x48469C00, 0x48802900, 0x46ED3000, 0xC6A75800]⟩,
        ⟨2, 5, 0x84DE07393D54894FF1D7DE3DD488940109C9BAC768ACC2EEFDD2FDA5F1EB1A7C9BF6D8D274476FDB262C6E7B4905D15F4244C07DDCB6EA223ADD, 0x23B5D20676F9865F173E2AB8BDABE8C350E4EF61AC20D3A632BB93765F3344603C95AF8F22151920C72F498D884841D9D6D307ACE4AD8139299E, [0x1F3BD3694670BF2428028C13BB52A5D7C06089A22A61CCE61D923A53E2B9FC8FDDB6768F8A4E171ABF4F743639BF74E2FEF5FC847D777A7E582166990EAEFA51C6FE3F7E60950E75, 0xC60AE343447F7A3F7B2CD1EF79A81F8EB19D20D668BF76741D1CEDD8C8AF863A5790B8146388261E1E5D594856D453AEE88C796CD69A33B039E40A285F40B77762C77970E76D0DC8], [0x470F7C00, 0xC670CC00, 0xC6B7F800, 0x45FEC800], [0x470F7C00, 0x46A69200, 0xC50B3000, 0x45B93000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.row7 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2834-2838):
      /-- Full rows through the forming, the atoms and the chain, part 7. -/
      def row7 : List RowVec := [
        ⟨2, 6, 0x84DE07393D54894FF1D7DE3DD488940109C9BAC768ACC2EEFDD2FDA5F1EB1A7C9BF6D8D274476FDB262C6E7B4905D15F4244C07DDCB6EA223ADD, 0x23B5D20676F9865F173E2AB8BDABE8C350E4EF61AC20D3A632BB93765F3344603C95AF8F22151920C72F498D884841D9D6D307ACE4AD8139299E, [0x1F3BD3694670BF2428028C13BB52A5D7C06089A22A61CCE61D923A53E2B9FC8FDDB6768F8A4E171ABF4F743639BF74E2FEF5FC847D777A7E582166990EAEFA51C6FE3F7E60950E75, 0xC60AE343447F7A3F7B2CD1EF79A81F8EB19D20D668BF76741D1CEDD8C8AF863A5790B8146388261E1E5D594856D453AEE88C796CD69A33B039E40A285F40B77762C77970E76D0DC8], [0x47167C00, 0xC6846400, 0xC6C5F800, 0x46176400], [0x47167C00, 0x46A89400, 0xC56B2000, 0x45B93800]⟩,
        ⟨2, 28, 0x84DE07393D54894FF1D7DE3DD488940109C9BAC768ACC2EEFDD2FDA5F1EB1A7C9BF6D8D274476FDB262C6E7B4905D15F4244C07DDCB6EA223ADD, 0x23B5D20676F9865F173E2AB8BDABE8C350E4EF61AC20D3A632BB93765F3344603C95AF8F22151920C72F498D884841D9D6D307ACE4AD8139299E, [0x1F3BD3694670BF2428028C13BB52A5D7C06089A22A61CCE61D923A53E2B9FC8FDDB6768F8A4E171ABF4F743639BF74E2FEF5FC847D777A7E582166990EAEFA51C6FE3F7E60950E75, 0xC60AE343447F7A3F7B2CD1EF79A81F8EB19D20D668BF76741D1CEDD8C8AF863A5790B8146388261E1E5D594856D453AEE88C796CD69A33B039E40A285F40B77762C77970E76D0DC8], [0x470BFC00, 0xC664CC00, 0xC6B0F800, 0x45E6C800], [0x470BFC00, 0x46A59200, 0xC4B66000, 0x45B93000]⟩,
        ⟨2, 1431, 0x84DE07393D54894FF1D7DE3DD488940109C9BAC768ACC2EEFDD2FDA5F1EB1A7C9BF6D8D274476FDB262C6E7B4905D15F4244C07DDCB6EA223ADD, 0x23B5D20676F9865F173E2AB8BDABE8C350E4EF61AC20D3A632BB93765F3344603C95AF8F22151920C72F498D884841D9D6D307ACE4AD8139299E, [0x1F3BD3694670BF2428028C13BB52A5D7C06089A22A61CCE61D923A53E2B9FC8FDDB6768F8A4E171ABF4F743639BF74E2FEF5FC847D777A7E582166990EAEFA51C6FE3F7E60950E75, 0xC60AE343447F7A3F7B2CD1EF79A81F8EB19D20D668BF76741D1CEDD8C8AF863A5790B8146388261E1E5D594856D453AEE88C796CD69A33B039E40A285F40B77762C77970E76D0DC8], [0x47127C00, 0xC668CC00, 0xC6BDF800, 0x45EEC800], [0x47127C00, 0x46B09200, 0xC4D66000, 0x45B93000]⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.salt0 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2708-2783):
      /-- Raw XOF words and the fields `extract` reads, part 0. -/
      def salt0 : List SaltVec := [
        ⟨0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00000000, 0, 0⟩,
        ⟨0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0x1FFFFFFF, 7, 511⟩,
        ⟨0x000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001, 0x00000000, 0, 0⟩,
        ⟨0x000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080, 0x00000000, 0, 8⟩,
        ⟨0x000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100, 0x00000000, 0, 16⟩,
        ⟨0x000002000000020000000200000002000000020000000200000002000000020000000200000002000000020000000200000002000000020000000200000002000000020000000200, 0x00000000, 0, 32⟩,
        ⟨0x000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000, 0x00000000, 0, 0⟩,
        ⟨0x000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000, 0x15555555, 2, 0⟩,
        ⟨0x000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000, 0x00000000, 0, 0⟩,
        ⟨0x004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000, 0x00000000, 0, 0⟩,
        ⟨0x008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000, 0x00000000, 0, 65⟩,
        ⟨0x010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000010000000100000001000000, 0x00000000, 0, 130⟩,
        ⟨0x020000000200000002000000020000000200000002000000020000000200000002000000020000000200000002000000020000000200000002000000020000000200000002000000, 0x00000000, 0, 260⟩,
        ⟨0x040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000, 0x00000000, 0, 0⟩,
        ⟨0x400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000400000004000000040000000, 0x00000000, 0, 0⟩,
        ⟨0x800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000800000008000000080000000, 0x0AAAAAAA, 5, 0⟩,
        ⟨0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF, 0x00000003, 0, 0⟩,
        ⟨0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF00000000, 0x0000000C, 0, 0⟩,
        ⟨0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF0000000000000000, 0x00000030, 0, 0⟩,
        ⟨0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF000000000000000000000000, 0x000000C0, 0, 0⟩,
        ⟨0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF00000000000000000000000000000000, 0x00000300, 0, 0⟩,
        ⟨0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF0000000000000000000000000000000000000000, 0x00000C00, 0, 0⟩,
        ⟨0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF000000000000000000000000000000000000000000000000, 0x00003000, 0, 0⟩,
        ⟨0x00000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF00000000000000000000000000000000000000000000000000000000, 0x0000C000, 0, 0⟩,
        ⟨0x000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFF0000000000000000000000000000000000000000000000000000000000000000, 0x00030000, 0, 0⟩,
        ⟨0x0000000000000000000000000000000000000000000000000000000000000000FFFFFFFF000000000000000000000000000000000000000000000000000000000000000000000000, 0x000C0000, 0, 0⟩,
        ⟨0x00000000000000000000000000000000000000000000000000000000FFFFFFFF00000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00300000, 0, 0⟩,
        ⟨0x000000000000000000000000000000000000000000000000FFFFFFFF0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00C00000, 0, 0⟩,
        ⟨0x0000000000000000000000000000000000000000FFFFFFFF000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x03000000, 0, 0⟩,
        ⟨0x00000000000000000000000000000000FFFFFFFF00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x0C000000, 0, 0⟩,
        ⟨0x000000000000000000000000FFFFFFFF0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x10000000, 0, 0⟩,
        ⟨0x0000000000000000FFFFFFFF000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00000000, 0, 0⟩,
        ⟨0x00000000FFFFFFFF00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00000000, 6, 504⟩,
        ⟨0xFFFFFFFF0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 0x00000000, 1, 7⟩,
        ⟨0xE519975C4CEE5CEB62C30CA54B02AF96FAD16B05CC4013C48D8CD6B3D8D1568A953F668CA5A8C9CA0E2ECA08B299DAD5EABF03F23B6E550335C8865CE9F1AD7A802B94BF32BF169C, 0x1AEB787C, 1, 74⟩,
        ⟨0x7122EBE216BB144A9D13766D9E6A5325A67E77C62A74E73A25A2180D7F508CF50FFA3041AE00E2C243EAD6446F2D2BC451493BC0C3F56D6494966CF5DA1EE19739946CFD37CDEC7C, 0x091342B1, 0, 322⟩,
        ⟨0xCA8EFD66DB8400C1FABB9C2952DF78A917C61B648CA0EA6623ABD4DAF05912D0952962FF08CD5FC43BA2B01408DB376D7E07F5AC5BBE7458488C5EB413AADC9EF8C6BFF5B176EB94, 0x0368441F, 5, 461⟩,
        ⟨0xAA6EC97695BB953CB0BA85EF7D70999D217E64DAFA3827B420768CCADED1B3F2F39EE9D287FEEB034A7CFD979A25021FAD2C97470A6C7D8E4816DCC220102C0BB168C80CC499EF38, 0x127F6C4F, 7, 212⟩,
        ⟨0x4ADF01FDF9CE7955A40E33B287634C4B148BEDB415A3876372B1767F9A7C492AED52E3172465E3F6E38DB6F20BB5A3F38FF929F7D0C6BBECB872DC36F9D1D8B8F77ABFCD70044970, 0x052DDBFC, 4, 213⟩,
        ⟨0xABB55258F078D6F80E5CC2BB95B18F68E997F64C50BFFBBA8258361CB057F2AF19A49AD4AC94477929630D8872818847F9A0025E8DEBE1DE22E2C134913DE829FC9284442FA9ACE0, 0x1DB61B7D, 7, 47⟩,
        ⟨0xC7D52215DBDDEA8B6ECF014586C4658F8FC0D900DF08C83B5DEC6B11E76814DC9656BD4ACF5CE3E48F9B686C2B8B6ACA062F1CBE0C67708EF5E2F162E841E63A469762C0331BC0A9, 0x0F2F80F1, 7, 495⟩,
        ⟨0xB5CD792C65FEEF0A45D5F06B3E7D7C477996569E29EF634251E364DADE551C29F27020E7725ACE3FA689699D808B8954A7A8C76DEBBFC7602BB52E591E4F84C02AB74E6880651C24, 0x0029BF12, 3, 243⟩,
        ⟨0x7C1ECF49D0A70406CFF53E5C7269685B9E158E7E32C7CC7EEB6630295400919EF26C78A6F6BC4E29F8D6259EFE05D2E0CA345FD21A983DDED86742E77FB0D8490173AF6345FED368, 0x0D9AB895, 4, 64⟩,
        ⟨0xDB45C6FDFFA0DEA435F4DF26BB9562AFFFCB80F1B9B784C0499BAD3312DC02B2251B708AB11872BBF72497174994B31B3D56ACE3251E2D2160AB72B477B1F8CCB8CA3BCA3385F424, 0x0F42D419, 7, 494⟩,
        ⟨0xBA853E1A733752C69B1FAF44921A9212D516EEFC16DE55718E2D2EC76687878992975FDF931E8A39D145C61B4CC1624B6ECD79CADB19A8EE5BE0D8AF1C5E02BFBA955464DB429196, 0x1C9BC34B, 1, 429⟩,
        ⟨0x53F69DB5329C5E60E96145B528AE2BFFF180509E05D0FFFAB7FFE4F0FEA06E272DE037D926FEBD1A900CF0BBBE430038A69354CE580CAFD09130609BA549233CBE64DDCB5A624FA2, 0x09E1E9AC, 0, 359⟩,
        ⟨0x226E34F35930D1958BBC18874D7753089C4E46CE554DD45C463FA64EEA8E6BFB6013789963302F713180B50576BA532AE019961B3831B4B34673E86FEA65EE38B9462BF5C9E13DFA, 0x09604D7A, 2, 156⟩,
        ⟨0xA7D0ACFB4B83C0D1A3AAD4D2CA622B814BDDF3B828A5906A93F84A37425CE4B56C905164BC9685017E446D2B77C8A9E6C66603F5F2A48D4F953CB5D7EA5DFE30C36B186C6A404769, 0x05931BF8, 3, 463⟩,
        ⟨0xEAA617359F9EE3EA6BE60E6A0AF8A15C9860BEE0681150C6EC6B30EDEF6D97CED612CA0B694D27392744416AFF949C0D70117F2DB4A8AFA6BC7CD7CD2C3A440D8498E5835434A338, 0x1CBC33CD, 7, 509⟩,
        ⟨0x544D7C797EF456119F122687C9DCA9661474C5E0BD2C06BB32729E34F844B4B98D49E37DC11884491C5662C2EA4180BF9487E1686B5ABC2966A0BD07F724523666DC4F2A4D027C1F, 0x167F3D60, 0, 352⟩,
        ⟨0x408EF0C04C1410634920F52CB8DE6429D6AC29477E2D8790713C2FE2F4698327369664534F97FCF94E0F210C1B6D03E60CF38A521FD5BFCF4C3A92414289558C90BE721E04B41D24, 0x09310548, 0, 1⟩,
        ⟨0xF0CFE34D3B3E23FFD1E9E1A339E2B51D7CAC438F077C3D529891DCF309A9CE6A19ABBBB1A85AE2F4835B32C73818ACC03EDF0456796F77B0E85E273EAC6709958E5E69F032F5CC9A, 0x10D790A9, 1, 441⟩,
        ⟨0xB5490E9763573783F72B891FE2FD0B86BD3ADFE910E28A19F236595F511E8A5009114730891BF16CE720745F8279A9869E89152759DF73BE808144CC6867E53D23687C69C09650AD, 0x0D93B892, 1, 442⟩,
        ⟨0x81B70959D7646450D68334D475B7561E9861C6DED9174BFAB2027A7A9A674B06BE0B90522B449EDEE401774449F4C7D7696E6236ADB061C36F7ADAC34C7E8F0B1C8042A6DF8F6B39, 0x0EAD9252, 5, 387⟩,
        ⟨0x953666DA3ADC6607F47710902103BCE26B865F2C77B48CA5DF60B75803043679F3CF12B7B6BC481684974C4BF3649C0CCBC2FA48F03B5EC38FA04690B004D802B0CB6AE2DA4CA69D, 0x11CABEBB, 1, 354⟩,
        ⟨0x0DC9C5A7585B6CF1B0B918B10935412D8D34921BC5579B52BCA50465272C2C9C24DAAFDEE9BF282D43700D04A2406B063D0976B6F0EE1AC4ADD9A85EA12DC0758EF49B53000E8A71, 0x0F8622FD, 0, 11⟩,
        ⟨0x93964F6238933F0F3399B470DE32E1B43C13616AA241E14977EA6B2657309ED404D6AF61E718FB70E1EFAF49FD59859FF09A903CB6BF8A0C4CCCEAAF9B5BC524C0CD53A39646A036, 0x1317FF7B, 1, 119⟩,
        ⟨0x02E9A044CBCCBE63E8EF223E90BD00404CB0C1B99CC08C5E042131505784ECDF3282C9312C6C0C1B0E8DD6C60D7D3D463A8ACE5E61CEAE9950B21DBAEC7CE3AEAAEF039071574E5C, 0x07144538, 6, 485⟩,
        ⟨0xE0B11515C3F0A3849D5B54D1D9F9E04C7511CB0740CB7DF883DC7A87A85C9D28FA81BD6BCA048938B2328D7B4C39C67F0E58E5AF2C3771ECB02BF4534C183A6D71CD09A192A9D4D0, 0x14BFD4C3, 7, 505⟩,
        ⟨0x99D86902DAC00E4B78D05A1CD79C8E486F64CCD9B0876F2075A1952DFD5C7C7ED079DCCC4F97FDE8B00742EC6ED2B36102214BC23BC37136DDC4F3D91021BBC9F013AA882532ED66, 0x166D90DD, 5, 355⟩,
        ⟨0x203742934D153DDD452410DF29982F880B898C2469CCD478D7B88686771FBF876EEA583D5A8663E154A8B6B2F2BCF5CE848EA670EE855279D60066F3F5AC29B0D543326A101BA6F5, 0x05D07EA9, 0, 152⟩,
        ⟨0xF92E3885EAA044C30719816392A5A1795E91669A2CFE51987BB007DE69D8C0D18BCE9782B275D736954232DC2BCF892E073BB31D0FACCB17E24735E66D338253DBB83D857137E896, 0x101F9599, 5, 330⟩,
        ⟨0x9EAA770FF6FEA55DBF1EBE2DD78C0478B92DBF580A5B500E6277FCDC965E3C08F0F1D9BE7EFD321E30FA5978BBA27045B8FAEBBD8D71C5913DEF803B019C24E712BD6A7F94606F57, 0x0C6C2F42, 7, 341⟩,
        ⟨0x6F94F3E9299840A90D4773A9C7530389F5BC0CAF0A205275EABA3C96D7E2F0373548E0D80DC18054188954AD4C30C1537FC06CE994112ACA2C86151A4C77AE70D488E1921A71EE45, 0x08B5121D, 0, 207⟩,
        ⟨0x67978C8102F890611A872E9836C189AEBF7E14E3884D0305C2CEE729D4B017EDB7141DD18B713509BEEFC0142FD4517EFB86E6320853AA11BAEE8168DE7C3B23F88F0C48DC5C1901, 0x1AEACDEA, 2, 327⟩,
        ⟨0xEC41E3240017D434481B27297382EC28F147E3C25DCCFA1B2C60DA0C4784746E26BF480A198B374D072EFD5A77F1B2DA9836961733E8DFDD91730E4E44CE77591D6B498251F40858, 0x1D405D80, 3, 0⟩,
        ⟨0x376EF96DD5EB03A95CC4759970025AAC45BB1737DC26F43D19437CBA64F26654984B02CA5D866B1135B20A6B01451EA7085620209155D339277AFE45732C9F1931FDBCBF1C5732CE, 0x03080354, 4, 254⟩,
        ⟨0x9A013194AFBFF057BFA9CB7D35A85F44A7BFC80F0E75797B69B627B496C9A817751B625EE9263E8B615DCDC5AF3D216B0A05E3D6E4E5F15441DE20DA2F0781982AC5FCB12E7C1DD3, 0x0C326714, 7, 452⟩,
        ⟨0x4AE6BAC062525D602E392088A24BDD19275DB56F585DA29D8BCF068D9BC7E4B74D7271411B3C4B2990E624C17F3DF00B5B621B631120F2E04EEFFE3DD27B3A0ED7CA1183470C809E, 0x15B09169, 0, 277⟩,
        ⟨0xCC25619E45C7F78D350A5124B457746B76CFEA8A0696E88BEA770CDA97E348BB9CDD90BD126D134720C3006A89D87FC9065CED2468BFB752E6352F4AE1B16719435B5F797ABD78D5, 0x05AC25A0, 3, 248⟩,
        ⟨0x3B8835FEEEF001D3CA1D74FD2A8D243866ED94A360373C3D081D1490A9274CABC4BF9904A97927C63CE2C9816A9E061777A18995C0FEA4DCDC1CEFE9220D4C447881F8487CB58497, 0x042E47C5, 4, 351⟩,
        ⟨0x062ACBDDE703F8C52E65FBDCCF8B54A0B7E774B6124520FFAB9EF10B55FADBACA33AA8A63ACFADB7BD414AED7E55C3DC44779CB9BD2042696994DEF0922849DBB2156407B97CEDD6, 0x08DD966B, 6, 396⟩,
        ⟨0x99037A2EAFF7DCA32969712CF956C9FA9C45F1ACFE0A5D71698A3B20C6E1833312F1F0EE2D909EA5DBBB0B28A560C95AD342E28554C01F97F0CA79F1668C23E26D787864FE0366E9, 0x1E35BC82, 7, 458⟩,
        ⟨0x8AC672DFCE3B478F5DD817D8BD22F2B083419335FECCE4214D8B74BCC30F76316AB48B6F391ADB8195DFF2904C0B4C0F5C7AED999701E248841EF9DD6D36D1629BE7BF0E61505884, 0x1F25C7DC, 5, 317⟩]
  definition Pouw.Fp8Atom.H1T.Vectors.tag0 (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2625-2706):
      /-- Every tag value's code and its negation's, part 0. -/
      def tag0 : List TagVec := [
        ⟨0, false, 0, 80, 208⟩,
        ⟨0, false, 1, 81, 209⟩,
        ⟨0, false, 2, 82, 210⟩,
        ⟨0, false, 3, 83, 211⟩,
        ⟨0, false, 4, 84, 212⟩,
        ⟨0, false, 5, 85, 213⟩,
        ⟨0, false, 6, 86, 214⟩,
        ⟨0, false, 7, 87, 215⟩,
        ⟨0, true, 0, 208, 80⟩,
        ⟨0, true, 1, 209, 81⟩,
        ⟨0, true, 2, 210, 82⟩,
        ⟨0, true, 3, 211, 83⟩,
        ⟨0, true, 4, 212, 84⟩,
        ⟨0, true, 5, 213, 85⟩,
        ⟨0, true, 6, 214, 86⟩,
        ⟨0, true, 7, 215, 87⟩,
        ⟨1, false, 0, 88, 216⟩,
        ⟨1, false, 1, 89, 217⟩,
        ⟨1, false, 2, 90, 218⟩,
        ⟨1, false, 3, 91, 219⟩,
        ⟨1, false, 4, 92, 220⟩,
        ⟨1, false, 5, 93, 221⟩,
        ⟨1, false, 6, 94, 222⟩,
        ⟨1, false, 7, 95, 223⟩,
        ⟨1, true, 0, 216, 88⟩,
        ⟨1, true, 1, 217, 89⟩,
        ⟨1, true, 2, 218, 90⟩,
        ⟨1, true, 3, 219, 91⟩,
        ⟨1, true, 4, 220, 92⟩,
        ⟨1, true, 5, 221, 93⟩,
        ⟨1, true, 6, 222, 94⟩,
        ⟨1, true, 7, 223, 95⟩,
        ⟨2, false, 0, 96, 224⟩,
        ⟨2, false, 1, 97, 225⟩,
        ⟨2, false, 2, 98, 226⟩,
        ⟨2, false, 3, 99, 227⟩,
        ⟨2, false, 4, 100, 228⟩,
        ⟨2, false, 5, 101, 229⟩,
        ⟨2, false, 6, 102, 230⟩,
        ⟨2, false, 7, 103, 231⟩,
        ⟨2, true, 0, 224, 96⟩,
        ⟨2, true, 1, 225, 97⟩,
        ⟨2, true, 2, 226, 98⟩,
        ⟨2, true, 3, 227, 99⟩,
        ⟨2, true, 4, 228, 100⟩,
        ⟨2, true, 5, 229, 101⟩,
        ⟨2, true, 6, 230, 102⟩,
        ⟨2, true, 7, 231, 103⟩,
        ⟨3, false, 0, 104, 232⟩,
        ⟨3, false, 1, 105, 233⟩,
        ⟨3, false, 2, 106, 234⟩,
        ⟨3, false, 3, 107, 235⟩,
        ⟨3, false, 4, 108, 236⟩,
        ⟨3, false, 5, 109, 237⟩,
        ⟨3, false, 6, 110, 238⟩,
        ⟨3, false, 7, 111, 239⟩,
        ⟨3, true, 0, 232, 104⟩,
        ⟨3, true, 1, 233, 105⟩,
        ⟨3, true, 2, 234, 106⟩,
        ⟨3, true, 3, 235, 107⟩,
        ⟨3, true, 4, 236, 108⟩,
        ⟨3, true, 5, 237, 109⟩,
        ⟨3, true, 6, 238, 110⟩,
        ⟨3, true, 7, 239, 111⟩,
        ⟨4, false, 0, 112, 240⟩,
        ⟨4, false, 1, 113, 241⟩,
        ⟨4, false, 2, 114, 242⟩,
        ⟨4, false, 3, 115, 243⟩,
        ⟨4, false, 4, 116, 244⟩,
        ⟨4, false, 5, 117, 245⟩,
        ⟨4, false, 6, 118, 246⟩,
        ⟨4, false, 7, 119, 247⟩,
        ⟨4, true, 0, 240, 112⟩,
        ⟨4, true, 1, 241, 113⟩,
        ⟨4, true, 2, 242, 114⟩,
        ⟨4, true, 3, 243, 115⟩,
        ⟨4, true, 4, 244, 116⟩,
        ⟨4, true, 5, 245, 117⟩,
        ⟨4, true, 6, 246, 118⟩,
        ⟨4, true, 7, 247, 119⟩]
  definition Pouw.Fp8Atom.H1T.formTable (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2844-2871):
      /-- The per-lane table (2540 lanes), from `scripts/h1t_vectors.py` (seed 2026092901). -/
      def formTable : List FormVec :=
        Vectors.form0 ++
        Vectors.form1 ++
        Vectors.form2 ++
        Vectors.form3 ++
        Vectors.form4 ++
        Vectors.form5 ++
        Vectors.form6 ++
        Vectors.form7 ++
        Vectors.form8 ++
        Vectors.form9 ++
        Vectors.form10 ++
        Vectors.form11 ++
        Vectors.form12 ++
        Vectors.form13 ++
        Vectors.form14 ++
        Vectors.form15 ++
        Vectors.form16 ++
        Vectors.form17 ++
        Vectors.form18 ++
        Vectors.form19 ++
        Vectors.form20 ++
        Vectors.form21 ++
        Vectors.form22 ++
        Vectors.form23 ++
        Vectors.form24 ++
        Vectors.form25
  definition Pouw.Fp8Atom.H1T.rowVectors (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2881-2890):
      /-- The full rows (31), from `scripts/h1t_vectors.py` (seed 2026092901). -/
      def rowVectors : List RowVec :=
        Vectors.row0 ++
        Vectors.row1 ++
        Vectors.row2 ++
        Vectors.row3 ++
        Vectors.row4 ++
        Vectors.row5 ++
        Vectors.row6 ++
        Vectors.row7
  definition Pouw.Fp8Atom.H1T.saltVectors (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2877-2879):
      /-- The salt vectors (74), from `scripts/h1t_vectors.py` (seed 2026092901). -/
      def saltVectors : List SaltVec :=
        Vectors.salt0
  definition Pouw.Fp8Atom.H1T.tagTable (Pouw.Fp8Atom.H1TVectors), read by Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance, Pouw.Fp8Atom.H1T.Proofs.h1tFormTable, Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance, Pouw.Fp8Atom.H1T.Proofs.h1tTagTable: new
    now (Pouw/Fp8Atom/H1TVectors.lean:2873-2875):
      /-- The tag table (80 values), from `scripts/h1t_vectors.py` (seed 2026092901). -/
      def tagTable : List TagVec :=
        Vectors.tag0
AUDIT .: PASS  5064 declarations in 126 modules; axioms propext, Classical.choice, Quot.sound; 310 pinned theorems; {'audit': 6.0, 'replay': 129.4, 'total': 135.5}
audit: pinned statements or the definitions they read changed in .: the merge handoff must name the statement reviewer who read the changes above (review.txt in each package's reports)
AUDIT: PASS; reports in /tmp/lean-audit-6bq_7gmu
