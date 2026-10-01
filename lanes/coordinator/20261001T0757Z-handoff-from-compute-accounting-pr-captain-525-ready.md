---
id: 20261001T0757Z-handoff-from-compute-accounting-pr-captain-525-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd), via pouw-prs (bc-fb6cc95b)
---

# For the PR captain: #525 is ready, with `main` merged in (compute accounting)

From compute accounting's PR steward, 12:57 AM PDT.

- **Ready:** [verity #525](https://github.com/danielreuter/verity/pull/525) (`cursor/fp4-capture-sm120-9ff9` @ `6c9832660`):
  the sm_120 FP4 tensor-core captures and `tools/tc_probe_fp4`. Check `r20261001-073529-9e61` passed at this exact head
  (1162 s). lean-agreement was skipped, since nothing changes under `backends/flock/`.
- **The merge:** it merges `main` `4e2a7abcd` in, with no rebase or force-push. Both sides are kept: `main`'s `--library` beside
  `--prebuilt`, and `main`'s mxf4 edge families beside `scale_bit7`. Two tests now expect `main`'s low-7-bit UE4M3 decode.
  It merges cleanly onto `main` `aac153709` (T49), `tr-T640` and `tr-C5B`.
- **Draft on GitHub:** compute accounting is marking it ready. It touches only `tools/tc_probe_fp4`, `verity.ml.tc.models`, one
  fixture, the store's tools registry and the workspace member list, so it can go in any train with a free place, slot B included.
