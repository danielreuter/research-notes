import Pouw.PearlC.HotGamma
import Pouw.PearlC.V2HotAccounting
import Pouw.PearlC.TTOutV2Hot
import Pouw.PearlC.KernelWrefGamma

open Pouw.PearlC Pouw.PearlC.Assumptions

/-- Scratch: the published 0.36217% as one closed statement, from the rev lane's TT_OUT and accounting lemma and the
price twin and value lemma. -/
theorem composeCheck {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (sem : PearlCSem Q R S) (hot : HotSem Q R S)
    (hTT : TTOutPearlCDevHot CM (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)) :
    Gγ CM (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)
        (8 - 8953 / 1000))
      (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) ((1521365753 / 420071150000 : ℚ) : ℝ) εPearlC := by
  have key := pearlCGammaSm120v2HotLoopCast8_8192 CM
    (pearlCProtocolDevHot (devSm120v2hot Prices.sm120Loop) sem hot (HotSizing.publicConst 64) (1 / 1000)
      (8 - 8953 / 1000))
    (pearlCDomainDevAt (devSm120v2 Prices.sm120Loop) sh8192) (devSm120v2 Prices.sm120Loop) (HotSizing.publicConst 64)
    rfl rfl (hotUnitAccounting_sm120v2hot Prices.sm120Loop sem hot _ _ sh8192)
    (ttOut_mono_domain (fun _ h => h.1) (ttOut_wref _ hTT))
  rwa [gammaHot_sm120v2HotLoopCast8_publicConst64_8192 _ rfl rfl] at key
#print axioms composeCheck
