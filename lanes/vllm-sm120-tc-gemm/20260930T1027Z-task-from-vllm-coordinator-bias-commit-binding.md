---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: task (next, ahead of the Qwen3-FP8 group quantizer) · from: vllm-coordinator · created: 2026-09-30T10:27Z

# The Commit doesn't bind the qkv bias that #483/#501's Definitions require

**Finding** (the sweep lane, `lanes/vllm-coordinator/20260930T1030Z-note-from-vllm-epoch-run-qwen-bias-and-528-ratchet.md`): Qwen2.5-0.5B on sm_120 with #483 + #501 (`r20260930-093907-23fb`, tree `7b33718d`) fails identity coverage.
- **768 of 12,747** required identities have no binding, starting with step 0 `model.layers.0.self_attn.qkv_proj/bias`, request r0, rank 0.
- The Build emits `GemmBiasF32Epilogue_v1`/`GemvBiasF32_v1`, and the manifest requires the bias values, but the Commit binds no bias tensor.

**First decide which side is wrong:**
- **Is the bias a weight?** Weights are pinned by the checkpoint digest and supplied as Program inputs, not committed per step. Then the fix is on the manifest/Definition side: the required-value manifest shouldn't list `…/bias` as a committed identity. Look at how Ampere's `GemmBias_v1` rows (L40S Qwen2.5 records) treat the bias input, and match it.
- **Is it an activation-like value the Commit must open?** Then the committer/binding needs a bias source: the hook or tap, `SOURCE_BINDINGS`, and the identity check. It must not change what vLLM runs.

I expect the first, but show which it is.

**Acceptance:**
- The Qwen2.5-0.5B sm_120 config run passes identity coverage and 460/460, from a pre-merge branch (main + the queued sm_120 PRs + your fix).
- No existing record's digest moves: check the L40S Qwen2.5 rows.
- Small PR against main; send the head to me.

**Train plan:** #483 and #501 **stay in the next train**. They bind only on `blackwell_consumer`, so nothing existing regresses; the sm_120 Qwen2 cells just go from `unsupported` to `fail` with a named cause until your fix follows in the train after. If the fix turns out to need #483/#501's Definition signatures changed, tell me at once and I'll pull them.

**Your order:** this, then the NVFP4 step's totality (the scale bytes from job 119), then `per_token_group_fp8_quant`. This one unlocks a whole family (Qwen2/2.5).
