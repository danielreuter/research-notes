---
lane: vllm-cross-call-check
kind: report
created: 2026-09-27T01:08Z
status: open
---

CHECKPOINT 91ceb79e (06:19Z) [open] S1c GemmBias PR #244 head b0b4b438: branch row Match PASS (r20260928-061041-13a2), S1 interior 8036 -> 0 on Qwen2.5-1.5B i256. Pod vy-vllm-cross-call-check-l40s still IN USE for the whole-row circuit-check (r20260928-061514-1f4e); terminate by ~06:40Z. jdiff head running locally; handoffs after it.
CHECKPOINT 91ceb79e (06:08Z) [open] S1c GemmBias: pod vy-vllm-cross-call-check-l40s (z4pavaficnfxq1, L40S, up since 05:49Z) IN USE for the Qwen2.5-1.5B i256 row A/B (base r20260928-060156-e62a Match PASS; branch d89dfdb6 r20260928-060206-064a Build fuses, Match FAIL: fold did not fuse). Debugging the fold on the capture now; terminating the pod when that is done. Future vLLM pods: vyv- prefix.
CHECKPOINT 91ceb79e (02:41Z) [open] #197 GRANTED by red-team-flock-3 at 4497a75d; X-09 test added, new head 67e7f669 (merges on main 51878fab); coordinator told (20260928T0240Z handoff); finding: X-09 chunked fallback refuses all stochastic top-p requests (SPLITS ordinal shift, older than #197, fails closed)
CHECKPOINT 91ceb79e (01:45Z) [open] PR #197 up (head 4497a75d on df3bc5e1): single-request splits constant; #101 ccc21347 -> 79caee21b124d591 (manifest 90f81868 -> eb393312); Builds r20260928-012525-4b0f (base, reproduces) / r20260928-012534-6768 preserved; pods terminated (~$0.45); handoffs: lowering (keep word) + coordinator merge request after #192; waiting on red-team-flock-3 review
CHECKPOINT 91ceb79e (01:26Z) [open] WAITING r20260928-012525-4b0f (base df3bc5e1) + r20260928-012534-6768 (branch bd4eb502) #101 Builds on vy-vllm-cross-call-check-l40s; CPU pod retired (vLLM needs a CUDA platform); agent bc-f7aadce6; next: digests into the PR
CHECKPOINT 91ceb79e (01:08Z) [open] single-request constant splits (Daniel approved proposal 1): branch cursor/splits-single-request-constant-666c at b81a9cfe on df3bc5e1; pod vy-vllm-cross-call-check (CPU, 50m2svxp4zi0gf) for the #101 Builds; next: bootstrap + base/branch Builds
CHECKPOINT 91ceb79e (05:56Z) [open] #111 @ 034ca061 partition/v1 = Q_word v1 query (236 B object), core evaluator + vector; #101 41.5 s, #74 largest 664 s
CHECKPOINT 91ceb79e (05:17Z) [open] #111 @ 7ddb7cca partition/v1 amended (cuts by content, no units/committed); sizes #101 858 MB, #74 up to 12.4 GB/Program (attention per-T cuts)
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

## partition/v1 amended (05:40Z)

- #111 @ 7ddb7cca: cuts table by SHA-512(canon(cut)) with owner + classes only; calls name cuts; units derived (Units.locate O(log n));
  committed derived (cut.derived_committed), verify(served=) checks serving's commits. Pinned: cut key 83cbe858..., digest 7273d670....
- Sizes (evidence/po_size.py, po_size_rows.py; within 0.6% of exact): #101 858 MB (indexed classes 244 MB); #74 per request Program
  317 MB-12.4 GB, all 8 LP Programs 30.8 GB (9.4 GB indexed). Driver: attention's one cut per T (quadratic in context); classes 131 B/unit.
- Spec amendment: internal/lanes/flock-verifier/20260927T0520Z-amendment-partition-object-v1.md (the verifier's note left unedited).

## partition/v1 = named query (06:10Z; Daniel 05:28Z)

- #111 @ 034ca061: object {format, program, query: Q_word v1 {X, W}} (236 B); core evaluator verity.ir.cut (CallGraph with interned ids,
  cut_word, separable shortcut, evaluate_definition; algorithm in its docstring); partition_object.evaluate / Partition.locate / verify
  (served); word.partition delegates to core; with_word_rules byte-identical on #101 #74 #73. Vector: tests/ir/partition_vectors.json
  (descriptor bytes -> graphs + owners; object digest 0eb7a6d3..., owners digest 555cd351...).
- Eval (evidence/eval_time.py): #101 333 specs 41.5 s, 274.0 M units (= graph); #74 largest Program 1,167 specs 664 s, 5.44 G units,
  program 1.84 GB JSON / 121 MB gz. Portability gaps listed in the flock-verifier amendment note.
