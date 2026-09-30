---
id: 20260930T2125Z-handoff-from-console-utilization-panel-spec
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/website
origin: console
---

# Console -> infra: four `infra/*` panels for Daniel's targets (both nodes ≥85% useful GPU busy by noon Oct 1); the page is ready, only your numbers are needed

Daniel, 2:06 PM PDT: a utilization panel live on the console, built with infra, before the targets end at noon tomorrow. Console
has deployed the page side (website `0db7592`): charts take a dashed `target` line and `stacked` bars, and chart times read in
Pacific. `infra/*` panels show first, in the Servers section at the top of `/admin/live`. You hold the definitions of useful and
held-idle, and the queue, so please publish these four from wherever you compute the target report, every 5 minutes.

**Key (once):** `research auth request --name infra-panels --scopes panels:write --file ~/.config/verity/panels.key`, which Daniel
approves in #ask-daniel. **Publish:** `PUT https://website-docs-sage.vercel.app/api/panels/{id}` with `Authorization: Bearer <key>`,
sending the whole panel each time. Format: `apps/docs/lib/panels/format.ts`. Each panel needs `updated_at` (ISO UTC) and `source`
(the command or run it came from).

1. **`infra/busy-now`** (bar, stacked, unit `%`, `target: 85`, `target_label: "useful GPU target"`). Columns
   `["node", "useful", "held idle"]`, rows `["node 1 GPU", 71.2, 9.5]`, `["node 2 GPU", 95.1, 0]`, `["node 1 CPU", …]`,
   `["node 2 CPU", …]`: busy % over the last hour. Useful plus held-idle is total busy.
2. **`infra/useful-gpu-24h`** (line, unit `%`, `target: 85`). Columns `["hour", "node 1", "node 2"]`, rows
   `["2026-09-30T20:00:00Z", 71.2, 95.1]`, …: useful GPU busy % per hour over the last 24 h.
3. **`infra/queue-depth`** (table). Columns `["queue", "node", "waiting GPU-h", "running GPU-h", "jobs waiting", "oldest wait"]`,
   one row per queue (Kueue `circuits`, `provers`, backfill, node 2's fill queue and Verity guest pool), plus a total row. Use
   `bar` with `stacked` over time instead if you'd rather show a history.
4. **`infra/targets`** (table). Columns `["target", "goal", "now", "trend", "status", "by"]`. One row per target you report
   against, e.g. `["node 1 useful GPU busy", "≥85%", "71.2%", "+6 pts/h", "behind", "noon Oct 1"]`. `status` is one of
   `met`, `on track`, `behind` or `at risk`.

**If publishing is a burden,** send console a JSON file or endpoint with the same numbers, readable from vy-nebius-1, and console's
`verity-console.timer` publishes them instead. Reply in `lanes/console/` with which, and the first publish time.
