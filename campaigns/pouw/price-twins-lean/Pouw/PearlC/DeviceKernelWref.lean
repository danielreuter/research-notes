import Pouw.PearlC.DeviceRev1

/-!
# Pearl-C at a device record with the honest kernel's `W_ref` (the price-twins lane's file; definitions only, staged)

The statement's `W_ref` (`wrefDev`, `wrefDevRev1`) prices the honest program's forming as the credit does, with the E4M3
cast at its cheapest bit-exact implementation. The kernel as it runs can cost more: sm_120's port casts at 32.06 per
code as written and 16.00 packed four per word (`internal/pouw/rtx-pro/server.md`, 10:05Z), against a credited 8.0.
These definitions add `c` per activation element to `W_ref`, the kernel's forming beyond what the record prices, and
change nothing else: the credit, the debit, the cap and the checks are the record's, so TT_OUT reads the same game.
-/

namespace Pouw.PearlC

variable {Q R S : Type}

/-- **The honest kernel's `W_ref` at a device record**: `wrefDev` plus `c` per activation element. -/
def wrefDevK (d : PearlCDevice) (c : ℚ) (s : Shape) : ℚ := wrefDev d s + c * s.m * s.k

/-- **The honest kernel's `W_ref` under rev1**: `wrefDevRev1` plus `c` per activation element. -/
def wrefDevRev1K (d : PearlCDevice) (c : ℚ) (s : Shape) : ℚ := wrefDevRev1 d s + c * s.m * s.k

/-- `pearlCProtocolDev` with `W_ref` at `wrefDevK d c`. -/
noncomputable def pearlCProtocolDevK (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : Protocol Q R S :=
  { pearlCProtocolDev d sem ρ with Wref := fun L u => (wrefDevK d c (L.shape u) : ℝ) }

/-- `pearlCTilesDev` with `W_ref` and the credited rows' `W_ref` at `wrefDevK d c`. -/
noncomputable def pearlCTilesDevK (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : TileRules Q R S :=
  { pearlCTilesDev d sem ρ with
    Wref := fun L g =>
      let tl := auditTiling 64 64 L
      let sh := L.shape (tl.unit g)
      ((wrefDevK d c sh * tileShare sh (tl.rows g) (tl.cols g) : ℚ) : ℝ)
    Wcred := fun L g act =>
      let tl := auditTiling 64 64 L
      let sh := L.shape (tl.unit g)
      ((wrefDevK d c sh * tileShare sh (sem.passRows sh act (tl.rows g)) (tl.cols g) : ℚ) : ℝ) }

/-- `pearlCProtocolDevRev1` with `W_ref` at `wrefDevRev1K d c`. -/
noncomputable def pearlCProtocolDevRev1K (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : Protocol Q R S :=
  { pearlCProtocolDevRev1 d sem ρ with Wref := fun L u => (wrefDevRev1K d c (L.shape u) : ℝ) }

/-- `pearlCTilesDevRev1` with `W_ref` and the credited rows' `W_ref` at `wrefDevRev1K d c`. -/
noncomputable def pearlCTilesDevRev1K (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : TileRules Q R S :=
  { pearlCTilesDevRev1 d sem ρ with
    Wref := fun L g =>
      let tl := auditTiling 64 64 L
      let sh := L.shape (tl.unit g)
      ((wrefDevRev1K d c sh * tileShare sh (tl.rows g) (tl.cols g) : ℚ) : ℝ)
    Wcred := fun L g act =>
      let tl := auditTiling 64 64 L
      let sh := L.shape (tl.unit g)
      ((wrefDevRev1K d c sh * tileShare sh (sem.passRows sh act (tl.rows g)) (tl.cols g) : ℚ) : ℝ) }

end Pouw.PearlC
