---
id: vllm-rf-a4/state
lane: vllm-rf-a4
kind: state
updated: 2026-09-25T06:05Z
---
# a4 (re-home into the §5.1 tree): state

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-a4`, branch
`lane/vllm-rf-a4`, base `8efb918e` (f1 head; f1 not merged into origin/main `2994bd25` as of 06:04Z).

## Done
- 06:05Z: read brief, SYNTHESIS §4-6, lint `_imports.py` / `test_p09_layering.py` / `_ratchet.py`.

## Running
- nothing

## Next
1. Build the full move map (SYNTHESIS 5.1/5.2) as a script over the source (no import of verity_vllm).
2. Commit per destination package; push after each.
3. Pods: lints, gate (b) head vs base same pod, gate (a) T0+T1 on cpu3m 512 GB, GPU smoke #101 on 1x L40S.

## Open questions
- none yet

## Found, not fixed
- none yet
