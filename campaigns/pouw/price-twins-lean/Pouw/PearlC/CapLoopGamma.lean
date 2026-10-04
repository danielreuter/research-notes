import Pouw.PearlC.DeviceCapGamma
import Pouw.PearlC.DevicePricesLoop

/-!
# v2 at the cap 1/1,000 and v1 under rev1 at sm_120's in-loop prices (the price-twins lane's file; staged)

γ's price rule computes γ at the issue-bound FP32 add (8.00) and at the measured in-loop one (8.376), and publishes the
larger. Each theorem here is the twin of a `DeviceCapGamma` instance at `Prices.sm120Loop` in place of `Prices.sm120`,
with the same hypotheses otherwise and the same general theorem.
* **v2 at the cap 1/1,000**, at any record with `G = 0`: `522517/139900000` (0.37349%) at 8192³ and `3000127/829300000`
  (0.36177%) at 16384³, per unit and per audit tile.
* **v1 under rev1**, at any record with `G = 4`, cap 1/400: `310284613/59477920000` (0.52168%) at 8192³ and
  `1802569231/352995040000` (0.51065%) at 16384³, per unit and per audit tile.

Each is above its issue-bound twin (0.36162%, 0.35576%, 0.51056%, 0.50503%).

Every γ here is an upper bound on the in-loop γ: `Prices.sm120Loop` rounds the A-only forming (1.047) up to 2. The
exact in-loop values for v1 under rev1 and v2 at the cap are `DeviceSm120KernelGamma`'s `…LoopCast8…` pins.
-/

namespace Pouw.PearlC

open Finset Pouw.PearlC.Assumptions Pouw.Fp8Atom

/-- **v2 at the cap 1/1,000, 8192³**, at sm_120's in-loop prices (an upper bound): `γ = 522517/139900000` (0.37349%).
Twin of `pearlCGammaUnpromotedCap1000_8192`. -/
theorem pearlCGammaUnpromotedCap1000Loop_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDev CM d sem (1 / 1000)) :
    Gγ CM (pearlCProtocolDev d sem (1 / 1000)) (pearlCDomainDevAt d sh8192) ((522517 / 139900000 : ℚ) : ℝ) εPearlC :=
  pearlCGammaDevAt CM d sem _ _ (349750 / 349317) _ (by norm_num)
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v2 at the cap 1/1,000, 16384³**, at sm_120's in-loop prices (an upper bound): `γ = 3000127/829300000` (0.36177%).
Twin of `pearlCGammaUnpromotedCap1000_16384`. -/
theorem pearlCGammaUnpromotedCap1000Loop_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDev CM d sem (1 / 1000)) :
    Gγ CM (pearlCProtocolDev d sem (1 / 1000)) (pearlCDomainDevAt d sh16384) ((3000127 / 829300000 : ℚ) : ℝ) εPearlC :=
  pearlCGammaDevAt CM d sem _ _ (2073250 / 2070927) _ (by norm_num)
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num) hTT

/-- **v2 at the cap 1/1,000 per audit tile, 8192³**, at sm_120's in-loop prices (an upper bound): `GγSampled` at
`γ = 522517/139900000`. Twin of `pearlCSampledUnpromotedCap1000_8192`. -/
theorem pearlCSampledUnpromotedCap1000Loop_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDev CM d sem (1 / 1000)) :
    GγSampled CM (pearlCProtocolDev d sem (1 / 1000)) (pearlCTilesDev d sem (1 / 1000)) (pearlCDomainDevAt d sh8192)
      ((522517 / 139900000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevAt CM d sem _ _ (349750 / 349317) _ (by norm_num)
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v2 at the cap 1/1,000 per audit tile, 16384³**, at sm_120's in-loop prices (an upper bound): `GγSampled` at
`γ = 3000127/829300000`. Twin of `pearlCSampledUnpromotedCap1000_16384`. -/
theorem pearlCSampledUnpromotedCap1000Loop_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 0)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDev CM d sem (1 / 1000)) :
    GγSampled CM (pearlCProtocolDev d sem (1 / 1000)) (pearlCTilesDev d sem (1 / 1000)) (pearlCDomainDevAt d sh16384)
      ((3000127 / 829300000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevAt CM d sem _ _ (2073250 / 2070927) _ (by norm_num)
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by rw [wrefDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num) hTT

/-- **v1 under rev1, 8192³**, at sm_120's in-loop prices (an upper bound), cap 1/400: `γ = 310284613/59477920000`
(0.52168%). Twin of `pearlCGammaSm120Rev1_8192`. -/
theorem pearlCGammaSm120LoopRev1_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 4)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDevRev1 CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolDevRev1 d sem (1 / 400)) (pearlCDomainDevAt d sh8192)
      ((310284613 / 59477920000 : ℚ) : ℝ) εPearlC :=
  pearlCGammaDevRev1At CM d sem _ _ (148694800 / 148289813) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v1 under rev1, 16384³**, at sm_120's in-loop prices (an upper bound), cap 1/400: `γ = 1802569231/352995040000`
(0.51065%). Twin of `pearlCGammaSm120Rev1_16384`. -/
theorem pearlCGammaSm120LoopRev1_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 4)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutPearlCDevRev1 CM d sem (1 / 400)) :
    Gγ CM (pearlCProtocolDevRev1 d sem (1 / 400)) (pearlCDomainDevAt d sh16384)
      ((1802569231 / 352995040000 : ℚ) : ℝ) εPearlC :=
  pearlCGammaDevRev1At CM d sem _ _ (882487600 / 880181631) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]
        norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num) hTT

/-- **v1 under rev1 per audit tile, 8192³**, at sm_120's in-loop prices (an upper bound): `GγSampled` at
`γ = 310284613/59477920000`. Twin of `pearlCSampledSm120Rev1_8192`. -/
theorem pearlCSampledSm120LoopRev1_8192 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 4)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDevRev1 CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolDevRev1 d sem (1 / 400)) (pearlCTilesDevRev1 d sem (1 / 400))
      (pearlCDomainDevAt d sh8192)
      ((310284613 / 59477920000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevRev1At CM d sem _ _ (148694800 / 148289813) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]; norm_num [Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num) hTT

/-- **v1 under rev1 per audit tile, 16384³**, at sm_120's in-loop prices (an upper bound): `GγSampled` at
`γ = 1802569231/352995040000`. Twin of `pearlCSampledSm120Rev1_16384`. -/
theorem pearlCSampledSm120LoopRev1_16384 {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (d : PearlCDevice) (sem : PearlCSem Q R S) (hG : d.G = 4)
    (hp : d.prices = Prices.sm120Loop) (hTT : TTOutTilePearlCDevRev1 CM d sem (1 / 400)) :
    GγSampled CM (pearlCProtocolDevRev1 d sem (1 / 400)) (pearlCTilesDevRev1 d sem (1 / 400))
      (pearlCDomainDevAt d sh16384)
      ((1802569231 / 352995040000 : ℚ) : ℝ) εPearlC :=
  pearlCSampledDevRev1At CM d sem _ _ (882487600 / 880181631) _ (by norm_num)
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]
        norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by rw [wrefDevRev1, creditDevRev1, firstAddDev, creditDev, hG, hp]
        norm_num [Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num) hTT

end Pouw.PearlC
