---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T07:46Z · re: `vllm-coordinator/20260928T0727Z-handoff-from-coordinator.md`

# Train-ready heads on main 3ba4d8b3: S2 a609d505, S3 ccceb54e, S4 3a25b56a, S1 11fb4439 (in that order; each merges cleanly on the previous)

| # | PR | Branch @ head | Takes |
|---|---|---|---|
| S2 | [#233](https://github.com/danielreuter/verity/pull/233) | `cursor/epoch-s2-source-ids-150d` @ `a609d505` | main `3ba4d8b3`. The `vllm_meta.py` conflict with #197 is resolved: `DERIVE_SOURCE` plus #197's `S=None` wrapper arguments |
| S3 | [#242](https://github.com/danielreuter/verity/pull/242) | `cursor/epoch-s3-taps-default-150d` @ `ccceb54e` | main (clean) |
| S4 | [#246](https://github.com/danielreuter/verity/pull/246) | `cursor/epoch-s4-constructions-150d` @ `3a25b56a` | S3 `ccceb54e`, which includes main |
| S1 | [#232](https://github.com/danielreuter/verity/pull/232) | `cursor/epoch-s1-q-word-record-150d` @ `11fb4439` | S4 `3a25b56a` |

**Resolutions:**
- **S4:** `registry/prims.py` keeps #223's `verity.ml.fp32` re-exports and binds core's `AmpereBF16TcDot16` v2. It deletes #223's `tests/program/test_ampere_tc_versions.py`, whose own docstring says the re-key deletes it. The README keeps main's "proof-unit" wording.
  - #197's new `test_a_single_request_takes_S_as_a_constant` now counts the shared-greedy select of record (`3a25b56a`).
- **S1:** the README, `manifest.py`, `format.py` and `verify.py` combine S1's query of record, word check and `--query` with S3's default-on taps and S4's `scale_products` policy. `word.py` merged cleanly.
- **Train simulation:** `git merge-tree` of main → S2 → S3 → S4 → S1 is clean at every step.

**Tests (CPU, `-n 3`):** every head's failures are the base set only.
- **S2:** `test_derive_source_id` and `test_derive_stochastic` pass. The lints fail only on main's P1 (below).
- **S3:** the targeted tap, acquire, pipeline and lint tests.
- **S4:** `tests/program`, `query`, `acquire`, `lint`, `observe`, `check`, `commit` and `pipeline`.
  - Extra failure: `test_lifted_tiny::test_specified_list_is_closed`, an order-dependent flake that passes alone.
- **S1:** `tests/query`, `check`, `commit`, `acquire`, `pipeline`, `lint`, `correspondence`, `regression/test_attempt_resolution` and `test_rebaseline`, plus `tools/research/tests/test_store_vllm_tools.py`. The S1 A/B on #73 is unchanged: identities equal, strict word check passes.
- **The base failures:**
  - `test_compiled_source`, which needs a CUDA driver;
  - `test_research_tools::test_closure_covers_every_core_file`;
  - `test_gen_dense2`;
  - `test_gen_ov_easy` ×2;
  - `test_analytic`;
  - `test_derive` s3_untied;
  - `test_gelu_ref_vs_torch` ×2;
  - `test_sampling_rows` nv_logf;
  - `test_patterns_synthetic` gumbel;
  - and, **new on main from #223**, `tests/lint/test_p01_core_abstractions.py`.

**Two things for you:**
1. **Main's P1 lint fails since #223:** `registry/prims.py:33` imports `verity.ml.fp32._decode` / `_round_f32`, which are core-private. #223's branch had the fix, `de3d49b0` (public `f32_decode` / `f32_round` in core), but main's merge doesn't carry it. That's the consolidation coordinator's to land; I didn't touch core.
2. **Integrator: migrate the protected golden corpus** (`properties/golden/corpus.json`) in S4's merge. The re-key moves two entries' Program digests; their attributions are unchanged.
   - `smollm2-135m-m1`: `d2b299f5…` → `d72cd7ad…`.
   - `qwen2.5-1.5b-m6`: `14a3ac66…` → `074e6cab…`.

**Not in this train:**
- S1b ([#253](https://github.com/danielreuter/verity/pull/253)) is being extended to B=8 manifests; it takes S1 when that's done.
- The rebaseline tooling ([#243](https://github.com/danielreuter/verity/pull/243)) is independent. It can go in any train.
