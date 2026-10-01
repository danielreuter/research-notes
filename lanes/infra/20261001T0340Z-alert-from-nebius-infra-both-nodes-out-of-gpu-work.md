---
id: 20261001T0340Z-alert-from-nebius-infra-both-nodes-out-of-gpu-work
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# alert: both nodes are out of GPU work (8:40 PM PDT): node 1 has nothing queued at all, and node 2's 58 queued jobs are all CPU

No idle-GPU alert fired, because those alerts need work waiting.

- **Node 1:**
  - All 8 GPUs are at 0% with no memory held. Every Kueue queue is empty (0 pending, 0 admitted), and the dispatcher's `ready/` is
    empty.
  - The last jobs (replays of `cov-g043`, `g073` and `n129`) ended at 8:07 PM PDT.
  - The pacer has nothing to release; its cap is 1000 GB, raised by someone.
  - GPU-busy was 21% over the last hour and is 0% over the last 10 minutes. CPU busy is about 4%.
  - `/workspace` is at 29%, after about 2.2 TB was freed tonight.
- **Node 2:**
  - 7 of 8 GPUs are free. `fill_runner` has 58 jobs queued, all of them CPU (`gpu 0, cpu 58`), and 4 are running.
  - `/workspace` is at 54%.
- **What would fill them:**
  1. **GPU work from the feeders.** circuits' epoch run (vllm-coordinator) and proofs have nothing queued on either node. Please ask
     them for the next batch.
  2. **Node 2's CPU backlog onto node 1's idle CPUs.** That's 58 jobs, with node 1 at about 4% CPU, "one pool, borrowing both ways"
     (Daniel 12:12 PM PDT). The move is node2-ops' and kueue-fold's to make.
- **On my side:** the disk guard (80%) and the pacer (300 GB cap, latched to 150 GB at 78%) are idle and ready. The hourly notes
  continue, though the 8:00 PM PDT one was skipped while my VM was suspended.
