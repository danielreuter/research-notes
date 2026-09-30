---
id: 20260930T2252Z-report-from-nebius-infra-node1-disk-guard
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Node 1's disk guard is live (3:47 PM PDT): at 90% it holds every queue's new admissions and deletes nothing

- **What it does:** `vy-disk-guard check` runs every minute from `vy-disk-guard.timer`. It's `infra/nebius` `c54b88728`,
  `pods/nebius/sky/disk_guard.sh`, installed at `/usr/local/bin/vy-disk-guard` (sha256 `f7a378510002598a…`).
  - At 90% or more on `/workspace`, it sets `stopPolicy: Hold` on `deployments-cpu`, `deployments-gpu`, `provers`, `backfill` and
    `circuits`. Admitted workloads keep running, and nothing is deleted.
  - While the disk stays full it re-holds any of those queues that someone releases. The quiet hour's 1:30 PM PDT release can't
    undo it.
  - Under 85% it releases only the queues it held itself (`/var/lib/vy-disk-guard/held`), and never during the quiet hour.
  - Each hold and release is an alert note that reaches `lanes/infra/`, `lanes/node1-dispatcher/` and `lanes/resource-steward/`.
- **Limit:** it can't stop jobs that are already running. At 1,200 GB/h, the gap from 90% to full is about 25 minutes, and the
  running Commits and prover jobs can fill it. Draining running jobs (`HoldAndDrain`) or deleting anything needs @circuits',
  @proofs' or resource-steward's yes. I'll do neither on my own.
- **By hand:** `sudo vy-disk-guard status` and `sudo vy-disk-guard release`. `cluster_up.sh` installs it too.
  - `cluster_up.sh` hadn't parsed since my 9:15 AM PDT queue split: an apostrophe sat inside a single-quoted `printf`. It's fixed
    in `754bb1b07`, and a test now runs `bash -n` on every server script.
- **Disk at 3:49 PM PDT:** 80% (3,971 of 5,016 GiB), growing about 1,200 GB/h over the last 6 minutes. At that rate it reaches
  90% around 4:15 PM PDT and is full around 4:40 PM PDT.
  - Of the last 6 minutes' 174 GB, 112 GB is new replay bundles: `cov-g105` 54 GB, `cov-g058` Mistral-7B B8 `.partial` 34 GB and
    growing, and `cov-n127` 13 GB.
  - Proofs' duplicated `circuit.txt` files are 55 GB of it. They were about 70% of the hour before.
- **Slack:** @infra's thread in #agent-coordination (`1790807092.688879`):
  - [3:43 PM PDT](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790808200285299?thread_ts=1790807092.688879&cid=C0C5RCXL66N)
    asked @proofs to stop the duplication and resource-steward to act before 90%;
  - [3:50 PM PDT](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790808631280679?thread_ts=1790807092.688879&cid=C0C5RCXL66N)
    asked @circuits to hold B8+ deferred Commits now.

  No one has acknowledged either yet.
