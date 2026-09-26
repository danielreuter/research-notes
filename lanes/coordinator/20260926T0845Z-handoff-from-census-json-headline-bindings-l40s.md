---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
---

# census-json: #101's attention, sampling and embedding bound; router bytes model; L40S line. Merge request (PR #64)

**To:** research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628).

## Merge request
- **PR:** [PR #64](https://github.com/danielreuter/verity/pull/64), `cursor/headline-bindings-l40s-574a` into `main`. It is one commit on top of main `2ba5e62c`, which already has #61 and your preview switches.
- **Tests:** the whole `backends/numerical` suite passes (921). CPU only.
- **Byte identity:** the legacy renders, the raw JSON of every rule set, the frozen tables and parity are byte-identical to main. Only the headline section's text changes.

## What changed
1. **Bound census subcircuits with bench-spine's ids:**
   - `attention-head/d64-bn128/sm80-fa2-bf16`, whose `variable_ranges` gives T as 1–383 over #101's strata. The upper end is 383, not 384, because the NB = 3 stratum is partial.
   - `gumbel-top-p-token-select/v128256/fp32`.
   - `embedding-row/v128256-h2048/bf16`. Bench-spine has no embedding template, so the id follows its form.
2. **Embedding:** the ontology has no covered-by-commitment state, so embedding is marked `commitment_opening`. The headline lists it as uncovered with the reason `commitment opening`. Its work stays in the denominator and is never imputed.
3. **Router:** `moe-router-topk` gets `port_datatypes` (logits bf16, from `MoeRouterTopK`'s port `Array(E, BF16)`) and bytes `2*E + 8*TOPK`. Every template of every workload is now modelled.
4. **L40S line (the real blocker for flock-l40s-101):**
   - **Before:** an L40S-proved cell was rejected K, because no target is anchored on the L40S. #101's headline could never go above zero from L40S cells.
   - **Now:** `views.L40S_BF16` is the `sm80.mma` bf16 instruction on the L40S, a line with rows only where it has results.
   - **Rehoming (spec rules only):** a result proved on another device moves to the line of its instruction on that device (GEMM) or the line its GPU picks (other templates). Only L40S provers are affected today.
   - **Your test updated:** your `hardware_target` assertion (L40S → `None`) now expects the L40S line.

## Told the lane
Note written: `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lanes/flock-l40s-101/20260926T0845Z-note-from-census-json-matching-101.md`. That folder did not exist, so I created it. The note covers:
- the exact statement ids, relation and profile;
- the registered-input-set requirement;
- that the L40S results need their own red-team `proof_class` verdict, since statement labels are per line and the H100 clearance does not carry over;
- that cells show as rejected K until #64 merges.

## For you to note
- **Attention and sampling lanes:** flock-ir-lowering and flock-ir-sampling cells on the **H100** match the ids, but under strict hardware matching they will not cover #101, which was served on an L40S. They count only under your any-hardware preview. To count in the published headline they must also be proved on an L40S.
- **Other workloads:** their GEMM Ks (for example Gemma's 2304 and 9216), heads (D = 128, 256) and greedy selection still have no bound census subcircuit. I bound #101 only, as asked.
