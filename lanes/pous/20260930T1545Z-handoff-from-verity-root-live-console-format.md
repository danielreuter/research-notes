---
id: 20260930T1545Z-handoff-from-verity-root-live-console-format
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: verity-root
---

# Live console: format and endpoint for POUS panels

This follows `20260930T1518Z-handoff-from-verity-root-live-console-panels`. The website agent has posted the format at `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/live-console/panel-format.md`.

- Panel: `{id: "pous/<name>", title, kind: table|line|bar, unit?, note?, updated_at, source, columns, rows}`. Unknown fields are refused and a body is at most 64 KiB. For charts, the first column is x, every other column is a series, and `null` leaves a gap. `rows: []` shows a "No data yet" placeholder.
- Publish: `PUT https://website-docs-sage.vercel.app/api/panels/{id}` with `Authorization: Bearer <key>`, sending the whole panel each time. The key that first publishes a panel owns it.
- Key: `research auth request --name pous-panels --scopes panels:write --days 90 --file ~/.config/verity/panels.key`. Daniel approves it on the site. Keys never pass through chat or another agent.
- Not live yet: the production deploy and key approvals are waiting on Daniel. Build and dry-run your producer now, then file the key request, so you can publish as soon as both land.
