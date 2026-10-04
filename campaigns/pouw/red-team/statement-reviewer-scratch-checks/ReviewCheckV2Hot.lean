import Pouw.PearlC.V2HotChainOnly
import Pouw.PearlC.HotGamma

namespace Pouw.PearlC
open Pouw.PearlC.Assumptions

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (sem : PearlCSem Q R S) (hot : HotSem Q R S)

theorem e2e_0 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_1 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_2 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_3 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_4 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_5 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_6 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_7 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (8 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (8 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_8 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8p72_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_9 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8p72_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_10 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8p72_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_11 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8p72_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_12 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8p72ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_13 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8p72ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_14 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast8p72ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_15 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (218 / 25 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast8p72ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (218 / 25 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_16 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast32p06_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_17 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast32p06_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_18 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast32p06_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_19 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast32p06_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_20 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast32p06ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_21 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast32p06ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_22 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast32p06ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_23 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (1603 / 50 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast32p06ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (1603 / 50 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_24 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast16_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_25 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast16_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_26 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast16_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_27 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHot (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast16_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_28 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast16ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_29 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast16ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_30 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotCast16ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_31 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8)) (pearlCDomainDevAt (devSm120v2 Prices.sm120) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120) (HotSizing.publicConst 64) (16 - 8) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotCast16ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120 sem hot (1 / 1000) (16 - 8) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_32 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_33 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_34 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_35 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_36 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_37 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_38 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_39 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (8 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (8 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (8 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_40 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8p72_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_41 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8p72_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_42 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8p72_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_43 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8p72_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_44 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8p72ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_45 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8p72ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_46 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast8p72ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_47 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (218 / 25 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (218 / 25 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast8p72ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (218 / 25 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_48 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast32p06_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_49 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast32p06_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_50 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast32p06_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_51 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast32p06_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_52 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast32p06ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_53 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast32p06ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_54 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast32p06ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_55 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (1603 / 50 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (1603 / 50 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast32p06ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (1603 / 50 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_56 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast16_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_57 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast16_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_58 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast16_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) hT)

theorem e2e_59 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCTilesDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHot (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast16_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) hT)

theorem e2e_60 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast16ChainOnly_8192 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_61 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh8192 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast16ChainOnly_8192 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh8192 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_62 (hT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCGammaSm120v2HotLoopCast16ChainOnly_16384 CM _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotUnitAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh16384)
    (ttOut_mono_domain (fun _ h => h.1) (ttOutPearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

theorem e2e_63 (hT : TTOutTilePearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    GγSampled CM (pearlCProtocolDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCTilesDevHotChainOnly (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000) (16 - 8953 / 1000)) (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384) (gammaHotChainOnly (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64) (16 - 8953 / 1000) (1 / 1000) sh16384 : ℝ) εPearlC :=
  pearlCSampledSm120v2HotLoopCast16ChainOnly_16384 CM _ _ _ (devSm120v2 Prices.sm120Loop) _ rfl rfl
    (hotTileAccountingChainOnly_sm120v2hot Prices.sm120Loop sem hot (1 / 1000) (16 - 8953 / 1000) sh16384 (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120, Prices.sm120Loop, Params.pi, sh8192, sh16384]))
    (ttOutTile_mono_domain (fun _ h => h.1) (ttOutTilePearlCDevHotChainOnly_of_ttOut CM _ sem hot _ _ hT))

end Pouw.PearlC
