---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: handoff · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T07:10Z

# S4 [#246](https://github.com/danielreuter/verity/pull/246) at `727c80fd`: approved, merge after #221 and #223

The prep lane's handoff is `lanes/vllm-coordinator/20260928T0634Z-handoff-from-vllm-epoch-prep.md`.

**Check 1: every integration v1 binding is gone.** Yes.
- Main `6746f408` has 42 Python references to `AmpereBF16TcDot16_v1`, `_tc_dot16_total` or the integration's own `@primitive("AmpereBF16TcDot16", 1, …)`.
- #246 has none left in code. What remains is two comments that describe the re-key and one test name.
- The consolidation note listed these sites; each now binds `_v2`:
  - `pipeline/vu_export.py` lines 67, 179, 272, 305 and 403;
  - `query/word.py` line 256;
  - `program/kernels/rows.py` lines 40, 45, 63 and 299;
  - `program/kernels/derived_rows.py` lines 451 and 521.
- `registry/prims.py` imports `AmpereBF16TcDot16` from `verity.ml.prims`.
- `tests/program/test_ampere_tc_versions.py` is absent, and `test_derived_rows.py` evaluates `P.AmpereBF16TcDot16` (v2).
- The `AmpereBF16TcDot16_v1|batch` keys under `data/census/` are old census snapshots, not bindings.

**Check 2: ordering with #223 (`de3d49b0`).** It's safe.
- The S3 head `8f567db6` and main `6746f408` are both ancestors of #246.
- I trial-merged #223 into #246. It conflicts in one place: the import block of `registry/prims.py`.
- On the #246 side is the v2 import; on the #223 side are the `verity.ml.fp32` re-exports. The resolution keeps both, which is the one the prep lane recorded.

**Merge order:** #221, then #223, then S2 (#233), then S3 (#242), then S4 (#246), with the head where the prep lane has merged main after #223.
- I'll re-check that head's delta when it's pushed. It should be only this import resolution.
- Integrator action on S4: migrate `properties/golden/corpus.json`. Two entries move digest only: `smollm2-135m-m1` `d2b299f5…` → `d72cd7ad…`, and `qwen2.5-1.5b-m6` `14a3ac66…` → `074e6cab…`.

**G0 left after this:** #197 (in its train), #231 (lint hold), #111, then S1 (#232) and S1b.
