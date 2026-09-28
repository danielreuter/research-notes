---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T06:34Z

# MERGE-READY after #221: S4 [#246](https://github.com/danielreuter/verity/pull/246), stacked on S3 (#242); it takes main when #223 lands

**Branch:** `cursor/epoch-s4-constructions-150d` @ `727c80fd`, pushed at 06:30Z once auth returned.
- It's based on main `6746f408`, with S3 merged in: S4 is stacked on #242, and the `acquire/sources/taps.py` conflict is resolved.
- **Order:** S2 (#233), then S3 (#242), then S4 (#246). **#221 must be on main before S4**: C-Flock lowers v2 only with #221.
- When #223 lands, I merge main into S4. The `registry/prims.py` resolution keeps #223's re-exports and binds core's v2.

**What's in it:** the details are in #246's description.
- MoE ordered, FA3 v4, `once` (with the Match fold) and shared-greedy as defaults.
- The FP8 shared scale, with its fold pattern and the `scale_products` policy and source.
- The Ampere re-key.
- `fp8.scale_products` is exact and now about 157 M products/s, up from about 0.3 M.

**Moves:**
- Program digests on every L40S row (the re-key);
- #67, #68, #70 and #75 (the router);
- #73 and #74 (FA3 v4);
- #74 (the shared scale, plus its `scale_products` identities);
- #57 (request and workload Programs, through `once`);
- #101 (the sampler).

**Gates:**
- **jdiff:** the full `integrations/vllm/tests` run on the assembled branch equals the base-failure set, plus `test_golden` and the known flake `test_roundtrip` (#151).
- The affected directories after S3 merged in: base failures only.
- **Lints:** P1–P12, by-name and dead modules pass; no allowlist grew.
- **circuit-check:** 0 failures on the six new defaults and the shared-scale GEMM.
- **Flock with #221:** equal to base.

**Recomputes under Q_word v1** (verify-optins' real Builds of these constructions, plus #86):
- 0 on #57 (`once`), #73 (v4), #74 (shared scale: 747,936 → 0), and the MoE ordered router.
- With S4, every row's program graph has 0 recomputes.

**Integrator action:** migrate the protected golden corpus, `properties/golden/corpus.json`.
- Two entries move digest only: `smollm2-135m-m1` `d2b299f5…` → `d72cd7ad…`, and `qwen2.5-1.5b-m6` `14a3ac66…` → `074e6cab…`.
- Their attributions are unchanged.

**S1 (#232):** pre-resolved over S3 + S4 on a scratch merge. The affected directories pass, and the resolutions are recorded with `git rerere`, so S1 takes main cleanly after S4.
