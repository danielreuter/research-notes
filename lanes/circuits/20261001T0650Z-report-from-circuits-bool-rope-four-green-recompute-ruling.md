---
id: 20261001T0650Z-report-from-circuits-bool-rope-four-green-recompute-ruling
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# circuits-bool-rope -> @circuits: all four RoPE Definitions are Boolean and agree with their words; circuit-check is green; as Calls they fail `gate-recomputed` (needs a ruling)

**Branch** `cursor/bool-rope-8c79`, head `43d7e4309`, based on proofs-ir's frozen head `46c768b2c`. proofs-ir is not on main yet,
so there was no rebase. No PR (circuits-bool-switch integrates). The first Definition was green at 11:22 PM PDT and all four at
11:38 PM PDT, ahead of the 2:05 AM and 4:50 AM PDT targets.

## What landed

- `integrations/vllm/verity_vllm/program/registry/boolean_rope.py` sits next to the word Definitions (`prims.RopeOut` /
  `RopeOutAdd`, `b1.RoPEHead` / `RoPE`).
  - `RopeOut_v2` and `RopeOutAdd_v2` are traced (`trace.definition`) from core's `fp` builders: `bf16_to_f32` (free wiring),
    `f32_mul`, `f32_fma`, `f32_neg` and `f32_to_bf16`, with the torch NaN `0x7FC0`.
  - `RoPEHead_v2{D}` and `RoPE_v2{NHEADS,D}` are b1's bodies on bits. Each is a batch of Calls, separable, so every output
    element is one proof unit, exactly as in the word Program.
  - `word=` is set on all four: `RopeOut_v1`, `RopeOutAdd_v1`, `RoPEHead_v1{D}`, `RoPE_v1{NHEADS,D}`.
- `integrations/vllm/tests/program/test_boolean_rope.py` has 17 tests, about 28 s with the slow ones.
- `circuit_check.targets._boolean_roots` gains `bind(boolean_rope.RoPE, NHEADS=2, D=8)`, which reaches the head and both halves.
  `pins.json` "definitions" gains their four AND counts.
- No proofs-ir file was edited. `tests/test_boundaries.py` and the protocol boundaries are untouched: vLLM imports core, never
  the reverse.

| Boolean | word view | And / Xor / Not | standalone ANDs, C-Flock lowering | agreement checked on |
|---|---|---|---|---|
| `RopeOut_v2` | `RopeOut_v1` | 2,966 / 4,608 / 295 | 2,966 (pinned, 0 redundant) | 22^4 = 234,256 special quadruples + 90k |
| `RopeOutAdd_v2` | `RopeOutAdd_v1` | 2,966 / 4,608 / 294 | 2,966 (pinned, 0 redundant) | 22^4 special quadruples + 90k |
| `RoPEHead_v2{D=64}` | `RoPEHead_v1{D=64}` | 189,824 / 294,912 / 18,848 | (over the 60k lowering budget) | 1,500 heads (IR reference) |
| `RoPE_v2{NHEADS=9,D=64}` (q) | `RoPE_v1{NHEADS=9,D=64}` | 1,708,416 / 2,654,208 / 169,632 | (over budget) | 81k heads |
| `RoPE_v2{NHEADS=3,D=64}` (k) | `RoPE_v1{NHEADS=3,D=64}` | 569,472 / 884,736 / 56,544 | (over budget) | 81k heads |

- **Special words:** 0, the smallest subnormal, the smallest normal, 2^-64, 1, √2, 2^64, the largest finite value, inf, the quiet
  NaN and a signalling NaN, each in both signs. All 22^4 tuples are checked per half.
- **The 90k random quadruples per half:**
  - 40k uniform.
  - 20k activations against real cos/sin.
  - 10k cancelling x·c ≈ y·s.
  - 10k with about 72% of y·s products subnormal.
  - 10k bf16 rounding ties.
- **Served shapes:** 81k random heads each (`@slow`, about 7 s each), compared bit for bit against `RoPE_v1`'s registered kernel.
- **Negative controls:** a wrong NaN word gives 136,920 special mismatches. A product that drops subnormals gives 9,864 special
  and 17,634 random mismatches.
- **Pins:** each count and standalone program digest is pinned in the test. A test checks that the traced Ands are exactly the
  builders' live ANDs.
- **Purity:** every gate, in every sub-Call, is And2/Xor2/Not/Const1.

## circuit-check: green

The reports are `art:803fc1b93feee93c33203f24a0298dec0e397316f7ec375ef2f5fa949fad8f72`. They were run at `50156733c`;
`43d7e4309` changes only how the two composites are constructed, and the pinned program digests are unchanged.

- **`uv run circuit-check 'RoPE_v2{NHEADS=2,D=8}' 'RoPEHead_v2{D=8}' RopeOut_v2 RopeOutAdd_v2`:** 4 targets, 0 failures.
  - Each target compares 1,024 word-view vectors with 0 mismatches.
  - The C-Flock lowering runs whole, with 0 mismatches and ANDs equal to the pins: 2,966, 2,966, 23,728 and 47,456.
  - The halves have 0 warnings, and each is 1 unit of 16 bits.
  - The composites warn `redundant-gates/ir` (1,120 and 2,960) and `redundant-gates/boolean` (416 and 1,104). These are the
    shared operand decode described in the next section.
- **Served shapes `RoPEHead_v2{D=64}`, `RoPE_v2{NHEADS=3,D=64}`, `RoPE_v2{NHEADS=9,D=64}`:** 3 targets, 0 failures.
  - Each compares 1,024 word-view vectors with 0 mismatches.
  - The lowering is skipped as over budget.
  - Units are 64, 192 and 576 output units of 16 bits, the word Program's.
  - Run times were 60 s, 139 s and 402 s.
- `circuit-check --all` was not run here.

## Partition: as Calls, the composites fail `gate-recomputed`. Ruling needed (proofs / Daniel)

`circuit-check 'RoPEHead_v2{D=16}' --as-call` gives `FAIL partition/gate-recomputed (2,240 gates)`, 280 per rotation pair. The
cause:
- `RopeOut_v2` and `RopeOutAdd_v2` on the same (x[i], x[i+R], c[i], s[i]) both decode those words with identical gates
  (exponent and mantissa or-reductions, the NaN/inf/zero flags).
- `Q_word` v1's no-recompute rule forbids the same gate on the same operands in two units.
- Across heads, the shared cos/sin row is decoded again in every head. At q's shape, circuit-check isolates 92,160 gates.

This is not RoPE-specific: two `GemmCoordinate_v3{K=16}` sharing `x` in one Call fail the same way (1,776 gates). So Boolean
Gemm, attention and norms hit it as soon as their composites are Calls. A word primitive hides the decode inside one gate.

Computing the decode once (a fused pair Definition) passes `verify`, but it is not worth it. It saves 104 ANDs per pair and commits
83 interior bits per pair: 115 committed bits against the word's 32.

**Recommendation:** let `Q_word` (a v2) read each Call of a Boolean Definition as one opaque node, keyed by Definition and operand
tokens as a word primitive is. Units and committed sets would then stay the word Program's. Until a ruling, I keep the
per-element design. The full note is the project store's `internal/circuits/bool-rope-recompute.md`.

**For the switch:** when `RoPE_v2` becomes a call family (the served Program), circuit-check will fail it with
`partition/gate-recomputed`. Either take the ruling or add a `known.py` entry; the precedent is
`partition/gate-recomputed ScaledMmFp8Block_v1`.

## Element-wise and MUFU

- **Element-wise:** nothing was duplicated. `F32Mul_v3` and `F32Fma_v3` (`cursor/bool-elementwise-8c79`) trace the same core
  builders (`fp.f32_mul`, `fp.f32_fma`). `RopeOut_v2` traces them inline on widened bf16 operands, so constant propagation keeps
  an 8×8 product.
  - Sub-Calling them would cost 2,430 + 4,485 ANDs plus the cast per element, against 2,966.
  - It would also add 32-bit interior values, above X = 16.
  - So there is nothing to swap.
- **MUFU:** none. RoPE makes no table read.
- **Merging with element-wise:** `git merge-tree` shows two trivial conflicts.
  - `pins.json`: both append sorted keys after `HopperBF16WgmmaDot16_v2`. Keep both, with `I32Add_v2` before `RoPE*`.
  - The `_boolean_roots` docstring in `targets.py`: keep both sentences.

## Suites

At `43d7e4309`, `uv run tools/check/suites.py verity-vllm verity-circuit-check repository --quick --jobs 1` passed all three:
- vLLM: 4,566 passed and 327 skipped, in 33 min on this 4-core VM.
- circuit_check: 22 passed.
- repository: 33 passed.

Without `--quick`, `pytest -m circuit_suite -k "RoPE or RopeOut"` gives 35 passed, the four new ids among them.
`test_boolean_rope.py`, slow tests included, gives 17 passed.

The first run, at `50156733c` with the suites in parallel, failed two vLLM tests:
- **P9 layering lint (fixed in `43d7e4309`):** a decorator-built composite's `.word = lambda` reads as a runtime patch; see the
  next section.
- **The stored qwen3 TP2 MoE `build-global`:** "the build process died", from memory pressure with three suites sharing 15 GB. It
  passed when run alone (15 min) with `boolean_rope` loaded, and in the sequential run.

Other suites list `integrations/vllm` as an input but were not run here; `check` will run them.

## For every vLLM Boolean lane: the P9 lint and `word`

In `verity_vllm`, `X.word = lambda b: ...` on a composite built with `@composite` fails `tests/lint/test_p09_layering.py` as a
`runtime-patch`. The lint reads a decorator-built object as a live object being patched. Build the composite with
`CompositeDefinition(name, version, statics, signature, body, doc=body.__doc__, conformance=...)` and then set `.word`: the
lint accepts that as construction, and the descriptor is byte-identical. core's `verity.ml.boolean.gemm` is not linted, so it
can keep the decorator.

## Friction (fixed for this VM)

This Cloud Agent VM had no `~/.research/notes`, so `research notes checkpoint` wrote into a fresh non-git directory and `sync`
failed. I cloned `danielreuter/research-notes` there, with a credential helper that reads `RESEARCH_NOTES_TOKEN` from the
environment, so no token is written to disk. The next lane VM will hit the same thing until the environment's setup clones it.
