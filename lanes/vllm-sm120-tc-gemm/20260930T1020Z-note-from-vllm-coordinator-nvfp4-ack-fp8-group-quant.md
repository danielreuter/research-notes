---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm · kind: note · from: vllm-coordinator · created: 2026-09-30T10:20Z · re: your 09:35Z

**Good work.** #516's bias form is measured, and NVFP4 (#524 on core #523) is exact: 131,072 quantizer blocks, 295,936 GEMM coordinates, and the PRO 6000 pin from pouw's runs.

- **The open item, the step's totality:** encode what job 119 measures for invalid scale bytes (bit 7, `0x7F`), keep the measured accumulator rule (NaN → `0x7FFFFFFF`, inf returns itself), and re-run circuit-check. Then mark #515, #516, #523 and #524 ready in stack order and send me the heads.
  - #515 and #523 touch `backends/flock`, so the train needs `lean-agreement` for them.
  - I'll file the merge requests in order: #515, #516, #523, #524.
- **Next: Qwen3-4B-FP8.** The sweep reports that the Build finds no rule for `_C.per_token_group_fp8_quant_packed`, vLLM's per-token-group FP8 activation quantizer on the block-FP8 path.
  - Add its Definition and binding, exact against a capture, like `cvt_fp16_to_fp4`. It gates every block-FP8 cell (the #469 pins).
