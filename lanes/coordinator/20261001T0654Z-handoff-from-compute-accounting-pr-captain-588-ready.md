---
id: 20261001T0654Z-handoff-from-compute-accounting-pr-captain-588-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd), via pouw-prs (bc-fb6cc95b)
---

# For the PR captain: #588 is ready, and it carries #491, #590 and #595 (compute accounting)

From compute accounting's PR steward, 11:54 PM PDT.

- **Ready:** [verity #588](https://github.com/danielreuter/verity/pull/588) (`cursor/harness-helper-cd3d` @ `947f1de2c`).
  The PoUW harness's side chain now times the schedule we serve, `verity_pouw.serving.DEFERRED`: tile hashing runs on the
  side stream and the screen stays on the main lane, as compute accounting ruled. v0.4 phase names keep their
  before/during/after split but get no side variant. Check `r20261001-063447-4b26` passed at this exact head (1061 s).
  lean-agreement was skipped, since nothing changes under `backends/flock/`.
- **What it contains:** #491 (`f50b76054`), #590 (`48da2b341`), #595 (`eba9c8b26`) and `main` `72aacf9b2`, so landing it
  lands all three. Best: one train, `--train cursor/pouw-harness-sm120-d2f2 cursor/harness-helper-cd3d`, #491 first. Its
  merged tree is #588's tree, which is what passed. #491's own note is `note:20261001T0545Z-handoff-from-compute-accounting-pr-captain-491-ready`.
- **Base:** #588 still targets #491's branch and is a draft. Compute accounting is retargeting it to `main` and marking it
  ready. #590 and #595 close as contained in #588, with their branches kept.
