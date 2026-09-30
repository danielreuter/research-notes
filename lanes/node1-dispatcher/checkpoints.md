---
cursor:
  subagentId: "bc-70706bc3-bf17-5315-9276-4811c214ffee"
id: node1-dispatcher-checkpoints
campaign: overnight-sep30
lane: node1-dispatcher
kind: report
status: open
repo: danielreuter/verity
origin: node1-dispatcher (bc-70706bc3), launched by RC bc-8ece7cde for postmortem action 3
---

# node1-dispatcher: hourly checkpoints

One line an hour. Busy % is from node 1's Prometheus. `gpu_busy` is the share of GPU-minutes with DCGM utilization above 0 (the
steward's definition); `gpu_util` is mean DCGM utilization. The dispatcher runs in tmux `node1-dispatch` on vy-nebius-1, with its
record in `/workspace/jobs/dispatch/{log,done}.jsonl`.

- 20260930T1610Z live: loop ticking since 15:57Z. Smoke SmolLM2 two-task in `backfill`: Build SUCCESS `r20260930-155637-7035` in the store; GPU task preempted by `provers`' reclaim and waiting on CPU quota (steward asked). 10 min: gpu_busy 7.5%, gpu_util 0.3%, cpu 50%. 60 min: gpu_busy 11%, cpu 38%.
- 20260930T1634Z smoke done: SmolLM2 two-task, as plain Jobs, both Attempts in R2 (Build `r20260930-155637-7035`, Commit `r20260930-162255-f52c` citing `art:5029be70…`). Dispatcher `031d68a0` follows `ebf0d3f8` (deployments-cpu/gpu, backfill priority, CPUs 96-127, ready files `/workspace/jobs/ready/<lane>/`). No ready files from any lane yet; queues empty. 10 min: gpu_busy 1.8%, cpu 37%. 60 min: gpu_busy 10.8%, cpu 46%. Handoff to RC: `lanes/coordinator/20260930T1634Z-…`.
