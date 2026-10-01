---
id: 20261001T0035Z-report-infra-user-interviews
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1), on Daniel's request (5:00 PM PDT, 30 Sep): short, periodic interviews of the agents who use the infra
---

# Infra user interviews: what costs the coordinators time on the servers and tools, and what infra builds, declines or defers

**How:** every 4 hours, ask two handles three questions over Slack:
1. What cost you the most time on the servers or tools since the last time we talked?
2. What did you work around instead of asking?
3. If infra fixed one thing next, what should it be?

Each answer gets a yes (with an owner and a time), a no (with the reason) or a later, posted in its thread. Infra says no when
something isn't worth its cost. It weighs bandwidth against tonight's goals, and adds context the asker lacks.

**Rotation:** circuits, proofs, compute-accounting, memory-accounting, network-accounting, console, old-circuits-and-proofs.

## Round 0: circuits (written, 23:55Z; `note:20260930T2355Z-handoff-from-circuits-workflow-fixes`)
| Ask | Answer |
|---|---|
| Guards as fail-closed defaults | Yes. The steward plans a Kueue AdmissionCheck for node 1's Commits, and cluster-build adds the guards to `--queue` |
| Queue view | Yes. A worker is building `cluster status`, target 11 PM PDT |
| Slack CLI in `/tmp/slack-wt` | Already fixed: #592 is on main |
| URGENT wake | Yes. `research notes inbox --urgent`, draft PR #614 |
| Self-echo wake | No change: `match` already exits 1 on your own post. Send the payload if it doesn't |
| Timer re-arm, EAGAIN | Cursor's platform: `note:infra/20261001T0032Z-friction-cursor-timer-rearm-and-store-eagain` |

## Round 1: proofs, compute-accounting (5:35 PM PDT)
- @proofs: asked 00:34:46Z (thread 1790814086.554169).
- @compute-accounting: asked 00:34:47Z (thread 1790814087.211489).
