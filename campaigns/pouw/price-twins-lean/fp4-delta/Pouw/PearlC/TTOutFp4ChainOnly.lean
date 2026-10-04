import Pouw.PearlC.TTOutFp4
import Pouw.PearlC.DeviceFp4ChainOnly

/-!
# TT_OUT under the chain-only reading at an FP4 record (the price-twins lane's file; staged, nothing pinned)

The two chain-only forms of `TTOutFp4`: `TTOut` and `TTOutTile` at the chain-only protocol and tiles
(`DeviceFp4ChainOnly`), unit and per audit tile. Each is implied by the record's own TT_OUT
(`Fp4ChainOnlyGamma`'s `…ChainOnly_of_ttOut`) at non-negative `fs`, so neither is a new assumption. They sit in an
assumptions module as the bundle's named `Prop`s do.
-/

namespace Pouw.PearlC.Assumptions

open Pouw.PearlC

variable {Q R S : Type}

/-- **TT_OUT(1/400) at an FP4 record, chain-only**: `TTOut` at `pearlCProtocolFp4ChainOnly d sem ρ`, whose credit leaves
out the forming. It is weaker than `TTOutFp4` (`ttOutFp4ChainOnly_of_ttOut`). -/
def TTOutFp4ChainOnly [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S) (d : Fp4Device)
    (sem : Fp4Sem Q R S) (ρ : ℚ) : Prop :=
  TTOut CM (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCDomainFp4 sem) (1 / 400) εPearlC

/-- **TT_OUT(1/400) per audit tile at an FP4 record, chain-only.** -/
def TTOutTileFp4ChainOnly [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S) (d : Fp4Device)
    (sem : Fp4Sem Q R S) (ρ : ℚ) : Prop :=
  TTOutTile CM (pearlCProtocolFp4ChainOnly d sem ρ) (pearlCTilesFp4ChainOnly d sem ρ) (pearlCDomainFp4 sem) (1 / 400)
    εPearlC

end Pouw.PearlC.Assumptions
