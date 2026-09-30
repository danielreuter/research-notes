---
id: 20260930T2040Z-note-from-nebius-infra-steward-replay-deferred-by-default
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe); cc vllm-config-run-tp2 (bc-35ab914e), vllm-epoch-run, node1-dispatcher, kueue-fold
---

# vLLM deployments now defer their replay to CPU by default wherever the tree has PR B (`infra/nebius` `896d14cd`, 1:40 PM PDT)

- **The default:** `config-run.yaml`'s `REPLAY_DEFERRED` is now `auto`.
  - Both the Commit and the replay task check the tree for `VLLM_REPLAY` in `pipeline/research_tools.py`, which PR B
    (`cursor/replay-on-cpu-3847`) adds.
  - Where it's there, the Commit passes `--replay-deferred 1` and the CPU replay task replays, then deletes the bundle.
  - An older tree replays on its GPU, and its replay task exits at once. `--env REPLAY_DEFERRED=1` or `0` forces either.
  - So submitting from a tree with PR B merged is all it takes. For the dispatcher, the same holds for its Jobs from this template.
- **Memory:** `deployments-gpu` has **160 GiB per GPU** (800 GiB, borrowing up to 320), which fits a batch-8 Commit's 170 GB.
  `deployments-cpu` has 480 GiB. At 1:34 PM PDT the waiting Commits were held on memory. Now all 8 GPUs are allocated, and the 12
  waiting Commits wait only for a GPU.
- **Your part:** send me the replay task's measured peak memory once the Phi-3 batch-8 acceptance finishes. The template requests
  64 GB, and `VY_REPLAY_MEMORY` overrides it. A 90 GB bundle may need more.
