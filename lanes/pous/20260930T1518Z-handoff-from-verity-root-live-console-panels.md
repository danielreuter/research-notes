---
id: 20260930T1518Z-handoff-from-verity-root-live-console-panels
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: verity-root
---

# Live console panels: please publish POUS's plots and tables

Daniel wants one page in the website console that shows a live version of every plot and table he has asked for, from both Verity and POUS. The website agent (bc-41cff24f) owns the page and a minimal format: one JSON panel per plot or table. The format will be at `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/live-console/panel-format.md`, with the endpoint and key to follow.

Asks for the POUS coordinator:

1. List POUS's plots and tables and their live sources in `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/live-console/pous-panels.md`.
2. Publish them in that format on a timer once the format is posted.
3. For a format change, write a `-reply-` note in `internal/live-console/`.

Keep it simple; Daniel asked us not to over-engineer this.
