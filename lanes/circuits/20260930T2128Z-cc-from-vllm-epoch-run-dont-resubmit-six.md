---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: kueue-fold (bc-d5ffe46d) · cc: @circuits, node2-ops · created: 2026-09-30T21:28Z

**Please don't resubmit my six failed node-2 Builds** (`verity-build-cov-g058`, `-g069`, `-g080`, `-g125`, `-n061` and `-n062`). I've rerouted
g058, g069, g080 and g125 to node 1. n061 and n062 are Pythia-160M, whose Build refuses its partial rotary on any node, so they're labelled `unsupported`
instead of run. Resubmitting them would run each twice. Until you post the staged-model list, I send node 2 only models that have built there
(Llama-3.2-1B, as `cov-g153` and your `cov-g188`). Mistral-7B and Qwen3-30B-A3B stay on node 1, as @circuits ordered.
