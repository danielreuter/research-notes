import Pouw.PearlC.DeviceSm120LoopGamma
import Pouw.PearlC.ChainOnlyGamma

/-!
# v2's TT_OUT is the same statement at both FP32 prices (the price-twins lane's file; staged)

At `devSm120v2` (G = 0) the FP32 add enters neither the credit (`creditDev` has no promotion term, and rev1's first
add is none) nor the debit (`debitDev`'s `add/G` is 0, and rev1's later promotions into +0 are none without promotion).
`fs` and `bf16` agree between `Prices.sm120` and `Prices.sm120Loop`, and `qa` enters only `W_ref`, which TT_OUT doesn't
read. So each TT_OUT form at `devSm120v2 Prices.sm120` is the one at `devSm120v2 Prices.sm120Loop`, and one grant covers
both: per unit and per tile, the cap (`ttOutPearlCDev_sm120v2_loop`, `ttOutTilePearlCDev_sm120v2_loop`), the chain cap,
U-only binding and the chain-only reading. The unrev'd forms hold by `Iff.rfl`; the rev1-based U-only forms need the
debit's later-promotion sum to vanish first.

For v1 (G = 4) they are different statements: the credit prices the `k/(32·G) − 1` promotion adds at the record's add,
so a v1 grant has to name both records.
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions

variable {Q R S : Type}

/-- At `devSm120v2`, rev1's unit debit is the same at both FP32 prices: no later promotions without promotion. -/
theorem unitDebitRev1_sm120v2_loop (sem : PearlCSem Q R S) (H : Q → R) (s : S) (U : Workload) (u : ℕ) (act : Codes) :
    sem.unitDebitRev1 (devSm120v2 Prices.sm120) H s U u act =
      sem.unitDebitRev1 (devSm120v2 Prices.sm120Loop) H s U u act := by
  simp only [PearlCSem.unitDebitRev1, laterZeroPromos, show (devSm120v2 Prices.sm120).G = 0 from rfl,
    show (devSm120v2 Prices.sm120Loop).G = 0 from rfl, ite_true, Nat.cast_zero, sum_const_zero, mul_zero, add_zero]
  rfl

/-- At `devSm120v2`, rev1's tile debit is the same at both FP32 prices. -/
theorem tileDebitRev1_sm120v2_loop (sem : PearlCSem Q R S) (H : Q → R) (s : S) (U : Workload) (u : ℕ)
    (rows cols : Finset ℕ) (act : Codes) :
    sem.tileDebitRev1 (devSm120v2 Prices.sm120) H s U u rows cols act =
      sem.tileDebitRev1 (devSm120v2 Prices.sm120Loop) H s U u rows cols act := by
  simp only [PearlCSem.tileDebitRev1, laterZeroPromos, show (devSm120v2 Prices.sm120).G = 0 from rfl,
    show (devSm120v2 Prices.sm120Loop).G = 0 from rfl, ite_true, Nat.cast_zero, sum_const_zero, mul_zero, add_zero]
  rfl

/-- At `devSm120v2`, rev1's protocol at `Prices.sm120Loop` is the one at `Prices.sm120` with its own `W_ref`. -/
theorem pearlCProtocolDevRev1_sm120v2_loop (sem : PearlCSem Q R S) (ρ : ℚ) :
    pearlCProtocolDevRev1 (devSm120v2 Prices.sm120Loop) sem ρ =
      { pearlCProtocolDevRev1 (devSm120v2 Prices.sm120) sem ρ with
        Wref := (pearlCProtocolDevRev1 (devSm120v2 Prices.sm120Loop) sem ρ).Wref } := by
  simp only [pearlCProtocolDevRev1, unitDebitRev1_sm120v2_loop]
  rfl

/-- At `devSm120v2`, rev1's tiles at `Prices.sm120Loop` are the ones at `Prices.sm120` with their own `W_ref`s. -/
theorem pearlCTilesDevRev1_sm120v2_loop (sem : PearlCSem Q R S) (ρ : ℚ) :
    pearlCTilesDevRev1 (devSm120v2 Prices.sm120Loop) sem ρ =
      { pearlCTilesDevRev1 (devSm120v2 Prices.sm120) sem ρ with
        Wref := (pearlCTilesDevRev1 (devSm120v2 Prices.sm120Loop) sem ρ).Wref
        Wcred := (pearlCTilesDevRev1 (devSm120v2 Prices.sm120Loop) sem ρ).Wcred } := by
  simp only [pearlCTilesDevRev1, tileDebitRev1_sm120v2_loop]
  rfl

variable [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S) (sem : PearlCSem Q R S) (ρ : ℚ)

/-- **v2's TT_OUT at the cap is the same at both FP32 prices.** -/
theorem ttOutPearlCDev_sm120v2_loop :
    TTOutPearlCDev CM (devSm120v2 Prices.sm120) sem ρ ↔ TTOutPearlCDev CM (devSm120v2 Prices.sm120Loop) sem ρ := Iff.rfl

/-- v2's TT_OUT per tile is the same at both FP32 prices. -/
theorem ttOutTilePearlCDev_sm120v2_loop :
    TTOutTilePearlCDev CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutTilePearlCDev CM (devSm120v2 Prices.sm120Loop) sem ρ := Iff.rfl

/-- v2's TT_OUT at the chain cap is the same at both FP32 prices. -/
theorem ttOutPearlCDevChainCap_sm120v2_loop :
    TTOutPearlCDevChainCap CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutPearlCDevChainCap CM (devSm120v2 Prices.sm120Loop) sem ρ := Iff.rfl

/-- v2's TT_OUT at the chain cap per tile is the same at both FP32 prices. -/
theorem ttOutTilePearlCDevChainCap_sm120v2_loop :
    TTOutTilePearlCDevChainCap CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutTilePearlCDevChainCap CM (devSm120v2 Prices.sm120Loop) sem ρ := Iff.rfl

/-- v2's chain-only TT_OUT is the same at both FP32 prices. -/
theorem ttOutPearlCDevChainOnly_sm120v2_loop :
    TTOutPearlCDevChainOnly CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutPearlCDevChainOnly CM (devSm120v2 Prices.sm120Loop) sem ρ := Iff.rfl

/-- v2's chain-only TT_OUT per tile is the same at both FP32 prices. -/
theorem ttOutTilePearlCDevChainOnly_sm120v2_loop :
    TTOutTilePearlCDevChainOnly CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutTilePearlCDevChainOnly CM (devSm120v2 Prices.sm120Loop) sem ρ := Iff.rfl

/-- v2's TT_OUT under U-only binding is the same at both FP32 prices. -/
theorem ttOutPearlCDevUOnly_sm120v2_loop :
    TTOutPearlCDevUOnly CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutPearlCDevUOnly CM (devSm120v2 Prices.sm120Loop) sem ρ := by
  unfold TTOutPearlCDevUOnly
  rw [pearlCProtocolDevRev1_sm120v2_loop]
  exact Iff.rfl

/-- v2's TT_OUT under U-only binding per tile is the same at both FP32 prices. -/
theorem ttOutTilePearlCDevUOnly_sm120v2_loop :
    TTOutTilePearlCDevUOnly CM (devSm120v2 Prices.sm120) sem ρ ↔
      TTOutTilePearlCDevUOnly CM (devSm120v2 Prices.sm120Loop) sem ρ := by
  unfold TTOutTilePearlCDevUOnly
  rw [pearlCProtocolDevRev1_sm120v2_loop, pearlCTilesDevRev1_sm120v2_loop]
  exact Iff.rfl

end Pouw.PearlC
