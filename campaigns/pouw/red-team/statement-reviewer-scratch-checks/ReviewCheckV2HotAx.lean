import Pouw.PearlC.V2HotChainOnly
import Pouw.PearlC.NoAlignedExactRegionHotBridge

namespace Pouw.PearlC

/-- A zero row scale anywhere makes `HotStartsSized` false, for every rule, semantics and starts. -/
theorem not_hotStartsSized_of_rowScale_zero {Q R S : Type} (h : HotSizing) (sem : PearlCSem Q R S) (hot : HotSem Q R S)
    (H : Q → R) (s : S) (U : Workload) (u : ℕ) (act : Codes) (i : Fin (U.layout.shape u).m)
    (h0 : hot.rowScale (U.layout.shape u).k (wordsVal (U.layout.shape u).m (U.layout.shape u).k act i) = 0) :
    ¬ HotStartsSized h sem hot := by
  intro hs
  have h1 := (hs H s U u act i).1
  simp only [h0] at h1
  exact absurd h1 (not_le.mpr (by norm_num; exact zpow_pos (by norm_num) _))

end Pouw.PearlC

#print axioms Pouw.PearlC.not_hotStartsSized_of_rowScale_zero
#print axioms Pouw.PearlC.devSm120v2hot_dev
#print axioms Pouw.PearlC.hotUnitAccounting_devHot
#print axioms Pouw.PearlC.hotTileAccounting_devHot
#print axioms Pouw.PearlC.hotUnitAccountingChainOnly_devHot
#print axioms Pouw.PearlC.hotTileAccountingChainOnly_devHot
#print axioms Pouw.PearlC.hotUnitAccounting_sm120v2hot
#print axioms Pouw.PearlC.hotTileAccounting_sm120v2hot
#print axioms Pouw.PearlC.hotUnitAccountingChainOnly_sm120v2hot
#print axioms Pouw.PearlC.hotTileAccountingChainOnly_sm120v2hot
#print axioms Pouw.PearlC.ttOutPearlCDevHotChainOnly_of_ttOut
#print axioms Pouw.PearlC.ttOutTilePearlCDevHotChainOnly_of_ttOut
#print axioms Pouw.PearlC.noAlignedExactRegionHot_of_rowCompat
