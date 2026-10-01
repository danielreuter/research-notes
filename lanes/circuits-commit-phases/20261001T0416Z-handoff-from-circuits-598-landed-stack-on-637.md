---
id: 20261001T0416Z-handoff-from-circuits-598-landed-stack-on-637
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: #598 and #599 landed on main (T4B, 9:12 PM PDT, at `618d6a01`). Stack your branch on #637, not on #598

- The train took #598 at `618d6a01`. Its last commit, `3875376bd` (slim bundles opt-in), goes to main through **#637**
  (`cursor/replay-slim-opt-in-8c79` @ `0b828ab41`, cherry-picked onto main `923b5acb`). #637 is granted and ready. #598 is closed, and
  its branch stays as it is.
- **Rebase `cursor/commit-gpu-phases-8c79` onto `origin/cursor/replay-slim-opt-in-8c79`.** That is main plus the slim opt-in, so your PR's
  diff is only your own work. Once #637 lands, rebase onto main.
- Nothing else changes: fixes 1 and 2, the advisor's no-draw-before-root constraint, the perturbation row, and the folded token-budget
  commit `b642a4a4b`.
