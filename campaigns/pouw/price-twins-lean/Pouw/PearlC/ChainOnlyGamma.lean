import Pouw.PearlC.KernelWrefGamma
import Pouw.PearlC.TTOutChainOnly

/-!
# γ under the chain-only reading, against the honest kernel's `W_ref` (the price-twins lane's file; staged)

* **The chain-only TT_OUT is weaker** (`ttOutPearlCDevChainOnly_of_ttOut`, `ttOutPearlCDevRev1ChainOnly_of_ttOut`, and
  per tile `ttOutTilePearlCDevChainOnly_of_ttOut`, `ttOutTilePearlCDevRev1ChainOnly_of_ttOut`): its credit is the
  record's less `fs·m·k ≥ 0`, so the record's TT_OUT gives it.
* **γ from it at any record**, on the one-shape domain at `γ = 1 − (399/400)/ω`, where
  `wrefDevK d c = ω·(creditDevChainOnly − ρ·creditDev)` (rev1: `wrefDevRev1K`, `creditDevRev1ChainOnly`,
  `creditDevRev1`): `G_γ` (`pearlCGammaDevKChainOnlyAt`, `pearlCGammaDevRev1KChainOnlyAt`) and `GγSampled`
  (`pearlCSampledDevKChainOnlyAt`, `pearlCSampledDevRev1KChainOnlyAt`). The game is the kernel protocol's: neither
  `G_γ` nor `GγSampled` reads the credit.
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions Pouw.Fp8Atom

section Weaker

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ : ℚ)

theorem creditDevChainOnly_le (s : Shape) : creditDevChainOnly d s ≤ creditDev d s := by
  have : (0 : ℚ) ≤ (d.prices.costs.fs : ℚ) * s.m * s.k := by positivity
  unfold creditDevChainOnly
  linarith

theorem creditDevRev1ChainOnly_le (s : Shape) : creditDevRev1ChainOnly d s ≤ creditDevRev1 d s := by
  have : (0 : ℚ) ≤ (d.prices.costs.fs : ℚ) * s.m * s.k := by positivity
  unfold creditDevRev1ChainOnly
  linarith

theorem chainOnly_tile_le (s : Shape) (t : ℚ) (ht : 0 ≤ t) :
    (creditDevChainOnly d s - ρ * creditDev d s) * t ≤ (1 - ρ) * creditDev d s * t := by
  have := creditDevChainOnly_le d s
  nlinarith

theorem chainOnlyRev1_tile_le (s : Shape) (t : ℚ) (ht : 0 ≤ t) :
    (creditDevRev1ChainOnly d s - ρ * creditDevRev1 d s) * t ≤ (1 - ρ) * creditDevRev1 d s * t := by
  have := creditDevRev1ChainOnly_le d s
  nlinarith

/-- The record's TT_OUT gives the chain-only one. -/
theorem ttOutPearlCDevChainOnly_of_ttOut (h : TTOutPearlCDev CM d sem ρ) : TTOutPearlCDevChainOnly CM d sem ρ := by
  refine ⟨h.1, fun U hU T hT q hq A hA => le_trans (Pouw.pr_mono ?_) (h.2 U hU T hT q hq A hA)⟩
  intro x hx
  refine lt_of_lt_of_le hx (sum_le_sum fun u _ => ?_)
  simp only [pearlCProtocolDevKChainOnly, pearlCProtocolDevK, pearlCProtocolDev]
  exact_mod_cast sub_le_sub_right (creditDevChainOnly_le d _) _

/-- The record's TT_OUT rev1 gives the chain-only one. -/
theorem ttOutPearlCDevRev1ChainOnly_of_ttOut (h : TTOutPearlCDevRev1 CM d sem ρ) :
    TTOutPearlCDevRev1ChainOnly CM d sem ρ := by
  refine ⟨h.1, fun U hU T hT q hq A hA => le_trans (Pouw.pr_mono ?_) (h.2 U hU T hT q hq A hA)⟩
  intro x hx
  refine lt_of_lt_of_le hx (sum_le_sum fun u _ => ?_)
  simp only [pearlCProtocolDevRev1KChainOnly, pearlCProtocolDevRev1K, pearlCProtocolDevRev1]
  exact_mod_cast sub_le_sub_right (creditDevRev1ChainOnly_le d _) _

/-- The record's TT_OUT per tile gives the chain-only one. -/
theorem ttOutTilePearlCDevChainOnly_of_ttOut (h : TTOutTilePearlCDev CM d sem ρ) :
    TTOutTilePearlCDevChainOnly CM d sem ρ := by
  refine ⟨h.1, fun U hU T hT q hq A hA => le_trans (Pouw.pr_mono ?_) (h.2 U hU T hT q hq A hA)⟩
  intro x hx
  refine lt_of_lt_of_le hx (sum_le_sum fun g _ => ?_)
  simp only [pearlCTilesDevKChainOnly, pearlCTilesDevK, pearlCTilesDev]
  exact_mod_cast chainOnly_tile_le d ρ _ _ (tileShare_nonneg _ _ _)

/-- The record's TT_OUT rev1 per tile gives the chain-only one. -/
theorem ttOutTilePearlCDevRev1ChainOnly_of_ttOut (h : TTOutTilePearlCDevRev1 CM d sem ρ) :
    TTOutTilePearlCDevRev1ChainOnly CM d sem ρ := by
  refine ⟨h.1, fun U hU T hT q hq A hA => le_trans (Pouw.pr_mono ?_) (h.2 U hU T hT q hq A hA)⟩
  intro x hx
  refine lt_of_lt_of_le hx (sum_le_sum fun g _ => ?_)
  simp only [pearlCTilesDevRev1KChainOnly, pearlCTilesDevRev1K, pearlCTilesDevRev1]
  exact_mod_cast chainOnlyRev1_tile_le d ρ _ _ (tileShare_nonneg _ _ _)

end Weaker

/-- Chain-only TT_OUT at a device record gives `G_γ` against the kernel's `W_ref` on the one-shape domain at
`γ = 1 − (399/400)/ω`, where `wrefDevK d c = ω·(creditDevChainOnly − ρ·creditDev)`. -/
theorem pearlCGammaDevKChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hω : wrefDevK d c s = ω * (creditDevChainOnly d s - ρ * creditDev d s)) (hγ : γ = 1 - (1 - 1 / 400) / ω)
    (hTT : TTOutPearlCDevChainOnly CM d sem ρ) :
    Gγ CM (pearlCProtocolDevK d sem ρ c) (pearlCDomainDevAt d s) (γ : ℝ) εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevKChainOnly d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
        (pearlCProtocolDevKChainOnly d sem ρ c).actOK (U.layout.shape u) act →
        (pearlCProtocolDevKChainOnly d sem ρ c).capOK H s' U u act →
          (pearlCProtocolDevKChainOnly d sem ρ c).Wref U.layout u ≤
            (ω : ℝ) * (pearlCProtocolDevKChainOnly d sem ρ c).credit H s' U u act := by
    intro U hU H s' u hu act _ hcap
    have hsh : U.layout.shape u = s := hU.2.1.2 u hu
    have hc : debitDev d (sem.unitDebitDev d H s' U u act) ≤ ρ * creditDev d (U.layout.shape u) := hcap
    show (wrefDevK d c (U.layout.shape u) : ℝ) ≤
      (ω : ℝ) * ((creditDevChainOnly d (U.layout.shape u) - debitDev d (sem.unitDebitDev d H s' U u act) : ℚ) : ℝ)
    rw [hsh] at hc ⊢
    rw [hω]
    have : ω * (creditDevChainOnly d s - ρ * creditDev d s) ≤
        ω * (creditDevChainOnly d s - debitDev d (sem.unitDebitDev d H s' U u act)) :=
      mul_le_mul_of_nonneg_left (by linarith) hω0.le
    exact_mod_cast this
  have key := gammaFromTTOut CM (pearlCProtocolDevKChainOnly d sem ρ c) (pearlCDomainDevAt d s) (1 / 400) (ω : ℝ)
    εPearlC (by exact_mod_cast hω0) hW (ttOut_mono_domain (fun _ h => h.1) hTT)
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

/-- Chain-only TT_OUT per tile at a device record gives `GγSampled` against the kernel's `W_ref` on the one-shape domain
at `γ = 1 − (399/400)/ω`, where `wrefDevK d c = ω·(creditDevChainOnly − ρ·creditDev) ≥ 0`. -/
theorem pearlCSampledDevKChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hw0 : 0 ≤ wrefDevK d c s) (hω : wrefDevK d c s = ω * (creditDevChainOnly d s - ρ * creditDev d s))
    (hγ : γ = 1 - (1 - 1 / 400) / ω) (hTT : TTOutTilePearlCDevChainOnly CM d sem ρ) :
    GγSampled CM (pearlCProtocolDevK d sem ρ c) (pearlCTilesDevK d sem ρ c) (pearlCDomainDevAt d s) (γ : ℝ)
      εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevKChainOnly d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ g < ((pearlCTilesDevKChainOnly d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevKChainOnly d sem ρ c).capOK H s' U g act →
        (pearlCTilesDevKChainOnly d sem ρ c).Wcred U.layout g act ≤
          (ω : ℝ) * (pearlCTilesDevKChainOnly d sem ρ c).credit H s' U g act := by
    intro U hU H s' g hg act _
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevKChainOnly, pearlCTilesDevK, pearlCTilesDev]
    rw [hsh, hω]
    push_cast
    exact le_of_eq (by ring)
  have hWc : ∀ U : Workload, U.InDomain (pearlCProtocolDevKChainOnly d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ g < ((pearlCTilesDevKChainOnly d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevKChainOnly d sem ρ c).Wcred U.layout g act ≤
          (pearlCTilesDevKChainOnly d sem ρ c).Wref U.layout g := by
    intro U hU g hg act
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevKChainOnly, pearlCTilesDevK, pearlCTilesDev]
    rw [hsh]
    exact_mod_cast mul_le_mul_of_nonneg_left (tileShare_mono _ (passRows_subset sem _ _ _) _) hw0
  have key := gammaSampled CM (pearlCProtocolDevKChainOnly d sem ρ c) (pearlCTilesDevKChainOnly d sem ρ c)
    (pearlCDomainDevAt d s) (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc
    (ttOutTile_mono_domain (fun _ h => h.1) hTT)
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

/-- Chain-only TT_OUT rev1 at a device record gives `G_γ` against the kernel's `W_ref` on the one-shape domain at
`γ = 1 − (399/400)/ω`, where `wrefDevRev1K d c = ω·(creditDevRev1ChainOnly − ρ·creditDevRev1)`. -/
theorem pearlCGammaDevRev1KChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hω : wrefDevRev1K d c s = ω * (creditDevRev1ChainOnly d s - ρ * creditDevRev1 d s))
    (hγ : γ = 1 - (1 - 1 / 400) / ω) (hTT : TTOutPearlCDevRev1ChainOnly CM d sem ρ) :
    Gγ CM (pearlCProtocolDevRev1K d sem ρ c) (pearlCDomainDevAt d s) (γ : ℝ) εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevRev1KChainOnly d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
        (pearlCProtocolDevRev1KChainOnly d sem ρ c).actOK (U.layout.shape u) act →
        (pearlCProtocolDevRev1KChainOnly d sem ρ c).capOK H s' U u act →
          (pearlCProtocolDevRev1KChainOnly d sem ρ c).Wref U.layout u ≤
            (ω : ℝ) * (pearlCProtocolDevRev1KChainOnly d sem ρ c).credit H s' U u act := by
    intro U hU H s' u hu act _ hcap
    have hsh : U.layout.shape u = s := hU.2.1.2 u hu
    have hc : sem.unitDebitRev1 d H s' U u act ≤ ρ * creditDevRev1 d (U.layout.shape u) := hcap
    show (wrefDevRev1K d c (U.layout.shape u) : ℝ) ≤
      (ω : ℝ) * ((creditDevRev1ChainOnly d (U.layout.shape u) - sem.unitDebitRev1 d H s' U u act : ℚ) : ℝ)
    rw [hsh] at hc ⊢
    rw [hω]
    have : ω * (creditDevRev1ChainOnly d s - ρ * creditDevRev1 d s) ≤
        ω * (creditDevRev1ChainOnly d s - sem.unitDebitRev1 d H s' U u act) :=
      mul_le_mul_of_nonneg_left (by linarith) hω0.le
    exact_mod_cast this
  have key := gammaFromTTOut CM (pearlCProtocolDevRev1KChainOnly d sem ρ c) (pearlCDomainDevAt d s) (1 / 400)
    (ω : ℝ) εPearlC (by exact_mod_cast hω0) hW (ttOut_mono_domain (fun _ h => h.1) hTT)
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

/-- Chain-only TT_OUT rev1 per tile at a device record gives `GγSampled` against the kernel's `W_ref` on the one-shape
domain at `γ = 1 − (399/400)/ω`, where `wrefDevRev1K d c = ω·(creditDevRev1ChainOnly − ρ·creditDevRev1) ≥ 0`. -/
theorem pearlCSampledDevRev1KChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hw0 : 0 ≤ wrefDevRev1K d c s)
    (hω : wrefDevRev1K d c s = ω * (creditDevRev1ChainOnly d s - ρ * creditDevRev1 d s))
    (hγ : γ = 1 - (1 - 1 / 400) / ω) (hTT : TTOutTilePearlCDevRev1ChainOnly CM d sem ρ) :
    GγSampled CM (pearlCProtocolDevRev1K d sem ρ c) (pearlCTilesDevRev1K d sem ρ c) (pearlCDomainDevAt d s)
      (γ : ℝ) εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevRev1KChainOnly d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ g < ((pearlCTilesDevRev1KChainOnly d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevRev1KChainOnly d sem ρ c).capOK H s' U g act →
        (pearlCTilesDevRev1KChainOnly d sem ρ c).Wcred U.layout g act ≤
          (ω : ℝ) * (pearlCTilesDevRev1KChainOnly d sem ρ c).credit H s' U g act := by
    intro U hU H s' g hg act _
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevRev1KChainOnly, pearlCTilesDevRev1K, pearlCTilesDevRev1]
    rw [hsh, hω]
    push_cast
    exact le_of_eq (by ring)
  have hWc : ∀ U : Workload, U.InDomain (pearlCProtocolDevRev1KChainOnly d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ g < ((pearlCTilesDevRev1KChainOnly d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevRev1KChainOnly d sem ρ c).Wcred U.layout g act ≤
          (pearlCTilesDevRev1KChainOnly d sem ρ c).Wref U.layout g := by
    intro U hU g hg act
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevRev1KChainOnly, pearlCTilesDevRev1K, pearlCTilesDevRev1]
    rw [hsh]
    exact_mod_cast mul_le_mul_of_nonneg_left (tileShare_mono _ (passRows_subset sem _ _ _) _) hw0
  have key := gammaSampled CM (pearlCProtocolDevRev1KChainOnly d sem ρ c) (pearlCTilesDevRev1KChainOnly d sem ρ c)
    (pearlCDomainDevAt d s) (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc
    (ttOutTile_mono_domain (fun _ h => h.1) hTT)
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

end Pouw.PearlC
