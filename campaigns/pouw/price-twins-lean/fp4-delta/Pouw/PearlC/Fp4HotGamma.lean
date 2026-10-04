import Pouw.PearlC.TileGamma
import Pouw.PearlC.DeviceFp4Hot

/-!
# Pearl-C4 v2's price twins, at any FP32 price and scale path (the price-twins lane's file; staged)

* **γ from TT_OUT at any protocol meeting v2's accounting** (`pearlCGammaFp4HotAt`, `pearlCSampledFp4HotAt`): with the
  credited bound `K` and `W_ref = wrefFp4Hot`, TT_OUT gives `G_γ` (per tile, `GγSampled`) at
  `1 − (399/400)/(wrefFp4Hot/K)`.
* **The twins**, forming credited (`pearlC{Gamma,Sampled}Fp4Sm120HotAt_…`, at `gammaFp4Hot`) and chain-only
  (`pearlC{Gamma,Sampled}Fp4Sm120HotChainOnlyAt_…`, at `gammaFp4HotChainOnly`): at any record priced
  `Fp4Prices.sm120At fadd p`, the removal at `a = 2·fadd`, any `fadd ≥ 0` and scale path `p`, cap `1/400`. The
  chain-only twins take the positivity of their worst case, which the values give.
* **The values** (`gammaFp4Hot{,ChainOnly}_sm120{Issue,Loop}_{rcpApprox,lut256}_…`): at FADD 8.00 and `1047/125` =
  8.376.

Held, as the rest of the FP4 delta is: `tt-out/fp4-sm120` is rated D until the base-split fix, and TT_OUT at the v2
protocol is its T1 form.
-/

namespace Pouw.PearlC

open Pouw.PearlC.Assumptions

/-- TT_OUT at a protocol meeting Pearl-C4 v2's per-unit accounting with credited bound `K > 0` gives `G_γ` at
`1 − (399/400)/(wrefFp4Hot/K)`. -/
theorem pearlCGammaFp4HotAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (P : Protocol Q R S) (D : Layout → Prop) (d : Fp4Device) (a K : ℚ) (s : Shape) (hK : 0 < K)
    (hW0 : 0 < wrefFp4Hot d a s) (hacc : Fp4HotUnitAccounting P D d a K s) (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D ((1 - (1 - 1 / 400) / (wrefFp4Hot d a s / K) : ℚ) : ℝ) εPearlC := by
  set ω := wrefFp4Hot d a s / K with hωdef
  have hω0 : 0 < ω := div_pos hW0 hK
  have hid : wrefFp4Hot d a s = ω * K := by rw [hωdef, div_mul_cancel₀ _ hK.ne']
  have hW : ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
      P.actOK (U.layout.shape u) act → P.capOK H s' U u act → P.Wref U.layout u ≤ (ω : ℝ) * P.credit H s' U u act := by
    intro U hU H s' u hu act ha hcap
    obtain ⟨hw, hcr⟩ := hacc U hU H s' u hu act ha hcap
    rw [hw, hid]
    push_cast
    exact mul_le_mul_of_nonneg_left hcr (by exact_mod_cast hω0.le)
  have key := gammaFromTTOut CM P D (1 / 400) (ω : ℝ) εPearlC (by exact_mod_cast hω0) hW hTT
  have e : ((1 - (1 - 1 / 400) / ω : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by push_cast; ring
  rw [e]
  exact key

/-- TT_OUT per tile at a protocol and tiles meeting Pearl-C4 v2's per-tile accounting with credited bound `K > 0` gives
`GγSampled` at `1 − (399/400)/(wrefFp4Hot/K)`. -/
theorem pearlCSampledFp4HotAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : Fp4Device) (a K : ℚ) (s : Shape) (hK : 0 < K)
    (hW0 : 0 < wrefFp4Hot d a s) (hacc : Fp4HotTileAccounting P TR D d a K s)
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D ((1 - (1 - 1 / 400) / (wrefFp4Hot d a s / K) : ℚ) : ℝ) εPearlC := by
  set ω := wrefFp4Hot d a s / K with hωdef
  have hω0 : 0 < ω := div_pos hW0 hK
  have hid : wrefFp4Hot d a s = ω * K := by rw [hωdef, div_mul_cancel₀ _ hK.ne']
  have hW : ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes,
      TR.capOK H s' U g act → TR.Wcred U.layout g act ≤ (ω : ℝ) * TR.credit H s' U g act := by
    intro U hU H s' g hg act hcap
    obtain ⟨t, _, hw, _, hcr⟩ := hacc U hU g hg act
    rw [hw, hid]
    have e2 : ((ω * K * t : ℚ) : ℝ) = (ω : ℝ) * ((K * t : ℚ) : ℝ) := by push_cast; ring
    rw [e2]
    exact mul_le_mul_of_nonneg_left (hcr H s' hcap) (by exact_mod_cast hω0.le)
  have hWc : ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes,
      TR.Wcred U.layout g act ≤ TR.Wref U.layout g := by
    intro U hU g hg act
    obtain ⟨t, _, _, hle, _⟩ := hacc U hU g hg act
    exact hle
  have key := gammaSampled CM P TR D (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc hTT
  have e : ((1 - (1 - 1 / 400) / ω : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by push_cast; ring
  rw [e]
  exact key

section Twins

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)

/-- **Pearl-C4 v2, 8192³**, at any FP32 price `fadd` and scale path `p`, the H removal credited at `2·fadd` per word,
cap `1/400`: γ = `gammaFp4Hot d (2 * fadd) (1 / 400) sh8192` (the `gammaFp4Hot_…` lemmas give its values). -/
theorem pearlCGammaFp4Sm120HotAt_8192
    (P : Protocol Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hacc : Fp4HotUnitAccounting P D d (2 * fadd) ((1 - 1 / 400) * creditFp4Hot d (2 * fadd) sh8192) sh8192)
    (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaFp4Hot d (2 * fadd) (1 / 400) sh8192 : ℝ) εPearlC := by
  have key := pearlCGammaFp4HotAt CM P D d _ _ _ (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh8192]
      push_cast
      nlinarith) (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh8192]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4Hot] using key

/-- **Pearl-C4 v2, 16384³**, at any FP32 price `fadd` and scale path `p`, the H removal credited at `2·fadd` per word,
cap `1/400`: γ = `gammaFp4Hot d (2 * fadd) (1 / 400) sh16384` (the `gammaFp4Hot_…` lemmas give its values). -/
theorem pearlCGammaFp4Sm120HotAt_16384
    (P : Protocol Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hacc : Fp4HotUnitAccounting P D d (2 * fadd) ((1 - 1 / 400) * creditFp4Hot d (2 * fadd) sh16384) sh16384)
    (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaFp4Hot d (2 * fadd) (1 / 400) sh16384 : ℝ) εPearlC := by
  have key := pearlCGammaFp4HotAt CM P D d _ _ _ (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh16384]
      push_cast
      nlinarith) (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh16384]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4Hot] using key

/-- **Pearl-C4 v2, per audit tile, 8192³**, at any FP32 price `fadd` and scale path `p`, the H removal credited at
`2·fadd` per word, cap `1/400`: γ = `gammaFp4Hot d (2 * fadd) (1 / 400) sh8192` (the `gammaFp4Hot_…` lemmas give its
values). -/
theorem pearlCSampledFp4Sm120HotAt_8192
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hacc : Fp4HotTileAccounting P TR D d (2 * fadd) ((1 - 1 / 400) * creditFp4Hot d (2 * fadd) sh8192) sh8192)
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaFp4Hot d (2 * fadd) (1 / 400) sh8192 : ℝ) εPearlC := by
  have key := pearlCSampledFp4HotAt CM P TR D d _ _ _ (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh8192]
      push_cast
      nlinarith) (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh8192]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4Hot] using key

/-- **Pearl-C4 v2, per audit tile, 16384³**, at any FP32 price `fadd` and scale path `p`, the H removal credited at
`2·fadd` per word, cap `1/400`: γ = `gammaFp4Hot d (2 * fadd) (1 / 400) sh16384` (the `gammaFp4Hot_…` lemmas give its
values). -/
theorem pearlCSampledFp4Sm120HotAt_16384
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hacc : Fp4HotTileAccounting P TR D d (2 * fadd) ((1 - 1 / 400) * creditFp4Hot d (2 * fadd) sh16384) sh16384)
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaFp4Hot d (2 * fadd) (1 / 400) sh16384 : ℝ) εPearlC := by
  have key := pearlCSampledFp4HotAt CM P TR D d _ _ _ (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh16384]
      push_cast
      nlinarith) (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh16384]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4Hot] using key

/-- **Pearl-C4 v2, chain-only, 8192³**, at any FP32 price `fadd` and scale path `p`, the H removal credited at `2·fadd`
per word, cap `1/400`: γ = `gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh8192` (the `gammaFp4HotChainOnly_…` lemmas
give its values). -/
theorem pearlCGammaFp4Sm120HotChainOnlyAt_8192
    (P : Protocol Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hK : 0 < creditFp4HotChainOnly d (2 * fadd) sh8192 - 1 / 400 * creditFp4Hot d (2 * fadd) sh8192)
    (hacc : Fp4HotUnitAccounting P D d (2 * fadd)
      (creditFp4HotChainOnly d (2 * fadd) sh8192 - 1 / 400 * creditFp4Hot d (2 * fadd) sh8192) sh8192)
    (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh8192 : ℝ) εPearlC := by
  have key := pearlCGammaFp4HotAt CM P D d _ _ _ hK (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh8192]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4HotChainOnly] using key

/-- **Pearl-C4 v2, chain-only, 16384³**, at any FP32 price `fadd` and scale path `p`, the H removal credited at `2·fadd`
per word, cap `1/400`: γ = `gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh16384` (the `gammaFp4HotChainOnly_…` lemmas
give its values). -/
theorem pearlCGammaFp4Sm120HotChainOnlyAt_16384
    (P : Protocol Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hK : 0 < creditFp4HotChainOnly d (2 * fadd) sh16384 - 1 / 400 * creditFp4Hot d (2 * fadd) sh16384)
    (hacc : Fp4HotUnitAccounting P D d (2 * fadd)
      (creditFp4HotChainOnly d (2 * fadd) sh16384 - 1 / 400 * creditFp4Hot d (2 * fadd) sh16384) sh16384)
    (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh16384 : ℝ) εPearlC := by
  have key := pearlCGammaFp4HotAt CM P D d _ _ _ hK (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh16384]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4HotChainOnly] using key

/-- **Pearl-C4 v2, chain-only, per audit tile, 8192³**, at any FP32 price `fadd` and scale path `p`, the H removal
credited at `2·fadd` per word, cap `1/400`: γ = `gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh8192` (the
`gammaFp4HotChainOnly_…` lemmas give its values). -/
theorem pearlCSampledFp4Sm120HotChainOnlyAt_8192
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hK : 0 < creditFp4HotChainOnly d (2 * fadd) sh8192 - 1 / 400 * creditFp4Hot d (2 * fadd) sh8192)
    (hacc : Fp4HotTileAccounting P TR D d (2 * fadd)
      (creditFp4HotChainOnly d (2 * fadd) sh8192 - 1 / 400 * creditFp4Hot d (2 * fadd) sh8192) sh8192)
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh8192 : ℝ) εPearlC := by
  have key := pearlCSampledFp4HotAt CM P TR D d _ _ _ hK (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh8192]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4HotChainOnly] using key

/-- **Pearl-C4 v2, chain-only, per audit tile, 16384³**, at any FP32 price `fadd` and scale path `p`, the H removal
credited at `2·fadd` per word, cap `1/400`: γ = `gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh16384` (the
`gammaFp4HotChainOnly_…` lemmas give its values). -/
theorem pearlCSampledFp4Sm120HotChainOnlyAt_16384
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : Fp4Device) (fadd : ℚ) (p : Fp4ScalePath)
    (hf : 0 ≤ fadd) (hp : d.prices = Fp4Prices.sm120At fadd p)
    (hK : 0 < creditFp4HotChainOnly d (2 * fadd) sh16384 - 1 / 400 * creditFp4Hot d (2 * fadd) sh16384)
    (hacc : Fp4HotTileAccounting P TR D d (2 * fadd)
      (creditFp4HotChainOnly d (2 * fadd) sh16384 - 1 / 400 * creditFp4Hot d (2 * fadd) sh16384) sh16384)
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaFp4HotChainOnly d (2 * fadd) (1 / 400) sh16384 : ℝ) εPearlC := by
  have key := pearlCSampledFp4HotAt CM P TR D d _ _ _ hK (by
      have h1 := p.fixed_nonneg
      have h2 := mul_nonneg p.fp32Ops_nonneg hf
      rw [wrefFp4Hot, creditFp4Hot, creditFp4, hp]
      simp only [Fp4Prices.sm120At, Params.pi, sh16384]
      push_cast
      nlinarith) hacc hTT
  simpa only [gammaFp4HotChainOnly] using key

end Twins

/-! ## The values: both FP32 prices, both scale paths, both readings -/

/-- Pearl-C4 v2, FP32 at 8.00, the `rcpApprox` scale path, 8192³, cap `1/400`: `25671209/3630560000` (0.70709%). -/
theorem gammaFp4Hot_sm120Issue_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    gammaFp4Hot d (2 * 8) (1 / 400) sh8192 = 25671209 / 3630560000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4 v2, FP32 at 8.00, the `rcpApprox` scale path, 16384³, cap `1/400`: `271674457/44838880000` (0.60589%). -/
theorem gammaFp4Hot_sm120Issue_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    gammaFp4Hot d (2 * 8) (1 / 400) sh16384 = 271674457 / 44838880000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4 v2, FP32 at 8.00, the `lut256` scale path, 8192³, cap `1/400`: `19503599/2757920000` (0.70719%). -/
theorem gammaFp4Hot_sm120Issue_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    gammaFp4Hot d (2 * 8) (1 / 400) sh8192 = 19503599 / 2757920000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4 v2, FP32 at 8.00, the `lut256` scale path, 16384³, cap `1/400`: `310423/51232000` (0.60592%). -/
theorem gammaFp4Hot_sm120Issue_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    gammaFp4Hot d (2 * 8) (1 / 400) sh16384 = 310423 / 51232000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

/-- Pearl-C4 v2, FP32 at `1047/125` = 8.376, the `rcpApprox` scale path, 8192³, cap `1/400`: `549538679/76666880000`
(0.71679%). -/
theorem gammaFp4Hot_sm120Loop_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    gammaFp4Hot d (2 * (1047 / 125)) (1 / 400) sh8192 = 549538679 / 76666880000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4 v2, FP32 at `1047/125` = 8.376, the `rcpApprox` scale path, 16384³, cap `1/400`: `1174078873/192194560000`
(0.61088%). -/
theorem gammaFp4Hot_sm120Loop_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    gammaFp4Hot d (2 * (1047 / 125)) (1 / 400) sh16384 = 1174078873 / 192194560000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4 v2, FP32 at `1047/125` = 8.376, the `lut256` scale path, 8192³, cap `1/400`: `9888398749/1379343520000`
(0.71689%). -/
theorem gammaFp4Hot_sm120Loop_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    gammaFp4Hot d (2 * (1047 / 125)) (1 / 400) sh8192 = 9888398749 / 1379343520000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4 v2, FP32 at `1047/125` = 8.376, the `lut256` scale path, 16384³, cap `1/400`: `5477935583/896687840000`
(0.61091%). -/
theorem gammaFp4Hot_sm120Loop_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    gammaFp4Hot d (2 * (1047 / 125)) (1 / 400) sh16384 = 5477935583 / 896687840000 := by
  rw [gammaFp4Hot, wrefFp4Hot, creditFp4Hot, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

/-- Pearl-C4 v2, chain-only, FP32 at 8.00, the `rcpApprox` scale path, 8192³, cap `1/400`: `71274809/3630560000`
(1.96319%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Issue_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    0 < creditFp4HotChainOnly d (2 * 8) sh8192 - 1 / 400 * creditFp4Hot d (2 * 8) sh8192 ∧
      gammaFp4HotChainOnly d (2 * 8) (1 / 400) sh8192 = 71274809 / 3630560000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4 v2, chain-only, FP32 at 8.00, the `rcpApprox` scale path, 16384³, cap `1/400`: `560497257/44838880000`
(1.25003%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Issue_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    0 < creditFp4HotChainOnly d (2 * 8) sh16384 - 1 / 400 * creditFp4Hot d (2 * 8) sh16384 ∧
      gammaFp4HotChainOnly d (2 * 8) (1 / 400) sh16384 = 560497257 / 44838880000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4 v2, chain-only, FP32 at 8.00, the `lut256` scale path, 8192³, cap `1/400`: `52859999/2757920000`
(1.91666%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Issue_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    0 < creditFp4HotChainOnly d (2 * 8) sh8192 - 1 / 400 * creditFp4Hot d (2 * 8) sh8192 ∧
      gammaFp4HotChainOnly d (2 * 8) (1 / 400) sh8192 = 52859999 / 2757920000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4 v2, chain-only, FP32 at 8.00, the `lut256` scale path, 16384³, cap `1/400`: `628103/51232000` (1.22600%),
with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Issue_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    0 < creditFp4HotChainOnly d (2 * 8) sh16384 - 1 / 400 * creditFp4Hot d (2 * 8) sh16384 ∧
      gammaFp4HotChainOnly d (2 * 8) (1 / 400) sh16384 = 628103 / 51232000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

/-- Pearl-C4 v2, chain-only, FP32 at `1047/125` = 8.376, the `rcpApprox` scale path, 8192³, cap `1/400`:
`4559347637/230000640000` (1.98232%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Loop_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    0 < creditFp4HotChainOnly d (2 * (1047 / 125)) sh8192 - 1 / 400 * creditFp4Hot d (2 * (1047 / 125)) sh8192 ∧
      gammaFp4HotChainOnly d (2 * (1047 / 125)) (1 / 400) sh8192 = 4559347637 / 230000640000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4 v2, chain-only, FP32 at `1047/125` = 8.376, the `rcpApprox` scale path, 16384³, cap `1/400`:
`2421535273/192194560000` (1.25994%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Loop_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    0 < creditFp4HotChainOnly d (2 * (1047 / 125)) sh16384 - 1 / 400 * creditFp4Hot d (2 * (1047 / 125)) sh16384 ∧
      gammaFp4HotChainOnly d (2 * (1047 / 125)) (1 / 400) sh16384 = 2421535273 / 192194560000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4 v2, chain-only, FP32 at `1047/125` = 8.376, the `lut256` scale path, 8192³, cap `1/400`:
`26694119149/1379343520000` (1.93528%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Loop_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    0 < creditFp4HotChainOnly d (2 * (1047 / 125)) sh8192 - 1 / 400 * creditFp4Hot d (2 * (1047 / 125)) sh8192 ∧
      gammaFp4HotChainOnly d (2 * (1047 / 125)) (1 / 400) sh8192 = 26694119149 / 1379343520000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4 v2, chain-only, FP32 at `1047/125` = 8.376, the `lut256` scale path, 16384³, cap `1/400`:
`11079842383/896687840000` (1.23564%), with its worst case positive. -/
theorem gammaFp4HotChainOnly_sm120Loop_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    0 < creditFp4HotChainOnly d (2 * (1047 / 125)) sh16384 - 1 / 400 * creditFp4Hot d (2 * (1047 / 125)) sh16384 ∧
      gammaFp4HotChainOnly d (2 * (1047 / 125)) (1 / 400) sh16384 = 11079842383 / 896687840000 := by
  constructor
  · rw [creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]
  · rw [gammaFp4HotChainOnly, wrefFp4Hot, creditFp4HotChainOnly, creditFp4Hot, creditFp4, hp]
    norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

end Pouw.PearlC
