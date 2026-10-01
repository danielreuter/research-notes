---
id: 20261001T0920Z-handoff-from-circuits-grid-models-node2-no-commit-slot
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (for infra): node 2 can start no Commit until 9:30 AM PDT; offloaded Commits carry max_min=90

This is a placement problem for "node 2 first" (note:20261001T0821Z-handoff-from-circuits-go). `n2_commit.sh` belongs to infra, so
please relay it.

**What I see on node 2** (`/workspace/pouw/fill/`, 2:17 AM PDT):

- `windows` holds timed windows at 10:00, 11:30, 13:00, 14:00, 15:00, 15:30 and 16:00Z, 30 min each. Its header says "no GPU fill
  starts whose max_min reaches one".
- `n2_commit.sh` writes every Commit guest with `max_min=90` (since infra's runner `ad91739ef`, 07:45Z).
- The gaps until 16:30Z (9:30 AM PDT) are 60, 60, 30 and 30 min, so no Commit guest can start on node 2 before then.
- Since the five Commits preempted at 08:32Z, `events.jsonl` has no `verity-commit` start.
- `verity-commit-vllm-epoch-run-cov-gm014.sh` has been queued since 08:49Z (1:49 AM PDT) and hasn't started. Node 2 shows 3 of 8 GPUs
  free, and three proof guests (prio below its 20) started at 09:15Z.

**Effect:**

- Every Commit that `n2_commit.sh offload` moves tonight sits for `VY_N2_RECLAIM_MIN` (60 min) and then goes back to node 1's queue.
  gm014 is a 5-minute Commit on node 1 (qwen25-coder-1.5b B8 256/32), and it returns at about 2:49 AM PDT.
- The plan to send long Commits to node 2 has no 90-minute slot tonight. That covers my 36 held rows, Gemma-2, and the TP2 rows once
  approved.

**Suggestions for infra** (my reading; their call):

- Give each Commit guest a `max_min` from its row rather than a flat 90. The Commits of my TP1 rows under 7B at 256/32 take 4.4–8.6
  min on node 1, so 20 would do.
- A long row could take 55. That fits the 10:30–11:30Z and 12:00–13:00Z gaps (3:30–4:30 and 5:00–6:00 AM PDT), if its Commit
  really is under about 50 min.
- Until then, `VY_N2_FIRST=0` would stop offload from moving a Commit while node 1 has a free GPU. Node 1 has had 1 to 4 GPUs free
  in `deployments-gpu` since GO, because Builds are what's limiting.

**Meanwhile, on my side:** nothing changes. The 36 holds, Gemma-2 and TP2 stay held, and gm014 comes back by reclaim.

**One measurement for your pacing**, from cgroup `memory.peak` of running pods on node 1:

- My Builds peak at 1–10 GB of their 48 GB request (`build_request` peaks at 14 GB for B1 1024/128), and my replays at about
  20 GB of 64 GB.
- `deployments-cpu` is bound by memory (about 521 GiB admitted, borrowing, at 44 of 100 CPUs). Smaller Build requests would admit
  more Builds. I copied cov-cg10's resources and have left them unchanged; say if you want them lowered.
- Going the other way, cov-cg07's replay pod peaks at 112 GB on a 64 GB request. Memory is only requested, with no limit, so that is
  the overcommit to watch.
