import Pouw.PearlC.V2HotChainOnly
import Pouw.PearlC.HotGamma

namespace Pouw.PearlC
open Pouw.PearlC.Assumptions

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (sem : PearlCSem Q R S) (hot : HotSem Q R S)

local notation "d8" => devSm120v2hot Prices.sm120Loop
local notation "H64" => HotSizing.publicConst 64

/-- Headline, per tile, forming credited, 8,192³, in-loop FADD, cast 8: 0.36217%. -/
theorem head_tile_8192 (hT : TTOutTilePearlCDevHot CM d8 sem hot H64 (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot d8 sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCTilesDevHot d8 sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) ((1521365753 / 420071150000 : ℚ) : ℝ) εPearlC := by
  rw [← gammaHot_sm120v2HotLoopCast8_publicConst64_8192 (devSm120v2 Prices.sm120Loop) rfl rfl]
  exact pearlCSampledSm120v2HotLoopCast8_8192 CM _ _ _ _ _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot _ _ sh8192
      (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst,
        Prices.sm120Loop, Params.pi, sh8192]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

/-- Headline, per tile, chain-only, 8,192³: 0.83709%, from the forming-credited TT_OUT. -/
theorem head_tile_chainOnly_8192 (hT : TTOutTilePearlCDevHot CM d8 sem hot H64 (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly d8 sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCTilesDevHotChainOnly d8 sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) ((3516365753 / 420071150000 : ℚ) : ℝ) εPearlC := by
  rw [← gammaHotChainOnly_sm120v2HotLoopCast8_publicConst64_8192 (devSm120v2 Prices.sm120Loop) rfl rfl]
  exact pearlCSampledSm120v2HotLoopCast8ChainOnly_8192 CM _ _ _ _ _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot _ _ sh8192
      (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst,
        Prices.sm120Loop, Params.pi, sh8192]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

/-- Headline, per tile, chain-only, 16,384³: 0.59649%. -/
theorem head_tile_chainOnly_16384 (hT : TTOutTilePearlCDevHot CM d8 sem hot H64 (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly d8 sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCTilesDevHotChainOnly d8 sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) ((235663893 / 39508150000 : ℚ) : ℝ) εPearlC := by
  rw [← gammaHotChainOnly_sm120v2HotLoopCast8_publicConst64_16384 (devSm120v2 Prices.sm120Loop) rfl rfl]
  exact pearlCSampledSm120v2HotLoopCast8ChainOnly_16384 CM _ _ _ _ _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot _ _ sh16384
      (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst,
        Prices.sm120Loop, Params.pi, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

end Pouw.PearlC

#print axioms Pouw.PearlC.head_tile_8192
#print axioms Pouw.PearlC.head_tile_chainOnly_8192
#print axioms Pouw.PearlC.head_tile_chainOnly_16384
