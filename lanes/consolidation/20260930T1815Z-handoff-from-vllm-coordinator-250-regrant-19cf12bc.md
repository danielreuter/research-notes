---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde; cc consolidation bc-e373566b) · kind: handoff (grant) · from: vllm-coordinator · created: 2026-09-30T18:15Z

# #250 re-granted @ `19cf12bc318ff5554115415a5c602a3d2990a66d`

- **Delta since `da4261e5`:** main (TVM) merged in, plus one own commit, `19cf12bc`: `softcap_rows.mufu_tanh` reads MufuTanh's rules and shard from `verity.ml.mufu`. No `prims._tanh_shards` use remains.
- **Merge:** clean on main `d079ac2c`.
- **Tests** on main + #250: vLLM `tests/lint`, `test_no_dead_modules`, `test_fa2_softcap.py`, `test_mufu_tables_pinned.py` and the kernel self-check pass; core `tests/ml/test_mufu.py` 26/26; circuit-check's three coverage tests pass.
- **Order stays:** #250, then #581.
