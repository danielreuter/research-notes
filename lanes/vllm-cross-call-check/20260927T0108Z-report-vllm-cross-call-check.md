---
lane: vllm-cross-call-check
kind: report
created: 2026-09-27T01:08Z
status: open
---

CHECKPOINT 91ceb79e (04:50Z) [open] PR #111 partition object v1 + verity.ir.cut (stacked on #98), nothing moves; handoff 05:20Z
CHECKPOINT 91ceb79e (02:43Z) [open] #98 d7f76916 (cross-call + unit_rule members: #74 FP8 581k Calls; #57 Gemma w+1 102.6M gates), #99 13c294d6, #103 cbe3db97, #101 merged; graphs art:c74deac4, cross art:e8b4aada; handoffs sent
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

## Results (03:00Z)

- **Cross-Call** (`art:e8b4aada`): #57 `AddScalarBf16_v1{C=1}` T x 105 copies per request Program, 102.6 M gates over 8 Programs; 0 on #11 #23 #39 #60 #67 #68 #70 #73 #74 #75
  and #101 (r19-reference Build `art:a9be8f7c`). #4's request Programs and #101's record Build are not in the store.
- **Member check** (word.unit_rule, PR #98): #74 `ScaledMmFp8Block_v1` 4 Definitions, 144 groups, 581,040 Calls, 113.6 G gates; all other rows 0.
- **Program graphs** `art:c74deac4` (supersedes `art:f0c33059`; `art:d583032e` is an intermediate put, ignore): main fa662029 + #98 d7f76916 + #99 13c294d6;
  structure, units, gates, committed identical to the old; max_scaled words = the plan table; param_inputs on 11 rows (#4, #101 kept).
- **PRs:** #98 @ d7f76916, #99 @ 13c294d6, #101 merged (c822ca7a), #103 @ cbe3db97. Handoffs in the Project store `internal/lanes/vllm-coordinator/2026092702*..0300Z-*`.
- **Gotcha:** `verity.ir.refs.runs` on a batch member's Strided column view (Embedding's table column) expands to one run per row: 590 M runs for
  Gemma's Embedding; hold such operands by descriptor (cross_call `_view`).

## Partition checker owner (05:20Z)

- **PR #111** (stacked on #98): `verity/partition/v1` in core (`verity.ir.partition_object`: build, canonical, SHA-512 digest, validate,
  verify) and the references in `verity.ir.cut` (CallGraph = word.Graph off numpy, fits = the width rule in bits, check_cut =
  validate_unit_cut + unit-too-wide). word.Graph is CallGraph + numpy views; with_word_rules byte-identical on #101 #74 #73.
