---
lane: vllm-cross-call-check
kind: report
created: 2026-09-27T01:08Z
status: open
---

CHECKPOINT 91ceb79e (01:08Z) [open] PR #98 cross-call check (Gemma #57: 5,460 duplicate AddScalarBf16 Calls); #99 max_scaled label; #101 sampler SharedGreedy; 13 graphs rebuilt (11 w/ param_inputs), finish+cross running

## Work (01:08Z-02:10Z)

- **PR #98 `query.cross_call`** (program-level partition check, opt-in `manifest build --cross-call-check`): Calls (spec, form, runs; copies canonicalised),
  operand subsets (support masks from `analyze`, hierarchical = flat on attention/Gemm/RoPE/norms/TokenSelect/Embedding), gates (`_partners`: another
  candidate Call must read a leaf of every operand in the support). Folded in (root 01:31Z / coordinator 01:35Z items 1-2):
  `word.unit_rule` compares a separable body's members (`members_check`); a pure-wiring Call returns its inputs (no `committed-unread`);
  `query/call_scope.py` breaks the word <-> cross_call cycle.
- **Findings:** #57 Gemma: 5,460 duplicate `AddScalarBf16_v1{C=1}` Calls (the norm weight + 1 per token; 105 distinct), 12.58 M gates computed again
  in one request Program (build_request_LP31_T52). #74 FP8: `ScaledMmFp8Block_v1` scale product, 127 copies per (weight block, kb), 144 groups,
  113.6 G gates (members check). All other rows: 0.
- **PR #99** labels: `max_scaled` not committed today (MS plane); guarded max new tap under `GUARDED_MAX_TAP=1` (#95).
- **PR #101** sampler `Gumbel*TokenSelectSharedGreedy_v1` (opt-in, same circuit with the flag merged, 0 redundant gates).
- **PR #103** `TopPMaskWordx{V}` total over every splits word (keep word 0 outside the six; digests unchanged).
- Evidence scripts: `evidence/regen13.py`, `cross13.py`, `members13.py`, `label13.py`, `index13.py`.
