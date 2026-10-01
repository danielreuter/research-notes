---
id: 20261001T0715Z-handoff-from-circuits-zero-prs
campaign: verity
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: Daniel's new goal (12:11 AM PDT): zero open PRs at 7:50 AM PDT. Every circuits PR lands or closes, with its branch kept

- **#565, #566, #582** (FP8 and NVFP4 vLLM linears): rebased on main with tests green and circuit-check reports by **4:30 AM PDT**, then
  tell circuits the heads in `lanes/circuits/`. Circuits closes any that aren't ready at 4:50 AM PDT (branches kept). Boolean IR is circuits'
  first priority tonight, so don't take time from it.

- **Landing path:** circuits marks a PR ready and grants vLLM changes. The PR captain's trains need roughly 1–2 h from ready to landed, so
  "ready" means ready at a head that passes its tests.
- Don't open a PR that can't land by 7:50. Anything not ready by your deadline stays on its branch, and you list it in your final message
  for circuits' backlog.
