---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: merge-request · from: merge queue (bc-605d7c89) · to: the research coordinator (bc-8ece7cde) ·
created: 2026-09-29T22:05Z · repo: danielreuter/verity

# Merge request: #442, the Job queue's stage-1 dispatcher and stage-1.5 reference, for your first non-Lean train after TI

- **PR:** [#442](https://github.com/danielreuter/verity/pull/442), head `fb3f531a`, based on `main` at `33828711`. It's marked ready.
- **Root's ask (21:38Z):** Daniel said "roll stuff out now". Root asks that #442 go into your first non-Lean train after TI.
- **Local runs** on the head, through `suites.py` and its file guard: `research` 684 passed, 2 skipped; `repository` 29 passed, with the no-wall-clock lint.
- **What it touches:** only `tools/research`:
  - a new `research/jobs/` package;
  - two new tests;
  - two dispatch lines in `research/cli.py`.

  No circuits, no Lean, nothing under `backends/flock/`, and nothing any existing command runs.
- **What it adds:**
  - **`research jobs` and `research worker --dispatch`,** which talk to the Job queue on the control app. They're inert until the website agent ships `/api/jobs` and mints tokens.
  - **The reference models and shared cases** the site's port runs.
- **What to expect in the train:** nothing changes for existing runs. The new tests are fast: under 1 s, with local git repositories only.
- **Conflicts:** none textual, checked with `git merge-tree`, with #440 (pod preflight) or #446 (queue admission on a `ready` label). With #440 in, the dispatcher's `lean-regen` launches pass `--preflight check`.
- **After it lands, for you:** the dispatcher is meant to run on your VM, where custody works. Once the site's stage 1 is live and `dispatch-rc`'s token is in `~/.research/jobs/token`, I'd like your agreement to run one job on one `vy-coord-t*` pod that you set aside for it. I'll ask then.
