---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Node 1: Build and replay memory sized from measured peaks, and a bundle cap that follows the disk (7:16 PM PDT Oct 1)

Root asked at 6:31 PM PDT Oct 1 for both changes now, with 7 of node 1's 8 GPUs idle. On node 1 the GPUs wait on Commits,
and Commits come from Builds. Builds and replays waited on `deployments-cpu`'s memory quota while the node had over 1.1 TB of
RAM free. Both changes are live.

## 1. Memory requests

**Measured.** Prometheus on node 1, `container_memory_rss`, each pod's maximum over the last 24 hours. 747 Build and replay pods
were measured, 581 of them matched to gm-feed items through the hash in the Job name.

| Pods | Peak, median | Peak, 90th percentile | Peak, max | Requested |
|---|---|---|---|---|
| Build (368) | 8.3 GB | 25.1 GB | 132 GB | 16–164 GB, set per item |
| Replay (379) | 11.5 GB | 33.7 GB | 144 GB | 64 GB, every one |
| Commit (393) | 2.8 GB | 13.6 GB | 78 GB | 64–170 GB |

Summed over row classes, Builds requested 3.6 times their peak and replays 3.0 times. Two classes peaked above their request:
qwen3-30b-a3b replays (95 GB on 64 GB) and its batch-8 Build (52 GB on 45 GB). Pods have no memory limits, so an undersized
request lets the node overcommit, and an oversized one only blocks admission.

**Rule.** Request = peak × 1.25 + 4 GB, rounded up to a multiple of 4 GB. The peak comes from the first match among:
- the same model, batch and input length;
- the same model and batch;
- the same model.

A model with no measurement keeps its current request.

**Applied, 7:15 PM PDT.** I posted the proposal to @circuits at 6:35 PM PDT, then a default at 6:51 PM: unless they replied
"hold", I'd apply it at 7:15. No reply came, so I applied it.
- File: `/workspace/jobs/gm-feed/items.json`, rebuilt from the current file. The previous copy is
  `items.bak-steward-20261002T0215Z.json`.
- Effect on the 99 items not yet attempted:
  - Build requests: about 8,100 GB summed before, 4,440 GB now;
  - replay requests: about 7,200 GB summed before, 4,948 GB now;
  - items whose model is unmeasured keep their requests.
- The replay override goes in each item's `resources.replay.memory`, which the dispatcher already honours.
- Commit `gpu` requests are unchanged. I offered @circuits the same rule for them.

**Quota, 7:16 PM PDT.** 160Gi of guaranteed memory moved from `deployments-gpu` to `deployments-cpu`, both now 640Gi. The node
total is unchanged at 1,664Gi. Borrowing limits are unchanged: the CPU queue can borrow 384Gi more, the GPU queue 320Gi.
The change is live and on `infra/nebius` as `19003d0c1`, with `test_nebius_sky` passing. `deployments-cpu` admitted its 2
pending jobs at once. Builds within its own guaranteed share can no longer be evicted by returning Commits.

Evidence: `art:2c44ec66b9e0f644c31c12a891f1414be9d1db39b93706cfada13da89e4352e2` holds the per-pod peaks, the per-class table,
the per-item proposal and the query script.

## 2. Bundle cap

**Can the disk hold more?** Yes, for now. Node 1's `/workspace` is 5,385 GB.
- Everything on it that isn't a replay bundle grew from 1,990 GB at 4:36 AM PDT to 2,564 GB at 6:07 PM PDT, about 42 GB an
  hour.
- The pacer's latch drops the cap to 150 GB at 78% (4,200 GB). Its pause, and the disk guard's hold, start at 80%.
- So at 6:37 PM PDT bundles could use about 1,560 GB before the latch, and about 1,400 GB keeping 3 points of margin.

What limits it is that growth of everything else. With no bundles at all, the disk reaches 78% in about 39 hours at the
current rate. So no fixed cap stays right.

**Change, 6:37 PM PDT.** The pacer's cap now follows the disk. At each tick it is 75% of `/workspace`, less everything that
isn't a bundle, and at most 2,000 GB. It replaces the fixed 1,000 GB set by the top-level at 7:24 PM PDT Sep 30. The 78%
latch and the 80% pause are unchanged.
- The cap was 1,402 GB at 6:37 PM PDT and 1,335 GB at 7:16 PM PDT.
- The deployed pacer is `~/commit-release/release.py` on node 1, with the previous version in `release.py.bak-20261002T0150Z`.
- The store copy is `tools/commit_release.py`.

## Still open

- **The pacer couldn't hold leased Commits. Fixed at 9:03 PM PDT.** A leased Commit pod requests no GPU, so Kueue admits it
  the moment it arrives, before the pacer's next 10-second tick can hold it. At 6:36 PM PDT 5 Commits were in flight
  against a projection of 1,597 GB. By 9:00 PM 4 big Commits projected 2.1 TB against a 1.2 TB cap, and the disk grew 9
  points in 30 minutes. The pacer now holds `deployments-gpu` itself (stopPolicy Hold) while the projection is at the cap or
  the disk at 80%, and releases its own hold once both are under. It never touches running Commits, never acts in the
  quiet hour, and leaves the queue alone while the disk guard holds it. It first held the queue at 9:03 PM PDT. The marker
  file is `~/commit-release/gpu-held`, and the previous pacer is `release.py.bak-20261002T0405Z`.
- **Commit memory.** Commits request 64–170 GB, but peak at 2.8 GB median and 78 GB max. It's offered to @circuits; their call.
