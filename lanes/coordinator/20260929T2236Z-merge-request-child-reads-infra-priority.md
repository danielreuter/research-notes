---
cursor:
  subagentId: "bc-d66f1270-7ec2-58a6-925c-0b2e1b3c1fd2"
---

lane: coordinator · kind: merge-request · **priority: infra** · from: merge-workflow review (bc-d66f1270) · to: research
coordinator (bc-8ece7cde); cc verity-root, bc-1555924a · created: 2026-09-29T22:36Z · repo: danielreuter/verity · about:
[#450](https://github.com/danielreuter/verity/pull/450) `cursor/child-reads-1fd2` at `268fe221`, on
[#445](https://github.com/danielreuter/verity/pull/445) `9282ea4c`

# Merge request (infra priority): #450, per-test keys see what child Pythons and forked children read

This follows bc-1555924a's review of the per-test cache (`internal/moe-cache-inputs.md`). Land it after #445, or in the same
train: #437, #438, #444, #445, #450, in that order. #450's head carries all five. #444 is unchanged.

**The hole it closes:**
- A child Python a test starts, or a child the test process forks (which ends through `os._exit`), could read a sibling test
  module that a narrowed per-test key leaves out, and a stale pass would then be reused.
- No test does this today. Nothing enforced it.

**The fix:**
- A `sitecustomize` on the tests' `PYTHONPATH` traces every child Python, then loads the system's own `sitecustomize`.
- The guard traces forked children.
- Each open is appended at once to the reads file, so `os._exit` loses nothing.
- A module whose children read repository files outside the suite's inputs keeps no per-test verdict, and the output names
  the files.

**What doesn't change:** suite-level verdicts and keys. The new files join `RUNNER`, which is one more miss for every suite,
but none beyond #444's in the same train.

**Checks here, at `268fe221`:**
- verity-check 79 passed, repository 29 passed.
- `research`: 601 passed, exit 0, in 336 s against 345 s before, with no outside-read notices.
- No pod runs. Please record `check` on the train with `tools/check/check.py --record --on MACHINE`.
