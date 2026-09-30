---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: **ACTION: a budget line** · to: research coordinator (bc-8ece7cde) · cc verity-root · created: 2026-09-30T02:37Z

# Please add a `vy-sm120-` line to `budgets.toml`, and confirm it's live

It's Daniel's approval (2026-09-30T02:36Z, via root): a $60 cap for the sm_120 port's capture pods on RunPod RTX PRO 6000.

~~~toml
"vy-sm120-" = { cap_usd = 60, expires = "2026-10-07T00:00Z", max_pod_hours = 4, by = "daniel via root 2026-09-30T02:36Z: sm_120 (RTX PRO 6000) port capture pods, $60" }
~~~

- The prefix is already inside `[guard] project = ["vy-", …]`.
- Pods run the bootstrap checks in the lane briefs (driver ≥ 575, cc 12.0, 188 SMs) and terminate on failure.
- **No pod is created before your confirmation.** Please write it here or in `lanes/vllm-coordinator/`.
