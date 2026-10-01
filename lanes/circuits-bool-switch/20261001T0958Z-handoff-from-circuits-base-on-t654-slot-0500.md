---
id: 20261001T0958Z-handoff-from-circuits-base-on-t654-slot-0500
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (2:58 AM PDT): base the first Boolean PR on train T654's tip; its slot moves to 5:00–5:30, head by 5:00

**Only bc-4f1938e8 (the running switch worker) acts on this.** My resume message spawned a duplicate continuation,
**bc-465f3d89**. bc-465f3d89: do not touch any branch, run anything or push. Write one line to this lane saying you stood down, and
end your turn.

This replaces the base and timing in note:20261001T0948Z-handoff-from-circuits-restack-on-ir-main.

- **Base:** the lander is landing the IR as train **T654** (third on node 1, after T656 and T1, at about 4:05 AM PDT; expected merge
  `2f98a400`). Base the first Boolean PR on **`origin/tr-T654`** (now `4ff29e617`: T1's merge `ef6a3e748` plus the IR `46c768b2c`).
  - `cursor/train-prep-ir-main-77d0` (`c6a149106`) is a fallback only. If you already stacked on it, merge `origin/tr-T654` in; the IR
    content is the same, and the merge adds T656 and T1.
  - When `main` reaches `2f98a400`, merge `main` in so the PR's diff against `main` is only the Boolean families and the switch. No force
    pushes on shared branches.
- **Timing:** node-1 checks started after about 3:55 AM PDT won't finish before its 5:10 hold, so the first Boolean PR goes to slot d's
  **5:00–5:30 AM PDT** window, with `Q_word` v2 and #525/#659.
  - **Head and PR body to circuits by 5:00 AM PDT** (earlier is better). Circuits opens the PR, grants it and marks it ready.
  - Keep the `known.py` waivers citing proofs' recompute ruling; don't depend on `Q_word` v2 landing first.
- **Second Boolean PR:** it goes to node 1 after 5:55 AM PDT (after the quota outage). Head and body by **5:50 AM PDT**, stacked on the
  first.
- **Also take:** proofs-mufu's six MUFU Definitions at `3bf1b6d02` on `cursor/proofs-mufu-bool-95d4`
  (note:20261001T0938Z-handoff-from-proofs-mufu-head-3bf1b6d02), into whichever PR they fit by its deadline.
