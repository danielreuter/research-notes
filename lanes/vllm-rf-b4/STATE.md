---
id: vllm-rf-b4/state
lane: vllm-rf-b4
kind: state
updated: 2026-09-25T08:25Z
---
# b4 (engine and hooks): state

Coordinator: vLLM coordinator bc-ba6cec03. Agent: bc-95aa165d. Worktree `~/projects/verity-wt/rf-b4`, branch
`lane/vllm-rf-b4`. **a4 base: 10996616.** Budget $25 of pod spend.

## Scope (SYNTHESIS §6 B4, behavior-preserving part of D12)
- `engine/` builds vLLM from the pinned record; `engine/env.py` is the only writer of vLLM env pins, at construction.
- `engine/hooks.py` owns every vLLM/torch patch (FA taps, Triton hook, collective hooks, observer install, setattr on
  vLLM/torch objects); each hook uninstalls; a test shows uninstall restores the originals.
- P9 `runtime-patch` allowlist entries cleared as sites move.
- Engine build entry point signature stays stable (a5 builds `verity_vllm.LLM` on it).
- No identity changes (C3's).

## Done
- (none yet)

## Running
- (nothing)

## Next
1. Survey patch sites (rg + P9 runtime-patch allowlist) and env-pin writers.

## Open questions
- none

## Found, not fixed
- none
