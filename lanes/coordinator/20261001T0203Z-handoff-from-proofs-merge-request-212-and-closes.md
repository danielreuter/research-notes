---
id: 20261001T0203Z-handoff-from-proofs-merge-request-212-and-closes
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# For the next train: #212 on its own. Proofs has already closed #279, #308, #313 and #441, so skip them in your sweep

to: old-circuits-and-proofs (bc-8ece7cde), the train runner. This follows the top-level's PR hygiene audit
(`docs/pr-hygiene.md`) and Daniel's 7:01 PM PDT ruling: a PR's owner closes it without asking once another PR has replaced
it, with a one-line comment naming the replacement, and keeps the branch.

- **Merge request: [#212](https://github.com/danielreuter/verity/pull/212)**, `cursor/sweep-counts-866f` @ `af560de9e`,
  the backend sweep re-aggregation (per-shape row counts).
  - It's ready, and it merges cleanly with `origin/main`: 5 files and +170/−33, all under `backends/flock/`. So the train's
    `check` needs `lean-agreement`.
  - #554 and #601 carry its changes. Landing it on its own takes them out of their diffs.
- **Already closed by proofs** (comment, branch kept), so drop them from your list of 16 superseded PRs and from the sweep:
  - #279, replaced by #225;
  - #308, replaced by #282;
  - #313, the Rust mirror of #308, also replaced by #282;
  - #441, whose head landed through #430.
- **Closed when #630 opened:** #487, #515, #502 and #523. #630 carries their heads, and
  `note:20261001T0203Z-handoff-from-proofs-merge-request-630-fp-defs` is its merge request.
- **#554's base is now `infra/nebius`.** It is built on #496, so its diff no longer shows #485's commits: 23 files against
  `infra/nebius`, down from 232 commits against main. When #496 lands, I'll retarget it to main.
- **#601 stays on `main`.** It merged main after `infra/nebius`, so against `infra/nebius` its diff would be larger. It's not
  for merge until infra calls priority 1 settled, and it shrinks when #496 and #212 land.
