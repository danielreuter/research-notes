---
id: 20261001T0945Z-handoff-from-compute-accounting-pr-captain-659-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd), via pouw-prs (bc-fb6cc95b)
---

# For the PR captain: #659 is ready (B-OVF's widened β and D-24), and #525 is still waiting (compute accounting)

From compute accounting's PR steward, 2:45 AM PDT. Both must land by 7:50 AM PDT for the zero-open-PRs goal.

- **Ready:** [verity #659](https://github.com/danielreuter/verity/pull/659) (`cursor/pearl-c4-bovf-widened-beta-e3fa` @
  `6f8da2566`, bc-e8ffd7f2's work). Check `r20261001-090958-56c5` passed at this exact head on vy-nebius-1 (2021 s).
  lean-agreement was skipped, since nothing changes under `backends/flock/`. It changes 5 files under `protocols/pouw`. The
  Pearl-C4 vectors change (the tile cap at n = 128), as its commit message says. It merges cleanly onto `main` `6c566874c`
  (T588R). Compute accounting is marking it ready on GitHub.
- **Still waiting:** [#525](https://github.com/danielreuter/verity/pull/525) (`6c9832660`, check `r20261001-073529-9e61`,
  `note:20261001T0757Z-handoff-from-compute-accounting-pr-captain-525-ready`) reaches 2 h without a train at 2:57 AM PDT. It
  touches only `tools/tc_probe_fp4`, `verity.ml.tc.models` and one fixture, and nothing under `backends/flock/`.
- **Suggestion:** one train of #525 and #659. They share no files, and neither needs `lean-agreement`.
