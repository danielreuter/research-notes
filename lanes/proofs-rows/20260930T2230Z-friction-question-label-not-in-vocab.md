---
id: proofs-rows/20260930T2230Z-friction-question-label-not-in-vocab
lane: proofs-rows
kind: friction
status: open
---

# Daniel's "every job names its research question" rule has no `question` key in the label vocabulary

`note:20260930T2153Z-handoff-from-proofs-name-the-question` says a job carries `question: "..."` in its run meta or labels.
`research data label <run> question ...` refuses it, because `question` isn't in `tools/research/src/research/store/vocab.py`.
I wrote it with `--off-vocab` on `r20260930-220702-2e96`, and the same text in `note`, so `vocab-check` will list it under
`unknown_keys`. Every lane will hit this. The fix is a one-line `_k(QUESTION, GROUP_RESULT, TEXT, ...)` in `vocab.py`, or a
`--question` flag on `research run` that writes it into the run meta. That's a tools/research PR, which a worker lane can't open.
