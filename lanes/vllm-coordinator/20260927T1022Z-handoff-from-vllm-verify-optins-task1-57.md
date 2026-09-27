---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T10:22Z

# Task 1 DONE: #57 (Gemma-2-2B, L40S) real Builds with `weight_only_calls` unset and `"once"`: 0 recomputes; unset = record

**Tree.** The verification merge `b7a4092a` (main `ae5db5d3` + #98 `4f87f275` + #105 `b0a12771` with #102 + #106 `df13126f` + #109 `39e3b24c`).

**The Builds.** Two real Builds of the row, both in run `r20260927-070353-8a9b` (PRESERVED):
- They ran on `vyv-rf-verify-optins-l40s` with the GPU hidden, under the record's device target (sm_89, 142 SMs).
- Each is the row's own Build stage (`vo_row_build.py`): the step Program, 9 request Programs, GP-01's workload Program and the manifest. Both passed.
- The outputs are `art:f5671a8f…` (unset) and `art:3ede2457…` (`once`), kind `vllm-build/v1`, PRESERVED.

## `once`: `query.cross_call` (#98) on the real request Programs
| arm | Programs | recomputed Calls | recomputed gates | `+ 1` Calls |
|---|---|---|---|---|
| unset | 9 request + step | 57,855 | 133,297,920 | 58,905 |
| `once` | 9 request + step | **0** | **0** | **1,050** |

- **Per Program.** With `once`, every Program has exactly **105** `+ 1` (`AddScalarBf16_v1`) Calls, one per norm weight.
- **Unset, per Program.** The `+ 1` Calls range from 210 (LP779_T1) to 13,440 (LP1024_T127 main and LP10_T127), and the step Program has 105.
- **Same as the recompute lane.** The 8 extra shapes, unset, give exactly its numbers on the recorded Programs: 44,520 Calls, 102,574,080 gates and 45,360 `+ 1` Calls.
- **`once` removes only the repeated adds.** Its Programs have 5,572,996 Calls against 5,630,851 unset.

## Unset = the record
**The record's Program digests can't be reproduced by any current tree.** A Program's id carries an `SRC` static, the wrapper's description, and that includes the wrapper class's module path.
- The 09-22 records were built when the wrapper lived in `verity_capture/experimental/cb_a/`. So `SRC` went from `609750e4714a` to `bfb0f1dba532`, identically on every row and model.
- On the step Program everything structural is equal to the record: gates, dead gates, root nodes, spec histogram, rules applied, weights, KV rewrites and the export op histogram.

So I checked it three ways:
1. **Row for row.** All 9 request Programs equal the recorded ones (`art:5e925a59`): 5,622,349 Calls, 0 differing, and every params list equal (`vo_rows_vs_record.py`).
2. **Manifest.** 163,484 identities, complete, the record's count. Against the recorded v1 `manifest.json` (163,052), with `program_digest` set aside, 0 identities are missing. The 432 extra are exactly the record's sanctioned `only_new: 432` (the promoted `model/out`, F-r19-int-20).
3. **Head = base.** The unset Build equals base main `ae5db5d3` byte for byte, on the step Program (`7bdaffd1…`) and `LP31_T52` (`b342ff30…`). The base run is `r20260927-070450-ab07`.

The `once` Build keeps the step Program (`7bdaffd1`, one forward) and the identity count (163,484). The request and workload Programs change, as designed.

## Not changed / found, not fixed
- **Cross-request copies.** GP-01 hoisting is still open. The workload Program issues 105 `+ 1` Calls per request Program, 8 copies per norm, because `cross_call` checks each Program on its own.
- **Match.** The eager Match fold still issues weight-only Calls per step. The Match was not in scope (Build only).

**Evidence.** In the notes repo under `lanes/vllm-verify-optins/evidence/`:
- `results/r57/` (the digest comparisons, `calls.jsonl`, the summary, `rows-vs-record.json`) and `results/base/`;
- the scripts `vo_run57.sh`, `vo_build.sh`, `vo_row_build.py`, `vo_calls.py` and `vo_rows_vs_record.py`.
