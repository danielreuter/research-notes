---
id: vllm-rf-b5vb/state
lane: vllm-rf-b5vb
kind: state
created: 2026-09-25T14:40Z
updated: 2026-09-25T14:40Z
---
# vllm-rf-b5vb: split program/frontend/rules/vllm_bindings.py into a package (B5) (state)

base: 33e4d8d1

- Coordinator: vLLM coordinator (Cursor agent bc-ba6cec03). Briefs: `../vllm-refactor/WAVE2_BRIEF.md`, `LANE_BRIEF.md`.
- Worktree: `~/projects/verity-wt/rf-b5vb`, branch `lane/vllm-rf-b5vb` (pushed at `33e4d8d1`).
- Budget: $18 of pod spend. vyv- deadline 2026-09-25T18:30Z (extended in steps by the coordinator).
- Scope: `integrations/vllm/verity_vllm/program/frontend/rules/vllm_bindings.py` (1,905 lines) -> package
  `rules/vllm_bindings/`, one module per rule family + pins/targets + observation state; `__init__` re-exports exactly
  the names importers use; verbatim moves (AST/source check); `VLLM_BINDING_RULES` order identical; lints re-keyed, no
  allowlist growth.

## Done
- 14:40Z worktree + branch at `33e4d8d1`, pushed.

## Running
- (none)

## Next
- Read the module, its importers, tests that monkeypatch it, and its allowlist entries; design the split.

## Open questions
- (none)

## Found, not fixed
- (none)
