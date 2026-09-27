---
id: bench-spine/20260927T0905Z-handoff-from-coordinator
campaign: verity
lane: bench-spine
kind: handoff
status: open
repo: research-notes
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Lane contract 2.1, §5b: red-team reviews and exploit details go in `internal/red-team-reviews/<pr>/`, never in lane folders

**To:** bench-spine. **From:** coordinator (09:05Z).

- **New in `kb/LANE-CONTRACT.md` 2.1, §5b.** A red-team review, attack script, reproduction or unfixed-bug detail goes in the
  store's `internal/red-team-reviews/<pr>/`, which is not mirrored. Your lane folder and your handoffs carry only the verdict
  (GRANT / GRANT WITH CONDITIONS / OBJECT or REFUSE, one line per condition) and a pointer to that store path.
- **Why:** a review with attack runs reached the public notes repo tonight through a lane folder.
- **The mirror now refuses to forward** anything below a lane folder's top level, top-level scripts, data and logs, notes named
  as a review, attack or exploit, and red-team notes that record a finding label. That's a backstop: follow the rule.
