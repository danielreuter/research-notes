---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T12:20Z

# STATUS (FINAL): goal 10 done; all three opt-ins verified on real Builds; no pods; $11.55 of $20

## Morning report summary
Overnight goal 10 verified the three opt-in constructions on real Builds of their rows: the FA3 per-iteration `Check_inf`, Gemma's weight + 1 once per norm, and FP8 scale products computed once. With each opt-in, the checkers find no recomputed value. With each opt-in unset, the Build equals the record.
- **#57, Gemma-2-2B, `weight_only_calls = "once"`.** `cross_call` finds 0 recomputes (it was 57,855 Calls and 133 M gates unset), with 105 `+ 1` Calls per request Program.
- **#73, Qwen3-4B, `fa3_construction = "check-inf-per-iteration"`.** The partition checker finds 0 violations and 0 recomputed gates over all 1,164 specializations. The H100 Match under the new construction passes GM-01, all eight checks. The fold builds `Attention_v4` for every one of the 133,128 attention Calls, and the tokens are equal.
- **#74, Qwen3-4B-FP8, `SHARED_SCALE`.** The member check goes from 747,936 violations and 146 G recomputed gates to 0 and 0, at +1.15 G committed words.
  - The host-computed scale products equal the old construction's `F32Mul_v1` at all 2.72 G coordinates of two recorded requests, and all 14 tokens equal the record.
  - There were no NaN or subnormal scale pairs.
- **The follow-up, [PR #128](https://github.com/danielreuter/verity/pull/128) (stacked on #106).** The committer's `fp8.scale_products` computes through `F32Mul_v1`, because numpy's array multiply picks the other NaN on two-NaN pairs.
- **The digest caveat.** The 09-22 records' Program digests can't be reproduced by today's tree. That's only because the Program id's `SRC` names the wrapper's old module path. So "equals the record" is shown row for row on every request Program and identity for identity on the manifest, and head = base main byte for byte.

## Per-task handoffs (all in this directory)
- Task 1 (#57): `20260927T1022Z-handoff-from-vllm-verify-optins-task1-57.md`.
- Task 2 (#73), with the Match verdict: `20260927T1024Z-handoff-from-vllm-verify-optins-task2-73.md`.
- Task 3 (#74): `20260927T1137Z-handoff-from-vllm-verify-optins-task3-74.md`.
- PR #128, merge-ready: `20260927T0712Z-handoff-from-vllm-verify-optins-scale-products.md`.

## Branches, PRs, artifacts
- **The verification merge**, `cursor/verify-optins-merge-a795`: `b7a4092a` (main `ae5db5d3` + #98 + #105/#102 + #106 + #109), then `d6ea2dc3` (+ #128). It's pushed and not for merging.
- **[PR #128](https://github.com/danielreuter/verity/pull/128)**, `cursor/fp8-scale-products-a795` @ `a763a41a`, draft, stacked on #106. It asks the research coordinator to update #106's "Serving" paragraph.
- **The Builds**, all kind `vllm-build/v1` and PRESERVED:
  - #57: `art:f5671a8f` (unset), `art:3ede2457` (`once`);
  - #73: `art:24c603a7` (unset), `art:622fbaf1` (`check-inf`);
  - #74: `art:fcd189dc` (unset).
- **The runs**, all PRESERVED: `065759-3c10`, `070450-ab07`, `070757-78c4`, `070353-8a9b`, `070351-283d`, `070406-c1be`, `080159-be00` and `102456-f038`. There is also the CPU-pod setup `064517-eb5b`.

## Pods and spend
| pod | RunPod | ran | $ |
|---|---|---|---|
| CPU cpu5m 16/128 | `l32zhicuc7ce1b` | 06:41Z to 06:51:40Z (smoke Build failed: no driver) | 0.19 |
| L40S secure, GPU hidden | `69t3tqnpjam7kc` | 06:57Z to 11:32:29Z | 5.00 |
| H100 SXM secure | `2m29px5hjgtci2` | 10:24Z to 12:13:15Z | 6.36 |
| **total** | | all terminated and unregistered | **11.55** |

## Found, not fixed
1. **No current tree reproduces the 09-22 records' Program digests.** The Program id's `SRC` static holds the wrapper class's module path (`verity_capture/experimental/cb_a/` then; `verity_vllm/program/frontend/` now). This holds for #57, #73 and #74, and likely any record from that period. The re-baseline will record new ones anyway.
2. **A CPU-only host can't run a Build.** vLLM resolves `UnspecifiedPlatform`, and `vllm._C` and the flash-attention extensions need the driver. A GPU host with the GPU hidden works, and costs the same Build time.
3. **`verity-vllm match` passes no `--target` to the capture.** A construction knob reaches the Match only through the workload's `target` block. A row that opts in (for example `fa3_construction`) has to declare it there, not only as the Build's `--target`.
4. **Two items carried from the recompute lane, not addressed here.** GP-01 hoisting of weight-only Calls (8 copies per norm on #57's workload Program), and the Match fold's weight-only Calls per step under `once`.

There are no blockers.
