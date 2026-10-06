lane: coordinator · kind: handoff · from: merge-queue · to: bc-b8aaadaa-aefd-503e-9863-5eabb3a28c79 · created: 20261006T0203Z

# #1026 conflict: conflicts with `next` in integrations/vllm/tests/lint/allowlists/p09_layering.json, integrations/vllm/verity_vllm/program/frontend/rules/vocab.py, integrations/vllm/verity_vllm/program/registry/boolean_fp8_moe.py, tools/circuit_check/src/circuit_check/targets.py

- **PR:** #1026 vllm: block-FP8 fused-MoE experts on sm_120 (Qwen3-235B-A22B-FP8 TP8), and the pinned MoE backend
- **Head:** `e41e2260bca82f589ffe7f9c538468203448ea6a`
- **What happened:** conflicts with `next` in integrations/vllm/tests/lint/allowlists/p09_layering.json, integrations/vllm/verity_vllm/program/frontend/rules/vocab.py, integrations/vllm/verity_vllm/program/registry/boolean_fp8_moe.py, tools/circuit_check/src/circuit_check/targets.py
- **Next:** push a fix; a new head is admitted again at the tip of `next`.
