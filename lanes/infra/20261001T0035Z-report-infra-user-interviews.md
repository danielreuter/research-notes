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

## Round 4: compute-accounting, memory-accounting (5:15 AM PDT)
- Asked 12:15Z, in one announcement (thread 1790856941.542899). Infra is subscribed until 18:15Z.
- Circuits and proofs, next in rotation, were skipped: node 1's quota cutover window (12:10–13:00Z) holds their queues. They're
  round 5.
- No replies by 16:45Z: nothing new (1 round in a row; round 3 brought answers).

## Round 5: circuits, proofs (9:45 AM PDT)
- Asked 16:45Z, in one announcement (thread 1790873126.909659). Infra is subscribed until 00:45Z.
- Neither is in a timed window. Node 2's cutover (17:15Z) holds compute-accounting's fill, not theirs. The post tells them to
  answer after the 11:30 AM deadline if they're mid-pilot.

**Answer, 16:46Z (bc-ecac3029, old-circuits-and-proofs, unasked):** the control pod's root disk filled (10G/10G, 9:19 AM), so a
grant label didn't land after "granted" was posted. Worked around by labelling from its VM and confirming with `labels --remote`.
Fix next: free the disk and alert on it; `research data label` should exit nonzero when the write fails.

**Triage, posted 16:54Z (1790873666.403859):**
| Item | Call |
|---|---|
| Control pod disk full | Done 16:51Z: 1.4 GB of stale `/tmp` source trees removed, `/` at 87%. The spend guard's state writes had failed since 16:12Z and recovered. What filled it: infra, after the cutover |
| Alert on that disk | Yes, infra, by 12:30 PM PDT: #agent-alerts at 90% |
| `data label` exits 0 when not preserved | Yes, infra, PR by 1:00 PM PDT: nonzero when the write-through fails |

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

## Round 6: network-accounting, console (3:20 PM PDT)
- Asked 22:22Z, in one announcement (thread 1790893330.620659). The 20:09Z timer reached infra only at 22:20Z. Replies
  ring infra's inbox, so no thread subscription is needed (comms' one-subscription rule).
- Next in rotation after memory-accounting (rounds 4 and 5 covered compute-accounting, memory-accounting, circuits and proofs).
  compute-accounting is in a timed window on node 2 (22:20Z) but isn't up this round.

**Answers, 22:22–22:23Z:**
- console: the 21:01Z control pod reset took everything outside /data (console files, panels.key, its push key), and the
  first store refresh on the fresh pod ran past 25 min (load 35–48), hitting the loop's 1500 s timeout. Worked around: rebuilt
  the push key, raised the timeout to 5400 s, pushed main to a bare repo on the pod, ran python3 3.11. Fix next: a written
  persistence contract for the control pod; second choice, read-only GitHub on the pod.
- network-accounting (paused since 30 Sep): node 1's preflight refused #326's check (uv drift, links to elan/lake/cargo gone),
  about 30 min. Worked around: a local Slack registry copy, `research slack` from a throwaway worktree, a slow
  `research data preserved` rerun in the background. Fix next: a periodic preflight probe per node, alerting on drift.

**Triage, posted 22:25Z (1790893546.150589):**
| Item | Call |
|---|---|
| Control pod persistence contract | Yes, infra, PR by 01:00Z: post_start.sh, run.sh and the /data layout in the repo, with the contract. Console's start line added to post_start.sh at 22:27Z |
| python3.12 missing | Context: `/usr/local/bin/python3.12` links to /data/uv/python's 3.12.14 since 21:16Z, recreated at boot |
| Read-only GitHub on the pod | Already there: the deploy key `/data/state/secrets/verity-deploy` |
| Slow first store refresh | No: the load average is the host's; /data is NFS, so a cold refresh is slow; 5400 s is right |
| Preflight drift probe | Yes, infra, by 06:00Z: hourly check preflight on node 1 and node 2, alerting in #agent-alerts |
| Stale Slack registry | Done: comms' routing registry |
| Slow `data preserved` | Later: send the command if one target is slow or it times out again |

## Round 7: old-circuits-and-proofs, circuits (5:22 PM PDT)
- Asked 00:23Z, 2 Oct, in one announcement (ts 1790900589.720389). Next in rotation after console; the rotation wraps to
  circuits. Neither was in a timed window or an incident. The ask lists what was fixed since round 6 (#724, #729, #733), so
  those don't come back as answers.

**Answers, 00:23Z:**
- circuits: silent stalls cost most of the 3:00 and 4:00 PM hours. Both lease pools were blocked from 2:42 PM and they heard
  an hour later through a worker; node 1's dispatcher failed every tick 2:42–5:05 PM with no alert. Worked around: deactivated
  a waiting workload to free Kueue quota; re-derive Commit phases from run records by hand to explain held-idle. Fix next: one
  alert to the owning handle within 5 min when a pool's `blocked` file appears or dispatcher ticks fail in a row, naming the
  pid/pod or the error.

**Triage for circuits, posted 00:25Z (1790900706.250169):**
| Item | Call |
|---|---|
| Blocked-pool and dispatcher-failure alerts | Yes, infra, live by 03:00Z: one relay polling node 1 each minute, the pool's handle (circuits / proofs) or @circuits plus infra, once per incident plus "cleared"; the 06:00Z preflight probe joins it |
| Deactivating workloads for Kueue quota | No longer needed: holders request only their GPU since 23:09Z (#724) |
| Commit phases by hand | Later: a per-phase split in held-idle-hourly once circuits names where the phase timestamps are |
| Dispatcher failing 2:42–5:05 PM | Context: #732 is on ci's next train |
