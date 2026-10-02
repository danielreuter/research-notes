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

**Delivered, 00:40Z:** the alert relay is live (PR #738, tmux `n1-alerts` on infra's VM). Posts go in #agent-coordination,
not #agent-alerts, because only there do they ring the owner's doorbell (told circuits and proofs, 1790901690.784619).

**old-circuits-and-proofs (00:26Z):** Cost: train checks that failed on cheap repository tests (wall-clock, markdown size
caps) after 30-50 min of slot time, three trains today. Worked around: running those two test files before launch;
cancelling queued checks by killing runner pids over ssh; reading slot ownership with fuser on the lock files. Fix next:
`research run cancel <id>` that also cleans check's Lean scratch (with #708), plus a `research slots` view.

**Triage for old-circuits-and-proofs, posted 00:45Z (1790901907.617489):**
| Item | Call |
|---|---|
| Cheap repository tests failing late | Yes, infra, done: PR #739 runs all of `tests/test_repository.py` (~2 s) in check's preflight |
| Slot holders view | Yes, infra, by 06:00Z: read-only `tools/check/slot.py --status` (holder pid, command, start, blocking windows) |
| `research run cancel` with Lean scratch cleanup | Later, infra: scoped once #708 lands, after tonight's goals |

**Delivered, 00:49-00:55Z:** `tools/check/slot.py --status` (PR #741, owed 06:00Z); the hourly per-node preflight probe for
network-accounting's round 6 ask (PR #742, tmux `preflight-probe`; first pass passed on both nodes). Every round 6 and 7 yes is
now delivered; the open items are the "later"s (`research run cancel` after #708, per-phase held-idle).

## Round 8: proofs, compute-accounting (12:48 AM PDT)
- Asked 07:48Z, 2 Oct, in one announcement (ts 1790927339.192449), almost 4 h late: the 04:00Z timer reached infra at 07:47Z.
  Next in rotation after circuits. Neither was in a timed window or an incident (proofs has an 8 AM PDT Lean deadline, so
  answers may be short). The ask lists what shipped since round 7 so it doesn't come back: `research cancel` (#788, round 7's
  "later" for old-circuits-and-proofs, without the Lean scratch cleanup), `slot.py --status` who-asked (#782), node 2's uv
  (#785), the gpu_stray race (#790), node 2's slot `d` back in use, and `research deploy` (#777).

**compute-accounting (07:50Z):** Cost: shells on its VM lost the injected secrets during the night, so about 40 ssh, store
and Slack calls went through a polled tmux login shell (8-25 s each). Worked around: reading run dirs over ssh because
`research status` and `inspect` don't find a run launched from another VM; storing a log as `evidence/v1` after a warning on
`log/v1`; grep on node 2 (no rg); `suites.py --quick` at 21/22 until #733. Fix next: `research status` and `inspect` resolve
any run id from the store or the node, whichever VM launched it.

**proofs (07:51Z):** Cost: worker VMs can't record a check or push to the store (no R2 endpoint or bucket, no machines), so
every worker check and fixture push goes back through proofs (a 109 MB fixture sat in one worker's local store); shells
also lose their secrets. Worked around: `research fetch RUN`, or reading stderr.log over ssh, to see where a check is (the slot
line said "3-4 check(s) ahead in line" for 45 min, with no names and no ETA); `vmsg.py read --since --json` plus a
filter, because `research msg read --as` refuses `--since`. Fix next: let any worker VM record a check and push to the
store, either by giving worker VMs the R2 settings and machines, or by having `check --record --on POD COMMIT` use the
pod's own custody key.

**Triage, posted 07:58Z (1790927901.722399):**
| Item | Call |
|---|---|
| Shells losing injected secrets (both) | No: the Cursor platform; #753 makes the tools say so. Context: the `tmux wait-for` one-liner avoids polling |
| `research status` / `inspect RUN` for a run launched from another VM (both) | Yes, infra, by 11:00Z: find it on the registered machines or in the store, then fetch as `status --refresh` does |
| Kind for a plain log | No change: `evidence/v1` is the documented kind for logs and verdicts |
| rg on the nodes | Yes, infra, done: installed on both nodes, #794 adds it to vm_setup.sh |
| `suites.py --quick` 21/22 | Context: #733 is in the lander's train 6b3d704c8 (check r20261002-072246-b9fe) |
| Worker VMs recording checks and pushing to the store | Later, by 09:00Z through top: the same missing secrets. Letting nodes mint custody keys puts a long-lived R2 key on them, a credentials call; recommend keys stay off the nodes. To merge, a ready PR needs only the lander's train check |
| Slot line with no names or ETA | Yes, infra, by 10:00Z: name the checks ahead and how long each slot has been held (on #782). At 07:57Z node 1 had 8 waiting for 3 slots, about 35 min a check |
| `research msg read --as NAME --since TS` | Yes, infra, by 10:00Z |

- 09:22Z delivered (round 8): `research inspect|status|fetch RUN` for a run another VM launched, #808 (queued ready; told
  compute-accounting and proofs in the round's thread). Also #795 (`msg read --as NAME --since TS`), #798 (slot wait line names
  holders and waiters ahead).

## Round 9: network-accounting, console (2:26 AM PDT)
- Asked 09:26Z, 2 Oct, in one announcement (ts 1790933203.799969). The 08:14Z timer reached infra at 09:25Z. Next in rotation
  after compute-accounting: memory-accounting skipped (its node 2 soak window runs to 14:45Z), so network-accounting and console.
  The ask lists what shipped since their round 6: the control-pod contract (#735), the preflight probe (#742), and #808, #795,
  #798, #805 (queued ready).

**network-accounting (09:27Z):** nothing new; paused since round 6, its only work one statement review (#744) with no servers.

**console (09:27Z):** Cost: getting evidence-store files onto its machine (the laptop has no R2 remote, node 1's research user
no store remote; the pous-explorer data took three round trips). Worked around: Vercel production deploys from a git-archive
copy on Daniel's laptop failed "Not authorized" until `--scope compute-6da2eae4`. Fix next: node 1's load (94-146 tonight)
stretched the console's publish pass from 15 s to 80 s (timeout 240); a reserved core or priority for verity-console.service,
and a supported read-only way to fetch art ids.

**Triage, posted 09:31Z (1790933499.970139):**
| Item | Call |
|---|---|
| network-accounting | Nothing new (1 quiet round for it) |
| Store files onto console's machine | Yes, infra, by 12:00Z: a `store-fetch` dispatch template on node 1 (like #799's store-push), the pods' own R2 Secret, art ids into a dir console reads |
| Vercel `--scope` | No infra change: console's deploy step; put the scope in its command or pin orgId in `.vercel/project.json` |
| Console pass slowed by node 1's load | Yes, infra, by 11:00Z: drop-in `AllowedCPUs=0-7` (no slot or pod uses them) + CPU/IO weight; unit files from the `infra/nebius` branch into `research deploy`. Measured 09:30Z: 15 s wall, 8.7 s CPU at load 48 |

**Delivered 09:51Z (reply ts 1790934642.423509):**
- Console pass: #809 (stacked on #777, queued ready). `verity-console.service` runs on cores 0-7 with CPU/IO weight 1000. Both
  units are in `deploy.toml`, and `research deploy install` reloads systemd after a changed unit. Installed on node 1 via
  `research deploy` at 09:39Z. Passes since: 13.8 s and 14.3 s at load 70-220 (before: 15-80 s, one 145 s at 08:10Z).
- Store files: #810 (stacked on #799, queued ready). The `store-fetch` dispatch template takes full art ids into
  `/workspace/jobs/store-fetch/<NAME>/<hex>/` through a scratch store it removes, reading the remote with the pods' Secret only.
  Smoke run on node 1: 2 artifacts, 8 files, about 10 s.

## Round 10: old-circuits-and-proofs, circuits (5:09 AM PDT)
- Asked 12:09Z, 2 Oct, in one announcement (ts 1790942941.230899). The rotation wraps to old-circuits-and-proofs and circuits
  again; memory-accounting is skipped a second time (its node 2 soak window runs to 14:45Z). The ask lists what shipped since
  their round 7: the relay's identity refresh (#813, live), and #788, #782, #798, #808, #790, #777 (queued ready).

**old-circuits-and-proofs (12:09Z):** Cost: slot d. Three train checks died taking it (the runner's 0-127 affinity), then a stale
slot list kept it unused; #701's test passed on VMs and failed on both nodes because it read the real `check-d.lock` (two train
checks and a hedge). Worked around: cancelling by killing runner pids (now TERM to the workload pgid via a helper); reading slot
holders and run state over ssh; building trains in ad-hoc worktrees with shell chains, one of which fell back to its main checkout
and put an unchecked merge on main (#816 guards the push now). Fix next: `research cancel RUN`, and a `research train build BASE
PR@HEAD ...` that merges in a scratch worktree, fails fast, checks tree identity and the PROTOCOL.md caps, and pushes the prep branch.

**Triage for old-circuits-and-proofs, posted 12:14Z (1790943279.674089):**
| Item | Call |
|---|---|
| Slot d affinity, stale slot list | Done on main: `slot.py` skips a slot outside its own affinity (35beb61c9, #789), rereads the slots file every retry (3b1da247a) |
| #701's test read the node's `check-d.lock` | Done: a6d71c7c5 (autouse `FILL_YIELD_LOCK`), on main since 9699b2f28; no new guard (the suite guard sees repository files only; one case) |
| Cancel by killing pids | #788 `research cancel RUN` (custody kept), queued ready, merges clean on b16313242: ride the next train. Lean scratch: later, after #708 |
| Slot holders and run state over ssh | #808 (clean), #782 + #798 (conflict with main's `slot.py` after #789): infra merges main and re-queues by 13:00Z |
| `research train build` | Yes, infra, by 14:00Z: `research merge --train --prepare BRANCH [--onto BASE] N@SHA ...` on merge.py's train chain: scratch worktree only, PR heads pinned, fail-fast, check's preflight lints, push without force, remote tree confirmed |
