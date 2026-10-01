---
id: 20261001T0715Z-handoff-from-circuits-zero-prs
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: Daniel's new goal (12:11 AM PDT): zero open PRs at 7:50 AM PDT. Every circuits PR lands or closes, with its branch kept

- **The Boolean integration PR** must LAND by 7:50 AM. Open it by **5:00 AM PDT** with every family that's green by then, rebased on main
  once proofs-ir's IR PR lands, and tell circuits the number and head so it can grant and mark it ready. Families that turn green after
  5:00 stay on their branches for the next train. Don't block the PR on them.

- **Landing path:** circuits marks a PR ready and grants vLLM changes. The PR captain's trains need roughly 1–2 h from ready to landed, so
  "ready" means ready at a head that passes its tests.
- Don't open a PR that can't land by 7:50. Anything not ready by your deadline stays on its branch, and you list it in your final message
  for circuits' backlog.
