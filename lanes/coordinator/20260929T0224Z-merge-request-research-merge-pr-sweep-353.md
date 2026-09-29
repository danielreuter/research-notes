---
cursor:
  subagentId: "bc-b1290f5f-21ce-5207-b811-f3da5ada70e3"
lane: coordinator
kind: merge-request
from: open-pr-census (bc-b1290f5f), for verity-root
to: research coordinator (bc-8ece7cde)
cc: verity-root
created: 2026-09-29T02:24Z
repo: danielreuter/verity
---

# Merge request: #353, `research merge` closes the PRs that landed and retargets their children (first train)

- **The PR:** [#353](https://github.com/danielreuter/verity/pull/353), branch `cursor/merge-closes-landed-prs-70e3`, head
  `45c7f557fece4bc6a72c7eb5a522c288c23bd0a5`, on `main` `b4fd93e9`. It is ready, not a draft.
- **Order:** the first train, as verity-root asked. It speeds up merges by keeping landed PRs off the open list.
- **What it changes:** only `tools/research` (`merge.py`, one new test file, the README).
  - After a merge or a train lands, `research merge` fetches the remote's `--into` branch. It then closes every open PR whose
    head is on it, with the comment `Merged into main at <sha12> (<merge subject>).`, and retargets onto `main` every open PR
    whose base branch's tip is on it.
  - `research merge --sweep [--dry-run]` runs the same sweep on its own.
  - It is idempotent. GitHub is read and written through `gh`.
- **What changes in your routine:** `research merge` doesn't push, so the sweep only acts on what `origin/main` already
  holds. Right after a local merge, it closes nothing new and says "push it". After `git push origin main`, run
  `research merge --sweep` (after `--dry-run` if you want to see the list first). That closes what the merge landed. After
  #345 lands, that is the 15 stacked PRs it carries.
- **If `gh` or the network fails,** the sweep is reported on stderr and the merge's exit code is unchanged. Without an
  `origin` remote, the sweep is skipped.
- **Tests:** a bare repository in tmp stands in for `origin`, and a fake `gh` for GitHub, so nothing reaches the network.
  There are no sleeps and no clock reads.
  - `test_merge_sweep.py` and `test_merge_gate.py`: 12 passed.
  - All of `tools/research/tests`: 483 passed, 2 skipped (pytest -n 4, on this VM).
- **Check:** not recorded; this VM has no evidence store. Please record `check` on `45c7f557` in the train. The change
  touches no circuit, Lean file or `backends/flock/`, so no agreement inputs are needed.
- **Already done by hand for the census:** the 22 PRs already on `main` are closed, each with a one-line comment naming its
  merge commit (train H `432edb3b`, train XD `4b75ba16`, train V `a8e72c81`). The 21 PRs that #345 supersedes stay open
  until it merges. See `docs/open-pr-census.md`.
