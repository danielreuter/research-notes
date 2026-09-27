---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T11:37Z

# Task 3 DONE: #74 (Qwen3-4B-FP8, H100) `SHARED_SCALE` on the real Build: 0 recomputes; host products = the old construction's at every coordinate; unset = record

**Tree.** The verification merge `b7a4092a`; the value check ran on `d6ea2dc3` (= `b7a4092a` + #128 `fp8.scale_products`).

**The Build.** A real Build of the row, knob unset, in run `r20260927-070406-c1be` (PRESERVED):
- It ran on `vyv-rf-verify-optins-l40s` with the GPU hidden, under the row's declared target (sm_90, 132 SMs, `fp8_block_gemm` cutlass).
- It passed, with 10 Programs and 262,885 manifest identities.
- Its output is `art:fcd189dc…`, kind `vllm-build/v1`, PRESERVED.

## The member check on the request Programs with `SHARED_SCALE` applied
The check is `Q_word_v1{X=16,W=32,R=no-recompute}` with #98's member check, over all 1,167 distinct specializations of the Build's 10 Programs (every family, cut exactly), and `query.cross_call`. `SHARED_SCALE` substitutes each Call's Definition; the Calls and operands stay the same.

| construction | violations | recomputed gates | redundant | gates | committed interior words | `cross_call` |
|---|---|---|---|---|---|---|
| recorded (`ScaledMmFp8Block_v1`) | 747,936 (every FP8 Call, `cut:gate-recomputed`) | 146,281,322,880 | 0 | 1,169,864,803,915 | 7,645,689,946 | 0 |
| `SHARED_SCALE` | **0** | **0** | 0 | 1,023,583,481,035 | 8,797,511,386 | 0 |

- **The cost.** It commits +1,151,821,440 words: the products, 6,160 per token per layer × 186,984. Those are the recompute lane's per-Call numbers.
- **Everything else is clean.** No specialization outside the four FP8 ones has a violation, under either construction.

## The value check: host products against the old construction at every coordinate, on the recorded Build's steps
**How.** The recorded request Programs (`art:9d14bd11`) are evaluated Call by Call with the replay's row kernels (`evidence/vo_fp8_values.py`), from the prompt ids and the checkpoint of record (sha256 `b6154d74…`). No committed value is read: every activation, `x_s` included, is the Program's.
- At every `ScaledMmFp8Block_v1` Call, the host products are `fp8.scale_products(x_s, w_s)` (#128, through `F32Mul_v1`).
- They are checked against the old construction's `F32Mul_v1(sx[kb], sw[n // G][kb])` at every output coordinate n and every kb.
- On sampled Calls, each coordinate's old Definition is evaluated gate by gate, and its own `F32Mul` gates are read from the transcript. Its output, and the new `GivenScale` coordinate fed the host products, are compared with the row kernel.

| sample | FP8 Calls | coordinates host = old `F32Mul_v1` | coordinate-level checks | mismatches | tokens vs record |
|---|---|---|---|---|---|
| `LP73_T1`, both steps (VM) | 10,656 | 2,100,510,720 | 1,335 Calls, 57,280 coordinates (every coordinate of layer 0's 4 linears) | **0** | 2/2 equal |
| `LP11_T94`, first 12 steps (pod `r20260927-080159-be00`) | 3,168 | 624,476,160 | 792 Calls, 15,814 coordinates | **0** | 12/12 equal |

- **NaN and subnormal scale pairs: none in the sample.**
  - `x_s`: 511,488 words, 0 zero / subnormal / inf / NaN.
  - `w_s`: 21,288,960 words, likewise 0.
  - Products: 21,288,960 words, likewise 0. They range from 1.08e-11 to 1.54e-2.
- **A bare numpy multiply** agrees on this data too (0 differences).
- **The edge cases where they could differ** are two-NaN pairs only: 40 of 784 edge pairs, payload only. That's PR #128, merge-ready in `20260927T0712Z-…-scale-products.md`. #74 can't reach them, because `x_s` is never NaN.
- **The rotary table** is the analytic `program/model.cos_sin_table`, because the record keeps no served table. The 14 matching tokens show the evaluation reproduces the served run.

## Unset = the record
The Program digests differ from the 09-22 record only through the Program id's `SRC` static, as in tasks 1 and 2. So I checked it three ways:
1. **Row for row.** All 9 request Programs equal the recorded ones: 10,093,224 Calls, 0 differing, every params list equal.
2. **Manifest.** All 262,885 identities equal the record's `manifest.json`, with `program_digest` set aside. None are missing and none are extra.
3. **Head = base.** The Build equals base main byte for byte on the step Program (`e67b48c5…`) and `LP73_T1` (`573a2732…`). The base run is `r20260927-070450-ab07`.

**The earlier VM check agrees.** On the 6 smaller stored Programs, the FP8-only member check found 293,760 recorded violations and 0 with `SHARED_SCALE`, and `cross_call` found 0.

**Pods.** The L40S `69t3tqnpjam7kc` ran 06:57Z to 11:32:29Z, about $5.00. It is terminated and unregistered, and all 7 of its runs are fetched and PRESERVED.

**Evidence.** In the notes repo under `lanes/vllm-verify-optins/evidence/`:
- `results/r74/off/` (digests, `calls.jsonl`, `word-summary.json`, `word.jsonl.gz`), `results/r74/rows-vs-record.json`, and `results/r74/fp8-LP73_T1/` and `fp8-LP11_T94/` (the value summaries, and each FP8 Call's line);
- the scripts `vo_run74.sh`, `vo_fp8_values.py` and `vo_run74v.sh`.
