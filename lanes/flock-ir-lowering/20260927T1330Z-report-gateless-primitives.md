---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

lane: flock-ir-lowering · kind: report · created: 2026-09-27T13:30Z, updated 21:10Z · for: coordinator, docs site (bc-41cff24f)

# The gateless primitives left across the 13 rows, and their lowering

## Summary
- **Before (the 08:00Z export):** 22 primitive families had no gates, on 12 of the 13 rows.
- **Now (21:07Z):** every primitive of every row is gates. The embedding and MoE gathers are multiplexers, and the table reads are plain gate circuits (§4). No opening or lookup kind is left.
- **Sizes:** they follow the ground-truth audit's corrections.
  - The MoE rows and #74 were 400× to 4,400× too large (a per-Call count times per-coordinate instances). They're right now, and a per-template cross-check in the export refuses that class of error.
  - Attention is weighted by the actual T histogram.
- **Where it lives:**
  - [PR #125](https://github.com/danielreuter/verity/pull/125): the keep word, following #169;
  - [PR #140](https://github.com/danielreuter/verity/pull/140), stacked on #125: the rest;
  - the export in the agent store, `internal/datasets/boolean-circuits/`.

## 1. Every gateless primitive, with the rows it affects
Instances are word gates executed per row. "Share" is the primitive's ANDs over the row's headline, which now includes them.

| primitive | rows (instances) | ANDs each | share of each row's headline | status |
| --- | --- | --- | --- | --- |
| `Bf16GtStrict_v1` | #4 3.26e+07, #11 6.57e+07, #23 3.28e+08, #39 7.78e+07, #57 1.11e+08, #60 1.69e+07, #67 6.58e+07, #68 6.51e+07, #70 2.18e+07, #73 7.23e+07, #74 7.69e+07, #75 1.98e+07 | 87 | #4 <0.01%, #11 <0.01%, #23 <0.01%, #39 <0.01%, #57 <0.01%, #60 <0.01%, #67 <0.01%, #68 <0.01%, #70 <0.01%, #73 <0.01%, #74 <0.01%, #75 <0.01% | lowered, PR #140 |
| `F32BitsShl23_v1` | #67 1.02e+07, #68 1.03e+07, #70 4.28e+06, #75 7.13e+06 | 0 | #67 0, #68 0, #70 0, #75 0 | lowered, PR #140 |
| `F32Div_v1` | #4 3.4e+05, #39 2.58e+05, #67 1.59e+05, #68 1.61e+05, #70 6.69e+04, #73 2.66e+05, #74 2.77e+09, #75 1.11e+05 | 2,517 | #4 <0.01%, #39 <0.01%, #67 <0.01%, #68 <0.01%, #70 <0.01%, #73 <0.01%, #74 <0.01%, #75 <0.01% | lowered, PR #140 |
| `F32Fabs_v1` | #74 2.75e+09 | 0 | #74 0 | lowered, PR #140 |
| `F32FmaRm_v1` | #67 1.02e+07, #68 1.03e+07, #70 4.28e+06, #75 7.13e+06 | 4,518 | #67 <0.01%, #68 <0.01%, #70 <0.01%, #75 <0.01% | lowered, PR #140 |
| `F32Fmaxf_v1` | #74 5.5e+09 | 314 | #74 <0.01% | lowered, PR #140 |
| `F32Fminf_v1` | #74 2.75e+09 | 314 | #74 <0.01% | lowered, PR #140 |
| `F32IsFinite_v1` | #67 1.02e+07, #68 1.03e+07, #70 4.28e+06, #75 7.13e+06 | 7 | #67 <0.01%, #68 <0.01%, #70 <0.01%, #75 <0.01% | lowered, PR #140 |
| `F32Neg_v1` | #67 1.02e+07, #68 1.03e+07, #70 4.28e+06, #75 7.13e+06 | 0 | #67 0, #68 0, #70 0, #75 0 | lowered, PR #140 |
| `F32Sat_v1` | #67 1.02e+07, #68 1.03e+07, #70 4.28e+06, #75 7.13e+06 | 100 | #67 <0.01%, #68 <0.01%, #70 <0.01%, #75 <0.01% | lowered, PR #140 |
| `F32Sub_v1` | #67 1.02e+07, #68 1.03e+07, #70 4.28e+06, #75 7.13e+06 | 781 | #67 <0.01%, #68 <0.01%, #70 <0.01%, #75 <0.01% | lowered, PR #140 |
| `F32ToE4m3Sat_v1` | #74 2.75e+09 | 231 | #74 <0.01% | lowered, PR #140 |
| `Fa3InvSum_v1` | #73 4.26e+06, #74 4.65e+06 | 41,542 | #73 <0.01%, #74 <0.01% | lowered, PR #140 |
| `GatherBf16x128_v1` | #75 7.18e+14 | 2,032 (est.) | #75 79.51% | commitment opening (§4) |
| `GatherBf16x64_v1` | #67 5.46e+15, #68 5.54e+15, #70 1.15e+15 | 1,008 (est.) | #67 65.99%, #68 65.99%, #70 65.88% | commitment opening (§4) |
| `GeluTanhMulBf16_v1` | #57 9.94e+08 | 3,260 | #57 0.07% | lowered, PR #140 |
| `HopperE4m3QgmmaDot32_v1` | #74 2.24e+15 | 6,799 | #74 79.82% | lowered, PR #140 |
| `I32Eq_v1` | #67 8.14e+07, #68 8.26e+07, #70 3.43e+07, #75 5.71e+07 | 31 | #67 <0.01%, #68 <0.01%, #70 <0.01%, #75 <0.01% | lowered, PR #140 |
| `MufuTanh_v1` | #57 4.5e+08 | 131,976 | #57 1.26% | lowered, PR #140 |
| `SelectBf16_v1` | #4 3.26e+07, #11 6.57e+07, #23 3.28e+08, #39 7.78e+07, #57 1.11e+08, #60 1.69e+07, #67 6.58e+07, #68 6.51e+07, #70 2.18e+07, #73 7.23e+07, #74 7.69e+07, #75 1.98e+07 | 16 | #4 <0.01%, #11 <0.01%, #23 <0.01%, #39 <0.01%, #57 <0.01%, #60 <0.01%, #67 <0.01%, #68 <0.01%, #70 <0.01%, #73 <0.01%, #74 <0.01%, #75 <0.01% | lowered, PR #140 |
| `TanhF32Rn_v1` | #57 1.11e+08 | 131,998 | #57 0.31% | lowered, PR #140 |
| `TopPMaskWordx128256_v1` | #101 32 | 144,877,675,028 | #101 2.96% | lowered, PR #125 |

## 2. The headlines

See §4 for the corrected, gates-only headlines. The 08:00Z–13:00Z values were per-Call counts times per-coordinate instances on the MoE rows and #74.

## 3. Order and batches
The order follows how much of the headlines each primitive covers.

- **1. `HopperE4m3QgmmaDot32`, the H100 FP8 k-step.** It is 80% of row #74's headline, which goes from ≥3.85 × 10¹⁸ to exactly 1.907 × 10¹⁹ ANDs.
  - `fp.tc_dot_e4m3` is `tc_dot16`'s total step on E4M3 operands, with 6,799 ANDs. `tc_dot16`'s gates are unchanged.
  - Checked on 1,500 structured vectors against the IR.
- **2. The gathers:** held for the question below.
- **3. Gemma-2's tanh family (row #57):**
  - `MufuTanh` (1.27%): the measured MUFU.TANH table between the IR's exhaustively scanned identity and saturation regions;
  - `TanhF32Rn` (0.31%): a table of the IR's own RN32 `math.tanh`, between bounds found by evaluating every word below 10.0 of both signs;
  - `GeluTanhMulBf16` (0.07%): a 2¹⁶ table of the IR's activation word, then its add, multiply and bf16 round.
  - The two tanh tables are 2²⁷-word lookup slots of 131,816 ANDs, indexed by |x|'s low 27 bits. Tests cover the region bounds, NaN and ±inf, 7,000 words each, and every GELU gate word.
- **The scalars (each under 0.01% of any headline)** went with the FP8 step, because each is a small circuit and together they touch every greedy row:
  - `Fa3InvSum`;
  - the greedy argmax: `Bf16GtStrict`, `SelectBf16`;
  - the FP8 quantizer: `F32Fabs`, `F32Fmaxf`, `F32Fminf`, `F32ToE4m3Sat`;
  - the MoE router: `F32Sub`, `F32IsFinite`, `I32Eq`, `F32Sat`, `F32Neg`, `F32BitsShl23`, `F32FmaRm`;
  - `F32Div`, a restoring divider for non-power-of-two divisors.
  - Each is checked on 6,000 vectors with exact bits.
- **The top-p keep word** (#101, PR #125): 1.45 × 10¹¹ ANDs, 32 calls, 3% of #101's headline. It is checked against `sampling.topp_keep` on 480 rows at V = 1,025 to 9,000 and on 12 rows at V = 128,256 (the three captured Llama rows at all six split counts).

## 4. Gates only (Daniel's direction, 15:08Z), and the ground-truth audit's corrections (19:00Z)

The export now has only gates, and its sizes follow the ground-truth audit (`docs/vllm-circuit-ground-truth.md` §6.2). It was republished from PR #140 at `c37bb04d` on `main` `e40fa730` with #169.

- **Gathers from committed weights are multiplexers.** This covers the embedding's row gather and the MoE expert gathers, the gate_up experts' included.
  - A gather is `tail_pieces.gather_bf16`: V − 1 candidate-pair muxes by the index's low bits, then the range select. That is 1,049 ANDs at V = 64, 2,072 at V = 128, and 16(V − 1) + about 40 for a vocabulary.
  - The commitment-opening sizing stays in code (`--gathers opening`), unpublished.
- **Constant-table reads are plain gate subcircuits of kind `table`.** These are the MUFU ex2 / rcp / rsq / sqrt tables and Gemma's tanh and GELU tables.
  - They use M0's construction and sizes: 41,308 and 49,576 ANDs per MUFU read, 131,816 per 2²⁷-word tanh read, 2,232 for GELU.
  - No `lookup-slot` or `commitment-opening` kind is left in the data.
- **The granularity bug is fixed (audit fix 1).** A group whose Calls are batches of one Definition now has that member as its template: a GEMM's output coordinates, a MoE expert GEMM's, a block-scaled FP8 GEMM's.
  - The cache key and template id include the member, so N no longer collides.
  - The MoE gate_up coordinates get `MoeExpertCoordinate_v1` with its expert gathers, not the dense coordinate (fix 2).
- **Attention is weighted by the program graph's T histogram** (`instances_by_T`, fix 3).
- **A per-template cross-check** (`index.json` `crosscheck`, fix 4) holds each template's node ANDs against its Calls' units under the no-recompute cut.
  - Within 2% is `agree`; within ×4 is `differs`, the counting-convention gap of fix 6 (RMSNorm's hash-consed warp units about 0.5×, `TokenSelect` 1.22×); beyond that the export fails.
  - GEMM, MoE, FP8, attention, embedding, RoPE and SiLU·mul agree on every row.
- **The keep word follows #169** (fix 8): each lane takes its own warp half's stop.
  - Checked on #169's constructed divergent rows, and on 80 more random rows.
  - `MufuEx2Ftz` clamps its shift as the IR's model does since `main` `7d8a11e4`: 686 → 688 ANDs.
- **circuit-check sees the gather and the keep word** (fix 7).
  - `GatherBf16x{V}` is an `ir_lower` piece family.
  - `TopPMaskWordx{V}` has its own realization, `c-flock:topp_word`, which evaluates every piece instance on the correspondence vectors (64 vectors at V = 16, 0 mismatches).

**Headlines (ANDs, republished 21:07Z; every row exact):**

| row | ANDs now | published at 13:00Z |
| --- | --- | --- |
| #101 Llama-3.2-1B b1 top-p | 1.580 × 10¹⁴ | 1.568 × 10¹⁴ |
| #4 SmolLM2-135M b16 | 3.817 × 10¹⁴ | 4.160 × 10¹⁴ |
| #11 Llama-3.2-1B b1 | 3.030 × 10¹⁵ | 3.010 × 10¹⁵ |
| #23 Llama-3.2-1B b64 | 9.565 × 10¹⁵ | 9.756 × 10¹⁵ |
| #39 Qwen2.5-1.5B b1 | 3.863 × 10¹⁵ | 3.846 × 10¹⁵ |
| #57 Gemma-2-2B b8 | 4.680 × 10¹⁵ | 4.704 × 10¹⁵ |
| #60 Mistral-7B b8 | 1.388 × 10¹⁶ | 1.399 × 10¹⁶ |
| #67 OLMoE-1B-7B b32 | 1.416 × 10¹⁶ | ≥2.837 × 10¹⁸ |
| #68 OLMoE-1B-7B b32 arrivals | 1.437 × 10¹⁶ | ≥2.880 × 10¹⁸ |
| #70 OLMoE-1B-7B TP2 b8 | 2.991 × 10¹⁵ | ≥5.999 × 10¹⁷ |
| #73 Qwen3-4B H100 b8 | 7.019 × 10¹⁵ | 7.110 × 10¹⁵ |
| #74 Qwen3-4B-FP8 H100 b8 | 4.363 × 10¹⁵ | 1.907 × 10¹⁹ |
| #75 Qwen3-30B-A3B TP2 b2 | 3.116 × 10¹⁵ | ≥3.761 × 10¹⁷ |


**Still queued:**
- **Fix 5,** a constant-index `BitAt` as wiring (0.34% of #101). The walker has to see a scan's per-iteration counter as a constant.
- **Fix 6,** one counting convention for headlines.
- **Fix 9,** anchoring `splits`. The proposal is in `internal/lanes/vllm-cross-call-check/20260927T1935Z-handoff-from-flock-ir-lowering-splits-anchor.md`: a per-step constant on the single-request rows, and `SplitsForSMS(n_live)` on a workload program. It is a statement change.
- **Fix 10,** a lowering digest.

## 5. Also
- **A finding for the vLLM coordinator,** now resolved by #169: the reference `topp_split.mask_kernel` was partial on rows where its two warp halves diverge (details in the store's `private/`).
- **An identity fix:** the export's structural hash does not include which input feeds which part. The keep word's Python `max` and `min` pieces therefore shared one subcircuit type in the 10:30Z export (1 wiring instance differed). They are traced as named functions now, and the export regenerated since has 0 differing.
- **circuit-check's pins** (`tools/circuit_check/src/circuit_check/pins.json`, `known.py`) were `main`'s lowering counts. Each PR now carries its own:
  - #104 drops the `F32Add` / `F32Mul` known failures (fixed) and repins the hash-consed counts;
  - #125 pins its 25 new pieces;
  - #140 pins its 19.
  - `circuit-check --all` on each head: 808 targets, 0 new failures, the 2 known `ScaledMmFp8Block` recomputations.
- **PR heads (21:10Z):** #104 `a96febbf`, #125 `cfc7efc4` (#169's branch merged in) and #140 `a8695c7e`, all with `main` `e40fa730` and all pushed. The export ran from `c37bb04d`; the later commits are circuit-check's view of the gathers and the keep word, and pins.
- **The export (21:07Z):**
  - 86,825 subcircuit types;
  - 3,139 gate lists verified, 0 differ;
  - 59,690 wiring instances compared, 0 differ;
  - 9,009 commitment cuts agree with the program graphs' `q_word_v1`, 0 differ;
  - the cross-check: 119 agree, 37 differ by convention, 0 fail;
  - the integrity check finds 0 problems and no opening, lookup or unlowered primitive.
