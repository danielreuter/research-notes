---
id: 20260930T2132Z-handoff-from-infra-glide-path-rows-nebius-infra
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# Steward: your rows tonight: node 1 disk, hourly busy notes through 8 AM, and the alert sink to lanes/infra

Tonight's glide path (verity-top, 2:20 PM PDT; it lives in the Project store, so your rows are copied here). **Live-node cutoff: no live-node change starts after 9:00 PM PDT;** after that, only rollbacks, queue top-ups and resubmits. **Rejections are held:** tonight nothing is rejected, and a job without `--kind` still runs (it is recorded as `adhoc`). Times are Pacific.

- **Node 1 disk:** report `/workspace` and `~/.cache/verity-check` free space in `lanes/infra/`. The glide path lists it as unknown.
- **Hourly busy notes:** please extend them past 4 PM PDT, through 8 AM PDT. The morning readout depends on them.
- **The alert sink:** retarget it to `lanes/infra/` now (`LANE = "infra"`, one change; verity-root agrees). Infra reads it every 15 minutes overnight.
- **Rollbacks without asking** are pre-proposed to Daniel: the node-2 agent stop, template reverts, the StrictFIFO revert.
