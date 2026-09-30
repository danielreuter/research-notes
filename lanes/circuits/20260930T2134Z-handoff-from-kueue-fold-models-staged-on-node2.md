---
id: 20260930T2134Z-handoff-from-kueue-fold-models-staged-on-node2.md
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# Models staged on node 2 for Builds (2:34 PM PDT); `n2_build.sh` stages any other one itself

Plain files under node 2's `/workspace/jobs/hf/hub`: SmolLM2-360M, TinyLlama-1.1B, Llama-3.2-1B (unsloth), Qwen2.5-0.5B, Phi-3-mini-4k,
Mistral-7B v0.3 (unsloth), OLMoE-1B-7B and Pythia-160m; Qwen3-30B-A3B (57 GB) is copying for `cov-g080`. A Build for any other model on
node 1's `/workspace/hf` gets its snapshot copied when it's submitted, and `submit` refuses the Build if the copy isn't complete.
TP1 Builds only, as before.
