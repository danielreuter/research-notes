---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T11:20Z · for: 14:30Z morning summary

**vllm-serving-commit:** vLLM now commits at serving time in the exact format the Flock prover and the Lean verifier read. It's opt-in,
`vllm-v1` stays the record, and #101's run root `7adcef49` is unchanged in every run. Three runs were served from #101 onto serving's
own roots, and every served file is byte-identical to M0's own writer:
- A2: 183,680 RoPE heads;
- A4 P4: layer 0, four templates, 12,341 units;
- A4 P6: the whole of layer 0 including GEMM as shared rows, 6,771,765 units, committed in a 17 s hook.

The one-stage lane audited them end to end. #119 is approved at `dabffea5`, and #151 (a flaky-test bound) is open. About $3.9 spent;
every pod is terminated.
