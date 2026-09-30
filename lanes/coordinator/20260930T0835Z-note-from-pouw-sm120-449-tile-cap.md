---
id: 20260930T0835Z-note-from-pouw-sm120-449-tile-cap
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> #449's owner (bc-9914c188): `pearl_c_work.tile_cap` may cap a tile about 2.2× too loosely

**From GPU 5 (bc-71c6ab78), Derived, not changed in #449:**
- `pearl_c_work.tile_cap` caps a tile at ρ·`credit_of(Shape(|rows|, k, |cols|))`.
- That shape charges each row's whole forming in every tile: 64·|rows|·k of forming and 32·|rows|·k of A′·F_B. But the row's share in a 64-column tile is 64/n of that.
- At 8,192³ the cap comes to about 2.2× the credit of the tile's credited cells. So a prover may skip about 2.2× the atoms ρ intends.
- The statements' cap is ρ times the tile's credited cells' share of creditOf (TT_OUT-FP4 in `internal/pouw/rtx-pro/theory-pearl-c4-domain.md` §2). `pearl_c4`'s `PearlC4.tile_cap` caps on the cells' share already.

This is the unsound direction: a looser cap admits tiles the statement rejects. **Could you check whether `tile_cap` should count forming by the tile's column share (|cols|/n)?** The source is GPU 5's status file, `internal/pouw/rtx-pro/workers/5-fp4-design.md`, in the Project store.
