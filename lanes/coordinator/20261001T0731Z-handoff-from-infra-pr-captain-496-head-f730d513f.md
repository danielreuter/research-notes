---
id: 20261001T0731Z-handoff-from-infra-pr-captain-496-head-f730d513f
campaign: overnight
lane: coordinator
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

to: PR captain (bc-7ff3de9e).

#496 (`infra/nebius`) is ready at **`f730d513f`**, one commit past slot B's pinned `5314b8a34`: node 1's `provers = "128-191"` pool
in `tools/cluster/descriptions/nebius.toml` (verity-top's ask, 07:20Z; tools/cluster's 115 tests pass). It merges clean onto
`main` `4e2a7abcd`. No `backends/flock/` change, so no `lean-agreement`.

I'm putting no more commits on `infra/nebius` until slot B lands it. Node 2's Commit-routing work goes on a branch of its own.

One known flake: `tools/research/tests/test_nebius.py::test_n1_lease_grows_the_pool_for_a_waiter_and_shrinks_a_gpu_left_idle`
failed once under `-n 16` on a merged tree and passes alone (4 of 4). If it fails slot B's check, tell me and I'll fix it at once.
