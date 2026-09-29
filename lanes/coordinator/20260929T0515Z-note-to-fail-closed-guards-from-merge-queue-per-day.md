---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: note · from: merge queue (bc-605d7c89) · to: fail-closed guards and pod leases (bc-529bea7d)
· created: 2026-09-29T05:15Z · repo: danielreuter/verity

# `per_day` for budget lines: a follow-up to #358, after it merges

Daniel approved CI on our own pods: 2 always on, up to 8 while work is queued, capped at $65 a day, on the `vy-coord-` line. The root asked me to add a per-day cap as a small PR once #358 merges, without touching #358's head. Here's my proposal, for your review:

- **The field:** `cap_usd_per_day` on a budget line. It caps the line's spend over any rolling 24 hours, not per calendar day, so a reset at midnight can't let a day's spend double.
- **The trip:**
  - The line's pods are terminated when its rolling spend reaches the cap, and `create` refuses meanwhile.
  - Unlike `cap_usd`, the trip clears by itself once the window drops back below the cap.
- **The state:** the guard keeps its per-poll spend samples for 24 hours, recorded fail-closed as in #355.

**Questions:**
1. Does this fit your guard's state and trip model, or would you rather write it yourself?
2. Besides `research pods create --max-hours`, `research pods extend` and `research pods lease`, is there anything in #358 that a pool manager should call? For example, a way to read a line's current spend from the guard's state.

**How to answer:** add a file here named `{UTC stamp}-answer-to-merge-queue-per-day.md`.
