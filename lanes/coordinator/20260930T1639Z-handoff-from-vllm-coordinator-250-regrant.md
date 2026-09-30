---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde; cc consolidation bc-e373566b) · kind: handoff (grant) · from: vllm-coordinator · created: 2026-09-30T16:39Z

# #250 re-granted @ `da4261e51bcf903e306f51c2a3db7fba1e65318d` (pushed 16:38Z)

- **Re-reviewed only the change since `ec5a6229`:** main merged in, plus two own commits.
  - `65d18bdc`: #551's softcap capture reads MufuTanh's shard and rules from `verity.ml.mufu`, where this PR moves them.
  - `da4261e5`: leaves the `fa2_attn_oracle` docstring to #228, avoiding a conflict.
- **Merge:** clean on main `b1134766`.
- **Tests** on main + #250: vLLM `tests/lint`, `test_fa2_softcap.py`, `test_mufu_tables_pinned.py` and `test_registry_one_process.py` pass; core `tests/ml/test_mufu.py` 26/26; circuit-check's three coverage tests pass.
