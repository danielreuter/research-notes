---
id: 20260930T2126Z-handoff-from-kueue-fold-node2-builds-failed-and-requeued
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# Your 6 node-2 Builds failed at bootstrap; I fixed the cause and requeued them. Don't resubmit them.

`cov-g058`, `cov-g069`, `cov-g080`, `cov-g125`, `cov-n061` and `cov-n062` failed on node 2 between 1:54 and 1:59 PM PDT with
`BOOTSTRAP_FAIL_CHECKPOINT`. That was `n2_build.sh`'s bug, not yours: `manifests/checkpoints.json` pins every checkpoint under
`/workspace/hf`, which on node 2 is PoUW's cache, and `submit` had copied the weights as dangling links.

Fixed on `infra/nebius` (fa07d653c): the weights are copied, and the Build sees them at `/workspace/hf` in a private mount namespace.
`cov-g019` passed its bootstrap with the fix (run r20260930-212356-b1d3). Your 6 are requeued as `verity-build-<key>-r1`, and their Commits
come back under your original keys (`n2-build/cov-g058` and so on).

Node 1's held Builds now move to node 2 on their own (`n2_build.sh offload --loop`), so hand-submitting is no longer needed.
