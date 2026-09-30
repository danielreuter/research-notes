---
id: 20260930T1740Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: verity-root
---

# Live console is deployed: request `panels:write` once

`/admin/live` and `PUT /api/panels/{id}` are in production (a keyless PUT returns 401). Stop the 15-minute retries and send one `panels:write` key request now. Daniel approves at /approvals.
