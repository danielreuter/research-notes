---
id: vllm-rf-c1/state
lane: vllm-rf-c1
kind: state
agent: bc-9eae5bc7 (Cursor), coordinator bc-ba6cec03
created: 2026-09-25T06:52Z
updated: 2026-09-25T06:52Z
---
# vllm-rf-c1: C1, commitment scheme vllm-v1 (named-scheme form)

Deadline for vyv- pods: 2026-09-25T09:00Z (coordinator extends). Budget: $35 pod spend.

## Status
- Phase 1 (evidence only, no repo commits): started 06:52Z.
  - PR #15 (`fa9c4594`) is in `origin/main` (`00ffe398`, "Merge #15"). A4 (`lane/vllm-rf-a4`) is not yet in main.
- Phase 2: waiting for A4 in main.

## Phase 1 plan
1. CUDA SHA-256 copies vs `vllm-v1` vectors on 1x L40S (`vyv-rf-c1-g1`); H100 only if FA3 tap needed.
2. Weights root on a live model (SmolLM2-135M) vs core `vllm-v1` reference.

## Running
- (none yet)

## Results
- (none yet)

## Found, not fixed
- (none yet)
