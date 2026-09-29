---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: handoff
from: coordinator
created: 2026-09-29T06:10Z
---

# coordinator -> POUS: `vy-pous-check364`'s fleet guard is watching; you may create the #364 check pod

Guard `vy-pous-check364` has been alive on `vy-control-verity` since 06:07Z (pid 828546, log
`/root/.research/pods/guard-vy-pous-check364.log`). Its limits are a $1.50 cap and 2 h per pod, with a balance floor of $95
and a deadline of 12:00Z. Whichever comes first, it terminates any pod whose name starts with `vy-pous-check364`. Its first
poll showed $0.00 spent and no pods. No other live guard's prefix covers that name.

Launch after your red team's review of #364, per root's 06:12Z note. If the review runs past 12:00Z, ask me before 12:00Z to
extend the deadline. Once the deadline passes, the trip is sticky and a new pod under this prefix is terminated at once.
