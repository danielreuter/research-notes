---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note (two findings, one pre-merge PR) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T10:30Z · re: your 09:21Z and 10:02Z

**Qwen2.5-0.5B with #483 + #501 fails the Commit's identity coverage.**
- **Run:** `r20260930-093907-23fb`, tree `7b33718d`.
- **The failure:** 768 of 12,747 required identities have no binding, starting with step 0 `model.layers.0.self_attn.qkv_proj/bias`, request r0, rank 0.
- **What that shows:** the Build now emits the bias Definitions and the manifest requires the bias values, but the Commit binds no qkv bias tensor. It needs a committer or binding change beside #483/#501.
- **Label:** `fail`, with this cause. Qwen2.5-1.5B B8 is running on the same tree and will likely fail the same way.

**#528 on its own fails the P10 size ratchet.** `native_host.py` is 2,554 lines against a recorded 2,550 (#528 adds 5 lines and removes 1, with no allowlist change), so the train's `check` will stop it. I merged it into the run branch as it is. OLMoE and Qwen3-30B-A3B are re-running at `757fdf8c` with the router tap on, under the prefix `pre-merge #486 #481 #469 #487 #502 #483 #501 #528 @ 757fdf8c`.

**Other labels:**
- OLMoE's old attempt now reads "identity-count bug with router tap (#528); replay 460/460".
- Qwen3-30B-A3B's first attempt did not fail like OLMoE's. Its Build request derive hit the row's default 900 s cap, so it re-runs with `BUILD_TIMEOUT=7200`.
