---
id: 20261001T0658Z-report-from-circuits-bool-silu-both-green
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-silu
---

# circuits-bool-silu -> @circuits: SiluMulBf16_v3 and SiluMul_v3{I} are Boolean, agree with their words, circuit-check green; no word-id sub-Calls

**Branch** `cursor/bool-silu-8c79`, head `2b2e176f8`, from proofs-ir's frozen head `46c768b2c` (proofs-ir is not on main yet, so
no rebase). No PR opened (circuits-bool-switch integrates). Both Definitions were green at 11:36 PM PDT.

**What landed:** `verity_vllm.program.registry.boolean_silu`, beside `prims` and `b1`, since the word Definitions are vLLM's and
core may not import `verity_vllm` (`test_boundaries.py`). It uses proofs-ir's builders (`fp`, `forms`, `trace`) and edits none of
their files. Also edited: `circuit_check.targets` (the import that makes both Definitions catalog roots, with `SiluMul_v3{I=8}`
bound) and the `definitions` section of `pins.json`.

| Boolean | word view | And / Xor / Not | lowered ANDs (pinned) | C-Flock word piece | agreement checked on |
|---|---|---|---|---|---|
| `SiluMulBf16_v3` | `SiluMulBf16_v1` | 1372 / 7034 / 162 | 1372 | 2699 | all 65,536 g at 12 u; 156² special pairs; 100k random; 20k edge products |
| `SiluMul_v3{I=8}` | `SiluMul_v1{I=8}` | 10976 / 56272 / 1296 | 10976 | | 5,000 rows (40,000 elements) |

- **How it's built.** `SiluMulBf16_v3` is traced from one builder: the silu half `s = bf16_rn(silu_f32(f32(g)))` on bits, then
  `bf16_rn(f32(s) * f32(u))` through `fp.f32_mul` and `fp.f32_to_bf16` with torch's NaN 0x7FC0. The silu half depends on g's
  16 bits alone. Off a band of exponents it is a closed form on g's fields: NaN gives 0x7FC0; e < 118 gives `bf16_rn(g/2)`
  (-0 gives +0); positive g with e > 129 gives g; negative g with e > 133 gives -0. On the band it is a constant-table multiplexer
  over the word Definition's own values. The table has 14 rows (a sign and an exponent pair) × 256 minterms (g's mantissa and
  lowest exponent bit), and each output bit is one AND of a row with a shared XOR chain of low minterms. An exhaustive test over
  all 65,536 g checks the closed forms off the band, and that each band edge is needed.
- **`SiluMul_v3{I}`** is `SiluMul_v1`'s body on bits: a batch of I `SiluMulBf16_v3` Calls over `(gu[i], gu[I + i])`.
- **Special words:** per sign, zero, subnormal ends, each band edge's exponents at the mantissa ends, one, the finite maximum,
  infinity, and quiet, signalling and all-ones NaNs. The **edge products** pick u so the product's exponent lands in -26..3
  (f32's subnormal range, rounded twice) or 250..257 (overflow); they gave 4,058 subnormal and 1,188 inf/NaN products.
- **Pins:** gate counts and standalone program digests in `integrations/vllm/tests/program/test_boolean_silu.py` (19 tests).
  A test also checks that the traced Ands are exactly the builder's live ANDs (`Circuit(cse=True)`).

**circuit-check** (`uv run circuit-check SiluMulBf16_v3 'SiluMul_v3{I=8}' --as-call --fail-on-warnings`): 2 targets, 0 failures,
0 warnings. Both lower whole through C-Flock (0 mismatches, 0 redundant ANDs, lowered ANDs equal to the Definition's own And gates
and to the pin). Both match the word view on 1,024 vectors (0 mismatches). Under `Q_word_v1{X=16,W=32,R=no-recompute}`, a
`SiluMulBf16_v3` Call is 1 unit and a `SiluMul_v3{I=8}` Call is 8. Each unit has 16 out bits; there are 0 committed interior
words, 0 free gates and 0 dead gates. `--all` was not run here.

**Same units as the word Program.** Word `SiluMul_v1{I}` and Boolean `SiluMul_v3{I}` both partition into I units (checked at
I = 2 and 8; both `verify` ok), so the switch's sampled-unit comparison lines up one to one. Members read disjoint words, so
the shared-operand recompute that circuits-bool-rope reported does not arise.

**Word-id sub-Calls: none.** `SiluMulBf16_v1`'s silu (`prims._silu_f32_bits`) is a float64-exact stand-in for CUDA's `expf` and
division: one primitive, with no MUFU Definition inside it. So no MUFU sub-Call was needed and none was added. Its 16-bit domain is
why the silu half is a closed form plus a small table.

**Element-wise:** the multiply is not a local copy. It is proofs-ir's `fp.f32_mul`, the builder elementwise's `F32Mul_v3`
traces (`cursor/bool-elementwise-8c79`), fused into the same trace. So there's nothing to swap. A sub-Call of `F32Mul_v3` would
cost more: `F32Mul_v3` alone is 2,430 ANDs on general f32 operands, against 1,372 for the whole fused `SiluMulBf16_v3`, because
the trace folds the 16 zero low mantissa bits of each widened bf16. It would also add a 32-bit product inside each unit.

**Suites** (`tools/check/suites.py repository verity-circuit-check verity-vllm --quick`): repository 33 and circuit_check 22 pass.
verity-vllm: 4,555 pass and 2 fail.
- P9 layering flagged `SiluMul.word = lambda ...` on a decorator-built composite as a runtime patch. Fixed in `2b2e176f8`:
  `SiluMul_v3` is now built with `CompositeDefinition(...)`, the lint's "just constructed" exception, with no allowlist growth.
  The lint passes.
- `test_tp_moe_members[qwen3-30b-a3b ... tp2]`: its `build-global` was killed for running out of memory (dmesg: a 9.2 GB
  process on this 15 GB VM, beside 4 xdist workers). Run alone on `2b2e176f8`, it passes. On this 4-core, 15 GB cloud VM,
  the suite's 4 workers run it out of memory. The check pod is the place for the full suite.

**Inbox:** the 06:14Z (no ROM gate), 06:22Z (split accepted) and 06:41Z (element-wise green) handoffs are acted on. The only table
read is the silu band's constant multiplexer. There are no MUFU uses, and the branch sits on the frozen head. There was no local
copy to swap: the multiply is `fp.f32_mul`, the builder `F32Mul_v3` traces. Its `ir_nan` choice is moot because `f32_to_bf16`
makes every NaN 0x7FC0. The branch does not depend on `cursor/bool-elementwise-8c79`, so the two merge in either order.
