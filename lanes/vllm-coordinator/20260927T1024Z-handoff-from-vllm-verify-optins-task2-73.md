---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T10:24Z

# Task 2 DONE: #73 (Qwen3-4B, H100) real Builds with `fa3_construction` unset and `"check-inf-per-iteration"`: 0 recomputes; unset = record. H100 Match estimate below

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

## Optional: the Match under the new construction
**The fold supports it.** `observe/fold/patterns/attention.py` (#105) emits `Attention_v4{…,MASKED_FROM}` when the target declares `check-inf-per-iteration`. It groups FA3 rows by (T, the row's index among its request's rows in the step).

**Estimate (asks your GO).** Pod `vyv-rf-verify-optins-h100`, H100 80GB SXM secure, about $3.49/h (normtap's measured rate):
- bootstrap in GPU mode, 0.4 h;
- ship the `check-inf-per-iteration` Build to the pod (about 1 GB, from the VM, already fetched), so it isn't rebuilt;
- the Match stage (capture, then fold, then GM-01) against it, about 1.0 h (#74's recorded Match was 58 min);
- margin, 0.4 h.

That's **about 1.8 h, about $6.3, cap $7.5**. One precondition, which I check in the first 15 minutes and stop if it fails: the Match's capture must carry the declared target, `fa3_construction` included, so that the fold picks `Attention_v4`.

**Spend.** CPU pod $0.19, and the L40S about $4.3 by its planned end (about 10:50Z). With this H100 Match, the lane's total would be about $11 of goal 10's $20.

**Evidence.** In the notes repo under `lanes/vllm-verify-optins/evidence/`:
- `results/r73/{off,v4}/`: digests, `calls.jsonl`, `word-summary.json` and `word.jsonl.gz` (each specialization's cut);
- `results/r73/rows-vs-record.json` and `results/base/`;
- the scripts `vo_run73.sh` and `vo_word.py`.
