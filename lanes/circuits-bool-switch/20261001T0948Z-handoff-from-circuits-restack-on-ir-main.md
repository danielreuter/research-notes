---
id: 20261001T0948Z-handoff-from-circuits-restack-on-ir-main
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits, URGENT (2:48 AM PDT): re-stack the first Boolean PR on `cursor/train-prep-ir-main-77d0`, not `cursor/train-prep-ir-77d0`

- Train T496R failed. The old IR prep branch `cursor/train-prep-ir-77d0` (`25d54031c`) contained #496, so it's dead.
- The IR is now rebuilt alone on main as **`cursor/train-prep-ir-main-77d0`** (main `6c566874` plus proofs-ir `46c768b2c`). It's checking on
  node 1 now and on slot d at 3:30.
- Base your first Boolean PR's branch on it: merge or rebase onto `origin/cursor/train-prep-ir-main-77d0` (no force on shared branches), so
  the PR's diff against that base is only the Boolean families and the switch.
- If you already built on `train-prep-ir-77d0`, drop #496's content: nothing of #496 may be in the PR.
- **Timing is unchanged:** PR body and head to circuits by 3:30 AM PDT, and circuits opens the PR by about 3:40 for the 3:30–4:00 window.
