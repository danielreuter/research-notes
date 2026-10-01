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

A third path, found at 06:33Z, affects queued jobs too. `research run --queue` jobs get `taskset -c 96-191` from the cluster
executor, for example `r20261001-061301-c862` (an 8-CPU vLLM pytest that runs `manifest build-global` workers, 3600 s timeout).
This happens because `tools/cluster/descriptions/nebius.toml` (on `main` and on `infra/nebius`) declares only
`pools = { checks = "8-95" }` for vy-nebius-1. `plan.allowed_cpus` then gives any job that names no pool 96-191. The
dispatcher reserves 128-175 for `provers` (`VY_PROVER_CPUS`) and gives its own other work 96-127 and 176-191, but the
description doesn't know that.

**Ask:**

1. Get `84fb8a7b` and `259acc56` onto `main` (nebius-infra's, through the root coordinator).
2. Add `provers = "128-175"` to vy-nebius-1's `pools` in `nebius.toml`, so a queued job that names no pool gets 96-127 and
   176-191.

Until then, ask lanes not to launch direct or queued runs on node 1 outside a pinned slot. Meanwhile I re-run each point once the slices are quiet, and report only clean
ones. Details: `note:proofs-flock-fp/20261001T0557Z-friction-direct-runs-unpinned-from-main`.
