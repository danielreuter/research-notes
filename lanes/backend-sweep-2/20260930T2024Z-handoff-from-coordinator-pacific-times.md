---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: backend-sweep-2
kind: handoff
from: coordinator (relaying @infra, from Daniel)
to: backend-sweep-2 (bc-62b7c7a1)
created: 2026-09-30T20:24Z
---

From Daniel, effective 1:23 PM PDT: write any time a person reads in Pacific time with the zone shown, for example "2:30 PM PDT" (America/Los_Angeles). That covers report and handoff body text, deadlines and state files. Machine timestamps stay UTC: note filenames, front matter, log lines, run and store ids.

- Now: `TZ=America/Los_Angeles date "+%-I:%M %p %Z"`
- Convert a UTC time: `TZ=America/Los_Angeles date -d "2026-09-30 21:30Z" "+%-I:%M %p %Z"`

The rule is in lane contract 2.7 §5a.
