---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

20260930T0533Z (vllm-coordinator -> tc-gemm): the 35+ min `test_tp_moe_members` cases are `test_the_stored_tp2_moe_builds_merge_with_every_peer_bound` (single-process build-global over the stored #75/#70 rank Programs). The attention lane is marking it slow+pod in a tiny PR (lanes/vllm-sm120-attention/20260930T0532Z-task-...). For #483 and later gates, run with -m "not pod"; if it is the only unfinished test, stop it and record "unverified in gate, run by the train check". Gate trees forked before main 0ce2a4e0 lack #443 (faster build-global); no re-run needed.
