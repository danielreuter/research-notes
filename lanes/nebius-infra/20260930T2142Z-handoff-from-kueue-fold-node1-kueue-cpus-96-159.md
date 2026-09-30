---
id: 20260930T2142Z-handoff-from-kueue-fold-node1-kueue-cpus-96-159
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# Node 1's Kueue tasks now run on CPUs 96–159 (from 2:42 PM PDT); Build benches go to 160–191, beside M0's

Approved by infra (2:36 PM PDT). Kueue work on 96–127 was at 83–95% busy, while 128–159 averaged 24% over 6 h.
- **The dispatcher** (`dispatch.py`, default `VY_DISPATCH_CPUS=96-159`) is committed as 02f07081d on `cursor/node1-dispatcher-cpus-9bf0`, cut from `cursor/node1-dispatcher-ffee`. It's live on node 1: the old file is `dispatch.py.bak-20260930T2145Z`, and the `node1-dispatch` loop restarted between ticks at 21:41:41Z.
  Jobs submitted before then keep 96–127.
- **Build benches** (build-optimization's `build_bench.py`, `taskset -c 128-159`) must pin to **160–191** now. They share those cores with M0's
  benches, one bench at a time, in the quiet hour or for re-measures. A bench on 128–159 would now share its cores with Builds.
- **Unchanged:** check slots 8–95, k3s 0–7, and the quiet hour.
- **Your side:** the node CPU map and any alert keyed on 96–127, if you keep one.
