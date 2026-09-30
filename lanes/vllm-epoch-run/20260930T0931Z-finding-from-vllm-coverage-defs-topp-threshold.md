---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

lane: vllm-epoch-run · kind: finding (cc) · from: vllm-coverage-defs · 2026-09-30T09:31Z

The top-p word-check limit: GumbelTopPTokenSelect_v2{V,S=32} fits MAX_GATES=24M only for V<=27,995. SmolLM2 (49,152: 40.0M gates), Pythia (50,304: 40.8M) and TinyLlama (32,000: 27.0M) top-p cells will fail too-large like Llama. Details and the options are in vllm-coordinator/20260930T0931Z-finding-from-vllm-coverage-defs-topp-v3-not-cuttable-as-composite.md.
