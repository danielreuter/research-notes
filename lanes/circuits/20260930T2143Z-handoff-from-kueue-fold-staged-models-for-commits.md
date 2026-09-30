---
id: 20260930T2143Z-handoff-from-kueue-fold-staged-models-for-commits.md
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# Staged on node 2 for Builds and Commits (2:43 PM PDT): 13 models, plain files under `/workspace/jobs/hf/hub`, at the manifest's pinned revisions

SmolLM2-135M, SmolLM2-360M, TinyLlama-1.1B, Qwen2.5-0.5B, Qwen2.5-1.5B, Pythia-160m, Phi-3-mini-4k, Qwen3-4B-Instruct-2507 and its FP8,
Mistral-7B v0.3, Llama-3.2-1B, OLMoE-1B-7B, and Qwen3-30B-A3B (finishing its 61 GB copy). **Not staged:** the `verity-fp8/*` recipe
checkpoints and the Qwen2.5-1.5B-Instruct(-AWQ) pins, which aren't on node 1 either. The bootstrap makes the recipe ones from their BF16 pins.
To stage another model: `/workspace/verity-guest/bin/n2_build.sh stage REPO REV` on node 1.
