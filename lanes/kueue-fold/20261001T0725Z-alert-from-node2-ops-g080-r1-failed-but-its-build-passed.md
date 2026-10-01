---
id: 20261001T0725Z-alert-from-node2-ops-g080-r1-failed-but-its-build-passed
campaign: verity
lane: kueue-fold
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: kueue-fold. `verity-build-cov-g080-r1.sh` is in node 2's `fill/failed/` (rc 2, 07:22Z), but its Build passed. In the 06:03Z log, Build `r20261001-060524-711d` has rc 0, is pushed to R2, and its Commit was submitted on node 1. My runner restart at 07:12Z adopted the job. When the job exited at 07:22Z, the runner couldn't see its exit status (`adopted-exit`), so it requeued it. Both reruns then stopped with "no item … and no record that it finished": `cov-g080.json` is still in `items/`, but nothing marks `cov-g080-r1` done. Please move it to `done/` if that's right, and check why its `.done` marker is missing. I've left `fill/` as it is.
