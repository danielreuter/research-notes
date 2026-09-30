---
cursor:
  subagentId: "bc-b58c6093-e25d-5e1f-817b-9b7725e0e696"
---

# Handoff for research-notes `lanes/pous/`, to relay

From the TT_OUT restatements lane (bc-b58c6093). This VM has no `~/.research`, so the pous root relays the file between
the markers verbatim as `lanes/pous/20260930T0835Z-handoff-fp8-tile-lean.md`.

~~~markdown
---
id: 20260930T0835Z-handoff-fp8-tile-lean
campaign: pous
lane: pous
kind: handoff
from: ttout-restatements (bc-b58c6093, under the pous root bc-b729c175)
to: fp4-tile-model (bc-d9842080); the PoUW Lean coordinator (bc-824e54a2)
status: open
repo: danielreuter/verity
origin: pous Project store internal/pouw/fp8-tile-lean/
created: 2026-09-30T08:35Z
---

# The FP8-tile model on `Pouw.TileBound`: one shared cost lemma, and an FP16 gap in the FP4 table

**What:** the FP4-tile count carried to sm_120's E4M3 atom, as two files that import `Pouw.TileBound.Proofs` and change
none of it.
- `Pouw/TileBound/Fp8Defs.lean` (trusted): `capacity8`, the single-entry blocks `e4m3X`/`e4m3Y`, and
  `SlotProg.Representable8`.
- `Pouw/TileBound/Fp8.lean` (proofs): 15 theorems. Every bound comes from `quad_support`.

**State:** builds on the staged package (toolchain `v4.34.0`, Mathlib `5ed29652…`). The audit passes: 591 declarations
in 9 modules, standard axioms, 38 pins (the 23 of `fp4-tile-lean` unchanged, plus 15), every declaration replayed.
`fp8-tile-pins.json` is the delta (one layer rule, 15 pins, reads), and `fp8-tile-review.txt` is `--update`'s review.

**One core lemma, for both proofs (bc-d9842080).**
- `cost_ge_supportAt`: `quad_support` priced at any base price `p₀` and any per-product prices `c`.
- Your `cost_ge_support` is its instance at `p₀ = price .fp4`. `cost_ge_support_of_at` proves it in one line, and its
  type hash is yours, `6a0ba461`.
- **Proposal:** move `cost_ge_supportAt` (and `support_admits_openAt`, the same generalization of `support_admits_open`)
  into `Proofs.lean`, and re-prove `cost_ge_support` and `support_admits_open` as instances. Their statements and pins
  don't change. `Fp8.lean` then drops its copies. Your call on the names.

**A gap in the FP4 table, for bc-d9842080: FP16 at BF16's price holds 32 blocks, not 4.**
- `Fmt.bf16` is priced "BF16 or FP16" (2 units = 4 FP4 slots), but `capacity .bf16 = 4` is BF16's 8 bits.
- FP16 has 11 significant bits. A scaled E2M1 value has 6, so an FP16 value holds 32 same-scale blocks exactly. It also
  covers their range: single values run from 2^−10 to 2,688, inside FP16's normal range, and sums of up to 32 stay in
  range unless the block scale is near its top.
- So `fmt_closed_iff` closes BF16 but not an FP16 tile at the same price. FP16 pre-adds of FP4 data are closed only up
  to 4 blocks (4 × 0.5 = 2), that is Strassen depth 2, and open from 5.
- Suggested fix: split `.fp16` out of `.bf16` with capacity 32, or set `capacity .bf16 = 32`. Then add
  `fp16_closed_upto` (4 blocks) and `fp16_open_at` (5). The page's "FP4, FP8 and BF16 routes are closed" should say
  BF16, with FP16 alongside TF32 as a depth-limited closure.
- The FP8 file already takes the FP16 case (`capacity8 .bf16 = 128`, FP16's 11 bits against 4-bit E4M3 summands).

**What the FP8 count closes** (the store's `internal/pouw/ttout-restatements.md` §6 has the argument, with the lines v1
and v2):
- **Outright:** E4M3 (tie), and NVFP4 because its capacity on in-domain E4M3 blocks is 0: no 16-block is one NVFP4 limb
  (`fmt8_closed_iff`).
- **Up to a support:** BF16 or FP16 up to 2 entries (Strassen depth 1), TF32 up to 4 (depth 2), FFMA up to 8 (depth 3).
- **Open beyond those:** `support_admits_openAt` shows no support count can close them.

**To merge:**
1. Copy the two files next to `Pouw/TileBound/`, and add `import Pouw.TileBound.Fp8` to `Pouw/TileBound.lean`.
2. Apply `fp8-tile-pins.json`.
3. Run `check.sh`.

The 15 pins need a named statement reviewer, who reads `fp8-tile-review.txt`. If the core lemma moves into `Proofs.lean`,
`cost_ge_supportAt` and `support_admits_openAt` move with it, and their hashes stay the same.
~~~
