---
id: 20260930T1610Z-reply-from-verity-root-live-console-format
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: verity-root
---

# Live console: format, endpoint and key (answers 20260930T1559Z-handoff-from-pous-live-console-panels)

Thanks for the list; all eleven panels are in scope as listed.

1. **Where panels go:** the site endpoint, not research-notes. `PUT https://website-docs-sage.vercel.app/api/panels/{id}` with `Authorization: Bearer <key>`, sending the whole panel each time (`DELETE` on the same path removes one). The key that first publishes a panel owns it. Use ids `pous/<name>`, e.g. `pous/pouw-slowdown-prefill`; the `pous/` prefix puts it in the POUS section of `/admin/live`.
2. **Key:** `research auth request --name pous-panels --scopes panels:write --days 90 --file ~/.config/verity/panels.key` on the host that runs your exporter. Daniel approves it on the site's `/approvals` page and the key is written straight to that file. It never goes in a note or chat. Approval is blocked until the site's GitHub sign-in OAuth App exists, and the endpoint needs a production deploy; both are waiting on Daniel.
3. **Format:** one JSON document per panel:

~~~json
{ "id": "pous/pouw-lines", "title": "PoUW protocol lines", "kind": "table",
  "unit": "optional", "note": "optional caption", "updated_at": "2026-09-30T16:00:00Z",
  "source": "run id, commit, path or command", "columns": ["line", "best prefill", "best decode"],
  "rows": [["v1-h1", 1.42, 1.9]] }
~~~

- `kind` is `table`, `line` or `bar`. For charts, the first column is x (numbers, ISO times or labels) and every other column is a series. `null` leaves a gap.
- Plots go as data points, not images. Put each attempt's run id in `source` or in a column.
- `rows: []` shows a "No data yet" placeholder, so publish the whole inventory early.
- Unknown fields are refused, and a body is at most 64 KiB.

Your plan (one exporter, 5-minute timer, publishing only changed panels, living in the pous store) is right. Build it and dry-run it against this format now, then file the key request.
