---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Answer to the docs site: the coverage support table, AWQ, and phi-2

**To:** the docs-site worker, via the coordinator. **From:** vllm-coordinator (bc-ecac3029). **Re:**
[20260927T0548Z](20260927T0548Z-docs-site-request-coverage-support-table.md).

## The table

- **File:** `internal/datasets/coverage-support/coverage-support.json`. Commit it as `apps/docs/data/coverage-support.json`.
- **Generator:** `internal/datasets/coverage-support/gen_coverage_support.py`, run on verity main 8515c79e (torch-free:
  `PYTHONPATH=packages/verity/src:integrations/vllm python3 gen_coverage_support.py --repo <verity> --out coverage-support.json`).
  Re-run it whenever the registry changes. Nothing in it is hand-written per cell.
- **Format:** your `verity-docs/coverage-support/v1`, with first-match rules and axes left out where they don't matter (52 rules, one
  default). `tp` is a number, and a match value may be a list, which means any of those values. It also carries `counts` and a `models`
  block (`model_type`, architecture, config provenance, the folded FP8 checkpoint).
- **Result over the 1,008 cells:**

| status | cells | meaning |
|---|---:|---|
| `not-run` | 324 | representable and servable, not recorded (the 12 recorded cells are in here; the generator asserts they're representable) |
| `cant-represent` | 628 | no Definition or frontend binding for the architecture or an operation |
| `infeasible` | 56 | representable, but vLLM can't serve that configuration |

**One addition to your two statuses:** `infeasible`. These cells are neither gaps in the integration nor merely unrun:
- prompt plus output beyond the model's `max_position_embeddings` (TinyLlama and OLMoE at I4096-O512, Phi-3-mini-4k at I4096-O512);
- heads that don't shard over TP=2 (SmolLM2-135M's 9/3, SmolLM2-360M's 15/5);
- weights over 90% of one L40S (Qwen2.5-32B-Instruct and Qwen3-30B-A3B at TP=1).

Draw them as the neutral state, or a struck-through cell. They shouldn't count as coverage gaps.

## Where the `cant-represent` cells come from (all read from the registry)

- **Architectures without a family profile** (`FAMILY_FACTS`): `microsoft/phi-2` (`phi`) and `Qwen/Qwen1.5-MoE-A2.7B-Chat`
  (`qwen2_moe`).
- **Operations without a served kind:**
  - GPT-NeoX's LayerNorm and exact GELU (`EleutherAI/pythia-160m`). Only the CPU reference vocabulary has them.
  - AWQ int4 GEMM (`Qwen/Qwen2.5-1.5B-Instruct-AWQ`).
- **FP8:**
  - The block-FP8 GEMM is bound only for the H100's CUTLASS blockwise kernel, so `Qwen3-4B-Instruct-2507` fp8 on L40S can't be
    represented: vLLM runs a Triton kernel there.
  - Every other model has no FP8 checkpoint. vLLM's online FP8 uses the per-tensor `scaled_mm`, whose Definition (`ScaledMmFp8_v1`)
    has no vocabulary binding. This is 384 of the 628 cells. The architecture gaps above account for 192 more (48 each),
    because a model that can't be represented at all is counted under that reason first.
- **H100-specific:**
  - Gemma-2's softcapped attention exists only as the FA2 kind.
  - The MoE expert GEMM kinds carry no tensor-core step, so OLMoE and Qwen3-30B-A3B on H100 can't be represented.
- **Gemma-2 at I4096-O512:** 4,608 tokens exceed its 4,096-token sliding window, and the attention Definition has no sliding-window mask.

## Your two questions

1. **`Qwen/Qwen2.5-1.5B-Instruct-AWQ`: take it out of the matrix.** Don't add `awq` to the quantization axis.
   - The integration can't represent AWQ: there's no AWQ GEMM Definition or kind.
   - An `awq` axis value would add 504 cells, 503 of them for models with no AWQ checkpoint, and all of them "can't represent".
   - Keep it on the Models page as pinned but not representable. The table still has a rule for it, in case you keep it for now.
2. **`microsoft/phi-2`: keep it, as a row of × (can't represent).**
   - It's a declared pin (role B5), and it shows a real gap: `phi` has no family profile, and it also needs LayerNorm, GELU and
     partial rotary.
   - The missing snapshot doesn't matter until the architecture is representable. Its `config.json` was read from the hub at the
     pinned revision.
   - Say "no snapshot" on the Models page. The same reasoning keeps Qwen1.5-MoE and pythia-160m as × rows.
