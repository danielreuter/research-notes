---
id: 20261004T2140Z-report-steward-handover
campaign: infra
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1), Daniel's steer via top, 4 Oct 2:20 PM PDT
---

# The resource stewards move to infra: node timers plus infra's own passes, no old-project agent

Two old-project agents ran the stewards' jobs from their own VMs: the nebius-infra steward (bc-fd19a2fe, cron passes every 30 and
45 min) and resource-steward (bc-b154b9ef, a 6 h sweep; idle since 3 Oct 18:46Z). From 21:35Z on 4 Oct each job runs here:

| Job | Was | Now |
|---|---|---|
| Node 1 state line every 15 min (`steward-watch.jsonl`: disk, src trees, GPUs held, Kueue, pacer and dispatcher ticks, flags) | hand-installed timer | `vy-steward-watch.timer` from `deploy.toml` (verity #1134 on #997), installed on node 1 21:35Z |
| Node sweep (src/.trash, check scratch over 2 h, failed audits' `.lake/packages`, node 1's jobs/src over 24 h) | resource-steward's VM, ssh as root | `vy-node-sweep.timer` every 6 h at :30 on node 1 (enabled 21:36Z; dry run clean); node 2 after its timed windows end at 23:30Z |
| `src/` trees | node-sweep `--src` | `store/evict.py` `evict_src` (#1115); by hand hourly on node 1 until it merges |
| Disk 72% / 78% response, idle GPUs while work waits, stalls | steward passes nudging @infra, telling @top | infra's 15-min duty reads the watch's flags and acts; disk-78 goes to @top. Later: #991's monitors on node 1 |
| Daily utilization summary (`lanes/nebius-infra/utilization-summary.md`, `tools/util_collect.py`) | steward | infra's 16:00Z daily pass, same sources, into `lanes/infra/` |
| Infra PRs from the steward's backlog | steward queued them | infra's quick-tier chains (`research queue ready`) |

No job reads or writes an agent store. The state is this note, the node files above, and `lanes/nebius-infra/` as history.

**Standing rulings carried over** (from `lanes/nebius-infra/backlog.md`):
- A small infra fix goes straight to the queue once its tests pass, then to @ci.
- In Slack posts, mentions go first.
- GPU work runs only for owner-approved items that name a research question; idle GPUs are reported to @top, never filled
  (Daniel's rule via root, 06:33Z 4 Oct).

**Open asks carried over:**
- The steward's ask 1 (hourly src eviction) is #1115. After it merges: bump `tool-1028.conf` on both `vy-store-evict` units.
- @circuits' GLM footprint answer is still owed.

**Retiring the old ones:**
- bc-fd19a2fe: asked in the steward thread (1790807092.688879) at 21:40Z to unsubscribe `nebius-infra-steward-pass-v2`,
  `nebius-infra-steward-fallback` and the 9 Oct renewal reminder, then write FINAL in its backlog pointing here.
  If it hasn't by 23:30Z, its project's owner has to stop them.
- bc-b154b9ef: idle and its sweep hasn't run since 3 Oct. If it wakes, the shared lock
  (`/run/lock/resource-steward-sweep.lock`) keeps its sweep and the timer from overlapping.
