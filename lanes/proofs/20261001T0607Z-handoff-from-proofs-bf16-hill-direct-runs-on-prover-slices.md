---
id: 20261001T0607Z-handoff-from-proofs-bf16-hill-direct-runs-on-prover-slices
campaign: proofs-hillclimb
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-bf16-hill (bc-89f3138c)
---

# Direct `research run`s on node 1 land on the `provers` slices and flag timed points `cpu-slice-shared`; two fixes, both infra's

to: infra; the same note is in `lanes/proofs/` (coordinator).

**What happened.** bf16-hill's clean K=16384 step-0 re-run `r20261001-054728-3dde` had its own 16-core slice (144-159), with every
process of its pod pinned to it. It still carried 2.7 cores of foreign load on that slice through its timed sessions
(05:54–05:55Z), so it is flagged `cpu-slice-shared`, and no other `provers` pod was running then. The load began at 05:50:55Z
with `r20261001-055012-7395` (pouw's `sass_inventory.py`, a direct run, 05:50–05:59Z). Busy cores across the node rose by about
22 then, and about 16/192 of them landed on the slice.

**Why.** Two direct-run paths ignore the dispatcher's split (`VY_PROVER_CPUS=128-175`, Daniel 1 Oct 01:35Z, "vLLM jobs never
run on a prover's slice"):

1. A plain `research run --on vy-nebius-1` runs on 0-191. `/etc/vy/direct-cpus` (0-95) is read only by `remote.py` on
   `infra/nebius` (`259acc56c`), which is neither on `main` nor in the package shipped to node 1 (`tool/d98f39d7698045fc`).
2. `research run --queue` gets `taskset -c 96-191` from `cluster submit`. `tools/cluster/descriptions/nebius.toml` reserves
   only `pools = { checks = "8-95" }`, so `plan.allowed_cpus` gives every other job all of 96-191. circuits-build-speed's
   vLLM builds take this path (`r20261001-055617-3f39`, and `r20261001-060202-d606`, which is running now).

**Fix (not made: infra is widening the `provers` range now).** (1) Land `259acc56c` on `main` and ship it. (2) Reserve the
`provers` CPUs in `nebius.toml` (for example `pools = { checks = "8-95", provers = "128-175" }`, or the widened range), so
`--queue` jobs get 96-127,176-191.

**Effect.** Until both land, any timed point on node 1, in either prover lane, is flagged whenever a direct run overlaps its
timed sessions, which works against the overnight goal (`…T0606Z`). bf16-hill submits only while no direct run is running and
re-runs flagged points.

For proofs-flock-fp, via proofs: `backends/flock/pod/cpu-slices.sh` at `97d6ec5ee` (branch `cursor/proofs-bf16-hill-95d4`)
pins a job's whole pod to its slice, harness and telemetry sampler included. flock-fp's pods leave those on 128-175, where
they put a small load (about 0.04 cores now, more at start-up) on the other slices.
