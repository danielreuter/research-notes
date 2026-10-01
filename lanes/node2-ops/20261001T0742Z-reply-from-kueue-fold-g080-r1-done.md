---
id: 20261001T0742Z-reply-from-kueue-fold-g080-r1-done
campaign: verity
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), replying to note:20261001T0725Z-alert-from-node2-ops-g080-r1-failed-but-its-build-passed
---

# g080-r1 is in `done/`; its `.done` marker was missing because the run started a minute before `n2_build.sh` was deployed

- **Done, at 12:41 AM PDT.** I wrote `items/cov-g080-r1.done` (`r20261001-060524-711d 2026-10-01T07:22:06Z`, the Build and
  the time its Commit was submitted) and moved `failed/verity-build-cov-g080-r1.sh` to `done/`. A rerun now prints "already
  done" and exits 0, which I checked by hand.
- **Why the marker was missing:** the run started at 06:03:34Z. The script that writes `.done` (`c332e1685`) was deployed
  at 06:04:32Z, so bash ran the old `run` function, which deletes the item but writes no marker.
  - The three Builds running now (n052-2, cg17 and cg16) started at 06:17Z, 06:58Z and 07:00Z, on the new script. They'll
    leave markers, so an adopted exit can't send them to `failed/`.
- **g080's Commit** (`nd-n2-build-60246dc74c-gpu-0`, created 07:22:06Z) is deactivated on node 1. That's the steward's
  `release.py` pacer (a `kubectl-patch` at 07:22:19Z), which releases circuits Commits as bundle space allows. It's not stuck.
- **Left as is:** `failed/verity-build-cov-g080.sh` (the original g080, which ran out of memory) and its item
  `items/cov-g080.json`. Requeuing that job would rebuild g080, so don't. Say if you'd like the item moved aside.
