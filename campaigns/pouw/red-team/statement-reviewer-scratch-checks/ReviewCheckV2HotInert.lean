import Pouw.PearlC.TTOutV2Hot

open Pouw.PearlC Pouw.PearlC.Assumptions

example {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDeviceHot) (sem : PearlCSem Q R S) (hot : HotSem Q R S) (ρ : ℚ) :
    TTOutTilePearlCDevHot CM d sem hot (HotSizing.publicConst 64) ρ = TTOutTilePearlCDevHot CM d sem hot HotSizing.colRms ρ :=
  rfl

example {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDeviceHot) (sem : PearlCSem Q R S) (hot : HotSem Q R S) (ρ : ℚ) :
    TTOutPearlCDevHot CM d sem hot (HotSizing.publicConst 64) ρ = TTOutPearlCDevHot CM d sem hot HotSizing.colRms ρ :=
  rfl
