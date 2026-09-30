---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T03:14Z

- **#465 is approved,** and its merge request is filed (`lanes/coordinator/20260930T0314Z-merge-requests-…-466-465.md`). The `blackwell_consumer` name and the Hopper dot decision are accepted.
- **The cuBLASLt finding** is accepted: step 2 becomes a cuBLASLt correspondence under `VLLM_BATCH_INVARIANT=1` (split-K off) on the configs' linear shapes, for every M. Treat it as the analogue of H100's R17 dense probe.
- **Your fold question:** H100 rows fold cuBLASLt linears today. #73's Match PASSed at `14f027c3` with `Gemm_v2{…,DOT=Hopper…}` from the H100 GEMM target. So the fold resolves the linear from the target's registered GEMM record, not from a Triton launch. For sm_120, check that the same pattern resolves when `blackwell_consumer`'s record is the one selected, and cover that in step 2's correspondence. If it doesn't, write one line here and I'll route it.
- **Lane B's item:** `query/required.py::_profile`'s `cc[0] >= 9 → FA3` fallback is noted for the attention lane (FA2 on sm_120).
