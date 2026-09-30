---
id: 20260930T1900Z-handoff-from-verity-root-charter-console
campaign: verity
lane: verity-top
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Charter: console (website, docs site, live console)

Replies to `note:20260930T1842Z-handoff-from-verity-top-charters`. State as of 19:00Z Sep 30.

- **Owner:** website worker `bc-41cff24f-52d5-5d11-b42a-99f19870de55`. **Stays**; Daniel talks to it directly, from his laptop.
- **Remit:** the Verity docs app in the website repo, the console (live panels, infra diagram, circuit visualizer), fixtures served through the site, and the site-store API.

## Workers
| lane | id | owns |
|---|---|---|
| live console panels | `bc-94d0b126-b15b-58c6-a64e-7173c4901c99` | `cursor/live-console-de55` |
| infra diagram on site | `bc-52e0a086-df9d-55c2-8dce-f6c32ba68b4a` | diagram upkeep |
| Boolean circuit export for the visualizer | `bc-9916bbb1-de98-5d21-a511-aafa5255c78f` | visualizer data |

## Open items (**D** = needs Daniel)
- **D:** production go-ahead for the live console.
- **D:** an OAuth App for producer keys.
- **D:** fixture rewrite: an archive repo and the commit-map label (after #371 lands).
- Taking the live-console exporter over from POUS (or leaving it with infra).

## Hands to infra
- Metrics feeds (Grafana, queue busy %) as the console's data source, and the spend-broker-via-site design.

## Where state lives
- The website repo; the verity-root store's `docs/`: `website-morning-review.md`, `site-store-api.md`, `fixtures-access-via-site.md`, `docs-site-and-fixtures-walkthrough.md`, `spend-broker-via-site.md`; verity PR #371.
