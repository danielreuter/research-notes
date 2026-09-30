---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: note · from: vllm-coordinator · created: 2026-09-30T06:44Z · re: merge requests 05:52Z (#477, #486) and 06:17Z (#469, #481)

**#477 and #481 conflict with each other** in `integrations/vllm/verity_vllm/program/registry/targets.py`, `TARGETS["blackwell_consumer"]`. Each is clean on main `29f691be` alone. Putting both in one train (TVF) needs this resolution, and nothing else in the pair conflicts:
- keep #477's `"flash_attn_versions": (2,)` and `"evidence": {"attention_fa2": ...}`;
- add #481's `"moe_expert_dot": True` with its comment.

Checked locally: it parses, and main + #477 + #481 + #469 merges with only this conflict. **Merge order in the train:** #477, then #486 (when granted), then #481, then #469.

The epoch-run lane is building its sm_120 coverage run branch the same way, so TVF's result will match it.
