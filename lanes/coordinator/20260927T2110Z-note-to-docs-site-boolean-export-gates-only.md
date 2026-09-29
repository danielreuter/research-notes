---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the docs-site worker (bc-41cff24f): the Boolean export is republished with only gates and corrected sizes

**From:** flock-ir-lowering, 21:10Z. **Via:** coordinator. Supersedes [20260927T1335Z](20260927T1335Z-note-to-docs-site-boolean-export.md) on openings, lookup slots and sizes.

`internal/datasets/boolean-circuits/` was republished at 21:07Z from PR #140 at `c37bb04d` (`main` `e40fa730` plus #169). Its README is current. It follows Daniel's direction (the simplest ontology, only gates) and the ground-truth audit's corrections (`docs/vllm-circuit-ground-truth.md` §6.2).

- **No openings, no lookups.**
  - Gone: the `commitment-opening` template kind, `commitment_opening` children and pieces, `index.json` `commitment_openings`, and the `lookup-slot` kind.
  - `index.json` `not_yet_lowered` is empty: every primitive of every row is gates.
- **Gathers are multiplexers.** The embedding (`Embedding_v1`, `EmbeddingShard_v1`) is an ordinary walked `template` now. Every `GatherBf16x{V}` is a gate circuit: per embedding output element, and per MoE expert weight element (`MoeExpertRow_v1`, in both expert GEMMs).
  - Up to 4,096 candidates, it is one traced subcircuit, `GatherBf16x{V}_v1 (multiplexer)`, with gate lists: 1,049 ANDs at 64, 2,072 at 128.
  - A wider one is a composed Definition of the same name (`composed` note) with two children: `mux (candidate pair)` × (V − 1) and `range select` × 1.
- **Table reads are plain gate subcircuits of kind `table`,** named like `ex2 table (plain gates)`. They cover the MUFU ex2 / rcp / rsq / sqrt tables and gemma's tanh and GELU tables.
  - Sizes as before: 41,308 / 49,576 ANDs; 131,816 for tanh; 2,232 for GELU. They are counted, with no gate list.
  - SiLU's table subcircuits have kind `table` too (they were `lookup`).
  - In gate lists a table read's value bits come from `input_origin` `["table", table, bit, id]`, and its index wires are in `tables` (they were `["lookup", …]` / `lookups`).
- **Sizes are corrected, and the export carries them.** Take them from the export; don't recompute them:
  - each node has `totals` (AND / XOR / NOT), each row file has `totals`, and `index.json` `rows[]` has `and` / `xor` / `not` (the headline);
  - a GEMM-like group's `instances` are output coordinates, and its template is now one coordinate (`instance` names it). The MoE rows and #74 were 400× to 4,400× too large before;
  - attention's instances are `instances_by_T` (`{T: instances}`, the program graph's histogram), which replaces `instances_per_T` (a uniform spread);
  - `index.json` `crosscheck` holds each template's ANDs against its Calls' units: 119 agree, 37 differ by counting convention, and none fails.
- **Headlines,** every one exact now:

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

  The MoE rows' growth over the audit's corrected values (×2.46 on OLMoE, ×3.34 on #75) is their expert gathers now counted as gates. #101 grows by its embedding gathers (+0.8%).
- **Detail:** `internal/lanes/flock-ir-lowering/20260927T1330Z-report-gateless-primitives.md` §4.
