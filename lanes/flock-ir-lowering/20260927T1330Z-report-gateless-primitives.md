---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

lane: flock-ir-lowering · kind: report · created: 2026-09-27T13:30Z · for: coordinator, docs site (bc-41cff24f)

# The gateless primitives left across the 13 rows, and their lowering

## Summary
- **Before (the 08:00Z export):** 22 primitive families had no gates, on 12 of the 13 rows.
- **Now:** every one of them is lowered except the MoE expert gathers `GatherBf16x64` / `GatherBf16x128` (rows #67, #68, #70, #75). Each circuit is bit-exact against its IR primitive.
- **Exact headlines:** nine rows have no gateless primitive left, so their headline sizes are exact instead of lower bounds (table 2).
- **Open question:** are the gathers a commitment opening of the committed expert weight bank, like the embedding's row gather? Or are they a circuit? As circuits they would be about two thirds to four fifths of those four headlines.
- **Where it lives:**
  - [PR #125](https://github.com/danielreuter/verity/pull/125): the keep word;
  - [PR #140](https://github.com/danielreuter/verity/pull/140), stacked on #125: the rest;
  - the export in the agent store, `internal/datasets/boolean-circuits/`, regenerated from #140's head.

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
| `GatherBf16x128_v1` | #75 7.18e+14 | 2,032 (est.) | #75 79.51% | not yet lowered (open question, §4) |
| `GatherBf16x64_v1` | #67 5.46e+15, #68 5.54e+15, #70 1.15e+15 | 1,008 (est.) | #67 65.99%, #68 65.99%, #70 65.88% | not yet lowered (open question, §4) |
| `GeluTanhMulBf16_v1` | #57 9.94e+08 | 3,260 | #57 0.07% | lowered, PR #140 |
| `HopperE4m3QgmmaDot32_v1` | #74 2.24e+15 | 6,799 | #74 79.82% | lowered, PR #140 |
| `I32Eq_v1` | #67 8.14e+07, #68 8.26e+07, #70 3.43e+07, #75 5.71e+07 | 31 | #67 <0.01%, #68 <0.01%, #70 <0.01%, #75 <0.01% | lowered, PR #140 |
| `MufuTanh_v1` | #57 4.5e+08 | 131,976 | #57 1.26% | lowered, PR #140 |
| `SelectBf16_v1` | #4 3.26e+07, #11 6.57e+07, #23 3.28e+08, #39 7.78e+07, #57 1.11e+08, #60 1.69e+07, #67 6.58e+07, #68 6.51e+07, #70 2.18e+07, #73 7.23e+07, #74 7.69e+07, #75 1.98e+07 | 16 | #4 <0.01%, #11 <0.01%, #23 <0.01%, #39 <0.01%, #57 <0.01%, #60 <0.01%, #67 <0.01%, #68 <0.01%, #70 <0.01%, #73 <0.01%, #74 <0.01%, #75 <0.01% | lowered, PR #140 |
| `TanhF32Rn_v1` | #57 1.11e+08 | 131,998 | #57 0.31% | lowered, PR #140 |
| `TopPMaskWordx128256_v1` | #101 32 | 144,877,675,028 | #101 2.96% | lowered, PR #125 |

## 2. The headlines

| row | headline at 08:00Z (≥: a lower bound) | headline now (ANDs) | gaps now |
| --- | --- | --- | --- |
| #4 smollm2-135m | ≥4.16e+14 | 4.16e+14 | none |
| #11 llama32-1b | ≥3.01e+15 | 3.01e+15 | none |
| #23 llama32-1b | ≥9.756e+15 | 9.756e+15 | none |
| #39 qwen25-15b | ≥3.846e+15 | 3.846e+15 | none |
| #57 gemma2-2b | ≥4.626e+15 | 4.704e+15 | none |
| #60 mistral-7b | ≥1.399e+16 | 1.399e+16 | none |
| #67 olmoe-1b-7b | ≥2.837e+18 | ≥2.837e+18 | GatherBf16x64_v1 |
| #68 olmoe-1b-7b | ≥2.88e+18 | ≥2.88e+18 | GatherBf16x64_v1 |
| #70 olmoe-1b-7b | ≥5.999e+17 | ≥5.999e+17 | GatherBf16x64_v1 |
| #73 qwen3-4b | ≥7.11e+15 | 7.11e+15 | none |
| #74 qwen3-4b-fp8 | ≥3.849e+18 | 1.907e+19 | none |
| #75 qwen3-30b-a3b | ≥3.761e+17 | ≥3.761e+17 | GatherBf16x128_v1 |
| #101 llama32-1b | ≥1.522e+14 | 1.568e+14 | none |

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

## 4. The open question: the MoE expert gathers
`MoeExpertRow_v1` selects the routed expert's weight row out of the whole expert weight bank, one `GatherBf16x{E}` per weight element. The expert index comes from the router; the bank is a committed weight. The embedding's row gather has the same shape, and the export (with `census/subcircuits.json`) treats that one as a commitment opening, not a circuit. There are two options:
- **An opening:** mark the gathers `commitment_opening`, as for the embedding. The four rows' headlines become exact at their current values.
- **A circuit:** a 6- or 7-level mux tree, about 1,008 ANDs per x64 gather and 2,032 per x128. That adds about 66% (the OLMoE rows) and 80% (#75) to those headlines.

## 5. Also
- **A finding for the vLLM coordinator:** the reference `topp_split.mask_kernel` is partial on rows where its two warp halves diverge. Details are in the store's `private/` (a pointer is in the coordinator note); nothing sensitive is here.
- **An identity fix:** the export's structural hash does not include which input feeds which part. The keep word's Python `max` and `min` pieces therefore shared one subcircuit type in the 10:30Z export (1 wiring instance differed). They are traced as named functions now, and the export regenerated since has 0 differing.
- **circuit-check's pins** (`tools/circuit_check/src/circuit_check/pins.json`, `known.py`) were `main`'s lowering counts. Each PR now carries its own:
  - #104 drops the `F32Add` / `F32Mul` known failures (fixed) and repins the hash-consed counts;
  - #125 pins its 25 new pieces;
  - #140 pins its 19.
  - `circuit-check --all` on each head: 808 targets, 0 new failures, the 2 known `ScaledMmFp8Block` recomputations.
- **PR heads:** #104 `f5531113`, #125 `a3c1d675` and #140 `6d168e5a`, all pushed. The export ran from `b778d521`; later commits change only the pins and merges.
- **The export (13:00Z):**
  - 86,828 subcircuit types;
  - 3,126 gate lists verified, 0 differ;
  - 59,817 wiring instances compared, 0 differ;
  - 9,009 commitment cuts agree with the program graphs' `q_word_v1`, 0 differ;
  - the integrity check finds 0 problems.
