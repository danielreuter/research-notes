import Pouw.PearlC.DeviceChainCap
import Pouw.PearlC.DeviceKernelWref

/-!
# The chain cap at a device record with the honest kernel's `W_ref` (the price-twins lane's file; definitions only,
staged)

`pearlCProtocolDevChainCap` and `pearlCTilesDevChainCap` with `W_ref` (and the tiles' credited rows' `W_ref`) at
`wrefDevK d c`, as `DeviceKernelWref.lean` does for the unit cap. The credit, the debit, the chain cap and the checks
are the record's, so TT_OUT reads the same game (`ttOut_wref`). At `c = 8 − 8953/1000` and `Prices.sm120Loop`,
`W_ref` is the exact in-loop one: the statement's cast at the credited 8.0 and the A-only forming at its measured 1.047.
-/

namespace Pouw.PearlC

variable {Q R S : Type}

/-- `pearlCProtocolDevChainCap` with `W_ref` at `wrefDevK d c`. -/
noncomputable def pearlCProtocolDevChainCapK (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : Protocol Q R S :=
  { pearlCProtocolDevChainCap d sem ρ with Wref := fun L u => (wrefDevK d c (L.shape u) : ℝ) }

/-- `pearlCTilesDevChainCap` with `W_ref` and the credited rows' `W_ref` at `wrefDevK d c`. -/
noncomputable def pearlCTilesDevChainCapK (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : TileRules Q R S :=
  { pearlCTilesDevChainCap d sem ρ with
    Wref := fun L g =>
      let tl := auditTiling 64 64 L
      let sh := L.shape (tl.unit g)
      ((wrefDevK d c sh * tileShare sh (tl.rows g) (tl.cols g) : ℚ) : ℝ)
    Wcred := fun L g act =>
      let tl := auditTiling 64 64 L
      let sh := L.shape (tl.unit g)
      ((wrefDevK d c sh * tileShare sh (sem.passRows sh act (tl.rows g)) (tl.cols g) : ℚ) : ℝ) }

end Pouw.PearlC
