---
id: 20260930T2026Z-handoff-from-infra-pacific-time-cluster-build
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: write times people read in Pacific time with the zone shown ("2:30 PM PDT"); machine timestamps stay UTC

This is Daniel's rule, in lane contract 2.7 §5a. Pacific covers report and ops-log body text, handoffs and deadlines. UTC
stays for note filenames, front matter, log lines, run ids and cron. Now: `TZ=America/Los_Angeles date '+%-I:%M %p %Z'`.
