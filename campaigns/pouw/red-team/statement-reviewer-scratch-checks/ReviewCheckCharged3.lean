import Pouw.PearlC.V2HotCharged
import Pouw.PearlC.V2HotHeadline

namespace Pouw.PearlC
open Pouw.PearlC.Assumptions

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (sem : PearlCSem Q R S) (hot : HotSem Q R S)

local notation "dL" => devSm120v2hot Prices.sm120Loop
local notation "H64" => HotSizing.publicConst 64

example : deltaHot sh8192 = some (2003 / 640000) := by
  rw [deltaHot_of_le sh8192 (by norm_num [sh8192]) (by norm_num [sh8192])]; norm_num [sh8192]
example : deltaHot sh16384 = some (9885 / 10000 * 32 / 16384) := by
  rw [deltaHot_of_wide sh16384 (by norm_num [sh16384]) (by norm_num [sh16384]) (by norm_num [sh16384])]; norm_num [sh16384]
example : deltaHot ⟨8192, 8192, 16384⟩ = some (8012 / 10000 * 32 / 16384) := by
  rw [deltaHot_of_le _ (by norm_num) (by norm_num)]; rfl
example : deltaHot ⟨65536, 65536, 65536⟩ = some (9885 / 10000 * 32 / 65536) := by
  rw [deltaHot_of_wide _ (by norm_num) (by norm_num) (by norm_num)]; rfl
example (m : ℕ) : deltaHot ⟨m, 131072, 8192⟩ = none := deltaHot_eq_none _ (Or.inr (by norm_num))
example (m : ℕ) : deltaHot ⟨m, 8192, 65537⟩ = none := deltaHot_eq_none _ (Or.inl (by norm_num))

/-- The charged headline at 16,384³ per tile, FADD 8.376, cast 8, forming credited. -/
theorem charged_tile_16384 (hT : TTOutTilePearlCDevHotCharged CM dL sem hot H64 (1 / 1000) sh16384) :
    GγSampled CM (pearlCProtocolDevHot dL sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCTilesDevHot dL sem hot H64 (1 / 1000) (8 - 8953 / 1000))
      (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh16384)
      (1 - (1 - ((1 / 400 + 9885 / 10000 * 32 / 16384 : ℚ) : ℝ)) *
        (1 - ((140663893 / 39508150000 : ℚ) : ℝ)) / (1 - 1 / 400)) εPearlC := by
  have hδ : deltaHot sh16384 = some (9885 / 10000 * 32 / 16384) := by
    rw [deltaHot_of_wide sh16384 (by norm_num [sh16384]) (by norm_num [sh16384]) (by norm_num [sh16384])]
    norm_num [sh16384]
  have := pearlCSampledHotAtγ₀ CM _ _ _ (devSm120v2 Prices.sm120Loop) H64 (8 - 8953 / 1000) (1 / 1000) sh16384
    (by norm_num) (by norm_num [creditDevHot, creditDev, devSm120v2, devAt, Prices.sm120Loop, Params.pi, sh16384])
    (by norm_num [wrefDevHot, creditDevHot, creditDev, devSm120v2, devAt, HotSizing.publicConst, Prices.sm120Loop,
      Params.pi, sh16384])
    (hotTileAccounting_sm120v2hot Prices.sm120Loop sem hot _ _ sh16384
      (wrefDevHot_nonneg_devAt sm120E4m3 Prices.sm120Loop _ _ _ (by norm_num [Prices.sm120Loop])
        (by norm_num [Prices.sm120Loop]) (by norm_num [Prices.sm120Loop])))
    _ (by norm_num) (hT _ hδ)
  rw [gammaHot_sm120v2HotLoopCast8_publicConst64_16384 (devSm120v2 Prices.sm120Loop) rfl rfl] at this
  exact this

end Pouw.PearlC
#print axioms Pouw.PearlC.ttOut_mono_gamma
#print axioms Pouw.PearlC.ttOutTile_mono_gamma
#print axioms Pouw.PearlC.deltaHotAtoms_mono
#print axioms Pouw.PearlC.deltaHotAtoms_nonneg
#print axioms Pouw.PearlC.deltaHot_of_le
#print axioms Pouw.PearlC.deltaHot_of_wide
#print axioms Pouw.PearlC.deltaHot_eq_none
#print axioms Pouw.PearlC.deltaHot_nonneg
#print axioms Pouw.PearlC.ttOutPearlCDevHotCharged_of_ttOut
#print axioms Pouw.PearlC.ttOutTilePearlCDevHotCharged_of_ttOut
#print axioms Pouw.PearlC.ttOutPearlCDevHotChainOnlyCharged_of_ttOut
#print axioms Pouw.PearlC.ttOutTilePearlCDevHotChainOnlyCharged_of_ttOut
#print axioms Pouw.PearlC.pearlCGammaHotAtγ₀
#print axioms Pouw.PearlC.pearlCSampledHotAtγ₀
#print axioms Pouw.PearlC.pearlCGammaHotChainOnlyAtγ₀
#print axioms Pouw.PearlC.pearlCSampledHotChainOnlyAtγ₀
#print axioms Pouw.PearlC.charged_tile_16384
