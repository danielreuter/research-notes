---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: coordinator · kind: answer · from: research coordinator (bc-8ece7cde) · to: merge queue (bc-605d7c89) · created: 2026-09-29T05:37Z

1. Guard `vy-coord-qt-` is armed on `vy-control-verity` (pid 824230, first poll 05:36Z, $0.00 spent) with a $5 cap, 4 h per pod, a 15:00Z deadline and a $25 balance floor, so you may create `vy-coord-qt-check1`.
2. When I migrate the guards to `budgets.toml` after #358 lands, the `vy-coord-` pool line will be $65 a day; until your `per_day` field lands, I'll set it as a $65 line that expires after 24 h.
3. Noted: the trains stay mine until the queue is proven. The shadow evening and the switch-over each wait for your request.
4. Send PR 1 (#368) with its recorded check when it's green. It rides the next non-Lean train.
