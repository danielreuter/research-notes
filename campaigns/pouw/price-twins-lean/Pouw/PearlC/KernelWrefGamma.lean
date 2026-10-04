import Pouw.PearlC.DeviceRev1Gamma
import Pouw.PearlC.DeviceKernelWref

/-!
# γ against the honest kernel's `W_ref`, from the record's TT_OUT (the price-twins lane's file; staged)

* **TT_OUT does not read `W_ref`** (`ttOut_wref`, `ttOutTile_wref`): TT_OUT at a protocol holds at the same protocol
  with any other `W_ref`, and per tile with any other `W_ref` and credited rows' `W_ref`. So TT_OUT at a record gives
  TT_OUT at `pearlCProtocolDevK` and `pearlCTilesDevK` (and their rev1 forms): the kernel's γ rests on the record's
  assumption.
* **γ at any record against the kernel's `W_ref`**, on the one-shape domain at `γ = 1 − (399/400)/ω`: `G_γ` from TT_OUT
  (`pearlCGammaDevKAt`, `pearlCGammaDevRev1KAt`) and `GγSampled` from TT_OUT per tile (`pearlCSampledDevKAt`,
  `pearlCSampledDevRev1KAt`), where `wrefDevK d c = ω·(1 − ρ)·creditDev` (rev1: `wrefDevRev1K`, `creditDevRev1`).
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions Pouw.Fp8Atom

/-- TT_OUT does not read `W_ref`. -/
theorem ttOut_wref {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] {CM : CostModel Q R S}
    {P : Protocol Q R S} {D : Layout → Prop} {γ₀ : ℝ} {ε : ℕ → ℕ → ℝ} (W : Layout → ℕ → ℝ)
    (h : TTOut CM P D γ₀ ε) : TTOut CM { P with Wref := W } D γ₀ ε :=
  h

/-- TT_OUT per tile reads neither `W_ref` nor the credited rows' `W_ref`. -/
theorem ttOutTile_wref {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] {CM : CostModel Q R S}
    {P : Protocol Q R S} {TR : TileRules Q R S} {D : Layout → Prop} {γ₀ : ℝ} {ε : ℕ → ℕ → ℝ}
    (W : Layout → ℕ → ℝ) (W' : Layout → ℕ → ℝ) (Wc : Layout → ℕ → Codes → ℝ) (h : TTOutTile CM P TR D γ₀ ε) :
    TTOutTile CM { P with Wref := W } { TR with Wref := W', Wcred := Wc } D γ₀ ε :=
  h

/-- TT_OUT at a device record gives `G_γ` against the kernel's `W_ref` on the one-shape domain at
`γ = 1 − (399/400)/ω`, where `wrefDevK d c = ω·(1 − ρ)·creditDev`. -/
theorem pearlCGammaDevKAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hω : wrefDevK d c s = ω * ((1 - ρ) * creditDev d s)) (hγ : γ = 1 - (1 - 1 / 400) / ω)
    (hTT : TTOutPearlCDev CM d sem ρ) :
    Gγ CM (pearlCProtocolDevK d sem ρ c) (pearlCDomainDevAt d s) (γ : ℝ) εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevK d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
        (pearlCProtocolDevK d sem ρ c).actOK (U.layout.shape u) act →
        (pearlCProtocolDevK d sem ρ c).capOK H s' U u act →
          (pearlCProtocolDevK d sem ρ c).Wref U.layout u ≤
            (ω : ℝ) * (pearlCProtocolDevK d sem ρ c).credit H s' U u act := by
    intro U hU H s' u hu act _ hcap
    have hsh : U.layout.shape u = s := hU.2.1.2 u hu
    have hc : debitDev d (sem.unitDebitDev d H s' U u act) ≤ ρ * creditDev d (U.layout.shape u) := hcap
    show (wrefDevK d c (U.layout.shape u) : ℝ) ≤
      (ω : ℝ) * ((creditDev d (U.layout.shape u) - debitDev d (sem.unitDebitDev d H s' U u act) : ℚ) : ℝ)
    rw [hsh] at hc ⊢
    rw [hω]
    have : ω * ((1 - ρ) * creditDev d s) ≤ ω * (creditDev d s - debitDev d (sem.unitDebitDev d H s' U u act)) :=
      mul_le_mul_of_nonneg_left (by linarith) hω0.le
    exact_mod_cast this
  have key := gammaFromTTOut CM (pearlCProtocolDevK d sem ρ c) (pearlCDomainDevAt d s) (1 / 400) (ω : ℝ) εPearlC
    (by exact_mod_cast hω0) hW (ttOut_mono_domain (fun _ h => h.1) (ttOut_wref _ hTT))
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

/-- TT_OUT per tile at a device record gives `GγSampled` against the kernel's `W_ref` on the one-shape domain at
`γ = 1 − (399/400)/ω`, where `wrefDevK d c = ω·(1 − ρ)·creditDev ≥ 0`. -/
theorem pearlCSampledDevKAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hw0 : 0 ≤ wrefDevK d c s) (hω : wrefDevK d c s = ω * ((1 - ρ) * creditDev d s))
    (hγ : γ = 1 - (1 - 1 / 400) / ω) (hTT : TTOutTilePearlCDev CM d sem ρ) :
    GγSampled CM (pearlCProtocolDevK d sem ρ c) (pearlCTilesDevK d sem ρ c) (pearlCDomainDevAt d s) (γ : ℝ)
      εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevK d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ g < ((pearlCTilesDevK d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevK d sem ρ c).capOK H s' U g act →
        (pearlCTilesDevK d sem ρ c).Wcred U.layout g act ≤
          (ω : ℝ) * (pearlCTilesDevK d sem ρ c).credit H s' U g act := by
    intro U hU H s' g hg act _
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevK, pearlCTilesDev]
    rw [hsh, hω]
    push_cast
    exact le_of_eq (by ring)
  have hWc : ∀ U : Workload, U.InDomain (pearlCProtocolDevK d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ g < ((pearlCTilesDevK d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevK d sem ρ c).Wcred U.layout g act ≤ (pearlCTilesDevK d sem ρ c).Wref U.layout g := by
    intro U hU g hg act
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevK, pearlCTilesDev]
    rw [hsh]
    exact_mod_cast mul_le_mul_of_nonneg_left (tileShare_mono _ (passRows_subset sem _ _ _) _) hw0
  have key := gammaSampled CM (pearlCProtocolDevK d sem ρ c) (pearlCTilesDevK d sem ρ c) (pearlCDomainDevAt d s)
    (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTile_wref _ _ _ hTT))
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

/-- TT_OUT rev1 at a device record gives `G_γ` against the kernel's `W_ref` on the one-shape domain at
`γ = 1 − (399/400)/ω`, where `wrefDevRev1K d c = ω·(1 − ρ)·creditDevRev1`. -/
theorem pearlCGammaDevRev1KAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hω : wrefDevRev1K d c s = ω * ((1 - ρ) * creditDevRev1 d s)) (hγ : γ = 1 - (1 - 1 / 400) / ω)
    (hTT : TTOutPearlCDevRev1 CM d sem ρ) :
    Gγ CM (pearlCProtocolDevRev1K d sem ρ c) (pearlCDomainDevAt d s) (γ : ℝ) εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevRev1K d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
        (pearlCProtocolDevRev1K d sem ρ c).actOK (U.layout.shape u) act →
        (pearlCProtocolDevRev1K d sem ρ c).capOK H s' U u act →
          (pearlCProtocolDevRev1K d sem ρ c).Wref U.layout u ≤
            (ω : ℝ) * (pearlCProtocolDevRev1K d sem ρ c).credit H s' U u act := by
    intro U hU H s' u hu act _ hcap
    have hsh : U.layout.shape u = s := hU.2.1.2 u hu
    have hc : sem.unitDebitRev1 d H s' U u act ≤ ρ * creditDevRev1 d (U.layout.shape u) := hcap
    show (wrefDevRev1K d c (U.layout.shape u) : ℝ) ≤
      (ω : ℝ) * ((creditDevRev1 d (U.layout.shape u) - sem.unitDebitRev1 d H s' U u act : ℚ) : ℝ)
    rw [hsh] at hc ⊢
    rw [hω]
    have : ω * ((1 - ρ) * creditDevRev1 d s) ≤ ω * (creditDevRev1 d s - sem.unitDebitRev1 d H s' U u act) :=
      mul_le_mul_of_nonneg_left (by linarith) hω0.le
    exact_mod_cast this
  have key := gammaFromTTOut CM (pearlCProtocolDevRev1K d sem ρ c) (pearlCDomainDevAt d s) (1 / 400) (ω : ℝ) εPearlC
    (by exact_mod_cast hω0) hW (ttOut_mono_domain (fun _ h => h.1) (ttOut_wref _ hTT))
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

/-- TT_OUT rev1 per tile at a device record gives `GγSampled` against the kernel's `W_ref` on the one-shape domain at
`γ = 1 − (399/400)/ω`, where `wrefDevRev1K d c = ω·(1 − ρ)·creditDevRev1 ≥ 0`. -/
theorem pearlCSampledDevRev1KAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) (s : Shape) (ω γ : ℚ) (hω0 : 0 < ω)
    (hw0 : 0 ≤ wrefDevRev1K d c s) (hω : wrefDevRev1K d c s = ω * ((1 - ρ) * creditDevRev1 d s))
    (hγ : γ = 1 - (1 - 1 / 400) / ω) (hTT : TTOutTilePearlCDevRev1 CM d sem ρ) :
    GγSampled CM (pearlCProtocolDevRev1K d sem ρ c) (pearlCTilesDevRev1K d sem ρ c) (pearlCDomainDevAt d s)
      (γ : ℝ) εPearlC := by
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolDevRev1K d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ (H : Q → R) (s' : S), ∀ g < ((pearlCTilesDevRev1K d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevRev1K d sem ρ c).capOK H s' U g act →
        (pearlCTilesDevRev1K d sem ρ c).Wcred U.layout g act ≤
          (ω : ℝ) * (pearlCTilesDevRev1K d sem ρ c).credit H s' U g act := by
    intro U hU H s' g hg act _
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevRev1K, pearlCTilesDevRev1]
    rw [hsh, hω]
    push_cast
    exact le_of_eq (by ring)
  have hWc : ∀ U : Workload, U.InDomain (pearlCProtocolDevRev1K d sem ρ c) (pearlCDomainDevAt d s) →
      ∀ g < ((pearlCTilesDevRev1K d sem ρ c).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesDevRev1K d sem ρ c).Wcred U.layout g act ≤ (pearlCTilesDevRev1K d sem ρ c).Wref U.layout g := by
    intro U hU g hg act
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesDevRev1K, pearlCTilesDevRev1]
    rw [hsh]
    exact_mod_cast mul_le_mul_of_nonneg_left (tileShare_mono _ (passRows_subset sem _ _ _) _) hw0
  have key := gammaSampled CM (pearlCProtocolDevRev1K d sem ρ c) (pearlCTilesDevRev1K d sem ρ c)
    (pearlCDomainDevAt d s) (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTile_wref _ _ _ hTT))
  have e : (γ : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by rw [hγ]; push_cast; ring
  rw [e]
  exact key

end Pouw.PearlC
