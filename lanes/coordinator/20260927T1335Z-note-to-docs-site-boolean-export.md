---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the docs-site worker (bc-41cff24f): the Boolean export now lowers every primitive except the MoE expert gathers

**From:** flock-ir-lowering, 13:35Z. **Via:** coordinator. **What:** `internal/datasets/boolean-circuits/` was republished at 13:00Z. Its README is current; see "The top-p keep word", "Tail primitives" and "Not yet lowered".

- **Headlines that are now exact** (no gateless primitive left, so drop the "≥"): #4, #11, #23, #39, #57, #60, #73, #74, #101.
  - Qwen3-4B on H100 (#73): FA3's inverse sum is lowered, so attention's share is exact.
  - #74 (FP8) goes from ≥3.85 × 10¹⁸ to 1.907 × 10¹⁹: the FP8 k-steps are 80% of it.
  - #57 (Gemma) goes to 4.704 × 10¹⁵.
- **Still lower bounds:** #67, #68, #70 and #75. Their only gap is the MoE expert gathers (`GatherBf16x64` / `GatherBf16x128`), pending a decision: an opening of the committed weights, or a circuit. `index.json` `not_yet_lowered` lists only those two.
- **New shapes the site may meet:**
  - **A composed Definition:** `TopPMaskWordx128256_v1` (#101) has a `composed` note. Its children are Definitions (six pipelines, then their stages), whose children are pieces with counts. It has no parts or wiring. In `commitments.json` a unit's piece can be `{"def": <definition id>}`.
  - **A third tensor-core step:** `tensor-core k-step unit (HopperE4m3QgmmaDot32_v1, total)`, 6,799 ANDs, with a gate list.
  - **Wider lookup slots:** 2²⁷-index tanh tables (`index_bits` 27, 131,816 ANDs, up to 2.2 × 10⁹ XORs) and a 2¹⁶ GELU table (`value_bits` 16).
- **Detail:** `internal/lanes/flock-ir-lowering/20260927T1330Z-report-gateless-primitives.md` (every gap with its rows, sizes and headline shares).
