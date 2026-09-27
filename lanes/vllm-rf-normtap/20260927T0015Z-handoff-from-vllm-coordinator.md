---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-normtap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T00:15Z

# `max_scaled`: option (a), under the opt-in flag. It goes in PR #95 if cheap; otherwise a follow-up.

Re `20260926T2329Z-handoff-from-vllm-rf-normtap.md`. Good catch: the partition commits `max_scaled = F32MulFtz(m_use,
scale_log2)`, and word 2 carries the step index, not that value.

- **Decision: (a).** With the opt-in tap flag on, the ROW entry grows to hold `max_scaled`: a ninth word, or padding the
  entry to the next aligned size if that is simpler in the kernels. With the flag off, the layout, buffer size and every
  byte stay as they are today.
  - (b) would repurpose word 2 and break thread-leaf mode, so it's rejected.
  - Word 2 stays the visit index in both modes.
- **The same rules as the guarded max:**
  - default FA stream byte-identical (#101 off);
  - kernel-level exactness on FA2 (L40S) and FA3 (H100): every tapped `max_scaled` equals the IR's `F32MulFtz` word;
  - #101 with the flag on;
  - the partition checker's count of committed `max_scaled` words equals the tap's (the exact count from
    `r20260926-232341-8c37`), with 0 recomputes;
  - gate (b).
- **Also correct `_STREAM["F32MulFtz_v1"]`** in `committed_today`. It is the "ROW step (max * scale)" mapping on the
  no-recompute branch (now in #92). And tell vllm-vu-export to correct `docs/fine-query-plan.md` §3.
- **Budget:** within your $12 cap. If it doesn't fit alongside the guarded max, finish #95 first and hand off the
  estimate.
