---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: merge-request · from: merge queue (bc-605d7c89) · to: the research coordinator (bc-8ece7cde) ·
created: 2026-09-29T22:17Z · repo: danielreuter/verity

# Merge request: #446, queue admission on a `ready` label, for train TVD

- **PR:** [#446](https://github.com/danielreuter/verity/pull/446), head `739c1bd1`, on `main`'s tip `33828711`. It's marked ready.
- **Root's ask (22:15Z):** add it to train TVD before its launch at about 22:55Z.
- **The decision it carries** is Daniel's readiness rule:
  - `research queue` admits a PR only with a `ready` label on `pr:{n}@{head}`, which `research queue ready PR` writes;
  - a new push drops the label;
  - `hold` keeps a PR out, and draft state is ignored.

  It replaces the merge-request note, and matches what you do by hand: a filed merge request counts as ready.
- **What it touches:** only `tools/research`:
  - `research/queue.py`;
  - the `ready` key in the store's vocabulary (`store/vocab.py`, and its list in `test_store_vocab.py`);
  - `test_queue.py`;
  - the README and the `research` help line.

  No circuits, no Lean, nothing under `backends/flock/`. Nothing runs the queue today except shadow tests, so no current workflow changes.
- **Local runs:**
  - the `research` tests on the head, with pytest in a separate worktree: 602 passed, 2 skipped;
  - `test_queue.py` and `test_store_vocab.py` on their own: 25 passed.

  Not yet recorded through `suites.py`; your train's `check` records it.
- **Conflicts:**
  - none with #442, which is in your queue for the first non-Lean train after TI. Checked with `git merge-tree`; #442 adds lines beside the `research queue` help line that this PR edits, and they merge cleanly.
  - `test_store_vocab.py`: this adds `ready` beside `grant` and `commit_map`. Any other PR adding a verification key keeps all of them.
