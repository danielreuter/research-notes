import Pouw.PearlC.Fp4IssueGamma
import Pouw.PearlC.TTOutFp4ChainOnly

/-!
# Pearl-C4 under the chain-only reading, at any FP32 price and scale path (the price-twins lane's file; staged)

* **The chain-only TT_OUT is weaker** (`ttOutFp4ChainOnly_of_ttOut`, `ttOutTileFp4ChainOnly_of_ttOut`): its credit is
  the record's less `fs·m·k ≥ 0`, so the record's TT_OUT gives it at non-negative `fs`.
* **γ from it at any FP4 record** (`pearlCGammaFp4ChainOnlyAt`, `pearlCSampledFp4ChainOnlyAt`), on the one-shape domain
  at `γ = gammaFp4ChainOnly d ρ s`, when the chain-only worst case `creditFp4ChainOnly − ρ·creditFp4` is positive. The
  game is the record's own protocol's: neither `G_γ` nor `GγSampled` reads the credit.
* **The twins** (`pearlC{Gamma,Sampled}Fp4Sm120ChainOnlyAt_{8192,16384}`): at any record priced
  `Fp4Prices.sm120At fadd p`, any `fadd ≥ 0` and scale path `p`, cap `1/400`.
* **The values** (`gammaFp4ChainOnly_sm120{Issue,Loop}_{rcpApprox,lut256}_…`): at FADD 8.00 and `1047/125` = 8.376, on
  both paths. Each also gives the twin's positivity side condition.

Held, as the forming-credited twins are: `tt-out/fp4-sm120` is rated D until the base-split fix.
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions

section Weaker

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (d : Fp4Device) (sem : Fp4Sem Q R S) (ρ : ℚ)

theorem creditFp4ChainOnly_le (hfs : 0 ≤ d.prices.fs) (s : Shape) : creditFp4ChainOnly d s ≤ creditFp4 d s := by
  have : (0 : ℚ) ≤ d.prices.fs * s.m * s.k := by positivity
  unfold creditFp4ChainOnly
  linarith

/-- The record's TT_OUT gives the chain-only one, at non-negative `fs`. -/
theorem ttOutFp4ChainOnly_of_ttOut (hfs : 0 ≤ d.prices.fs) (h : TTOutFp4 CM d sem ρ) :
    TTOutFp4ChainOnly CM d sem ρ := by
  refine ⟨h.1, fun U hU T hT q hq A hA => le_trans (Pouw.pr_mono ?_) (h.2 U hU T hT q hq A hA)⟩
  intro x hx
  refine lt_of_lt_of_le hx (sum_le_sum fun u _ => ?_)
  simp only [pearlCProtocolFp4ChainOnly, pearlCProtocolFp4]
  exact_mod_cast sub_le_sub_right (creditFp4ChainOnly_le d hfs _) _

/-- The record's TT_OUT per tile gives the chain-only one, at non-negative `fs`. -/
theorem ttOutTileFp4ChainOnly_of_ttOut (hfs : 0 ≤ d.prices.fs) (h : TTOutTileFp4 CM d sem ρ) :
    TTOutTileFp4ChainOnly CM d sem ρ := by
  refine ⟨h.1, fun U hU T hT q hq A hA => le_trans (Pouw.pr_mono ?_) (h.2 U hU T hT q hq A hA)⟩
  intro x hx
  refine lt_of_lt_of_le hx (sum_le_sum fun g _ => ?_)
  simp only [pearlCTilesFp4ChainOnly, pearlCTilesFp4]
  have hle := creditFp4ChainOnly_le d hfs
  have ht := tileShare_nonneg
  exact_mod_cast mul_le_mul_of_nonneg_right (by linarith [hle (U.layout.shape ((auditTiling 64 64 U.layout).unit g))])
    (ht _ _ _)

end Weaker

/-- Chain-only TT_OUT at an FP4 record gives `G_γ` on the one-shape domain at `gammaFp4ChainOnly d ρ s`. -/
theorem pearlCGammaFp4ChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (ρ : ℚ) (s : Shape)
    (hK : 0 < creditFp4ChainOnly d s - ρ * creditFp4 d s) (hw : 0 < wrefFp4 d s)
    (hTT : TTOutFp4ChainOnly CM d sem ρ) :
    Gγ CM (pearlCProtocolFp4 d sem ρ) (pearlCDomainFp4At sem s) (gammaFp4ChainOnly d ρ s : ℝ) εPearlC := by
  set ω := wrefFp4 d s / (creditFp4ChainOnly d s - ρ * creditFp4 d s) with hωdef
  have hω0 : 0 < ω := div_pos hw hK
  have hid : wrefFp4 d s = ω * (creditFp4ChainOnly d s - ρ * creditFp4 d s) := by
    rw [hωdef, div_mul_cancel₀ _ hK.ne']
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCDomainFp4At sem s) →
      ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
        (pearlCProtocolFp4ChainOnly d sem ρ).actOK (U.layout.shape u) act →
        (pearlCProtocolFp4ChainOnly d sem ρ).capOK H s' U u act →
          (pearlCProtocolFp4ChainOnly d sem ρ).Wref U.layout u ≤
            (ω : ℝ) * (pearlCProtocolFp4ChainOnly d sem ρ).credit H s' U u act := by
    intro U hU H s' u hu act _ hcap
    have hsh : U.layout.shape u = s := hU.2.1.2 u hu
    have hc : sem.unitDebit d H s' U u act ≤ ρ * creditFp4 d (U.layout.shape u) := hcap
    show (wrefFp4 d (U.layout.shape u) : ℝ) ≤
      (ω : ℝ) * ((creditFp4ChainOnly d (U.layout.shape u) - sem.unitDebit d H s' U u act : ℚ) : ℝ)
    rw [hsh] at hc ⊢
    rw [hid]
    have : ω * (creditFp4ChainOnly d s - ρ * creditFp4 d s) ≤
        ω * (creditFp4ChainOnly d s - sem.unitDebit d H s' U u act) :=
      mul_le_mul_of_nonneg_left (by linarith) hω0.le
    exact_mod_cast this
  have key := gammaFromTTOut CM (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCDomainFp4At sem s) (1 / 400) (ω : ℝ)
    εPearlC (by exact_mod_cast hω0) hW (ttOut_mono_domain (fun _ h => h.1) hTT)
  have e : ((gammaFp4ChainOnly d ρ s : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by
    rw [gammaFp4ChainOnly, ← hωdef]; push_cast; ring
  rw [e]
  exact key

/-- Chain-only TT_OUT per tile at an FP4 record gives `GγSampled` on the one-shape domain at
`gammaFp4ChainOnly d ρ s`. -/
theorem pearlCSampledFp4ChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (ρ : ℚ) (s : Shape)
    (hK : 0 < creditFp4ChainOnly d s - ρ * creditFp4 d s) (hw : 0 < wrefFp4 d s)
    (hTT : TTOutTileFp4ChainOnly CM d sem ρ) :
    GγSampled CM (pearlCProtocolFp4 d sem ρ) (pearlCTilesFp4 d sem ρ) (pearlCDomainFp4At sem s)
      (gammaFp4ChainOnly d ρ s : ℝ) εPearlC := by
  set ω := wrefFp4 d s / (creditFp4ChainOnly d s - ρ * creditFp4 d s) with hωdef
  have hω0 : 0 < ω := div_pos hw hK
  have hid : wrefFp4 d s = ω * (creditFp4ChainOnly d s - ρ * creditFp4 d s) := by
    rw [hωdef, div_mul_cancel₀ _ hK.ne']
  have hW : ∀ U : Workload, U.InDomain (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCDomainFp4At sem s) →
      ∀ (H : Q → R) (s' : S), ∀ g < ((pearlCTilesFp4ChainOnly d sem ρ).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesFp4ChainOnly d sem ρ).capOK H s' U g act →
        (pearlCTilesFp4ChainOnly d sem ρ).Wcred U.layout g act ≤
          (ω : ℝ) * (pearlCTilesFp4ChainOnly d sem ρ).credit H s' U g act := by
    intro U hU H s' g hg act _
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesFp4ChainOnly, pearlCTilesFp4]
    rw [hsh, hid]
    push_cast
    exact le_of_eq (by ring)
  have hWc : ∀ U : Workload, U.InDomain (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCDomainFp4At sem s) →
      ∀ g < ((pearlCTilesFp4ChainOnly d sem ρ).tiling U.layout).NT, ∀ act : Codes,
        (pearlCTilesFp4ChainOnly d sem ρ).Wcred U.layout g act ≤ (pearlCTilesFp4ChainOnly d sem ρ).Wref U.layout g := by
    intro U hU g hg act
    have hu := auditTiling_unit_lt 64 64 U.layout hg
    have hsh : U.layout.shape ((auditTiling 64 64 U.layout).unit g) = s := hU.2.1.2 _ hu
    simp only [pearlCTilesFp4ChainOnly, pearlCTilesFp4]
    rw [hsh]
    exact_mod_cast mul_le_mul_of_nonneg_left (tileShare_mono _ (Fp4Sem.passRows_subset sem _ _ _) _) hw.le
  have key := gammaSampled CM (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCTilesFp4ChainOnly d sem ρ)
    (pearlCDomainFp4At sem s) (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc
    (ttOutTile_mono_domain (fun _ h => h.1) hTT)
  have e : ((gammaFp4ChainOnly d ρ s : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by
    rw [gammaFp4ChainOnly, ← hωdef]; push_cast; ring
  rw [e]
  exact key

/-- **Pearl-C4 chain-only at any FP32 price and scale path, 8192³**, cap `1/400`: `G_γ` at
`gammaFp4ChainOnly d (1/400) sh8192`, when the chain-only worst case is positive (`hK`, which the values give). -/
theorem pearlCGammaFp4Sm120ChainOnlyAt_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hK : 0 < creditFp4ChainOnly d sh8192 - 1 / 400 * creditFp4 d sh8192)
    (hTT : TTOutFp4ChainOnly CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh8192)
      (gammaFp4ChainOnly d (1 / 400) sh8192 : ℝ) εPearlC := by
  have hw : 0 < wrefFp4 d sh8192 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [wrefFp4, creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh8192]
    push_cast
    nlinarith
  exact pearlCGammaFp4ChainOnlyAt CM d sem _ _ hK hw hTT

/-- **Pearl-C4 chain-only at any FP32 price and scale path, 16384³**, cap `1/400`: `G_γ` at
`gammaFp4ChainOnly d (1/400) sh16384`, when the chain-only worst case is positive (`hK`, which the values give). -/
theorem pearlCGammaFp4Sm120ChainOnlyAt_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hK : 0 < creditFp4ChainOnly d sh16384 - 1 / 400 * creditFp4 d sh16384)
    (hTT : TTOutFp4ChainOnly CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh16384)
      (gammaFp4ChainOnly d (1 / 400) sh16384 : ℝ) εPearlC := by
  have hw : 0 < wrefFp4 d sh16384 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [wrefFp4, creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh16384]
    push_cast
    nlinarith
  exact pearlCGammaFp4ChainOnlyAt CM d sem _ _ hK hw hTT

/-- **Pearl-C4 chain-only per audit tile at any FP32 price and scale path, 8192³**, cap `1/400`: `GγSampled` at
`gammaFp4ChainOnly d (1/400) sh8192`, when the chain-only worst case is positive (`hK`, which the values give). -/
theorem pearlCSampledFp4Sm120ChainOnlyAt_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hK : 0 < creditFp4ChainOnly d sh8192 - 1 / 400 * creditFp4 d sh8192)
    (hTT : TTOutTileFp4ChainOnly CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCTilesFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh8192)
      (gammaFp4ChainOnly d (1 / 400) sh8192 : ℝ) εPearlC := by
  have hw : 0 < wrefFp4 d sh8192 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [wrefFp4, creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh8192]
    push_cast
    nlinarith
  exact pearlCSampledFp4ChainOnlyAt CM d sem _ _ hK hw hTT

/-- **Pearl-C4 chain-only per audit tile at any FP32 price and scale path, 16384³**, cap `1/400`: `GγSampled` at
`gammaFp4ChainOnly d (1/400) sh16384`, when the chain-only worst case is positive (`hK`, which the values give). -/
theorem pearlCSampledFp4Sm120ChainOnlyAt_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hK : 0 < creditFp4ChainOnly d sh16384 - 1 / 400 * creditFp4 d sh16384)
    (hTT : TTOutTileFp4ChainOnly CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCTilesFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh16384)
      (gammaFp4ChainOnly d (1 / 400) sh16384 : ℝ) εPearlC := by
  have hw : 0 < wrefFp4 d sh16384 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [wrefFp4, creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh16384]
    push_cast
    nlinarith
  exact pearlCSampledFp4ChainOnlyAt CM d sem _ _ hK hw hTT

/-! ## The values: both FP32 prices, both scale paths -/

/-- Pearl-C4's chain-only γ at FP32 8.00, the `rcpApprox` scale path, 8192³, cap `1/400`:
`451194057/22950880000` (1.96591%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Issue_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    0 < creditFp4ChainOnly d sh8192 - 1 / 400 * creditFp4 d sh8192 ∧
      gammaFp4ChainOnly d (1 / 400) sh8192 = 451194057 / 22950880000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4's chain-only γ at FP32 8.00, the `rcpApprox` scale path, 16384³, cap `1/400`:
`1680852571/134388640000` (1.25074%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Issue_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    0 < creditFp4ChainOnly d sh16384 - 1 / 400 * creditFp4 d sh16384 ∧
      gammaFp4ChainOnly d (1 / 400) sh16384 = 1680852571 / 134388640000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4's chain-only γ at FP32 8.00, the `lut256` scale path, 8192³, cap `1/400`:
`17611477/917600000` (1.91930%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Issue_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    0 < creditFp4ChainOnly d sh8192 - 1 / 400 * creditFp4 d sh8192 ∧
      gammaFp4ChainOnly d (1 / 400) sh8192 = 17611477 / 917600000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4's chain-only γ at FP32 8.00, the `lut256` scale path, 16384³, cap `1/400`:
`65925247/5374240000` (1.22669%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Issue_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    0 < creditFp4ChainOnly d sh16384 - 1 / 400 * creditFp4 d sh16384 ∧
      gammaFp4ChainOnly d (1 / 400) sh16384 = 65925247 / 5374240000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

/-- Pearl-C4's chain-only γ at FP32 `1047/125` = 8.376, the `rcpApprox` scale path, 8192³, cap `1/400`:
`4557116829/229553920000` (1.98521%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Loop_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    0 < creditFp4ChainOnly d sh8192 - 1 / 400 * creditFp4 d sh8192 ∧
      gammaFp4ChainOnly d (1 / 400) sh8192 = 4557116829 / 229553920000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4's chain-only γ at FP32 `1047/125` = 8.376, the `rcpApprox` scale path, 16384³, cap `1/400`:
`16944054487/1344021760000` (1.26070%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Loop_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    0 < creditFp4ChainOnly d sh16384 - 1 / 400 * creditFp4 d sh16384 ∧
      gammaFp4ChainOnly d (1 / 400) sh16384 = 16944054487 / 1344021760000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4's chain-only γ at FP32 `1047/125` = 8.376, the `lut256` scale path, 8192³, cap `1/400`:
`26680734301/1376663200000` (1.93807%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Loop_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    0 < creditFp4ChainOnly d sh8192 - 1 / 400 * creditFp4 d sh8192 ∧
      gammaFp4ChainOnly d (1 / 400) sh8192 = 26680734301 / 1376663200000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4's chain-only γ at FP32 `1047/125` = 8.376, the `lut256` scale path, 16384³, cap `1/400`:
`11075380767/895794400000` (1.23638%), with the chain-only worst case positive. -/
theorem gammaFp4ChainOnly_sm120Loop_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    0 < creditFp4ChainOnly d sh16384 - 1 / 400 * creditFp4 d sh16384 ∧
      gammaFp4ChainOnly d (1 / 400) sh16384 = 11075380767 / 895794400000 := by
  constructor
  · rw [creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]
  · rw [gammaFp4ChainOnly, wrefFp4, creditFp4ChainOnly, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

end Pouw.PearlC
