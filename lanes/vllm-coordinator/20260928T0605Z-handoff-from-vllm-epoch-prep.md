---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T06:05Z

# MERGE-READY: S2 (#233) and S3 (#242), base main 6746f408; S4 assembled and in test, forks onto main after #223

Merge order, per your 0505Z: S2, then S3, then S4, then S1, then S1b. Gate (b) and `check` go through the research coordinator's merge gate.

## S2: [#233](https://github.com/danielreuter/verity/pull/233), `cursor/epoch-s2-source-ids-150d` @ `c0db84e1`
- **Change.** The row wrappers declare a versioned `DERIVE_SOURCE` (for example `verity-vllm/engine-step/v1`, and `verity-vllm/with-peers/v1[<inner>]` on TP rows). Derive uses it as the Program id's `SRC.class` instead of the module path. The Python class stays in the provenance.
- **Moves:** every row's step, request and workload Program digests, through `SRC` alone. Nothing structural changes: gates, Definitions, manifest identities.
- **CPU A/B on stored Builds:**
  - #57: 11/11 descriptors, workload included;
  - #73: 6/11;
  - #74: 4/11 (the rest skipped for VM memory).
  - Every stored digest recomputes exactly, every one moves, and no module path is left.
  - The method is validated against the new code on a toy wrapper.
  - Evidence: notes `evidence/s2_src_ab.py`, `s2_57.json`, `s2_73.json`, `s2_74.json`.
- **Tests:** `tests/program/test_derive_source_id.py` (4), and `tests/lint` including P10. On the first S2 commit, the full `integrations/vllm/tests` run failed 12 tests: the 11 known base failures (below) plus P10, which `c0db84e1` fixed.
- **Recomputes:** no Definition changes, so the program graphs equal main's. The remaining recomputes are #74's FP8 and #57's cross-Call `+ 1`, both removed by S4.

## S3: [#242](https://github.com/danielreuter/verity/pull/242), `cursor/epoch-s3-taps-default-150d` @ `8f567db6`
- **Change.** The four taps default on (`=0` for A/B). `manifest build` / `build-global` / `verify` default their policies on (`--no-*` for A/B).
  - Each row attaches a tap only where its manifest names the family.
  - The TP row path carries the guarded max and the norm tap.
  - The pod bootstrap builds the tap libraries (`ROW_TAPS=0` skips them).
- **Moves:** every row's manifest digest and run root:
  - `norm_scales` identities;
  - the MS class on every attention stream identity;
  - `router_softmax` on the MoE rows once S4's ordered router is in;
  - `vocab_range` on #70 and #75.
  - Program digests don't move.
- **CPU A/B, taps off vs on** (evidence: `evidence/s3_ab.py`):

| Row, shape | Identities | Added | Ranges changed | Removed |
|---|---|---|---|---|
| #73, LP10_T8 | 5,340 → 6,645 | 1,305 `norm_scales` | 324 `fa3_hidden_m1_stream` (MS) | none |
| #57, LP31_T52 | 21,304 → 26,869 | 5,565 `norm_scales` | 1,378 `fa2_hidden_m1_stream` | none |
| #74, LP73_T1 | 1,813 → 2,103 | 290 `norm_scales` | 72 `fa3_hidden_m1_stream` | none |

- **Tests (S3 implementer, `-n 2`):**
  - Targeted: 629 passed, 33 skipped, 2 failed. Adjacent: 733 passed, 165 skipped, 3 failed.
  - Every failure is in the base-failure set below.
  - Lints P1–P12, by-name and dead modules pass. Size caps were lowered only.
- **GPU lane must:** run `pod_bootstrap.sh`, and re-pin the canary and `known_roots.json`, because roots move.
- **Found, not fixed:**
  - a TP merge keeps rank 0's guarded-max header counts;
  - `fa3_row_negatives.sh` passes no norm or router sources;
  - the TP path is FA2-only.

## Base failures
These fail identically on `6746f408` on this CPU VM:
- `test_compiled_source`: needs a CUDA driver.
- `test_research_tools::test_closure_covers_every_core_file`.
- `test_gen_dense2`.
- `test_gen_ov_easy` ×2.
- `test_analytic`.
- `test_derive::test_s3_untied`.
- `test_ref_prims::test_gelu_ref_vs_torch` ×2.
- `test_sampling_rows` nv_logf.
- `test_patterns_synthetic` gumbel.

Also: running `tests/program` rewrites the tracked `docs/data/ref-prims/*.json`. That's pre-existing. Every branch here is checked clean of it.

## S4 status
`cursor/epoch-s4-constructions-150d`, local, not pushed yet. It merges S4-A, S4-B and the re-key onto main, plus one fix:
- **S4-A:** MoE `indexed-read-ordered`, FA3 `check-inf-per-iteration` and `weight_only_calls="once"` as defaults. The Match fold issues weight-only Calls once. The shared-greedy sampler is the default, via `sampler_construction`, and is added to `SAMPLING_EVENT_FAMILIES`.
- **S4-B:** `fp8_scale_construction` defaults to shared-per-block, with the fold pattern, the `scale_products` policy and its Commit source.
- **Re-key:** core's `AmpereBF16TcDot16_v2`.
- **Fix:** `fp8.scale_products` was about 0.3 M products/s through the reference evaluator, roughly 2 h per #74 Commit. It now takes numpy's multiply on non-NaN lanes and the IR on NaN lanes: exact, about 157 M/s.
- It's in its full CPU test run now. It forks onto main after #223 lands, and needs #221 first.
- **The golden corpus is the integrator's migration:** `properties/golden/corpus.json` is protected. Both entries' Program digests move with the re-key; their attributions don't.
