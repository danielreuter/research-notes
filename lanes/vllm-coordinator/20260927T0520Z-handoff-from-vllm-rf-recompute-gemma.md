---
cursor:
  subagentId: "bc-06147ba0-d1ae-5ddc-84d6-00cb2d93cbba"
---

lane: vllm-rf-recompute · kind: handoff · from: vllm-rf-recompute (bc-06147ba0) · created: 2026-09-27T05:20Z

# PR #109 merge-ready: #57's Gemma weight + 1 issued once per norm (`TargetProfile.weight_only_calls = "once"`, opt-in)

[PR #109](https://github.com/danielreuter/verity/pull/109), branch `cursor/vllm-rf-recompute-gemma-cbba` @ `39e3b24c`, base `main` `3040ac1f`, three commits:
- `7aeffc5d`: the construction and its tests;
- `51692785` and `39e3b24c`: two test-spelling fixes.

It touches `frontend/target_profile.py`, `frontend/rules/vllm_bindings/norm_chain.py` and one new test file. It does not touch `pipeline/manifest.py` or the query modules, so it doesn't conflict with #98 or #106.

## What it adds
- **`TargetProfile.weight_only_calls`:** None = `"per-forward"` (as vLLM executes it, the record) or `"once"`.
  - It is a declared Program static, like `moe_construction`, and never attested.
  - It is omitted from `to_json()` when None. The default profile digest is `86c255b3…` on main and on the head.
  - It is validated, and other spellings are refused.
- **`AddScalarRule`:** when the operand is a weight and the target says `"once"`, the first forward issues the add. Every later forward's add over the same weight leaves (same Definition, same operand runs) is bound to that value, and its provenance entry reads `… x0 (reads <fx node>)`. Unset, the rule's path is the old one: it doesn't touch `ctx.state` and makes the same `record` call.

## Partition checker, #57 with the selector on
**`query.cross_call` (#98).** I checked the 8 recorded request Programs (`art:5e925a59…`) as recorded, and rewritten the way `"once"` builds them: repeated weight-only Calls dropped, readers repointed. Scripts: `evidence/once_rewrite.py` and `evidence/r57_all.sh`. Output: `evidence/cross_r57_recorded_vs_once.jsonl`.
- Recorded: 44,520 duplicate `AddScalarBf16_v1{N=2304,C=1}` Calls and **102,574,080 gates** computed again, all at Call level, spread over the 8 Programs (4.35 M to 30.7 M each).
- `once`: **0 recomputes** in every Program. 105 `+ 1` Calls remain per request Program, one per norm weight.

**`Q_word_v1{16,32,no-recompute}` with #98's member check (row totals, program graph `art:c74deac4…`).** The Definitions are unchanged, so every group's cut is unchanged: 0 violations over all groups, both ways.

| | + 1 Calls | units | gates | committed interior words |
|---|---|---|---|---|
| recorded | 45,360 | 11,011,473,570 | 573,676,355,970 | 959,058,048 |
| `once` | 840 | 10,908,899,490 | 573,471,163,290 | 959,058,048 |

- The widths are unchanged: every unit of the add is one F32Add output of 32 bits.
- The words committed at the `+ 1` Calls' outputs drop from 104,509,440 to 1,935,360. They would be 241,920 if the workload Program hoisted them (found, not fixed).

## Digest A/B, selector off
- Unset and `"per-forward"` derive the same Program digest and the same rule applications (`test_unset_and_per_forward_…`).
- `test_norm_chain.py`'s exact emitted-kind lists pass unchanged in gate (b).
- The default `TargetProfile` digest is unchanged.
- No Definition changed, and `construction_version` enters only the artifact identity, not `program_digest`.
- No row declares the knob, so every Program, manifest, root and verdict of record is unchanged.
- The real-Build A/B on an L40S is deferred to the re-baseline (your 03:49Z).

## Tests
`tests/program/test_weight_only_once.py`, with torch, on a module that runs two Gemma norms in three forwards:
- Unset equals `"per-forward"`.
- `"once"` has one add per norm weight, with every other Call the same.
- Bit-equal outputs on edge words: bf16 weights and activations with ±NaN, ±inf, ±0, subnormals, ±max, and w = −1.
- `cross_call` sees exactly the repeated adds per-forward and nothing under `"once"`. It skips until #98 is on main.
- The knob's serialisation and refusals.

## Gate (b)
All on `vyv-rf-recompute-cpu`, using `gate_b2.sh` in git clones (tree check 0 differing entries, `verity_sampled_proofs` importable).

| side | run | lints | gate (b) |
|---|---|---|---|
| base `3040ac1f` | `r20260927-035144-299a` | rc 0 | 40 F / 3,996 P / 286 S / 6 xf / 11 E (4,339) |
| head `39e3b24c` | `r20260927-044046-03f9` | rc 0 | 39 F / 4,001 P / 287 S / 6 xf / 11 E (4,344) |

- **jdiff:** 0 new failures. The 4 new tests pass.
- **The 1 new skip** is `test_cross_call_finds_the_repeated_adds_only_per_forward`: its `importorskip` of `verity_vllm.query.cross_call` stands until #98 merges.
- **Fixed on head:** 1 test, `test_twins::test_check_writes_the_evidence_schema`. It flips on an extra `openmp` key, depending on whether the pod has a C++ build, so it is unrelated.
- **With #98's query modules applied** (the `d7f76916` vs `fa662029` diff of `word.py`, `cross_call.py` and `call_scope.py`; `evidence/gate-b/pr98-query-d7f76916.patch`): **all 5 pass**, the cross-Call test included. Recorded run: `r20260927-050958-682d` (`evidence/gate-b/x98_check.sh` and its log).
- **The first head, `7aeffc5d`** (`r20260927-035257-150f`), had 2 new failures. Both were test spellings: the descriptor writes the constant as `C={"f64":…}` and the provenance writes `C=1.0`. `51692785` and `39e3b24c` fix them.
- **The queued run for `51692785`** (`r20260927-043810-c5cf`) was stopped by TERM to its process group before it started work.
- **Evidence:** `evidence/gate-b/jdiff-3040ac1f-vs-39e3b24c.txt`. All six runs are preserved on R2 (`research data preserved`, rc 0).

## Serving: how the committer produces it
`w1 = weight + 1` depends only on a committed weight. The committer computes it at load, once per norm module, from the checkpoint's bf16 words: `F32Add_v1(Bf16ToF32_v1(w), 1.0f)`, `AddScalarBf16_v1`'s function in the IR's F32 semantics, NaN payloads included. It commits the result as `<norm module>/weight_plus_one`, f32 [N], once per rank, as `<field>/weight` is.
- ATen's CUDA `add_kernel` is the same single FADD, and it is equal on every non-NaN word.
- Unlike the FP8 product, ATen stores `w + 1` as a tensor. A collector that ever commits that tensor instead of the host value would need the `0x7FFFFFFF` mapping, as with #96. That is in the PR body.

## Not changed, and the switch points for the re-baseline
All three are kept in the PR:
- the eager Match fold (`batch_decomp` SHARED, one instance per engine step), so a row declaring `"once"` fails the Match by name until the fold matches;
- GP-01 hoisting of weight-only Calls into the workload's shared part, which removes the 8 per-request copies per norm that the per-Program check doesn't see;
- the `weight_plus_one` committer source and its manifest identity.

Switching the record is root's re-baseline item. No Program, manifest, root, leaf id or verdict moves, and no allowlist grows.

## Pods and spend
- `vyv-rf-recompute-cpu` (RunPod `qlirspls2cbwyr`, cpu3g 16 vCPU / 64 GB) ran 03:50:07Z to 05:12:41Z. It was terminated after every run was fetched and preserved, and it is unregistered.
- 82.6 min at $0.64/h is **about $0.88**, against the $2.50 cap. The lane made no other spend.
