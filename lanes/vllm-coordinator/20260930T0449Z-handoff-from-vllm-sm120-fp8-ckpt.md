---
cursor:
  subagentId: "bc-f23795f4-fb08-523a-a894-44ef03ab3ebd"
---

lane: vllm-coordinator · kind: handoff · from: vllm-sm120-fp8-ckpt (bc-f23795f4) · created: 2026-09-30T04:49Z

# Merge-ready: per-model FP8 checkpoint pins and the offline recipe, cursor/vllm-sm120-fp8-ckpt-3ebd @ 86476296 (PR #469)

- **Branch and head:** `cursor/vllm-sm120-fp8-ckpt-3ebd` @ `86476296`, base `origin/main` @ `3c924ab9`. PR: https://github.com/danielreuter/verity/pull/469 (draft).
- **It doesn't depend on lane A's #465:** checkpoint pins don't depend on the target.

## Which models have an FP8 pin (the 17 representable models of the matrix)

| Model | FP8 pin (role) | Source |
|---|---|---|
| Qwen3-4B-Instruct-2507 | `QWEN3_4B_FP8` (existing) | Qwen release |
| Qwen3-30B-A3B | `QWEN3_30B_A3B_FP8` (new) | Qwen release, pinned from the hub |
| Qwen2.5-0.5B, 1.5B, 1.5B-Instruct, 7B, 7B-Instruct, 14B-Instruct, 32B-Instruct | `QWEN05_FP8`, `B1_FP8`, `QWEN15_INSTRUCT_FP8`, `B7_FP8`, `QWEN7_INSTRUCT_FP8`, `QWEN14_INSTRUCT_FP8`, `QWEN32_INSTRUCT_FP8` | recipe |
| TinyLlama-1.1B, Llama-3.2-1B, Gemma-2-2B, Phi-3-mini-4k, Mistral-7B-v0.3 | `TINYLLAMA_FP8`, `LLAMA32_1B_FP8`, `GEMMA2_2B_FP8`, `PHI3_MINI_FP8`, `MISTRAL7B_FP8` | recipe |
| SmolLM2-135M, SmolLM2-360M | none | hidden 576 / 960 isn't a multiple of 128 |
| OLMoE-1B-7B | none | MoE: the recipe refuses it |

- **SmolLM2:** block-128 can't exist, and vLLM's CUTLASS block kernel is 128×128. These two need a per-tensor FP8 binding (5b's choice).
- **OLMoE:** no release in this format exists, and FP8 MoE isn't modelled.
- **Recipe pins** live under the local namespace `verity-fp8/`. The manifest is append-only: 13 entries appended, each with `fp8_of`, and recipe pins with `recipe: {id, base_repo, base_revision}`.

## What the recipe is (`verity-fp8-block128/v1`, `verity-vllm fp8-checkpoint make | pin`)

- **Data-free, so no calibration set and no seed.** Per 128×128 block, `s = amax/448` in float32, and `q = e4m3fn(W / s)`, nearest-even.
- **Linear weights come from structure, never names:** every 2-D tensor without a `vocab_size` dimension. MoE is refused.
- **The container is the recipe's own,** so the sha256 depends only on the base bytes.
- **Pods make recipe pins at bootstrap:** `pod_bootstrap.sh` step 3 makes a recipe pin from its BF16 pin (`fp8_checkpoint.remake`), then runs the usual shard sha256 check.
- **Why not reproduce Qwen's bytes:** Qwen's own FP8 isn't reproducible from its BF16 release. Its scales scatter ±0.33% around amax/448, which fits quantizing from master weights.

## Gates

- **Determinism:** every recipe pin was made twice on the VM with identical sha256s, under the final code.
- **Second-machine reproduction:** on vy-sm120-fp8-ckpt-1, `pod_bootstrap` re-made QWEN05, LLAMA32_1B, TINYLLAMA, GEMMA2_2B, PHI3_MINI and MISTRAL7B `_FP8`, with every shard sha256 equal to its pin (run `r20260930-035545-6692`, bootstrap log).
- **Weights:** the reference `safetensors` parser reads the small pins back within half an e4m3 step of the BF16 weights (relative RMS error about 2.7%).
- **sm_120 loads (run `r20260930-042207-1591`, preserved):**
  - all 8 FP8 pins given to the pod load and generate in vLLM `d9105ea80`, under the integration's engine environment;
  - every FP8 linear runs `CutlassFp8BlockScaledMMKernel`;
  - `cutlass_scaled_mm_supports_block_fp8(120)` is True;
  - Qwen3-30B-A3B runs `Fp8MoEMethod` (`Fp8MoeBackend`), with its routers as unquantized `ReplicatedLinear`;
  - greedy output is fluent, and follows the BF16 base for between 0 and all 24 tokens per prompt.
- **CPU tests** (on the VM, through a pytest shim; the rules keep pytest off the VM):
  - `test_fp8_checkpoint` 14, `test_fp8_pins` 28, `test_profiles_generic` 49, `test_fp8_profile` 16, `test_dense_generic` 13;
  - lints P1–P12, the by-name lint and dead-modules pass.
- **The vLLM suite, base vs head** on the pod, CPU-only (run `r20260930-041857-e985`): **0 unexpected**. The base ran 4,525 tests (22 failed, all on `main`); the head ran 4,579 (21 failed, each also failing on the base). All 54 new tests pass. Two outcomes changed: `test_derive_transfer::test_transfer_summary_written` went from failed to passed, and `test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation` went from passed to skipped; it's observer code this PR doesn't touch.
- **Not applicable:** no Definition, query or partition changes, so circuit-check and the partition checker don't apply. No existing digest, fixture or manifest entry moves, and the sm_89/sm_90 paths are untouched.

## Behaviour changes

- **Bootstrap:** `pod_bootstrap.sh` step 3 changes only for entries with `recipe`.
- **Profile test:** `test_profiles_generic`'s refused-roles case adds `QWEN3_30B_A3B_FP8` (refused by name: mixed precision).
- **New fixtures:** 12 `expected/derived_<ROLE>_FP8.json` profile fixtures and 13 `hf_configs/<ROLE>_FP8.config.json`.

## For lane A (5b), found on the PRO 6000

- **Block-scaled is the natural sm_120 FP8 format.** On sm_120, vLLM `d9105ea80` picks the same `CutlassFp8BlockScaledMMKernel` class as on H100. What needs extending is the binding, not the checkpoint format: `CutlassScaledMmFp8Block` refuses cc ≠ 9.0.
- **QKV bias:** the Qwen2.5 pins have a QKV bias, and the pattern refuses a bias passed into `cutlass_scaled_mm`. Check how vLLM applies the bias on this path.

## Found, not fixed

- **The coverage generator** (`internal/datasets/coverage-support/gen_coverage_support.py`) folds an FP8 pin into its base by the `-FP8` suffix, which the `verity-fp8/` pins don't satisfy.
  - Fold by `fp8_of` instead: `fp8_of = {(p.get("fp8_of") or p["repo"][:-len("-FP8")]): p for p in pins if fp8_scheme(p["config"])}`. `load_pins` must keep `fp8_of` from the manifest entry.
  - Every new pin's config is in `hf_configs` (sha-matched), so there's no hub fetch.
- **The recipe is single-threaded numpy.**
  - The 32B takes about 15 minutes on the VM.
  - Mistral took about 13 minutes on the pod, against 2.3 on the VM.
  - A per-shard process pool would cut FP8-night bootstrap time.
- **MoE FP8 needs a router exemption in `quant_refusal`,** as well as the fused-MoE FP8 Definitions.
- **A commit-message slip:** commit `59bde0ce`'s subject says "seven dense models"; it registers eight.

## Evidence and spend

- **Evidence:** `art:c0afdf95` (the hub survey, the Qwen reproducibility probe, the VM pin and re-make logs, the check script), and runs `r20260930-042207-1591`, `r20260930-035545-6692` and `r20260930-041857-e985`.
- **Pod:** vy-sm120-fp8-ckpt-1 (zg3ecxbicizu9p), created 03:43Z, terminated 04:48Z and unregistered; about 1.1 GPU-h, roughly $2.30 of the lane's $8 share.
