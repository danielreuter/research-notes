---
id: 20260930T2250Z-handoff-from-infra-merge-608-607
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# Merge requests: #608, a `question` vocab key (small, unblocks every lane's labels), and #607, the env/printenv secret guard

1. **#608**, `cursor/vocab-question-label-558b` @ `ca23caae5`: adds `question` to the store vocabulary, plus its pinned test.
   Every lane is using `--off-vocab` for it tonight under Daniel's rule. It touches `tools/research` only. `test_store_vocab.py` passes.
2. **#607**, `cursor/env-guard-558b` @ `183fd66ca` (draft until checked): `tools/agent-guard/`, redacting `env`/`printenv`. It
   answers the fourth Nebius key leak. It's a new directory, and no existing code changes.

Please put both in the next train after #449. Each needs a recorded `check`.
