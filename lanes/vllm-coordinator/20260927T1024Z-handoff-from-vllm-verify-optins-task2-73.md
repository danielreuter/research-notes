---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T10:24Z

# Task 2 DONE: #73 (Qwen3-4B, H100) real Builds with `fa3_construction` unset and `"check-inf-per-iteration"`: 0 recomputes; unset = record; the H100 Match under the new construction PASSES

**Tree.** The verification merge `b7a4092a` (main `ae5db5d3` + #98 + #105 `b0a12771` with #102 + #106 + #109).

**The Builds.** Two real Builds in run `r20260927-070351-283d` (PRESERVED):
- They ran on `vyv-rf-verify-optins-l40s` with the GPU hidden, under the record's device target (sm_90, 132 SMs, FA3 by the selector).
- Each is the full Build stage: the step Program, 9 request Programs, the workload Program and the manifest. Both passed, with `TARGET-FAMILY-OK built=9.0`.
- The outputs are `art:24c603a7…` (unset) and `art:622fbaf1…` (`check-inf-per-iteration`), kind `vllm-build/v1`, PRESERVED.

## The partition checker on the new construction
The check is `Q_word_v1{X=16,W=32,R=no-recompute}` with #98's member check, on every distinct specialization of the Build's 10 Programs. Each is cut exactly, with no interpolation between attention lengths (`vo_word.py`).

| arm | specializations | Calls | violations | recomputed gates | redundant gates | gates | committed interior words |
|---|---|---|---|---|---|---|---|
| unset (`Attention_v2`, 174,852 Calls) | 1,164 | 8,753,524 | 0 | 0 | 0 | 1,205,000,363,503 | 7,079,867,169 |
| `check-inf-per-iteration` (`Attention_v4`, 174,852 Calls) | 1,164 | 8,753,524 | **0** | **0** | 0 | 1,204,984,876,015 | 7,068,765,345 |

- **What the new construction removes.** It has 15,487,488 fewer gates and 11,101,824 fewer committed words (and units). Those are the -inf guards at FA3's unmasked iterations that the kernel doesn't execute.
- **Strict partition.** Every specialization's cut is ok: 0 violations and 0 redundant gates in both arms.
- **`query.cross_call`.** 0 recomputes in all 10 Programs, both arms.
- **The manifest.** Both Builds have 247,327 identities, complete.

## Unset = the record
The Program digests differ from the 09-22 record only through the Program id's `SRC` static (the wrapper's module path, `609750e4714a` to `bfb0f1dba532`), exactly as in task 1. So I checked it three ways:
1. **Row for row.** All 9 request Programs equal the recorded ones (`art:f9439154`): 8,739,106 Calls, 0 differing, every params list equal.
2. **Manifest.** All 247,327 identities equal the record's `manifest.json`, with `program_digest` set aside. None are missing and none are extra.
3. **Head = base.** The unset Build equals base main byte for byte on the step Program (`345ebaf9…`) and `LP10_T8` (`e2d6a391…`). The base run is `r20260927-070450-ab07`.

## Optional: the Match under the new construction: PASS (added 2026-09-27T12:15Z)
**Verdict.** `match PASS rc=0/0/0 wall=3073s verdict PASS global PASS dag concurrency 8 tokens_equal True fold True`, 2026-09-27T11:57Z.
- **Run.** `r20260927-102456-f038` on `vyv-rf-verify-optins-h100` (H100 80GB HBM3 secure, driver 580.126, $3.49/h), tree `b7a4092a`. PRESERVED.
- **GM-01.** All eight checks pass with 0 problems: G1 requests declared, G2 observed, G3 X-09 subcircuits, G4 identity map, G5 shared state, G6 chronology, G7 VU population and G8 within-step order.
- **Match summary.** `canonical_equal: true` against the `check-inf-per-iteration` workload Program, and the control and instrumented tokens are equal.

**The fold builds the new construction.** It folds 133,128 attention Calls, all `Attention_v4`, and 0 are `Attention_v2`. That is exactly the Build's 174,852 `Attention_v4` Calls less the unserved main shape (LP1024_T127, 41,436) and the step Program (288).

**How the target reached the capture.** The capture's engine target comes only from the workload's `target` block (`vllm_adapter.load_workload` → `target_of_workload`), because `verity-vllm match` passes no `--target`.
- In a working copy of the tree, row #73's workload gained `target = {compute_capability [9,0], num_sms 132, fa3_construction check-inf-per-iteration}`. That's the H100's own facts plus the knob, the way #74 declares `fp8_block_gemm`.
- The `check-inf-per-iteration` Build's 10 Programs (`art:622fbaf1`) were reused unchanged.
- GP-01 recomposed over the edited workload gives workload digest `c05b549f…`, the same as the Build's. The manifest was rebuilt too (247,327 identities).
- G1 ties the edited workload to both the Program and the capture header.

**The precondition was met.** 9 minutes after the pod started, a one-token probe capture's RunHeader carried `profile.target.fa3_construction = "check-inf-per-iteration"` (`probe-target.json`).

**Cost.** The H100 ran 10:24Z to 12:13:15Z, about $6.36, under the $10 cap root raised. It is terminated; its registry entry was already gone.

**Evidence.** `results/r73/match/` in the notes lane: `global_match.json`, `match_summary.json`, `match_decomp.json`, the fold summary, gates, card, `workload-edit.json`, `probe-target.json`, `stages.txt` and `row.log`. The script is `vo_match73.sh`.

**Evidence.** In the notes repo under `lanes/vllm-verify-optins/evidence/`:
- `results/r73/{off,v4}/`: digests, `calls.jsonl`, `word-summary.json` and `word.jsonl.gz` (each specialization's cut);
- `results/r73/rows-vs-record.json` and `results/base/`;
- the scripts `vo_run73.sh` and `vo_word.py`.
