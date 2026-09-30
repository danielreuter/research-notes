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

## Additions, 2:40 PM PDT (from circuits and the old vLLM coordinator, Slack thread `1790803930.928819`)

- **The first two Commits,** Build done and Commit-ready, both Llama-3.2-1B:
  - `/workspace/jobs/cov/cov-g153/llama32-1b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__stoch-t0.8-p0.95__bi-eager`
  - `/workspace/jobs/cov/cov-k12-4/llama32-1b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`
- **A row is ready** when it has `manifest.json` and `build_summary.json` and no `commit*`.
- **Match the environment before the first Commit on node 2** (n2-commits), and record it in the Attempt:
  - the driver at ≥575 (node 1 has 595.91);
  - the same vLLM pin (`d9105ea80`) and venv;
  - the clocks: node 1 is locked at 2,100 MHz; record node 2's clock state;
  - TP2 needs 2 GPUs on one node with P2P off (not in this first batch).
- **Caches:** the per-tree Triton/vLLM caches and JIT build dirs, or accept a cold first Commit per tree (about 5 minutes).
- **The CPU replay:** run each Commit's replay on node 2 too; bundles for these models are at most a few GB.
- **Staging list, exact:** SmolLM2-135M/360M, TinyLlama-1.1B, Qwen2.5-0.5B/1.5B, Pythia-160M, Phi-3-mini and Qwen3-4B, about 20 GB in
  all. Qwen2.5-7B deployments need their Builds first, which can also run on node 2.
