import Pouw.PearlC.DeviceChainCapGamma
import Pouw.PearlC.DevicePricesLoop

/-!
# v2 at the chain cap 1/1,000 at sm_120's in-loop prices (the price-twins lane's file; staged)

The twins of `DeviceChainCapGamma`'s instances at `Prices.sm120Loop` in place of `Prices.sm120`, with the same
hypotheses otherwise and the same general theorems. At any record with `G = 0`: per unit `64899/17487500` (0.37112%) at
8192³ and `373769/103662500` (0.36056%) at 16384³; per audit tile the cap's γ, `522517/139900000` and
`3000127/829300000`, as at `Prices.sm120`. Each is above its issue-bound twin (0.35925%, 0.35456%; per tile 0.36162%,
0.35576%).

Every γ here is an upper bound on the in-loop γ: `Prices.sm120Loop` rounds the A-only forming (1.047) up to 2. At the
exact 1.047 the chain cap's per-unit values are 0.35980% and 0.35484%, which no pin states; the per-tile rows' exact
values are `DeviceSm120KernelGamma`'s `pearlCSampledSm120v2LoopCast8Cap1000_…`.
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions Pouw.Fp8Atom

/-- **v2 at the chain cap 1/1,000, 8192³**, per unit, at sm_120's in-loop prices (an upper bound): `γ = 64899/17487500`
(0.37112%). Twin of `pearlCGammaUnpromotedChainCap1000_8192`. -/
theorem pearlCGammaUnpromotedChainCap1000Loop_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDevChainCap CM d sem (1 / 1000)) :
    Gγ CM (pearlCProtocolDevChainCap d sem (1 / 1000)) (pearlCDomainDevAt d sh8192) ((64899 / 17487500 : ℚ) : ℝ)
      εPearlC :=
  pearlCGammaDevChainCapAt CM d sem _ _ (524625 / 523988) _ (by norm_num)
    (by rw [wrefDev, creditDev, chainCreditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v2 at the chain cap 1/1,000, 16384³**, per unit, at sm_120's in-loop prices (an upper bound): `γ =
373769/103662500` (0.36056%). Twin of `pearlCGammaUnpromotedChainCap1000_16384`. -/
theorem pearlCGammaUnpromotedChainCap1000Loop_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDevChainCap CM d sem (1 / 1000)) :
    Gγ CM (pearlCProtocolDevChainCap d sem (1 / 1000)) (pearlCDomainDevAt d sh16384) ((373769 / 103662500 : ℚ) : ℝ)
      εPearlC :=
  pearlCGammaDevChainCapAt CM d sem _ _ (1036625 / 1035476) _ (by norm_num)
    (by rw [wrefDev, creditDev, chainCreditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num) hTT

/-- **v2 at the chain cap 1/1,000 per audit tile, 8192³**, at sm_120's in-loop prices (an upper bound): `GγSampled` at
`γ = 522517/139900000`. Twin of `pearlCSampledUnpromotedChainCap1000_8192`. -/
theorem pearlCSampledUnpromotedChainCap1000Loop_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDevChainCap CM d sem (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevChainCap d sem (1 / 1000)) (pearlCTilesDevChainCap d sem (1 / 1000))
      (pearlCDomainDevAt d sh8192) ((522517 / 139900000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevChainCapAt CM d sem _ _ (349750 / 349317) _ (by norm_num)
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v2 at the chain cap 1/1,000 per audit tile, 16384³**, at sm_120's in-loop prices (an upper bound): `GγSampled` at
`γ = 3000127/829300000`. Twin of `pearlCSampledUnpromotedChainCap1000_16384`. -/
theorem pearlCSampledUnpromotedChainCap1000Loop_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDevChainCap CM d sem (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevChainCap d sem (1 / 1000)) (pearlCTilesDevChainCap d sem (1 / 1000))
      (pearlCDomainDevAt d sh16384) ((3000127 / 829300000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevChainCapAt CM d sem _ _ (2073250 / 2070927) _ (by norm_num)
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num) hTT

end Pouw.PearlC
