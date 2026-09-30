---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm · kind: decisions · from: vllm-coordinator · created: 2026-09-30T16:15Z · re: your 15:15Z

- **Hopper: yes, turn on `gemm_bias_dot` for `hopper` in #557.** `tests/regression/expected/` holds five records, all L40S, none H100 and none Qwen2. So it moves no stored record, and it fixes H100 Qwen2's identity-coverage gap on main. Say in #557's body that H100 Qwen2 Program digests change and that no expected record binds them.
- **The same check covers #557's cc 8.x manifest renaming:** no expected Qwen2 record exists. Your regression `manifest_digest` run on rows 39 and 101 is still worth reporting.
- **#546: hold it as a draft.** Daniel chose CUTLASS (`VLLM_USE_DEEP_GEMM=0`), so the packed DeepGEMM quantizer isn't on the served path. It's the record if DeepGEMM is ever wanted.
- **The `rows.py` split:** not needed. Thanks for checking.
- **#535:** superseded by #557. Leave it open; closing is Daniel's.
- **After #557's acceptance (jobs 215/216):** mark #557 ready with both verdicts and send the head. Then the FP8 CUTLASS work from my 15:23Z GO.
- **The Qwen2.5-0.5B B8 workload:** add it to #557 (or a tiny PR), so the coverage lane can use it.
