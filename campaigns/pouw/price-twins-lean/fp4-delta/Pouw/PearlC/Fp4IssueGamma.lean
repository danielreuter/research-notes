import Pouw.PearlC.DeviceFp4Gamma
import Pouw.PearlC.DeviceFp4Issue

/-!
# Pearl-C4 at the issue-bound FP32 price (the price-twins lane's file; staged)

γ's price rule computes γ at the issue-bound FP32 operation (8.00, `Prices.sm120`'s FADD) and at the measured in-loop
one (8.38), and publishes the larger. `Fp4Prices.sm120` is the in-loop price; this file holds γ at the issue-bound one
(`Fp4Prices.sm120Issue`), cap `1/400`, forming credited, per unit and per audit tile: `162371257/22950880000`
(0.70747%) at 8192³ and `814384171/134388640000` (0.60599%) at 16384³. Both are below the in-loop headline at the
repriced record (0.71731% and 0.61104%, `fs = 21887/200`), so the rule publishes the in-loop one.

Each theorem holds at any FP4 record `d` with these prices (`hp`), for any `sem`: the forming, the ticket, U, the flags,
the sub-grid flags and the salt-dead predicate, which make up the domain rules' debit, are not fixed here. So the
statements read the domain rules only through `pearlCProtocolFp4`, `pearlCTilesFp4` and `pearlCDomainFp4At`, as the
general `pearlCGammaFp4At` does. `{ devFp4Sm120 with prices := Fp4Prices.sm120Issue }` meets `hp` by `rfl`.
-/

namespace Pouw.PearlC

open Pouw.PearlC.Assumptions

/-- **Pearl-C4 at the issue-bound price, 8192³**, at any FP4 record with those prices, cap `1/400`:
`γ = 162371257/22950880000` (0.70747%). -/
theorem pearlCGammaFp4Sm120Issue_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (hp : d.prices = Fp4Prices.sm120Issue)
    (hTT : TTOutFp4 CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh8192)
      ((162371257 / 22950880000 : ℚ) : ℝ) εPearlC :=
  pearlCGammaFp4At CM d sem _ _ (57377200 / 57114057) _ (by norm_num)
    (by rw [wrefFp4, creditFp4, hp]
        norm_num [Fp4Prices.sm120Issue, Params.pi, sh8192]) (by norm_num) hTT

/-- **Pearl-C4 at the issue-bound price, 16384³**, at any FP4 record with those prices, cap `1/400`:
`γ = 814384171/134388640000` (0.60599%). -/
theorem pearlCGammaFp4Sm120Issue_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (hp : d.prices = Fp4Prices.sm120Issue)
    (hTT : TTOutFp4 CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh16384)
      ((814384171 / 134388640000 : ℚ) : ℝ) εPearlC :=
  pearlCGammaFp4At CM d sem _ _ (335971600 / 334772571) _ (by norm_num)
    (by rw [wrefFp4, creditFp4, hp]
        norm_num [Fp4Prices.sm120Issue, Params.pi, sh16384]) (by norm_num) hTT

/-- **Pearl-C4 at the issue-bound price per audit tile, 8192³**, at any FP4 record with those prices, cap `1/400`:
`GγSampled` at `γ = 162371257/22950880000` (0.70747%). -/
theorem pearlCSampledFp4Sm120Issue_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (hp : d.prices = Fp4Prices.sm120Issue)
    (hTT : TTOutTileFp4 CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCTilesFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh8192)
      ((162371257 / 22950880000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledFp4At CM d sem _ _ (57377200 / 57114057) _ (by norm_num)
    (by rw [wrefFp4, creditFp4, hp]
        norm_num [Fp4Prices.sm120Issue, Params.pi, sh8192])
    (by rw [wrefFp4, creditFp4, hp]
        norm_num [Fp4Prices.sm120Issue, Params.pi, sh8192]) (by norm_num) hTT

/-- **Pearl-C4 at the issue-bound price per audit tile, 16384³**, at any FP4 record with those prices, cap `1/400`:
`GγSampled` at `γ = 814384171/134388640000` (0.60599%). -/
theorem pearlCSampledFp4Sm120Issue_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (hp : d.prices = Fp4Prices.sm120Issue)
    (hTT : TTOutTileFp4 CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCTilesFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh16384)
      ((814384171 / 134388640000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledFp4At CM d sem _ _ (335971600 / 334772571) _ (by norm_num)
    (by rw [wrefFp4, creditFp4, hp]
        norm_num [Fp4Prices.sm120Issue, Params.pi, sh16384])
    (by rw [wrefFp4, creditFp4, hp]
        norm_num [Fp4Prices.sm120Issue, Params.pi, sh16384]) (by norm_num) hTT

/-! ## At any FP32 price and scale path

The twins below hold at any record priced `Fp4Prices.sm120At fadd p`, at γ `gammaFp4 d (1/400) s`. So repricing the
scale step, or the FP32 price, instantiates `p` or `fadd` and re-proves nothing. The `gammaFp4_…` lemmas give γ at both
FP32 prices (8.00 and `1047/125` = 8.376) and both scale paths. The four pins above are the `rcp.approx`, 8.00 case,
as `Fp4Prices.sm120Issue_eq` shows. -/

theorem Fp4Prices.sm120Issue_eq : Fp4Prices.sm120Issue = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox := by
  simp only [Fp4Prices.sm120Issue, Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Fp4Prices.mk.injEq]
  norm_num

/-- **Pearl-C4 at any FP32 price and scale path, 8192³**, cap `1/400`: `G_γ` at `gammaFp4 d (1/400) sh8192`. -/
theorem pearlCGammaFp4Sm120At_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hTT : TTOutFp4 CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh8192) (gammaFp4 d (1 / 400) sh8192 : ℝ)
      εPearlC := by
  have hc : 0 < creditFp4 d sh8192 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh8192]
    push_cast
    nlinarith
  have hw : 0 < wrefFp4 d sh8192 := by
    have hq : 0 ≤ d.prices.qa * (sh8192.m : ℚ) * sh8192.k := by
      rw [hp]; simp only [Fp4Prices.sm120At, sh8192]; push_cast; nlinarith
    rw [wrefFp4]; linarith
  have hden : 0 < (1 - 1 / 400 : ℚ) * creditFp4 d sh8192 := by positivity
  exact pearlCGammaFp4At CM d sem _ _ (wrefFp4 d sh8192 / ((1 - 1 / 400) * creditFp4 d sh8192)) _
    (div_pos hw hden) (div_mul_cancel₀ _ hden.ne').symm rfl hTT

/-- **Pearl-C4 at any FP32 price and scale path, 16384³**, cap `1/400`: `G_γ` at `gammaFp4 d (1/400) sh16384`. -/
theorem pearlCGammaFp4Sm120At_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hTT : TTOutFp4 CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh16384) (gammaFp4 d (1 / 400) sh16384 : ℝ)
      εPearlC := by
  have hc : 0 < creditFp4 d sh16384 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh16384]
    push_cast
    nlinarith
  have hw : 0 < wrefFp4 d sh16384 := by
    have hq : 0 ≤ d.prices.qa * (sh16384.m : ℚ) * sh16384.k := by
      rw [hp]; simp only [Fp4Prices.sm120At, sh16384]; push_cast; nlinarith
    rw [wrefFp4]; linarith
  have hden : 0 < (1 - 1 / 400 : ℚ) * creditFp4 d sh16384 := by positivity
  exact pearlCGammaFp4At CM d sem _ _ (wrefFp4 d sh16384 / ((1 - 1 / 400) * creditFp4 d sh16384)) _
    (div_pos hw hden) (div_mul_cancel₀ _ hden.ne').symm rfl hTT

/-- **Pearl-C4 per audit tile at any FP32 price and scale path, 8192³**, cap `1/400`: `GγSampled` at
`gammaFp4 d (1/400) sh8192`. -/
theorem pearlCSampledFp4Sm120At_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hTT : TTOutTileFp4 CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCTilesFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh8192)
      (gammaFp4 d (1 / 400) sh8192 : ℝ) εPearlC := by
  have hc : 0 < creditFp4 d sh8192 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh8192]
    push_cast
    nlinarith
  have hw : 0 < wrefFp4 d sh8192 := by
    have hq : 0 ≤ d.prices.qa * (sh8192.m : ℚ) * sh8192.k := by
      rw [hp]; simp only [Fp4Prices.sm120At, sh8192]; push_cast; nlinarith
    rw [wrefFp4]; linarith
  have hden : 0 < (1 - 1 / 400 : ℚ) * creditFp4 d sh8192 := by positivity
  exact pearlCSampledFp4At CM d sem _ _ (wrefFp4 d sh8192 / ((1 - 1 / 400) * creditFp4 d sh8192)) _
    (div_pos hw hden) hw.le (div_mul_cancel₀ _ hden.ne').symm rfl hTT

/-- **Pearl-C4 per audit tile at any FP32 price and scale path, 16384³**, cap `1/400`: `GγSampled` at
`gammaFp4 d (1/400) sh16384`. -/
theorem pearlCSampledFp4Sm120At_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : Fp4Device) (sem : Fp4Sem Q R S) (fadd : ℚ) (p : Fp4ScalePath) (hf : 0 ≤ fadd)
    (hp : d.prices = Fp4Prices.sm120At fadd p) (hTT : TTOutTileFp4 CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolFp4 d sem (1 / 400)) (pearlCTilesFp4 d sem (1 / 400)) (pearlCDomainFp4At sem sh16384)
      (gammaFp4 d (1 / 400) sh16384 : ℝ) εPearlC := by
  have hc : 0 < creditFp4 d sh16384 := by
    have h1 := p.fixed_nonneg
    have h2 := mul_nonneg p.fp32Ops_nonneg hf
    rw [creditFp4, hp]
    simp only [Fp4Prices.sm120At, Params.pi, sh16384]
    push_cast
    nlinarith
  have hw : 0 < wrefFp4 d sh16384 := by
    have hq : 0 ≤ d.prices.qa * (sh16384.m : ℚ) * sh16384.k := by
      rw [hp]; simp only [Fp4Prices.sm120At, sh16384]; push_cast; nlinarith
    rw [wrefFp4]; linarith
  have hden : 0 < (1 - 1 / 400 : ℚ) * creditFp4 d sh16384 := by positivity
  exact pearlCSampledFp4At CM d sem _ _ (wrefFp4 d sh16384 / ((1 - 1 / 400) * creditFp4 d sh16384)) _
    (div_pos hw hden) hw.le (div_mul_cancel₀ _ hden.ne').symm rfl hTT

/-! ## The values: both FP32 prices, both scale paths -/

/-- Pearl-C4's γ at FP32 8.00, the `rcpApprox` scale path, 8192³, cap `1/400`: `162371257/22950880000` (0.70747%). -/
theorem gammaFp4_sm120Issue_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    gammaFp4 d (1 / 400) sh8192 = 162371257 / 22950880000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4's γ at FP32 8.00, the `rcpApprox` scale path, 16384³, cap `1/400`: `814384171/134388640000` (0.60599%). -/
theorem gammaFp4_sm120Issue_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox) :
    gammaFp4 d (1 / 400) sh16384 = 814384171 / 134388640000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4's γ at FP32 `1047/125` = 8.376, the `rcpApprox` scale path, 8192³, cap `1/400`: `1646385229/229553920000`
(0.71721%). -/
theorem gammaFp4_sm120Loop_rcpApprox_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    gammaFp4 d (1 / 400) sh8192 = 1646385229 / 229553920000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh8192]

/-- Pearl-C4's γ at FP32 `1047/125` = 8.376, the `rcpApprox` scale path, 16384³, cap `1/400`: `8211859687/1344021760000`
(0.61099%). -/
theorem gammaFp4_sm120Loop_rcpApprox_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.rcpApprox) :
    gammaFp4 d (1 / 400) sh16384 = 8211859687 / 1344021760000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.rcpApprox, Params.pi, sh16384]

/-- Pearl-C4's γ at FP32 8.00, the `lut256` scale path, 8192³, cap `1/400`: `6492677/917600000` (0.70757%). -/
theorem gammaFp4_sm120Issue_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    gammaFp4 d (1 / 400) sh8192 = 6492677 / 917600000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4's γ at FP32 8.00, the `lut256` scale path, 16384³, cap `1/400`: `32568847/5374240000` (0.60602%). -/
theorem gammaFp4_sm120Issue_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At 8 Fp4ScalePath.lut256) :
    gammaFp4 d (1 / 400) sh16384 = 32568847 / 5374240000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

/-- Pearl-C4's γ at FP32 `1047/125` = 8.376, the `lut256` scale path, 8192³, cap `1/400`: `9875013901/1376663200000`
(0.71732%). -/
theorem gammaFp4_sm120Loop_lut256_8192
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    gammaFp4 d (1 / 400) sh8192 = 9875013901 / 1376663200000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh8192]

/-- Pearl-C4's γ at FP32 `1047/125` = 8.376, the `lut256` scale path, 16384³, cap `1/400`: `5473473967/895794400000`
(0.61102%). -/
theorem gammaFp4_sm120Loop_lut256_16384
    (d : Fp4Device) (hp : d.prices = Fp4Prices.sm120At (1047 / 125) Fp4ScalePath.lut256) :
    gammaFp4 d (1 / 400) sh16384 = 5473473967 / 895794400000 := by
  rw [gammaFp4, wrefFp4, creditFp4, hp]
  norm_num [Fp4Prices.sm120At, Fp4ScalePath.lut256, Params.pi, sh16384]

/-- `devFp4Sm120`'s maps at the issue-bound prices meet the twins' `hp`. -/
example : ({ devFp4Sm120 with prices := Fp4Prices.sm120Issue } : Fp4Device).prices = Fp4Prices.sm120Issue := rfl

end Pouw.PearlC
