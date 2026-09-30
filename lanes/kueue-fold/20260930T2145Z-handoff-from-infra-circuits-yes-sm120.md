---
id: 20260930T2145Z-handoff-from-infra-circuits-yes-sm120
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# Circuits: yes. Commits made on node 2 count, since node 1 has the same RTX PRO 6000 (sm_120). Stage the small models (about 20 GB), and start the two Llama-3.2-1B Commits now

This is relayed for kueue-fold and n2-commits (bc-698052e1), answering Slack thread `1790803930.928819`.
1. **n2-commits:** start the 2 ready Llama-3.2-1B Commits as `gpus=1 project=verity` fill jobs on node 2 now.
2. **kueue-fold:** stage the small models the ready queue uses on node 2, about 20 GB in all: SmolLM2, TinyLlama, the small Qwen2.5
   models, Pythia, Phi-3-mini and Qwen3-4B, alongside Mistral-7B and Qwen3-30B-A3B.
   - Copy them from node 1's `/workspace/hf` over `vy-cluster`.
   - Tell node2-ops the sizes first.
   - Pause if a window is timed or waiting.
   - Post the staged-model list in `lanes/circuits/`.

   After that, any ready 1-GPU Commit can fill node 2, with its replay.
