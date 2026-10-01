---
id: 20261001T0714Z-handoff-from-compute-accounting
campaign: verity
lane: pouw-served
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c62f9726 (pouw-served): zero open PRs at 7:50 AM PDT. Land #610 first; the hill-climb works on a branch

From compute accounting, 12:15 AM PDT. Daniel's new goal: none of our PRs is open at 7:50 AM PDT. Each one either lands
through the PR captain's trains, or is closed with its branch kept and its contents listed in the backlog. Don't open a PR
that can't land by 7:50 AM.

1. **Land #610 now,** as window 8's code. Merge `main` into #610 in place, record one `check`, and send the captain a ready note.
   Retarget #610 to `main` (ask me in `lanes/accounting`, since I hold the PR tool). Then close #593 as contained, if #610
   carries its trims port `30879486`, with a comment and the branch kept.
2. **The overnight hill-climb** (whole-step graphs, the hashing host-overhead cut, `-h3`) runs on a fresh branch from `main`
   after #610 lands, with no PR.
   - If it has a passing `check` and a verified window by about 6:30 AM PDT, I open a PR and it goes into the last train before
     7:50.
   - Otherwise the branch stays as it is, and its contents go into the backlog.
3. **The 70B work** stays on a branch too, with no PR tonight.
