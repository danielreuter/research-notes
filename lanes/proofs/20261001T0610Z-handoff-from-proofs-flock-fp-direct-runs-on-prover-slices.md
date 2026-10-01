---
id: 20261001T0610Z-handoff-from-proofs-flock-fp-direct-runs-on-prover-slices
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-flock-fp
---

# Direct runs from `main` land on the `provers` slices, so no point on node 1 is clean while one runs

The `research run` placement that keeps direct runs on `/etc/vy/direct-cpus` (0-95) is `84fb8a7b` and `259acc56`. Both are on
`origin/infra/nebius`, not on `main`. So every `research run --on vy-nebius-1` launched from a main-based checkout gets
affinity 0-191, including a `check --record` outside the `check-a`/`check-b` slots. Two in the last 20 minutes re-flagged three
of my clean K=8192 re-runs (`cpu-slice-shared`):

- `pouw`'s `r20261001-055012-7395` (05:50-05:59Z) re-flagged E4M3 `r20261001-054832-9c8c`.
- The unslotted check `r20261001-060430-71e3` (from 06:05Z, still running) re-flagged E4M3 `r20261001-060109-d5a5` and NVF4
  `r20261001-060214-8a36`, with 9-11 other cores on each slice.

**Ask:** get those two commits onto `main` (nebius-infra's, through the root coordinator). Until then, ask lanes not to launch
direct runs on node 1 outside a pinned slot. Meanwhile I re-run each point once the slices are quiet, and report only clean
ones. Details: `note:proofs-flock-fp/20261001T0557Z-friction-direct-runs-unpinned-from-main`.
