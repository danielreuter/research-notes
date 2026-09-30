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

## Update 07:13Z: with #486 in the train, #481 conflicts in two hunks of `targets.py`
Checked locally: main `f0da69ad` + #477 + #486 + #481 (resolved) + #469 parses, and nothing else conflicts.
1. **`TARGETS["blackwell_consumer"]`:** keep HEAD's `"flash_attn_versions": (2,)`, `"fa2_construction": "check-inf-per-iteration"` and `"evidence": {"attention_fa2": ...}`. Add only #481's comment line and `"moe_expert_dot": True`. **Drop #481's `"flash_attn_versions": ()` and `"evidence": {}`.**
2. **`__all__`:** the union of both sides:
~~~python
__all__ = ["TARGETS", "DOTS", "UnregisteredTarget", "target_family", "gemm_target", "tensor_core_dot",
           "moe_expert_dot", "moe_expert_gemm_spec", "tuned_gemm_table",
           "check_flash_attn_registered", "fa3_kblock_n", "fa3_tile_m", "fa3_check_inf", "fa3_masked_from", "fa2_check_inf", "fa2_masked_from", "attention_geometry", "uses_accepted_kinds", "gemm_spec", "attention_spec", "describe",
           "LaunchContextConflict", "parse_launch_context", "launch_seqlen_q"]
~~~

## Update 08:21Z: #483 (granted @ `7cea7a99`) conflicts with #486 and #481 in `targets.py`. Queue it after TVF
#483 adds `gemm_bias_spec` where #486 changes `attention_spec`, and adds to `__all__` where #481 does. The GEMM lane will merge main into #483 after TVF, resolve it as a union, and send a new head for re-grant. For the pre-merge coverage run, the branch is `cursor/coverage-premerge-8ee1` @ `598c2a53` (main `f0da69ad` + #477 + #486 + #481 + #469 + #487 + #502), on origin.
