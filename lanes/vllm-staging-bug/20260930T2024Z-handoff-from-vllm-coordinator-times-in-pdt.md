---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff (rule, from now on) · from: @old-circuits-and-proofs

**Times people read go in Pacific, with the zone shown,** e.g. "1:25 PM PDT" (America/Los_Angeles; PDT is UTC−7 until 1 Nov). That covers handoff and report body text, PR bodies and deadlines.
- **Machine timestamps stay UTC:** note filenames (YYYYMMDDTHHMMZ), front matter, log lines, run and store ids, cron.
- **Now:** `TZ=America/Los_Angeles date "+%-I:%M %p %Z"`. **Convert:** `TZ=America/Los_Angeles date -d "2026-09-30 21:30Z" "+%-I:%M %p %Z"`.
- The rule is from Daniel, via @infra: using-slack skill #592, lane contract 2.7 §5a.
