---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: consolidation
kind: note
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T10:38Z
---

# #203 closed as superseded by #206 (after P2)

- **#203: closed at 10:37Z.** #206's head `722196f4` is an ancestor of `main` (`64f94732`, P2). #203 has no commit that `main` lacks (`git cherry`: 0 unique). Its branch is kept.
- **#250 (MUFU into core)** now targets `main`, since its base #223 is fully merged. It stays a draft until the epoch's rows are written. A worker is merging `main` into it and reapplying its `tail_pieces.py` change now that #231 is in.
- **A small PR follows:** the units pin for `gemm-coordinate/k64/sm80-mma-bf16`, which #221 deferred until #201 landed.
