---
id: 20261001T1015Z-ask-from-resource-steward-jobs-src-copies-unreaped
campaign: overnight-sep30
lane: infra
kind: handoff
status: open
repo: verity
origin: resource-steward (bc-b154b9ef)
---

to: infra (bc-17cc41f1). Not urgent.

# Node 1: 533 unused copies in `/workspace/jobs/src` hold about 2.5M inodes, and nothing removes them

- **What fired.** Node 1 `/workspace` inodes rose from 36.1% to 38.7% between 2:43 and 3:07 AM PDT, so the probe projected 80% within 11 h (a HARD line).
  - The burst has stopped: 39% (7.97M of 20.57M) at 3:13 AM.
  - At the net rate since 1 AM (about 190k inodes an hour, after my 6 h sweeps), 80% is about two days out.
  - The burst itself came from `research/cache/verity-check` (328k new inodes in 95 min), `research/build-speed/runs` (100k) and about 25 newly shipped `research/src` trees.
- **The largest holder is `/workspace/jobs/src`.**
  - It holds 654 copies of a synced tree: 3.16M inodes, 40% of the used inodes on node 1.
  - The oldest copies are from Sep 30 07:49Z.
  - Of these copies, 533 are older than 6 h and named by no Running or Pending pod (neither as `$(hostname)` nor through `by-pod/<hostname>`). They hold about 2.5M inodes.
  - A sample of 40 per-pod copies held no file newer than their `.research-sync-files`, so they hold nothing beyond the synced files. Outputs go elsewhere.
- **Where the copies come from.**
  - About 400 are per-pod copies made by `dispatch/infra/nebius/sky/jobs/prover-bench.yaml` and `prover-dev.yaml` (`JOB_SRC=/workspace/jobs/src/$(hostname)`), at 4.7k inodes each. These are mostly `nd-backend-sweep-*`, `nd-assumption-swe-*`, `nd-proofs-*` and `nd-vllm-*`.
  - `port-capture.yaml` also makes `pod-$(hostname)` copies.
  - The other 142 are `job_tree.sh`'s per-content `<id16>` copies.
- **Ask 1: may I add these copies to my sweep?** It is your directory and outside my policy (report §1), so I won't touch it without your yes.
  - The rule I'd apply: a copy older than 6 h, named by no Running or Pending pod.
  - Each copy is renamed into a trash directory and re-checked before it is deleted, the same way as `research/src` (`tools/node-sweep.sh`).
  - Every deletion is logged in my report's §4.
- **Ask 2: would you point `prover-bench` and `prover-dev` at `job_tree.sh`?** Jobs of one content would then share one copy, as its header intends. That would cut new copies to one per sync.

**Update at 13:53Z (6:53 AM PDT).** `/workspace/jobs/src` now holds 713 copies and 3.46M inodes, up 299k since 10:10Z. It
accounts for half of node 1's lasting inode growth over those 3.7 h. The check cache `research/cache/verity-check` added
another 174k. Node 1 is at 40%. A transient 660k-inode burst at 13:30Z (43%, a HARD projection of 80% in 6 h) was gone by
13:53Z.

Reply under this note, or in a note to `lanes/resource-steward/`. I re-read it at the 12:30Z sweep (5:30 AM PDT) and in the 15:00Z daily summary (8 AM PDT).

**Update at 03:09Z 2 Oct (8:09 PM PDT).** 877 copies and 4.23M inodes (measured 01:46Z), about 69k/h. Lean audits now
hold 1.07M inodes each, and node 1 peaked at 63% inodes at 03:00Z. With no reply here after 17 h, I sent Ask 1 to Daniel as
a blocking card (#approvals `1790910579.790289`, default "ask again past 70%", deadline 2 Oct 6:00 PM PDT). An answer from
you here still settles it.
