---
id: flock-ir-lowering/20260926T0330Z-draft-gadget-design
campaign: benchmark-coverage
lane: flock-ir-lowering
kind: draft
status: open
repo: danielreuter/verity
origin: cursor/flock-ir-lowering-c78f
---

# C-Flock generic IR lowering: the per-op piece library (design)

Goal: lower an IR subcircuit template (RoPE, SiLU·mul, both RMSNorms, later attention and sampling) into Flock's binary
R1CS by composing a small shared set of per-op pieces, so a template is a composition of pieces, never hand-written.

## 1. Pieces (`verity_flock/fp.py`, on flock-backend's `gf2.Circuit`, which is imported unchanged)

A word is a list of GF(2) linear forms, LSB first. XOR, NOT, shifts by constants and bit selection cost nothing; each AND
of two non-constant forms is one committed bit. Constants propagate: a piece is written once for general f32 operands, and
calling it on a bf16-widened operand (16 constant-zero mantissa bits) or on a constant (eps, N) specializes it
automatically, because `AND(0, x) = 0` never allocates a bit.

- **One rounding routine.** `round_f32(sign, exp, M, sticky)` normalizes an exact magnitude (leading-zero count and a
  left shift, or a right shift with sticky into the subnormal range), rounds to nearest even, carries into the exponent,
  overflows to inf and packs the word. Every op that produces an f32 ends here, so the rounding rule exists in one place.
- **f32 add, mul, fma** (sub = add with the sign bit flipped, free): exact integer datapath (swap and align with sticky,
  a 24×24 or narrower product, a wide aligned sum for fma), then `round_f32`. IEEE zero-sign rules are explicit. Specials
  (zero, subnormal, inf, NaN) go through a small mux on class flags. NaN is carried as the canonical 0x7FC00000; the
  pinned templates only observe NaN through the final bf16 casts, which canonicalize anyway (0x7FC0 torch, 0x7FFF F2FP).
- **Casts:** `Bf16ToF32` is a wire shift (free); `F2fpBf16` / `F32ToBf16Rn` / the torch variant are the 16-bit RNE add
  of `f32_to_bf16_rn_bits` plus a NaN mux.
- **Division** (`F32Div`, IEEE RN): the prover supplies the quotient as hint bits; the circuit checks the remainder
  inequality with one multiplier (a constant divisor, like RMSNorm's N, folds the multiplier away).
- **Lookups:** `lookup(idx, table)` for any unary function of a k-bit word: split idx into hi/lo, decode both to one-hot
  (≈2^lo + 2^hi ANDs), and each output bit is a sum over hi minterms of AND(hi_h, linear form over lo minterms). Costs
  ≈ 2^lo + 2^hi + 2^hi·out_bits committed bits; the table itself lives in the matrix (nnz ≈ ones in the table), which
  Flock folds once per proof, not per instance. SiLU's `bf16(silu_f32(g))` is a 16-bit lookup enumerated from the IR's
  own helper (≈2.1k bits).
- **MUFU (rsqrt, sqrt, rcp):** the exponent logic follows the IR's C++ model (`rms_triton_model.cpp`); the 2^24 (2^23)
  entry measured table is represented as `RN(f(x))` (a prover hint checked by an integer inequality, a few thousand bits)
  plus a sparse correction in {-2..+1} ulp (about 20% of entries nonzero) through `lookup`. The split is derived from the
  measured table and checked on every entry in a test, so the circuit's table is the IR's table.

## 2. Lowering (`verity_flock/ir_lower.py`)

Walk the IR Program of a Definition gate by gate, exactly as `verity.ir.evaluate` does. Each primitive id maps to one piece
(`PIECES[prim.id]`), constants become constant wires, and a primitive without a piece is an error that names it. The
walker also keeps the IR gate index of every piece's output, so a test can compare every intermediate word against the IR
evaluator's transcript, not just the outputs.

## 3. Units, derived from the IR

Flock proves `A = I ⊗ unit (+ Δ)`, so the per-instance cost is the unit's committed bits while the matrix is paid once.
The units come from the template's IR graph, not from hand-written glue:

- **Elementwise templates** (RoPE, SiLU·mul): the connected components of the gate graph (inputs included) are all the same
  shape; the unit is one component (a RoPE pair `RopeOut`+`RopeOutAdd` over x[i], x[i+R], c[i], s[i]; one `SiluMulBf16`),
  and the arrangement (which input and output leaves each unit takes) is read off the graph and checked to be total.
- **Row templates with a reduction** (both RMSNorms): the one component is split along the IR's own structure: per-element
  square units, the reduction tree (in the IR's order), one scalar unit (mean, eps, MUFU) and per-element epilogue units,
  joined by copy wires Δ. Piece circuits are built once per (primitive, constant-operand pattern) and instantiated by
  column relabelling, so a 2048-wide row never becomes millions of Python objects.

## 4. Netlist and statement

`flock-ir-unit/v1` generalizes `flock-unit-io/v1`: input words (128-bit columns, unused bits forced zero) first, then ANDs,
assertion rows, hint rows (`A = B = [i]`), output words as copy rows, and the constant column last. A pinned sha256 per
(template, parameters). The block statement `verity/flock-ir-block/v1` lives in its own module (`live/src/ir_block.rs`):
a block is U units, `A = I ⊗ unit` plus the constant pin; the unit input and output words are public regions (a
relation-only diagnostic). Binding the rows under the frame-v3 keyed-BLAKE3 scheme reuses flock-gpu-link's compression
slots and is the next step, with flock-gpu-link.

## 5. Tests

- Each piece against the IR primitive on random words over every class (zero, subnormal, normal, inf, NaN, both signs)
  and on exhaustive sweeps where cheap (every bf16 pair for the bf16-operand paths through bit-slicing).
- Each lowered template against the IR evaluator on the captured #101 sets (`art:b5bb0ca9`) and on spine synthetic
  sets: 0 mismatches, every intermediate word included.
- Negatives: a flipped output bit leaves a row unsatisfied; a mutated netlist (dropped AND, wrong table entry, swapped
  arrangement) is caught by the IR comparison.
