---
id: 20261001T0640Z-report-from-circuits-bool-elementwise-six-green
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-elementwise
---

# circuits-bool-elementwise -> @circuits: all six element-wise Definitions are Boolean, agree with their words, circuit-check green; no MUFU sub-Calls

**Branch** `cursor/bool-elementwise-8c79`, head `0d2dc46fe`, from proofs-ir's frozen head `46c768b2c` (proofs-ir is not on main
yet, so no rebase). No PR opened (circuits-bool-switch integrates).

**What landed** (11:40 PM PDT): `verity.ml.boolean.elementwise`, beside `attention`. Each Definition is traced (`trace.definition`)
from the builder C-Flock's lowering already runs for its word primitive, with `word=` the `_v1` word. None is flushed: subnormal
operands and results are kept, as the `_v1` words keep them. No new arithmetic was needed, because `fp` already had the non-FTZ builders
with the IR's NaN words. So there's no `fp_ieee` module and no edit to proofs-ir's files. Also edited: `circuit_check.targets`
(the import that makes the six Definitions catalog roots), the `definitions` section of `pins.json`, and the module maps in
`verity/ml/__init__.py` and `AGENTS.md`.

| Boolean | word view | And / Xor / Not | lowered ANDs (pinned) | C-Flock word piece, no CSE | agreement checked on |
|---|---|---|---|---|---|
| `F32Add_v3` | `F32Add_v1` | 812 / 1395 / 115 | 812 | 854 | 58² special pairs + 100k |
| `F32Mul_v3` | `F32Mul_v1` | 2430 / 4650 / 110 | 2430 | 2438 | 58² special pairs + 100k |
| `F32Fma_v3` | `F32Fma_v1` | 4485 / 7863 / 267 | 4485 | 4498 | 58³ special triples + 100k |
| `F32Div_v3` | `F32Div_v1` | 2517 / 5592 / 252 | 2517 | 2525 | 58² special pairs + 100k |
| `Bf16AddF2fp_v2` | `Bf16AddF2fp_v1` | 717 / 1061 / 122 | 717 | 754 | **all 2^32 pairs** (opt-in, 415 s) |
| `I32Add_v2` | `I32Add_v1` | 31 / 153 / 0 | 31 | 31 | 33² special pairs + 100k |

- **Special words:** signed zeros; subnormals (the smallest, the largest, and around the underflow boundary); the normal range's ends;
  ones and their neighbours; scaling powers of two; infinities; signalling and quiet NaNs with the smallest and largest payloads.
- **The 100k random inputs:** 60k uniform; 20k with exponent fields in [0, 24) or [100, 154), so products, quotients and fused sums cross
  into the subnormal range; and 20k cancelling pairs (b = -(a ± 4 ulps)).
- **Negative controls:** pointing `F32Add_v3` at the wrong word gives mismatches against `F32AddFtz_v1` (8,417) and `F32Add_v2`
  (1,114). The exhaustive harness catches a wrong NaN word and a flushed subnormal sum.
- **Exhaustive test:** `VERITY_ML_BOOLEAN_EXHAUSTIVE=1`. It packs each 2^20-pair chunk's input bits directly and compares them
  against numpy's vector add plus F2FP's batch kernel. Its own test checks that this reference equals `Bf16AddF2fp_v1`'s evaluator.
  Four of its chunks run in the default tier.
- **Gate counts and program digests:** pinned in `packages/verity/tests/ml/test_boolean_elementwise.py`. A test also checks that the
  traced Ands are exactly the builder's live ANDs (`Circuit(cse=True)`). The lowered count is below C-Flock's word piece only because
  the trace shares common ANDs.

**circuit-check** (`uv run circuit-check F32Add_v3 F32Mul_v3 F32Fma_v3 F32Div_v3 Bf16AddF2fp_v2 I32Add_v2`): 6 targets, 0 failures,
0 warnings. Each target passes the word-view correspondence (1,024 vectors, 0 mismatches), runs the C-Flock lowering whole
(0 mismatches, 0 redundant ANDs, lowered ANDs equal to its own And gates), and matches its pinned AND count. `circuit-check --all` was
not run here.

**Suites** (`tools/check/suites.py verity verity-circuit-check repository verity-flock`): all four pass. The counts are core 1,507
(1 skip, the opt-in exhaustive test), circuit_check 25, repository 33 and flock 298. Nothing new is over 5 s. Other suites only see
`packages/verity` change through the cache key, and their tests import nothing new.

**MUFU: none, and none was ever needed.** `F32Div_v1` is `div.rn.f32` (numpy's float32 division), a primitive with no MUFU inside, so
`F32Div_v3` is the IEEE divider (restoring division, one rounding) and makes no sub-Call. `DivFullRcp_v1` and `DivFullScaleA_v1` are
`div.full.f32`'s pieces. Separate Calls inside RMSNormTriton make them (`verity_vllm/program/registry/b1.py:214-217`), so they belong
to the norms worker's Definition, which sub-Calls proofs-mufu's `DivFullRcp_v2` / `DivFullScaleA_v3`.

**For circuits-bool-norms:** in SmolLM2, `F32Div_v1` is called only by `RMSNormFusedCuda`'s `mean = var / N`, with N a constant
(`b1.py:249`). C-Flock folds that constant when it lowers `F32Div_v3`:

| N | `F32Div_v3` lowered | C-Flock's word piece | why |
|---|---|---|---|
| 576 (SmolLM2) | 1,150 ANDs | 1,154 | |
| 960 | 1,120 | 1,124 | |
| 2,048 | 932 | 702 | the piece multiplies by the exact reciprocal of a power of two |

If a power-of-two N matters for a later model, the switch can emit `F32Mul_v3` by the reciprocal there, as the piece does.

**Inbox:** both 06:14Z and 06:22Z handoffs are acted on. No table reads and no MUFU uses were added, and the branch sits on the frozen head.
The 06:26Z checkpoint's "11:40 PM PDT" should read 11:26 PM PDT.
