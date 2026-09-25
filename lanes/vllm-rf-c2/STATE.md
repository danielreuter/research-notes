---
id: vllm-rf-c2/state
lane: vllm-rf-c2
kind: state
agent: bc-568d82f4 (Cursor), coordinator bc-ba6cec03
updated: 2026-09-25T08:20Z
---
# c2 (Definition library, D8/D9, decision 3a): state

a4 base: 10996616

- Worktree `~/projects/verity-wt/rf-c2`, branch `lane/vllm-rf-c2` from `10996616`.
- Budget: $25 of pod spend.

## Commits
(none yet)

## Running
(nothing)

## Next
1. Read the registry code (integration `program/registry/`, core `verity/ml/`), map the four duplicates.
2. CPU pod: exhaustive evaluator equality for Bf16ToF32 (2^16), F32ToBf16Rn and F2fpBf16 (2^32); HopperBF16WgmmaDot16 word tests + specials + seeded random.
3. Digest-neutral commit; one-process load test; drop P1 allowlist entries.
4. Inventory; move silicon/basic Definitions core lacks.
5. Epoch commit (AmpereBF16TcDot16 v1 -> v2) at the tip, separate.

## Open questions
(none)

## Found, not fixed
(none)
