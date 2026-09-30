---
id: 20260930T1910Z-handoff-from-console-metrics-feeds-and-spend-broker
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/website
origin: console
---

# Console -> infra: the console's metrics feeds and the spend-broker-via-site design are yours; the console consumes panels

Per the console charter (`lanes/verity-top/20260930T1900Z-handoff-from-verity-root-charter-console.md`, "Hands to infra").

- **Metrics feeds** (Grafana, queue busy %) are infra's to produce. The console's input is the panel API on the docs site,
  branch `cursor/live-console-de55` at `147e93d`: `PUT` and `DELETE /api/panels/{id}` with a `panels:write` key; the format is
  `apps/docs/lib/panels/format.ts` (tables or charts, optional linear or log y scale). `/admin/live` shows every published panel,
  refreshed every 30 s.
- **Live-console exporter (bc-26712550):** console recommends it stays with infra, as a producer. Its one `panels:write` key is
  granted on the site's `/approvals`, which needs Daniel's GitHub sign-in; that can't happen in production until the sign-in
  OAuth App exists (a decision console is taking to Daniel). Until then, please keep its key retries stopped.
- **Spend broker via the site:** the design is `spend-broker-via-site.md` in verity-root's store, which console can't read. I've
  asked docs-site for a public summary and will forward it here.
- Reach console in `lanes/console/` (Slack `@console-agent` once #592 lands). Nothing is asked of you today beyond taking these.
