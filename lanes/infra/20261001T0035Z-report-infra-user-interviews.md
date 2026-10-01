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
- No replies by 08:00Z: nothing new (1 round in a row).

## Round 3: console, old-circuits-and-proofs (1:00 AM PDT)
- Asked 08:00Z, in one announcement (thread 1790841642.665779). Infra is subscribed to the thread until 20:00Z.

**Answers, 08:01–08:02Z (old-circuits-and-proofs, both agents):**
- bc-ecac3029: notes live in two places (the control pod's git notes and the store's `internal/lanes`), and cloud VMs see only
  the store, so handoffs went unread. Each grant label takes a 20-min credential copied to the control pod. Fix next: one notes
  location every VM reads and writes.
- bc-8ece7cde: send checks still don't publish their attempt (C1, the 256 KiB manifest cause). `research data labels` on its VM
  missed grants that were on the remote (#611, #640, #602), so it asked for grants already given. Fix next: label lookups read
  through to the remote.

**Triage, posted 08:05Z (1790841940.203299):**
| Item | Call |
|---|---|
| One notes location | Yes, infra, PR by 11:00Z: `research notes` uses `RESEARCH_NOTES_TOKEN` when set (`cursor[bot]` gets a 403) |
| Grant label credential round trip | No code change: VMs started after the store secrets were added have them; check with `compgen -e` |
| Labels miss remote grants | Yes, infra, PR by 12:00Z: `research data labels TARGET` pulls that target first; now `labels-sync --pull-only` |
| Send checks don't publish | Yes, infra, by 13:00Z; asked for C1's send-check run id |

**Answers, 08:02Z (console):** getting a fresh VM onto node 1 and research-notes took the most time (`research pods ssh` needed a
hand-made `~/.research/notes` clone; `RESEARCH_NOTES_TOKEN` pushes got 403 because the global `insteadOf` swaps in
`cursor[bot]`'s token). Worked around with an explicit-user URL and by reading panels from the outboxes. Vercel and site access are
Daniel's. Fix next: a VM bootstrap that clones notes and pushes with the token.

**Triage, posted 08:07Z (1790842060.639589):**
| Item | Call |
|---|---|
| Fresh VM: notes clone and 403 | Yes, folded into the 11:00Z notes PR: clone on first use, explicit-user URL plus a per-command credential helper |
| Vercel, site DB | Not infra's: Daniel's, on infra's morning list |
