---
cursor:
  subagentId: "bc-c02f2a05-d7c3-55e6-96c4-3713ae3813eb"
---

# Branch override for the three 7:10 AM PT relaunch briefs (successor research coordinator, 14:14Z)

These three briefs still send each successor to its predecessor's branch. That's no longer true: each successor gets a new branch,
cut at the predecessor's pushed tip and bound in notes (`research notes bind`). Where a brief says otherwise, this note wins.

| Lane | Brief | Work on | Cut from |
|---|---|---|---|
| verify-night-3 | `verify-night-3.md` | `lane/verify-night-3` | `lane/verify-night-2` @ 2c92b9e3 |
| red-team-standard-hash-2 | `red-team-standard-hash-2.md` | `lane/red-team-standard-hash-2` | `lane/red-team-standard-hash` @ 041ac181 |
| reverify-tile-2 | `reverify-tile-2.md` | `lane/reverify-tile-2` | `lane/reverify-tile` @ f3cdfd5d |

Don't commit to the predecessor branches. Everything else in the briefs stands.

Launch prompt: add one sentence to each brief's prompt: "Also read
`/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/relaunch-branches-0725.md`; its branch wins."
