import Pouw.PearlC.TTOut
import Pouw.PearlC.DeviceChainOnly

/-!
# TT_OUT under the chain-only reading at a device record (the price-twins lane's file; staged, nothing pinned)

The four chain-only forms of the record's TT_OUT: `TTOut` and `TTOutTile` at the chain-only protocol and tiles
(`DeviceChainOnly`), unit and per audit tile, unrev'd and rev1. Each is implied by the record's own TT_OUT
(`ChainOnlyGamma`'s `…ChainOnly_of_ttOut`), so none is a new assumption; they sit in an assumptions module as the
bundle's named `Prop`s do.
-/

namespace Pouw.PearlC.Assumptions

open Pouw.PearlC

variable {Q R S : Type}

/-- **TT_OUT(1/400) at a device record, chain-only**: `TTOut` at `pearlCProtocolDevKChainOnly d sem ρ 0`, whose credit
leaves out the forming. It does not read `W_ref`, so `0` is no choice. It is weaker than `TTOutPearlCDev`
(`ttOutPearlCDevChainOnly_of_ttOut`). -/
def TTOutPearlCDevChainOnly [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ : ℚ) : Prop :=
  TTOut CM (pearlCProtocolDevKChainOnly d sem ρ 0) (pearlCDomainDev d) (1 / 400) εPearlC

/-- **TT_OUT(1/400) per audit tile at a device record, chain-only.** -/
def TTOutTilePearlCDevChainOnly [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ : ℚ) : Prop :=
  TTOutTile CM (pearlCProtocolDevKChainOnly d sem ρ 0) (pearlCTilesDevKChainOnly d sem ρ 0) (pearlCDomainDev d)
    (1 / 400) εPearlC

/-- **TT_OUT(1/400) rev1 at a device record, chain-only.** -/
def TTOutPearlCDevRev1ChainOnly [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ : ℚ) : Prop :=
  TTOut CM (pearlCProtocolDevRev1KChainOnly d sem ρ 0) (pearlCDomainDev d) (1 / 400) εPearlC

/-- **TT_OUT(1/400) rev1 per audit tile at a device record, chain-only.** -/
def TTOutTilePearlCDevRev1ChainOnly [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ : ℚ) : Prop :=
  TTOutTile CM (pearlCProtocolDevRev1KChainOnly d sem ρ 0) (pearlCTilesDevRev1KChainOnly d sem ρ 0)
    (pearlCDomainDev d) (1 / 400) εPearlC

end Pouw.PearlC.Assumptions
