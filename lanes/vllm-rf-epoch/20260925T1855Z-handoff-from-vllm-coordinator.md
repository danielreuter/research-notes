---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T18:55Z
---
# Epoch item 7 (root decision): `research_tools.CLOSURE` misses `verity/evaluation/**`

`harness/research_tools.py` (the code closure the research store hashes into tool ids and cache keys) doesn't include
core `packages/verity/src/verity/evaluation/**`, so a change to the evaluator doesn't move the key. gc found it. The
fix changes store keys, so it goes in the epoch: its own `epoch:` commit, with before and after closure digests in
READY.md.
- Check whether any other core package the integration imports is missing (for example `verity/commitments/**`;
  SYNTHESIS D5 already flagged `core/commitments`). Add the ones actually imported.
- If the recorded rows carry the tool id or closure digest in a checked field, this has to be in the recording tree;
  otherwise note that it's key-only.
