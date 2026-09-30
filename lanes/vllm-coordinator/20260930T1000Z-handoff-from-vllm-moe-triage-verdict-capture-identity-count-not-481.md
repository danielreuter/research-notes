---
cursor:
  subagentId: "bc-8d3fb01d-2827-5742-ac99-7a9eafaa27c8"
---

lane: vllm-coordinator · kind: handoff · from: vllm-moe-triage (bc-8d3fb01d) · created: 2026-09-30T10:00Z

# Verdict: capture (the committer's identity check miscounts the router-softmax tap). Not the binding: #481 can go in the train.

**The failure is a count, not a value.** Run `r20260930-091912-128d` is the OLMoE sm_120 config row on tree `cov-k15-3-113-ce1b86e4-head`; its evidence is in `/workspace/jobs/cov/cov-k15-3/olmoe-1b-7b__...__b1__i256__o32.../commit/` on vy-nebius-1.
- `moe_layers_bad {L: 7}` is `NativeHostCommitter.identity_check`'s count of `moe/L<k>/*` tensors per layer per step (`native_host.py` ~2211). It isn't "7 wrong identities".
- The manifest expects `moe_tensors_per_layer = 6`, the MoE block source's `TENSORS_PER_LAYER` (router_w, router_ids, up, act, down, sum).
- The row ran with the router tap on (`taps: norm_tap, router_tap`). `RouterSoftmaxSource` commits `moe/L<k>/router_softmax` into the same step stream.
- The captured layouts (`layouts_pair0_instrumented.json.gz`) hold exactly these per layer: `act, down, router_ids, router_softmax, router_w, sum, up`. That is 6 + 1 = 7 on all 16 layers x 32 steps.
- **First differing identity:** none. No value differs, so there is no dataflow-order first difference. The only extra identity is `moe/L0/router_softmax`, and it is correctly captured.

**The values are exact under the #481 binding.** The same run's C2 sampled exact replay (`sampled_replay_p0.json`) is COMPLETE, **460/460 equal, 0 mismatches**.
- The evaluated sample covers every MoE family: `MoeExpertGemm_v2` 94, `MoeExpertGemmW_v2` 107, `SiluMul_v1` 106, `MoeRouterTopKOrdered_v1` 9 and `MoeSum_v1` 6. The evaluators are `dot_bf16_for(DOT)`, the Hopper k16 step.
- Boundary linkage is 32/32, the MoE plane alias check 512/512 and the weights pin 212/212.
- The CPU v1-vs-v2 re-evaluation (step 2 of the brief) was therefore not needed. The v2 binding reproduces the captured words, and the #481 handoff already showed that v1 differs on sm_120 (`r20260930-032412-1313`).
- No Kueue re-capture was run.

**The bug is on main, not from #481 or the targets.py merge.** The count check is the same on `origin/main`, `cursor/coverage-v0-2622` and `cursor/vllm-sm120-kernels-69c6`. It has been latent since `fd265d7cb` (router tap opt-in): any MoE row with ROUTER_TAP=1 on any architecture fails it.
- **Expect Qwen3-30B-A3B (and Qwen1.5-MoE) to fail the same way** if they run with the router tap. That result says nothing about sm_120 MoE.
- **SiluMul edges:** no sampled SiLU unit mismatched (106/106). This is a sample, not a proof over the edge cases (NaN word, gates < -88.7, signed zeros), so those stay the open item from the #481 handoff.

## Fix (small, pushed, no engine change)
- Branch `cursor/moe-identity-router-tap-27c8` @ `67793c90c`, **against main**. I have not opened a PR; the gh CLI is read-only, so the train or the environment has to open it.
- `expected_manifest()` gains `router_softmax_layers` (the tap source's layers). `identity_check` then expects `moe_tensors_per_layer + 1` on those layers. A missing or duplicated router-softmax tensor still fails by count.
- New test: `tests/program/test_padding_pod_consumer.py::test_the_identity_check_counts_the_router_softmax_tap_as_one_more_moe_tensor_of_each_tapped_layer`.
- On vy-nebius-1 (CPU, run tree's venv312): every test file mentioning identity_check/expected_manifest passes, 119 tests; so do the router-tap tests.

## Proposed actions
1. Release the hold on #481.
2. Merge `cursor/moe-identity-router-tap-27c8` (into main, and merge it into the run branch), then re-run the OLMoE row.
3. Alternatively, re-run it with ROUTER_TAP=0; the check then expects 6 and should pass.
