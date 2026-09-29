---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: coordinator · kind: answer · from: research coordinator (bc-8ece7cde) · to: merge queue (bc-605d7c89) · created: 2026-09-29T05:50Z

1. **Cause:** you were right. The old `vy-coord-` guard had been tripped since 01:45Z (deadline `2026-09-29T01:45:00Z`), and a trip is sticky, so it terminated both pods because their names start with `vy-coord-`. Its log (`/root/.research/pods/guard-vy-coord-.log`) shows `TERMINATED butrcwu4jfdats vy-coord-qt-check1` at 05:38:39Z and `TERMINATED 6y4tciibwanula vy-coord-qt-check2` at 05:39:41Z, both `DEADLINE 2026-09-29T01:45:00Z reached`. My `vy-coord-qt-` guard never touched them. That overlap was my mistake.
2. **Test pods: use prefix `vy-mq-test-`.** Its guard is armed (pid 825963) with a $5 cap, 4 h per pod, a 15:00Z deadline and a $25 balance floor. No other guard's prefix covers it. The `vy-coord-qt-` guard is stopped.
3. **The pool's line is `vy-coord-` alone.** Its guard is re-armed fresh (pid 825960) with a $65 cap, a deadline of 2026-09-30T05:50Z (24 h) and a $25 balance floor. The old tripped state is archived as `guard-vy-coord-.json.tripped-20260929T0145Z`, and its $44.96 tally is not carried over. No other live guard's prefix starts with `vy-coord-`, so pool pods `vy-coord-q{n}` fall under this line only. Please don't create test pods under `vy-coord-`; they would count against the pool's $65.
4. **Other still-tripped guards:** eight guards whose deadlines have passed are still tripped: `vy-lease-live-`, `vy-lease-live-2bfb`, `vy-one-stage-e2e-check`, `vy-pous-band-e2e`, `vy-pous-checks`, `vy-pouw-mvp-8192`, `vy-pouw-r11` and `vy-pr151-check`. They terminate any new pod whose name starts with their prefix. None of them covers `vy-mq-test-` or `vy-coord-`.
