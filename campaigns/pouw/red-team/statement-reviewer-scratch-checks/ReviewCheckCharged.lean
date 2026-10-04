import Pouw.PearlC.V2HotCharged
import Pouw.PearlC.V2HotHeadline

namespace Pouw.PearlC
open Pouw.PearlC.Assumptions

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (sem : PearlCSem Q R S) (hot : HotSem Q R S)

local notation "dL" => devSm120v2hot Prices.sm120Loop
local notation "H64" => HotSizing.publicConst 64

theorem deltaHotFirst_8192 : deltaHotFirst sh8192 = 2003 / 640000 := by norm_num [deltaHotFirst, sh8192]
theorem deltaHotFirst_16384 : deltaHotFirst sh16384 = 2003 / 1280000 := by norm_num [deltaHotFirst, sh16384]

/-- Charged headline, per tile, forming credited, 8,192³, FADD 8.376, cast 8, end to end from the charged TT_OUT. -/
theorem charged_tile_8192 (hT : TTOutTilePearlCDevHotCharged CM dL sem hot H64 (1 / 1000) sh8192) :
    GγSampled CM (pearlCProtocolDevHot dL sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCTilesDevHot dL sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192)
      (1 - (1 - ((1 / 400 + deltaHotFirst sh8192 : ℚ) : ℝ)) *
        (1 - ((gammaHot (devSm120v2 Prices.sm120Loop) H64 (8 - 8953 / 1000) (1 / 1000) sh8192 : ℚ) : ℝ)) /
        (1 - 1 / 400)) εPearlC :=
  pearlCSampledHotAtγ₀ CM _ _ _ (devSm120v2 Prices.sm120Loop) H64 (8 - 8953 / 1000) (1 / 1000) sh8192 (by norm_num)
    (by norm_num [creditDevHot, creditDev, devSm120v2, devAt, Prices.sm120Loop, Params.pi, sh8192])
    (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120Loop,
      Params.pi, sh8192])
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot _ _ sh8192
      (wrefDevHot_nonneg_devAt sm120E4m3 Prices.sm120Loop _ _ _ (by norm_num [Prices.sm120Loop])
        (by norm_num [Prices.sm120Loop]) (by norm_num [Prices.sm120Loop])))
    _ (by rw [deltaHotFirst_8192]; norm_num) hT

/-- Its value: 0.67479%. -/
example : (1 - (1 - (1 / 400 + deltaHotFirst sh8192)) *
    (1 - gammaHot (devSm120v2 Prices.sm120Loop) H64 (8 - 8953 / 1000) (1 / 1000) sh8192) / (1 - 1 / 400) : ℚ) =
    1 - (1 - (1 / 400 + 2003 / 640000)) * (1 - 1521365753 / 420071150000) / (1 - 1 / 400) := by
  rw [deltaHotFirst_8192, gammaHot_sm120v2HotLoopCast8_publicConst64_8192 (devSm120v2 Prices.sm120Loop) rfl rfl]

/-- And the charged form follows from the GO'd TT_OUT at the headline shape. -/
example (hT : TTOutTilePearlCDevHot CM dL sem hot H64 (1 / 1000)) :
    TTOutTilePearlCDevHotCharged CM dL sem hot H64 (1 / 1000) sh8192 :=
  ttOutTilePearlCDevHotCharged_of_ttOut CM _ sem hot _ _ _ (by rw [deltaHotFirst_8192]; norm_num) hT

end Pouw.PearlC

#print axioms Pouw.PearlC.charged_tile_8192
#print axioms Pouw.PearlC.ttOut_mono_gamma
#print axioms Pouw.PearlC.ttOutTile_mono_gamma
#print axioms Pouw.PearlC.deltaHotFirst_nonneg
#print axioms Pouw.PearlC.ttOutPearlCDevHotCharged_of_ttOut
#print axioms Pouw.PearlC.ttOutTilePearlCDevHotCharged_of_ttOut
#print axioms Pouw.PearlC.ttOutPearlCDevHotChainOnlyCharged_of_ttOut
#print axioms Pouw.PearlC.ttOutTilePearlCDevHotChainOnlyCharged_of_ttOut
#print axioms Pouw.PearlC.pearlCGammaHotAtγ₀
#print axioms Pouw.PearlC.pearlCSampledHotAtγ₀
#print axioms Pouw.PearlC.pearlCGammaHotChainOnlyAtγ₀
#print axioms Pouw.PearlC.pearlCSampledHotChainOnlyAtγ₀
