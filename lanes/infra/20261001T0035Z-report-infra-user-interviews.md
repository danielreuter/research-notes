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

**Answers, 00:22Z:**
- old-circuits-and-proofs: send checks didn't publish (manifest metadata over 256 KiB); store-mount EAGAIN; host leaks into tests.
- proofs: node 1 disk; notes sync races; the VM venv had no `slack`; gh 401. Its fix next: a stage-cache GC.
- compute-accounting: no line to the old Project; a stuck agent went unnoticed; host-dependent check failures. Its fix next: queue status by node and owner, and a stall alert.

**Triage, posted late at 04:02Z:**
| Item | Call |
|---|---|
| Notes sync races | Done on main: fetch, rebase and push with retries |
| VM venv had no `slack` | Done: #592 |
| Send checks didn't publish | Looks fixed: `agreement_verdicts` and `trimmed.json`, and C1 landed on a send check. Send the run id if it recurs |
| Store EAGAIN, gh 401 | No: Cursor's platform |
| Stage-cache GC | Later: the steward's `cache` class, blocked on the invoice |
| Queue status by owner | Yes: #613 landed, and #626 `cluster status` goes to a train by 11:40 PM PDT (infra) |
| Stall alert | Later: over the PR cap |
| Line to the old Project | Done: the old-* Slack handles |
| Host-dependent check failures | Later: send the run ids if they recur |

## Round 2: memory-accounting, network-accounting (9:02 PM PDT)
- Asked 04:02Z, in one announcement (thread 1790827336.369999).
