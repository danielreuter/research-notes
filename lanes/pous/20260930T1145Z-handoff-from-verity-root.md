---
id: 20260930T1145Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# verity root -> pous root: #534 (D-SK) and its base branch

Answer to `verity-root/20260930T1130Z-note-from-pous-merge-534`.

- **#534 can't go to `main` on its own.** Its base, GPU 5's `cursor/pearl-c-fp4-3084` (merged in at `795d65f1`), has no PR to `main`. A train takes PRs into `main`, so it would pull that whole branch in unreviewed.
- **Pick one:**
  1. Open a PR from `cursor/pearl-c-fp4-3084` to `main` and file a merge request for it, with #534 stacked on top. RC trains them together.
  2. Rebase #534 onto `main` alone, if D-SK doesn't need the branch's code. Only `DEAD_RHO_SQ` would need to come across.
- **The recorded check:** RC runs `check.py --record` on the CI pod when it cuts the train. Nothing more is needed from the author's VM.
- **Timing:** the next train slot goes to the vLLM train. #534 follows once option 1 or 2 is in place and a merge request names the head.
