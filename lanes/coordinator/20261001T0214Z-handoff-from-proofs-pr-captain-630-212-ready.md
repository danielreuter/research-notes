---
id: 20261001T0214Z-handoff-from-proofs-pr-captain-630-212-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# For the PR captain: verity #630 and #212 are ready (proofs)

From proofs, 7:14 PM PDT.

- **Ready:** [verity #630](https://github.com/danielreuter/verity/pull/630) (`cursor/proofs-fp-defs-95d4` @ `90a988c1d`): the sm_120
  FP8 / FP4 step Definitions, their GemmCoordinates and the C-Flock pieces. `circuit-check --all` is in its body (1,154 targets,
  0 new failures). It touches `backends/flock/`, so its train's `check` needs `lean-agreement`. Details:
  `note:20261001T0203Z-handoff-from-proofs-merge-request-630-fp-defs`.
- **Ready:** [verity #212](https://github.com/danielreuter/verity/pull/212) (`cursor/sweep-counts-866f`), on its own. #554 carries
  13 of its 14 commits, so landing it shrinks #554. Details: `note:20261001T0203Z-handoff-from-proofs-merge-request-212-and-closes`.
- **Proofs' open PRs:** 10 after closing 7 records at 7:13 PM PDT (#97, #143, #168, #261, #414, #429, #601, branches kept), and
  8 once these two land.
