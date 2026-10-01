---
id: 20261001T0715Z-handoff-from-circuits-zero-prs
campaign: verity
lane: circuits-replay-keep-leaves
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: Daniel's new goal (12:11 AM PDT): zero open PRs at 7:50 AM PDT. Every circuits PR lands or closes, with its branch kept

- **Your main-side PR (replay keeps touched leaves):** ready, with tests green, by **3:00 AM PDT**. Ask circuits, then open it. The grid
  tree's copy isn't a PR, so it's unaffected.

- **Landing path:** circuits marks a PR ready and grants vLLM changes. The PR captain's trains need roughly 1–2 h from ready to landed, so
  "ready" means ready at a head that passes its tests.
- Don't open a PR that can't land by 7:50. Anything not ready by your deadline stays on its branch, and you list it in your final message
  for circuits' backlog.
