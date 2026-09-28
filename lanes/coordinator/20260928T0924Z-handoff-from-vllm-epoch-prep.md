---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T09:24Z · re: `vllm-epoch-prep/20260928T0900Z-handoff-from-vllm-coordinator-restack-on-p2.md`

# S-stack on P2: `cursor/epoch-s-stack-p2-150d` @ **b38d26d5** (S2 + S3 + S4 + S1 resolved on P2, golden corpus migrated)

**Head:** `b38d26d5`, pushed at 09:22Z. It carries, in epoch order, S2 (`a609d505`), S3 (`ccceb54e`), S4 (`3a25b56a`) and S1 (`11fb4439`), merged onto P2 and resolved.
- It replaces #233, #242, #246 and #232 for this train; those branches are unchanged.
- **Heads-up on the base.** `ff86208c` isn't on origin, and I couldn't fetch it: auth was also down at 09:01Z.
  - So the stack sits on my reconstruction of P2, `99d9cd1a`. That's main `3ba4d8b3` merged with the exact component heads, each clean and in order: #231 `cf92dbff`, #201 `f7612503`, #223's fix `de3d49b0`, #248 `883ece7c`. I checked those heads against the open PRs at 09:08Z.
  - If P2 is those merges, stacking `b38d26d5` behind `ff86208c` is conflict-free.
  - If P2 resolved something between them differently, the only possible conflicts are P2's own resolutions.

**Resolved against P2** (the eight files you listed):
- **`pipeline/manifest.py`:** S1's `query` and default word check and S3's default-on taps sit alongside P2's `word_max_gates` / `--word-max-gates`. `word_check` gets both `acquired` (with S4's `scale_products`) and `max_gates`.
- **`rules/vocab.py`, `rules/vllm_sampling.py`:**
  - Multi-request workloads bind the stochastic select through S4's `sampler_construction` (shared-greedy, `GumbelTopPTokenSelectSharedGreedy_v1`).
  - Single-request workloads bind P2's `GumbelTopPTokenSelect_v2{V,S}`, with the keep word as word gates.
  - **Note: v2 has no shared-greedy variant yet.** #101's select keeps its one redundant `temp == 0` gate. That's a redundant gate, not a recompute.
- **`sampling_event.py`:** both new ids are in `SAMPLING_EVENT_FAMILIES`. `required.STOCHASTIC_SAMPLING_EVENTS` is derived from it.
- **`registry/prims.py`:** P2's public `f32_decode` / `f32_round` re-exports, plus core's `AmpereBF16TcDot16` v2. The integration's v1 is deleted.
- **`circuit_check/targets.py`:** both statics, S4's `SCALE` and P2's `S`.
- **`tests/program/test_derive_stochastic.py`:** P2's single-request test, v2.
- **`query/word.py`:** P2's gate limits and S1's process-wide unit-rule memo. The memo is now keyed by the gate limits (`b38d26d5`), so P2's `test_the_gate_limit_is_the_runs_not_the_querys` passes.
- **S2** merged cleanly on top.

**Golden corpus migrated** (`15a715a5`) through `properties.golden.record`, with decision `rebaseline-2026-09-28 (Daniel: re-baseline epoch; AmpereBF16TcDot16_v1 -> core v2 re-key, G0c)`. `golden --check` passes 2 / 2.
- `smollm2-135m-m1`: `d2b299f5…` → `d72cd7ad…`;
- `qwen2.5-1.5b-m6`: `14a3ac66…` → `074e6cab…`;
- attribution and instance counts are unchanged.

**Gates (CPU, `-n 3`):**
- **vLLM lints:** P01–P12, by-name, dead modules and imports-resolve all pass (`rc 0`).
- **`tests/program`, `tests/query`, `tests/pipeline`, head vs reconstructed P2:**
  - P2's base failures: `test_research_tools::test_closure_covers_every_core_file`, `test_analytic`, `test_derive` s3_untied, `test_lifted_tiny` (order-dependent), `test_gelu_ref_vs_torch` ×2 and `test_sampling_rows` nv_logf.
  - The head fails that same set, plus two cross-test-order failures in the combined run: `test_codec::test_v1_kv_cache_arguments…` and `test_twins::test_check_writes_the_evidence_schema`. Both files pass whole, with and without xdist (34 passed).
- **Recomputes:** on CPU I can't build Programs under the new constructions (the Build needs vLLM's CUDA ops). The evidence for 0 recomputes is:
  - verify-optins' real Builds of these constructions: #57 `once` 0; #73 v4 0 violations and 0 recomputed; #74 shared scale 747,936 → 0;
  - the ordered MoE router (#86);
  - circuit-check with 0 failures on every new default Definition (S4 PR #246).
  - The strict word check of record (S1) enforces it at every GPU manifest build.

**Not in this head:** S1b (#253) is still being extended to B=8 manifests; it takes this stack when done.
