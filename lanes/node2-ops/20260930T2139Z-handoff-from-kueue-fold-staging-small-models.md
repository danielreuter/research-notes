---
id: 20260930T2139Z-handoff-from-kueue-fold-staging-small-models
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
From 2:39 PM PDT I'm staging models into `/workspace/jobs/hf` on node 2 for Builds and for n2-commits' Commits (circuits' yes, `note:20260930T2145Z-handoff-from-infra-circuits-yes-sm120`). The copy pauses whenever a window is timed or waiting, and runs at 300 MB/s.
- **New, 16.7 GB:** SmolLM2-135M (0.3 GB), Qwen2.5-1.5B (3.1 GB), Qwen3-4B-Instruct-2507 (8.1 GB) and its FP8 (5.2 GB).
- **Already there, 41 GB:** SmolLM2-360M, TinyLlama, Qwen2.5-0.5B, Phi-3-mini, Pythia-160m, Mistral-7B, OLMoE.
- **Qwen3-30B-A3B, 61 GB:** finishing now.

That's about 119 GB in `/workspace/jobs/hf` in all. The disk goes from 35% to about 37%.
