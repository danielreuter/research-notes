---
lane: merge-queue
kind: handoff
from: fixture-process (bc-dc2611ba)
to: merge-queue (bc-605d7c89, #368)
created: 2026-09-29T06:54Z
---

# Commit maps for the history rewrite: two small hooks for `research queue` (#387), and a one-line vocab conflict with #368

[#387](https://github.com/danielreuter/verity/pull/387) adds `research.commitmap` for the one history rewrite (the fixture process
plan, §4.2 and step 5). It changes nothing until Daniel accepts a `commit-map/v1`.

- **Landing:** nothing to do. `research queue land` calls `merge.gate()`, which now reads a passing `check` of an old commit for
  its image when the rewrite kept the tree, and refuses a head that holds a replaced commit.
- **Grants** (`StoreGrants.__call__`): please read the grants of every equivalent head:

  ~~~python
  from .commitmap import Maps
  heads = Maps.load(self.store).equivalent(head)          # [head, *old heads with the same tree]; just [head] with no map
  return {str(lab.value) for h in heads for lab in self.store.labels(grant_target(pr, h), key=vocab.GRANT)}
  ~~~

  A grant on the old head counts only when the tree is unchanged, the same rule as for attempts.
- **Admission:** refuse a head that brings back old history:
  `Maps.load(store).old_history(workdir, head, "origin/main")` non-empty means "move the branch with `research git remap`".
  `research git check HEAD --base origin/main` is the same check as a command.
- **Conflict:** both PRs add a verification key, #368 `grant` and #387 `commit_map`. `vocab.py` should merge cleanly (different
  lines), but `test_store_vocab.py`'s `VERIFICATION_KEYS` gets a one-line conflict for whichever lands second: keep both keys.

Which PR carries the hooks is your call. If you'd rather I add them to #387 behind a small interface, tell me which one.
