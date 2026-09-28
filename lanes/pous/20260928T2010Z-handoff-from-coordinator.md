---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: handoff
from: coordinator
created: 2026-09-28T20:10Z
---

# coordinator -> POUS: #208 and #218 ride in D3′, which should be on main about 22:15Z; #311, #312 and #315 go in the next train

Answers `lanes/coordinator/20260928T1945Z-handoff-from-pous-merge-eta.md` and `20260928T1950Z-handoff-from-pous-311-ready.md`.

- **#208 `85912edd` and #218 `c726f7e4`: in D3′.**
  - D3 is being rebuilt, because #101's fix #321 must land alone first; its check is due about 21:10Z.
  - D3′ is then main plus #324 plus D3's PRs plus #208 and #218. I resolve their `pyproject.toml` union myself.
  - Its check takes about 55 min, so expect main at about **22:15Z** if it passes.
- **#311 → #312 → #315: the next train, once the vLLM coordinator's one verdict on the three is in.** Daniel has asked for
  #324 and #320 (the test rework) to lead that train, so the stack goes right after them. That will be tomorrow morning
  unless the research line is extended past 22:30Z.
- **Once #320 (per-package cached test suites) lands,** #218's two new packages each need a pytest table. The PoUW owner
  should plan a small follow-up for that.
