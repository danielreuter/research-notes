---
lane: red-team-standard-hash-2
kind: handoff
from: coordinator
created: 2026-09-25T19:45Z
---

# Review request: the new vllm-v1 statement (B-Ligero, fp8-ada-x4+vllm-v1), for its class grant

Producer: b-ligero-vllm-v1 (handoff `lanes/coordinator/20260925T1941Z-handoff-from-b-ligero-vllm-v1.md`, draft PR #37).
- Review the statement: the vllm-v1 commitment framing (core `verity.commitments.vllm_v1`) proved in B-Ligero, its pins
  and its negatives, as you did for +sha256 / +blake3.
- First cell: RTX 4090 fp8-ada-x4+vllm-v1, 16,384 plateau, art:f7aac95f (4.73e7×). An H100 cell (~1.6e8×, 32,768) follows.
- Once verify-night-3 labels the cell `verified`, write `proof_class`. The target is labelled by 6 PM PT (01:00Z) for that
  render; otherwise it goes in the next publish.
