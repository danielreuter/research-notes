import Pouw.PearlC.TileUOnlyGamma
import Pouw.PearlC.DevicePricesLoop

/-!
# U-only binding at sm_120's in-loop prices (the price-twins lane's file; staged)

The twins of `UOnlyGamma`'s and `TileUOnlyGamma`'s instances at `Prices.sm120Loop` in place of `Prices.sm120`, with the
same hypotheses otherwise and the same general theorems, at 8192³, per unit and per audit tile: v1 under rev1 (`G = 4`,
cap 1/400) at `310284613/59477920000` (0.52168%) and v2 at the cap 1/1,000 (`G = 0`) at `522517/139900000` (0.37349%).
Each is above its issue-bound twin (0.51056%, 0.36162%).

Every γ here is an upper bound on the in-loop γ: `Prices.sm120Loop` rounds the A-only forming (1.047) up to 2. At the
exact 1.047 the values are those of `DeviceSm120KernelGamma`'s `…LoopCast8…` pins (0.51105% and 0.36218%), which state
them under (C̃, U) binding; no pin states them under U-only binding.
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions Pouw.Fp8Atom

/-- **v1 under rev1 with U-only binding, 8192³**, at sm_120's in-loop prices (an upper bound), cap 1/400:
`γ = 310284613/59477920000`. Twin of `pearlCGammaUOnlySm120Rev1_8192`. -/
theorem pearlCGammaUOnlySm120LoopRev1_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 4)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDevUOnly CM d sem (1 / 400)) :
    GγU CM (pearlCProtocolDevRev1 d sem (1 / 400)) (pearlCDomainDevAt d sh8192) ((310284613 / 59477920000 : ℚ) : ℝ)
      εPearlC :=
  pearlCGammaDevUOnlyAt CM d sem _ _ (148694800 / 148289813) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v2 at the cap 1/1,000 with U-only binding, 8192³**, at sm_120's in-loop prices (an upper bound): `γ =
522517/139900000`. Twin of `pearlCGammaUOnlyUnpromotedCap1000_8192`. -/
theorem pearlCGammaUOnlyUnpromotedCap1000Loop_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDevUOnly CM d sem (1 / 1000)) :
    GγU CM (pearlCProtocolDevRev1 d sem (1 / 1000)) (pearlCDomainDevAt d sh8192) ((522517 / 139900000 : ℚ) : ℝ)
      εPearlC :=
  pearlCGammaDevUOnlyAt CM d sem _ _ (349750 / 349317) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v1 under rev1 per audit tile with U-only binding, 8192³**, at sm_120's in-loop prices (an upper bound), cap 1/400:
`γ = 310284613/59477920000`. Twin of `pearlCSampledUOnlySm120Rev1_8192`. -/
theorem pearlCSampledUOnlySm120LoopRev1_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 4)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDevUOnly CM d sem (1 / 400)) :
    GγSampledU CM (pearlCProtocolDevRev1 d sem (1 / 400)) (pearlCTilesDevRev1 d sem (1 / 400))
      (pearlCDomainDevAt d sh8192) ((310284613 / 59477920000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevUOnlyAt CM d sem _ _ (148694800 / 148289813) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v2 at the cap 1/1,000 per audit tile with U-only binding, 8192³**, at sm_120's in-loop prices (an upper bound):
`γ = 522517/139900000`. Twin of `pearlCSampledUOnlyUnpromotedCap1000_8192`. -/
theorem pearlCSampledUOnlyUnpromotedCap1000Loop_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDevUOnly CM d sem (1 / 1000)) :
    GγSampledU CM (pearlCProtocolDevRev1 d sem (1 / 1000)) (pearlCTilesDevRev1 d sem (1 / 1000))
      (pearlCDomainDevAt d sh8192) ((522517 / 139900000 : ℚ) : ℝ)
      εPearlC :=
  pearlCSampledDevUOnlyAt CM d sem _ _ (349750 / 349317) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

end Pouw.PearlC
