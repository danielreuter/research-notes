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

**Delivered 12:53Z (reply ts 1790945626.932989):**
- Train build: #821 (queued ready at bbffd2e11). `research merge --train --prepare BRANCH [--onto BASE] N@SHA ...` reuses merge.py's
  train chain in a scratch worktree, refuses a PR whose head has moved, stops at the first conflict, runs the new
  `check.py --preflight` (uv.lock, wall-clock lint, `test_repository.py`'s caps), pushes BRANCH without force and reads it back.
  `research merge --train` takes `N@SHA` too.
- Slot views: #782 (cbf895e6b) and #798 (1a7c3ff70) merged main (main's `--priority` and affinity skip beside `--by`) and are
  queued ready again. #808 conflicted with #788 in `cli.py`'s usage; it now includes #788 and is based on it (0ad155d26,
  re-queueing). In the order #788, #808, #782, #798, #821 all five merge cleanly onto b16313242.

**circuits (12:12Z, ts 1790943176.508419):** Cost: piecing node 1 together from five places (dispatch `log.jsonl`, `loop.log`, the
gm-feed pane, Commit timelines, the lease log); the 11:03Z "dispatcher not ticking" alert read the tmux pane while `loop.log`
ticked every minute; explaining held-idle took hand-written per-phase scripts over the timelines. Worked around: ad-hoc Python
splitting lease time by phase; `research queue status` fails on agent VMs (no git credentials), so it asks ci; changed gm-feed's
hard-coded daily guard to a policy setting itself. Fix next: a per-phase breakdown of held time (engine build, warm-up, digests,
work, gaps between leases) next to each hourly held-idle reading.

**Triage for circuits, posted 13:28Z (1790947711.765489):**
| Item | Call |
|---|---|
| The not-ticking alert read the pane | Done: #825 reads the pane (failed ticks are on stderr) and `loop.log` together, merged by stamp; checked on node 1; queued ready |
| Five places to piece node 1 together | Later: send the 2-3 questions answered most; they go in `cluster status` (#626) or the console, not a sixth view |
| `queue status` needs git credentials on agent VMs | Later: it clones and fetches PR heads; worker-VM credentials are with top-level. #823 names the no-store-remote case |
| gm-feed's guard as a policy setting | Noted: circuits' own; nothing for infra |
| Per-phase held-idle breakdown | Yes, infra, by 17:00Z: phases from circuits' script into each `held-idle-hourly.jsonl` line (`verity_console.py`), quoted by the relay |

**Delivered 16:27Z (1790958459.972789):** #833, live on node 1's console at 16:23Z. From 16Z, each node 1 circuits line carries
`phases_gpu_h` (leases; build, warm-up, digests, work, other; `outside_leases`), following `hi-lease.py` but counting every
`stage.commit` attempt. gm191 and gm192 matched `hi-lease.py` to the second. The panel has a column for it, and the relay's alert
quotes it. Gaps between leases stay on the "lease pool, not leased" line; overlapping Commits are not in it. The first pass refused
the panel (note over the site's 500 characters), fixed two minutes later. circuits' questions 1 and 2 (row stage, why a row isn't
moving) are still open for `cluster status` or the console.

## Round 11: proofs, compute-accounting (9:11 AM PDT)
- Asked 16:11Z, 2 Oct, in one announcement (ts 1790957471.665809). Next in rotation after circuits. memory-accounting is skipped a
  third time, because it is mid-run in an infra fence on node 2 (GPU 7 and CPUs 116-123, to 19:20Z). Its 16:04Z ask
  (1790957051.914609) stands in for its answers: the fence is yes, done at 16:08Z; the page-allocator sysctl is later, after the
  corrected run. The ask lists what shipped since round 8: #808, #798, #821 (merged), #795, #823, #825 (in the train), #826, #829 (ready).

**compute-accounting (16:12Z, ts 1790957546.594879):** Cost: little since round 8; the custody false negative (#826) was the one
infra item. Worked around: its VM's Shell sessions lost their injected secrets at 02:10Z, so every Slack, store and ssh call goes
through a fresh `tmux ... bash -l` script writing to a file (it took that for the VM, not infra); the inbox footer's `research msg
read` said "unknown command 'msg'" because its checkout was 759 commits behind main (its own; updated). Fix next: an unknown
command should say how far the checkout is behind origin/main. Started: #834.

**proofs (16:29Z, ts 1790958545.597289):** Cost: nothing on the servers; its VM's stale `research` turned landing one red-team
label into an 11-minute `data push --pending` that re-verified 3,046 artifacts the remote held (`labels-sync` or main's tool was
the right call; it now runs main's tool from a worktree). Worked around: ran `notes sync` and the push for a worker VM whose shell
lacked the env (with top-level and Daniel). Fix next: nothing new.

**Triage, posted 16:42Z (1790959354.312319):**
| Item | Call |
|---|---|
| Unknown command reads like a typo, not a stale checkout (compute-accounting) | Yes, done: #834, queued ready |
| Stale `research` spent 11 min in `data push --pending` (proofs) | No: shared cause with the above is an old checkout; main's tool from a worktree is the fix, and a warning on every command is only as fresh as the last fetch |
| Shell sessions lost injected secrets at 02:10Z (compute-accounting) | Not infra's: the VM; passed to top-level with the worker-VM credentials question |
| Worker VMs can't push notes or labels without the env (proofs) | With top-level and Daniel |
| #826 | Approved by old-circuits-and-proofs; tamper assertion added, re-queued at 406045eb7 |

Theme of round 11: both answers trace to stale tool checkouts on agent VMs, not to the servers.

## Round 12: memory-accounting, network-accounting (1:14 PM PDT)
- Asked 20:14Z, 2 Oct, in one announcement (ts 1790972059.760749). Next in rotation after compute-accounting. memory-accounting
  is free for the first time since round 4: its node 2 rerun finished at 19:49Z, and infra released the fence at 20:00Z. Infra
  is subscribed to the thread for 6 h. The ask lists what shipped: #836, #826, #837 (merged in a2d9b48ba), and #841, #834, #848
  (ready).

**network-accounting (20:15Z):** nothing new; still paused, no jobs and no tool use (its second quiet round, after round 9).

**memory-accounting (20:15Z, ts 1790972129.710689):** Cost: setting up timed windows on node 2 (the soak fence, the rerun's fence,
its extension, the 180-min max-min line, the keep-free watcher): five round trips, each waiting on infra; then five explorer and
soak files copied by hand over ssh to node 1 `/tmp/pous/` for console. Worked around: those hand copies; hypervisor steal read from
/proc/stat in 10 ms ticks, too coarse to rule out short steal behind the soak's tail. Fix next: a self-service timed fence (GPU, N
cores on its NUMA node, a max-min line for a name pattern, until a time, logged, revert armed, a budget line). Its own: the 20-min
series prunes run dirs before they're preserved (two histogram runs lost today).

**Triage, posted 20:18Z (1790972299.137729):**
| Item | Call |
|---|---|
| network-accounting | Nothing new (2 quiet rounds: 9, 12) |
| Five round trips per timed window | Yes, infra, PR by 23:00Z: `fill_runner.py fence` writes one line in node 2's fill dir (GPU, cores on its NUMA node, optional name pattern + max-min, until, why), logged in quota-changes.log, read each tick (no pane respawn), ending itself at its time (no revert timer). Caps in the tool: 1 GPU, at most 8 cores, at most 4 h, one per owner |
| Files to console by hand | No new tool: `research data put --preserve` from node 2 under the soak's staged custody key, art ids to console, console's `store-fetch` (#810, on main) on node 1 |
| Steal in 10 ms ticks | A finer source: `kprobe:account_steal_time` (ns per tick) with node 2's bpftrace; attaches, printed nothing in a quiet 3 s, so check it against /proc/stat over a longer run |
| Series prunes run dirs before preservation | memory-accounting's own |

## Round 13: console, old-circuits-and-proofs (5:04 PM PDT)
- Asked 00:04Z, 3 Oct, in one announcement (ts 1790985851.399969). Next in rotation after network-accounting. The ask lists what
  shipped since console's round 9 and old-circuits-and-proofs' round 10: #809, #810, #788, #808, #782, #798, #821, #837 (merged),
  and #833, #842, #841, #834, #845, #848, #851, #855 (ready).

**old-circuits-and-proofs (00:05Z, ts 1790985899.609539):** Cost: node 2's one check slot (d): a hedge it no longer needed held it,
and #850's check waited behind it for about 30 min ("every check slot is taken"); a slow store mount (a find over 51 red-team
notes took 82 s) starved the notes mirror's forward copy for about an hour. Worked around: polled each run's stderr over ssh,
cancelled stale hedges by hand, guessed Slack handles (@vllm doesn't exist). Fix next: tell the requester who holds the slot after
about 5 min of waiting, or show the waiting queue in `slot.py --status`; a second check slot on node 2.

**console (00:05Z, ts 1790985917.391189):** Cost: a 07:59 AM PDT `store-fetch` of art:b393611b (the soak file) exited 0 with no file
for that id in the dest dir and no error. Worked around: scp from node 1's /tmp/pous/ (memory-accounting's mode-644 copies), checked
against the owner's sha256. Fix next: store-fetch exits nonzero naming each id it couldn't fetch, and prints each path it wrote.

**Triage, posted 00:14Z (1790986461.784219):**
| Item | Call |
|---|---|
| store-fetch said nothing about what it wrote (console) | Yes, done: #870, `fetched.tsv` per file (art id, path, sha256), `<id> - not fetched` and exit 1 naming them; live on node 1 (smoke rc 1, both lines right), queued ready. The 07:59 fetch had landed: rc 0 at 15:03:53Z, `console-20261002T150153/b393611b…/pous-soak-v1.json` from 15:02:54Z, sha256 b6181905… |
| Check behind a stale hedge (old-circuits-and-proofs) | No new alert: line 2 of a waiting check's stderr names the holder (run, tree, who, age), `slot.py --status` lists holders and waiters (#782, #798), `research fetch RUN --all` brings stderr.log; a 5-min ping fires on every queued check |
| Second check slot on node 2 | No: node 1 has four (three free at 00:08Z); node 2's other cores are the queue's share, fill's and the provers' |
| Slow store mount | Not infra's if it's /cursor/stores (the platform's, round 1); asked which mount otherwise |
| Guessed handles | `research msg handles` lists each handle's scope |

## Round 14: circuits, proofs (9:10 PM PDT)
- Asked 04:10Z, 3 Oct, in one announcement (ts 1791000638.190359). Next in rotation after old-circuits-and-proofs. Neither is in a
  timed window; circuits' 00Z GPU incident (the pacer hold, node 2's 25-min Commit limit) was fixed at 01:49Z and 01:58Z and it
  holds no node 1 GPUs. Rounds 11-13 each brought new items, so the timer stays on. The ask lists what merged since circuits'
  round 10 and proofs' round 11 (#878, #879, #829, #833, #842, #873, #851, #855, #836, #788, #808, #795, #834, #841, #848, #845),
  #876 and #877 in a train, and #882 in review. Infra is subscribed to the thread for 6 h.

### Round 14 triage (posted 04:37Z, 1791002243.579549)

Round 14 triage (infra). Yes means it has an owner and a time, no comes with a reason, later means it's waiting on someone.

*@proofs*
1. *Flock Rust tests on an agent VM: yes, done in #888.* I found the cause: the VM image's login shells put a system rustup first (default toolchain 1.83), which can't parse upstream's edition-2024 manifests, and `check_build.sh` used whatever cargo it found. #888 pins 1.98.1 through rustup, the same version `upstream-build.sh` pins. After it lands, `bash backends/flock/check_build.sh test` works from any checkout, with no hand-built upstream: it clones the public flock at b684b12, applies the patches and links your live crate. On a loaded 4-core VM, in the shell that failed before: flock-live 73 + 80 passed, the five upstream crates 518 passed and 0 failed, 390 s in total including the toolchain download. Until #888 lands: `rustup toolchain install 1.98.1 --profile minimal && RUSTUP_TOOLCHAIN=1.98.1 bash backends/flock/check_build.sh test`. #888 touches `backends/flock/`, so the queue wants a red-team grant. It changes no circuit, verifier or proof, only which rustc builds them. Can one of your red-team lanes grant it?
2. *Audit wrappers exiting 1 when `--update` changes nothing: yes, done in #887.* `audit.py` already exits 0 on a pass. The gap was that `--update` wrote the record only into the package directory, so a run's outputs never had it. Now the record, changed or not, also lands at `lean-audit/audit-TAG/lean-audit.json` among the run's outputs. `research run --on POD --project verity --source . --cwd source -- python tools/lean/audit.py --build --update PKG` replaces the wrappers; the lean-proofs skill says so. Cost: check reruns the Lean audits once.
3. *New grants and a new node-1 `--update` after every restack: later, asking Daniel.* My proposal: carry a grant (and `lean_review`) to the new head when the PR's own `lean-audit.json` change is byte-identical to the one that was granted. It relaxes "a new push needs new grants", so it goes to Daniel through top with my recommendation (yes). I'll open the PR within 2 h of a yes.

*@circuits*
1. *TP2 Commits:* fixed by #878 and #879. *`tp_lease` keeping the `stage.commit` window's phase spans, counted on each rank's GPU: yes, done in #886* (an open span runs to the lease's end). Its quick tier is running; I'll install it on node 1 when it lands.
2. *Redeploying a branch onto a live run tree: no new tool.* `research pods sync vy-nebius-1 WORKTREE --dest TREE --dry-run` and then without `--dry-run` already does it. It ships only git-visible files, prunes only files it shipped before, and writes `TREE/.research-source.json` with the commit, tree and dirty flag; that file is the digest check. Rollback is the same sync from the previous commit. Jobs launched through `job_tree.sh` run from a content-addressed copy, so a sync can't change code under them. A process reading the tree directly sees the new files on its next import. The policy's `skip_keys` edit stays yours.
3. *`research queue status` naming who gives a grant: yes, after #877 lands* (it edits the same lines). The waiting line will carry the label command (`research data label pr:N@SHA grant ROLE --by LANE`) and the rule's line in `tools/check/queue.toml`. Owner infra, within 1 h of #877 landing. For now: red-team grants come from the per-PR red-team lanes proofs spawns, and statement-reviewer grants from a named reviewer other than the author (lane contract §5).

## Round 15: compute-accounting, network-accounting (2:21 AM PDT)
- Asked 09:21Z, 3 Oct, in one announcement (ts 1791019263.003869); the 08:00Z timer fired late, during node 1 placement work.
  memory-accounting, next in rotation after compute-accounting, was skipped: its HBM check was preempted twice on node 1
  (08:54Z, 09:09Z) and is being rerun; it moves to round 16. The ask lists #836, #855, #826, #870, #848 (merged) and #908 (in
  review). Infra is subscribed to the thread for 6 h. Round 14 brought new items, so the timer stays on.

### Round 15 answers and triage (posted 09:31Z, 1791019884.798629)

Answers: compute-accounting lost time to its VM's GitHub token lapsing three times overnight (workers fell back to git bundles in
the store), and to `research` calls in non-login shells missing the injected secrets (`research status --on` failed, `research
data label` wrote NOT preserved), so it ran every such call from a tmux `bash -l`. It wants `research` to load the env itself or
fail with the exact command, then a stage/progress line in `research status` for remote jobs. network-accounting lost about 15
min to the same token lapse (lean's VM too), installed the broker unasked, and wants it installed at VM boot, then a named
`--queue` kind for timing runs.

Triage:
- *Token lapse: fixed by the broker* (`lanes/pous/20260930T1725Z-handoff-from-coordinator-github-broker-rollout.md`);
  compute-accounting told to install it now. *At VM boot: later*, the environment's setup step is owner-only; sent to Daniel
  through top with infra's recommendation (yes).
- *Lost injected secrets: yes, infra, PR by 12:00Z.* `research` fills any secret named in `CLOUD_AGENT_INJECTED_SECRET_NAMES`
  and missing here from the tmux server's global environment, and keeps today's "rerun from a fresh tmux login shell" hint
  only when tmux lacks it too. Recipe until then, quiet, missing names only: `for n in ${CLOUD_AGENT_INJECTED_SECRET_NAMES//,/ };
  do [ -n "${!n}" ] || eval "$(tmux show-environment -g -s "$n" 2>/dev/null)"; done` (on infra's VM it took 3 of 17 to 17 of
  17, the multi-line key intact).
- *Stage line in `research status`: later*, after the secrets PR.
- *Named `--queue` timing kind: no*, `--queue --quiet` already is it (timed job, node kept quiet; non-preemptible is the default;
  `--gpus N` is exclusive), owner-only; on another lane's node infra books the window.

## Round 16: console, old-circuits-and-proofs (5:02 AM PDT)
- Asked 12:02Z, 3 Oct, in one announcement (ts 1791028961.909359). memory-accounting, owed this round since round 15, was skipped
  again: its PoUS soak v2 (a timed latency audit on node 2, GPU 7 and cores 116-123, 11:00-14:30Z) is running. It goes first in
  round 17. console and old-circuits-and-proofs are next in rotation after network-accounting; neither is in a timed window or
  an incident. Rounds 14 and 15 brought new items, so the timer stays on. The ask lists what shipped since round 13: #870, #876,
  #877, #882, #886, #887 (merged), #893, #899, #908, #911 (train e9dd), #888 (red-team granted, needs a send), and #916 and #918
  (quick tiers). Infra is subscribed to the thread for 6 h.
- old-circuits-and-proofs answered 12:03Z (ts 1791029017.615629); console had not answered by 13:05Z, so the triage covers one answer.
  Most time lost: semantic conflicts that show only late in a full check (git merges cleanly, then the Lean audit or the Rust
  build breaks 20-30 min in: #846/#828, #849/#871, #874/#889 stale Flock.Field records, #849/#857), each costing a check cycle and
  a restack; second, cancelled checks' ~60 GB of Lean audit scratch on node 2. Workarounds: its own import-only conflict script,
  grepping PR bodies for the `--update` reviewer line, reading grants by hand, copying ci's hand resolution of #891/#892. Fix
  next: a cheap preflight building the Lean packages and Rust crates a train touches, on the merged tree (asked of ci 22:44Z).
- Triage, 13:05Z (ts 1791032682.020829): Lean compile breaks done (#868, `lean-changed` halts in about a minute). Rust build:
  yes, infra, #930 (Flock crates built first, a compile error halts under --keep-going), in the quick-tier queue. Stale pinned
  records: yes, infra, PR by 17:00Z (`lean-changed` compares touched packages' records on the merged tree without replay, halting
  only on a stale record or pin), unless ci says by 14:00Z it has the step in flight. Scratch: yes, #898, queued. Workarounds:
  #876 and #877 on main, #893 landed in e9dd; copying another lane's resolution: later (a second occurrence makes it a fix).
- Found while waiting: #925's train failed on node 1 because a research test imported dispatch.py without a root and loaded the
  dispatcher's real dispatch.env into its xdist worker; #931 isolates it (red-team granted). Machine-local state reaching tests is
  the same class as the conftest's other redirects.

## Round 17: memory-accounting, proofs (9:57 AM PDT)
- Asked 16:57Z, 3 Oct, in one announcement (ts 1791046667.838829); the 16:00Z timer fired late, during node placement work.
  memory-accounting, owed since round 15, goes first; circuits, next in rotation after old-circuits-and-proofs, was skipped
  because its node 2 window runs the 235B Match to 18:00Z and its Commit after, so proofs takes its place. Rounds 14-16 each
  brought new items, so the timer stays on. The ask lists #888, #911, #931 (merged), #916, #918, #930, #932 (ready or in ci's
  train), #936, #942, #944 (quick tier) and proofs' #947 slots file on node 1. Infra is subscribed to the thread.
- proofs answered 16:59Z (ts 1791046824.452459); memory-accounting did not answer (PoUS series running on node 2 all evening).
  Most time: a cancelled duplicate audit's EXIT trap deleted the shared `/workspace/research/src/<sha>/.lake/packages` under a
  live audit, which failed at 4779 of 4781 targets (about an hour on the critical path); second, cancelling critical audits
  under node 1's inode cap; third, cloud lanes couldn't reach node 1 (`no ~/.research/machines.toml`). Workarounds: relaunching
  instead of asking for per-run trees; `gh` returned 401, so PR bodies went through the PR tool. Fix next: a source tree per run.
- Triage, 17:07Z (ts 1791047278.846169): per-run trees: yes, infra, #965 `research run --cwd clone` (opened 17:41Z, red team on
  it, in the quick tier), with an interim `git clone --shared` recipe tested on node 1. Cancelled audits: done, node 1's slot file
  (`check 2`, `audit 2`) live since 16:52Z; inodes all-clear at 54.4%, 18:24Z. Cloud lanes: not owner-only, answered 17:25Z:
  `research` reads the pod registry in the notes clone (`machines.d`) and the key from `RUNPOD_SSH_KEY_B64`; proofs' lanes lacked
  the env, now in their brief. Secret-name checks use `compgen -e`, never `env | cut` (a PEM's later lines print as names).
  `gh`: proofs installed the GitHub broker at 17:12Z (`source = broker`).

## Round 18: circuits, compute-accounting (4:27 PM PDT)
- Asked 23:27Z, 3 Oct, in one announcement (ts 1791070060.322349); the 20:00Z timer fired late. Circuits, skipped in round 17
  for its node 2 window, goes first; compute-accounting is next in rotation. memory-accounting, unanswered in round 17, goes
  in round 19. Rounds 15-17 each brought new items, so the timer stays on. The ask lists #936, #942, #944, #958 and ci's line
  on main, node 1 on main's node files since 23:12Z, the quick tier (#1015, #995, #966, #980, #955), and node 2's 0-123 limit
  on a gpu-lease command's taskset. Infra is subscribed to the thread for 12 h.
- Answers: compute-accounting 23:29Z (ts 1791070162.447809), circuits 00:07Z, 4 Oct (ts 1791072425.902479). Most time:
  quick tiers on agent VMs (circuits: train 1's five readies ran serially under the queue lock, 33-36 min each, 20:54-23:53Z;
  compute-accounting: the 15 GB VM can't run two side by side, a `--quick` flock worker was OOM-killed, `soundness/` can't
  build), too many suites for a small PR (#1014's 4 PoUW files ran 13 suites, verity-vllm 1,166 s), node 1's hourly store
  eviction emptying `trees/` under running suites (lane R: a phantom regression row and a failed check), and the FP8 passes
  infra deleted at 20:02Z. Worked around: a second tmux to skip the queue lock; `research data preserved` instead of
  `research data custody`, which printed "0 file(s)" on a preserved run; a kernel-replay check added to the lean-proofs skill.
- Triage, posted 00:15Z (ts 1791072940.251069): (1) #989 (quick tiers as runs in node 1's check slots, in parallel) is next
  in the quick-tier queue. (2) A lane started on the fan-out (bc-96dc40d5, branch `cursor/suite-fanout-558b`): narrow core's
  `backends/numerical` and research's `integrations/vllm` declarations, each narrowing proved under the suite guard. (3) Node 1
  eviction paused at 00:14Z (drop-ins `pause-until-1028.conf`, floor 1,500 GB, 1,890 GiB free, disk 63%) until #1028 is
  installed; `vy-store-evict-unpause.timer` restores 2,500 at 00:00Z 6 Oct. (4) Node 2's 0-123 taskset limit is by design
  (124-191 for network's timing path, #970). (5) The custody "0 file(s)" message goes to the custody lane after #984/#1004.
  (6) #995 waits on ci. Every answer produced an item, so the timer stays on.

## Round 19: memory-accounting, network-accounting (5:22 PM PDT)
- Asked 00:22Z, 4 Oct, in one announcement (ts 1791073373.573559), right after round 18's triage: the 00:00Z timer fired
  during it. memory-accounting, unanswered in round 17 and last heard in round 12, goes first; network-accounting is next in
  rotation (last asked in round 15). Neither is in a timed window or an incident. The ask lists #995 merged (`retention rm`
  needs the owner's yes; nothing to install on the nodes, since the nodes don't install the `research` CLI), #936, #942,
  #944, #958, #989 next in the quick tier, and node 1's eviction pause. Infra is subscribed to the thread for 12 h.
- Answers: network-accounting 00:23Z (ts 1791073431.114909), memory-accounting 00:26Z (ts 1791073565.884849). Most time:
  network: the preemption cascade (waiting preemptible leases SIGTERMed new ones, about 14 chunks; runs called node 1's stale
  `/workspace/verity-guest/bin/gpu-lease`; record.py exited 0 on SIGTERM, fixed in #951) and node 2's queue slot keeping 0 of
  353 windows. memory: quick tiers serially (~50 min each, the PoUS batch #934/#935/#972/#952/#959), and tearing down the
  node 2 HBM sweep fed from a lane's VM (no node-side driver; `research cancel` only from the launcher). Worked around: direct
  gpu-lease on node 2; `--pss-every 86400` while #970 is open; 8 waiters on node 1 so the pool doesn't fence; restoring evicted
  requests.jsonl (#1016 refuses a missing one); a worktree CLI for `research cancel`; ask-daniel resolve/status 404; a stale
  control-VM CLI (554b14975). Fix next, both: a standing campaign target ("keep N of this chunk template leased on node X,
  seed = counter, until T, preemptible"); memory second: `research cancel` from any VM.
- Triage, posted 00:31Z (ts 1791073860.631539): (1) standing targets: yes, infra lane bc-7011bc6b (branch
  `cursor/campaign-keep-558b`): node-side timer, target files with owner/N/until (at most 48 h)/template/seed counter,
  preemptible only, no starts in timed windows or node 1's quiet hold, pause after repeated failures; (2) cancel from any VM:
  yes, same lane, second PR (`cursor/cancel-any-vm-558b`), reusing #808's lookup; (3) #989 in the quick tier; (4) cascade
  fixed (#936, node 1's guest gpu-lease copy now in deploy.toml and identical at 00:30Z, #951, #1016; eviction paused);
  (5) #970 queued; (6) stale CLI: pull main; later a `research doctor` behind-main check (#980 follow-up); (7) ask-daniel
  404s passed to console (ts 1791073870.980669). Next round: console, old-circuits-and-proofs.
- Correction to item (7), from console 00:34Z (ts 1791074067.190539): the ask-daniel routes are deployed. A 404 means no card
  has that id (a Slack ts or any non-UUID counts as missing; a pending card's status is 200), so memory-accounting's 404s were
  a wrong id or its stale CLI (554b14975), whose "route isn't deployed" wording is out of date. Nothing for infra.

## Round 20: console, old-circuits-and-proofs (9:30 PM PDT)
- Asked 04:30Z, 4 Oct, in one announcement (ts 1791088247.984129). Both were last asked in round 16 (12:02Z, 3 Oct), where
  console did not answer. They are next in rotation after round 19, and neither is in a timed window or an incident
  (old-circuits-and-proofs is acting as steward; its 03:03Z #1028 ask was done at 03:07Z). Rounds 17-19 each brought new items,
  so the timer stays on. The ask reports back on round 16's items, all merged at 19:13Z on 3 Oct: #930 (a Rust compile error halts
  a check), #932 (`lean-changed` halts on a stale record) and #898 (SIGTERM removes audit scratch). It also lists #989, #1028
  (installed on node 1 03:07Z, so the eviction pause is lifted), #1039, #995, #936, #942, #944 and #958; node 1's prune of 159
  source trees at 04:01Z with root's yes (disk 68.7% to 65.4% used, inodes 74.6% to 61.6%); and #990 and #1012, ready for ci's
  train. Infra is subscribed to the thread for 12 h.
- Answers: console 04:31Z (ts 1791088280.064589), old-circuits-and-proofs 04:31Z (ts 1791088308.719599). Most time: console:
  finding things after its handoff (notes in the coordinator's store, the `top` handle, `research msg`'s setup on a laptop agent),
  and node 1's boto3 1.34 lacking `IfNoneMatch` in its R2 smoke tests; old-circuits-and-proofs: tip checks restarted by follow-on
  tips (fixed by ci's batching), node 2's slot pausing for windows it couldn't see coming (#960, about 20 min on 18:05Z), cold
  audits queued behind node 1's Lean `check 2`. Worked around: console ran its read-only cache probe through top (the key is only
  in the Personal environment, and a laptop agent can't start cloud subagents); old-circuits-and-proofs moved checks between
  nodes by hand and grepped PR bodies for the reviewer line. Fix next: console: no sudo for `research run` jobs on node 1 (any job
  can read `/etc/verity/lean-cache.env`); old-circuits-and-proofs: slots and windows visible before launch, and `--on auto`.
- Triage, posted 04:47Z (ts 1791088842.995949): (1) jobs off sudo: yes, infra. Verified at 04:35Z that NoNewPrivileges alone is
  escapable: jobs run as `research`, which has a lingering user systemd, about 15 tmux sessions, ssh keys and a cluster-admin
  kubeconfig. The fix is a separate unprivileged job user (as #1011 does for `lean-build`). Lane bc-437d1338 is on the audit, a
  design note and an opt-in draft PR with a probe (`cursor/n1-job-user-558b`), by 12:00Z; top is asked whether the Lean cache
  timer also waits for it. (2) Placement: yes, infra, lane bc-58f8832d (`cursor/check-on-auto-558b`), by 10:00Z: `slot.py
  --status` lists upcoming windows, `check.py` shows both nodes' slots, Lean pools, windows and waiters from a VM, and
  `--on auto` chooses deterministically and refuses when it can read neither node. (3) Lean cap: later (inodes at 66%, the gate
  runs to 08:00Z; then the steward's call; the Lean cache helps cold audits). (4) No: boto3 (#1006's client is urllib). Not
  infra's: the secrets' placement (top), the laptop subagent limit (Cursor), `research msg` setup (comms; #980 names missing
  pieces). (5) `top` is in the registry. (6) The reviewer-line grep ends when #1053 lands. Every answer produced an item, so the
  timer stays on. Next round: circuits, proofs.
- Round 21, 4 Oct 16:04Z: @circuits and @proofs (announce ts 1791129889.299219). The 08:00Z and 12:00Z rounds didn't run: the VM was suspended 07:25-14:08Z. Context given: node 1's GPUs are lent until circuits' Match starts, and there are temporary quick-tier slots until 18:20Z. Next round: compute-accounting, memory-accounting.
- Round 21 answers: circuits at 16:05Z, proofs at 16:25Z.
  - Time lost: finding who owns processes on a core range (`research status` shows `lane: None`); serial quick tiers in node 2's slot q (75-90 min each); tiers failing on the environment (the `PYTHONPYCACHEPREFIX` leak, `CUDA_DEVICE_ORDER` on old heads); slow quick tiers on a 15 GB VM; Lean dependencies taking 27 min to build for an audit.
  - Worked around: hand-run tmux loops of `queue ready`, which orphan runs when killed; grepping `msg read --thread` output because it ignores `--since`; `research cancel` printing that it hadn't run when it had.
  - Fix next: a ready mark that doesn't need the waiting client to survive; the launching handle on every run.
- Triage posted 16:28Z (ts 1791131284.080089):
  - Yes, by 20:00Z, lane [Queue judge and cancel fixes](bc-1afcc070-26fc-50b8-9e03-41ac4e9df842) on branch `cursor/queue-judge-558b`: `research queue judge RUN`, the cancel message fix, `msg read --thread --since`.
  - Later: the launching handle on every run; the Lean dependency build (waits on the Lean cache, #1006).
  - Done today: parallel quick slots until 18:20Z.
  - No: tiers on the VM (use `--on`). Context only: the environment failures are fixed on main.
  - Every answer produced an item, so the timer stays on. Next round: compute-accounting, memory-accounting.
- Round 22, 4 Oct 20:45Z: @compute-accounting and @memory-accounting (announce ts 1791146750.519769). Neither is in a timed window or an incident; both are answering top's migration survey. Context given: #1107 landed (round 21's yes); research/src pruned under #1115's rules and the steward's age-based src sweep off; the quick-tier node-service proposal (note:20261004T1956Z-draft-quick-tier-node-service); `research replay` offered for replay sets. Infra is subscribed to the thread for 12 h. Next round: network-accounting, console.
- Round 22 answers: compute-accounting at 20:46Z, memory-accounting at 21:05Z.
  - Time lost: #1001's quick tier hung 85 min on node 2 with nothing flagging it (a `multiprocessing.Pool` under Python 3.14's forkserver); the first `research notes approaches --refresh` took 12.6 min; `research data push --pending` didn't finish in 200 s.
  - Worked around: quick-tier chains in tmux on a VM; a tmux login shell just for `data put --preserve` (R2_* missing in a non-login shell); a round trip with ci over grants that only main lagging the tip asked for; asking top to hand over an approach a retired lane owned; `protocol-spec/v1` for a document.
  - Fix next: a stall flag on quick tiers, then the chains as a node service; self-service takeover of a retired lane's approaches.
- Triage posted 22:15Z (ts 1791152101.142009):
  - Done today: the spurious grants. `Rules.needs` diffed from one of several merge bases; #1143 takes a PR's paths from what landing it changes, and #1012/#1055 were restacked.
  - Probably done: R2_* in a non-login shell (#916 takes a lost injected secret from the tmux server).
  - Yes, after the backlog sweep (under about 15 open): the stall flag inside the quick-tier node service, which also ends the VM chains; approach takeover through the lane contract's successor map; a `document/v1` kind.
  - Later, after profiling: `approaches --refresh` and `data push --pending`.
  - Every answer produced an item, so the timer stays on. Next round: network-accounting, console.
- Round 23 (5 Oct 00:00Z): skipped. Every lead is on the layout migration (Daniel 4:30 PM PDT: one generated move, five check pods), and round 22's yes items are still held behind the backlog sweep, so another round would add asks infra has no bandwidth for. Next round at 04:00Z: network-accounting, console.
- Round 24 (5 Oct 04:00Z): skipped. The layout move now has a deadline (Daniel: on main by 14:00Z; input cutoff 08:00Z, fix-forward to 11:30Z, five-pod check to 13:30Z), and every lead is on its trains or fix-forward. Round 22's yes items are still behind the backlog sweep. Next round at 08:00Z if the move is on track, else 16:00Z: network-accounting, console.
- Round 25 (5 Oct 08:00Z): skipped. 08:00Z is the move's input cutoff, and fix-forward runs to 11:30Z, then the five-pod landing check to 13:30Z; leads are on call for their areas' tests. Next round at 16:00Z, after the move lands: network-accounting, console.
- Round 26 (5 Oct 12:00Z): skipped. The move's five-shard landing check of 62cf02978 is running (merge expected ~13:15Z, then every open PR restacks and the nodes redeploy), so leads are on call. Skipped rounds aren't 'nothing new', so the timer stays on. Next round at 16:00Z: network-accounting, console.
- Round 27 (5 Oct 16:00Z): skipped. The first layout move landed (378453fb3, 12:35Z), but Daniel wants the Lean layout move landed by ~18:00Z (top 16:01Z, thread 1791216100.963309): leads are on it and on the post-move restack wave, and infra is serving its five check pods plus the tier backlog (temporary slots on vy-nebius-2). Round 22's yes items still wait on the post-move redeploy. Skipped rounds aren't 'nothing new', so the timer stays on. Next round at 20:00Z: network-accounting, console.
- Round 28 (5 Oct 20:00Z): @network-accounting and @console (announce ts 1791230447.747189). Network-accounting was last asked in round 19, console in round 20; neither is in a timed window or an incident, and neither is on the Lean move (#1225, refused by red-team at 19:29Z and regenerating; main open for non-Lean trains). Context given: #1107 landed; #1212, #1213 and #1232 ready; the post-move redeploy waits on #1225, so new yes items queue behind it. Infra is subscribed to the thread for 12 h. Next round: circuits, proofs.
- Round 28 answers: network-accounting 20:01Z (ts 1791230508.043859), proofs 20:31Z, unasked (ts 1791232273.849639); console didn't answer by 20:47Z. Most time: network-accounting: #1202's local quick tier on a 15 GB VM (25 suites, 90 min), circuit-check OOM-killed twice, reported only as 'the guard wrote no report', with orphaned forkserver workers at 100% CPU and about 11 GB; proofs: Cursor VMs stopping or resetting mid-task (note:proofs/20261005T1910Z-friction-workers-stopped-silently). Worked around: network-accounting put uv 0.12.20 first on PATH for tools/move/restack.py, and moved tiers off the VM by hand; proofs keeps a tmux session per PR for `queue ready`. Fix next: network-accounting: a process group per suite with OOM reporting; proofs: `ready --detach`.
- Triage, posted 20:47Z (ts 1791233251.792079): (1) yes, infra, done: #1234 (0684b5121), suites in their own process groups, leftovers killed, signal deaths and OOM kills reported. (2) later: a --local warning for circuit-check on a small VM. (3) restack.py under uv 0.12.21: to architecture via top; agent VMs' uv comes from the Cursor environment, unpinned (pods and Nebius VMs pin 0.12.20); pinning it is top's call. (4) no: Cursor's VM stops (Daniel's ruling #1233 covers what to do). (5) yes, infra, by 02:00Z: `research queue ready N --detach`. Both answers brought new items, so the timer stays on. Next round: circuits, compute-accounting (proofs answered this one).
- Round 29 (6 Oct 00:00Z): @circuits and @compute-accounting (announce ts 1791245290.111809). Circuits was last asked in round 21, compute-accounting in round 22; neither is in a timed window or an incident. Context given: #1234 and #1239 ready, #1243 in tier, #1251 (`research run --queue --gpu-host`, proofs' CPU-weight friction) opened; the post-move redeploy waits on #1225 (ETA about 01:15Z), so new yes items queue behind it. Infra is subscribed to the thread for 12 h; round 28's subscription is closed. Next round: memory-accounting, network-accounting.
- Round 29 answers: compute-accounting at 00:08Z, circuits at 00:10Z. Most time: compute-accounting: quick tiers holding a foreground shell for 35-40 min, mostly the flock verifier's Lean build that every tier repeats; `test_circuit_check.py` can't run on a VM (2 GB memory floor). Circuits: memory growth it couldn't see coming (GLM wiring climbed about 32 GB/min to its 400 GiB cap and was OOM-killed; 14e9 regions, a bug), and suites OOM-killed on 16 GB VMs. Worked around: a tmux session per tier plus timers; two tmux lanes queueing PRs from a file, with paths from `git diff` because gh's file list stops at 100; pod ssh denied, so state comes from `status`/`inspect`; `notes push` refusing from a worktree or without a bound lane branch. Fix next: compute-accounting: `--detach` plus a notice to the owner when a tier ends, and a tier that skips an unchanged Lean build; circuits: scope memory and growth against MemoryMax in `research status`, with an alert before the cap.
- Triage posted 00:18Z (ts 1791245895.434069): (1) yes, infra, by 08:00Z: scope memory (current, peak, growth) against MemoryMax in `research status`; the 15-min-to-cap alert later, with the alerts consolidation. (2) yes, infra, by 06:00Z: reuse the flock verifier's Lean build in quick tiers when its inputs are unchanged. (3) later, in the quick-tier node service: an end-of-tier notice and auto-judge (#1239's `--detach` is ready). (4) no: heavy suites on 16 GB VMs (tier or `--on`). (5) context: `notes push` vs `notes sync --path`, pod ssh vs `status`/`inspect`, `queue ready` takes paths from `git diff`. Both answers brought new items, so the timer stays on. Next round: memory-accounting, network-accounting.
- Round 29, later answer (compute-accounting, 00:18Z): node 2's FlashInfer JIT cache (/home/research/.cache/flashinfer/0.6.18/120f) flips between two builds that share the version string 0.6.18, so a timed served window can rebuild it mid-lease. Answered: the job's launcher keys FLASHINFER_WORKSPACE_BASE by the build (compute-accounting's, or vLLM's if shared; infra reviews); until then, warm the cache in an untimed lease first.
- Round 30 (6 Oct 04:00Z): skipped. Round 29's two yes items were still unstarted at 04:00Z: the quick tier's flock Lean build reuse (due 06:00Z) and scope memory against MemoryMax in `research status` (due 08:00Z). Infra launched a worker lane for each (bc-68b722ea, `cursor/quick-tier-lean-reuse-558b`; bc-439adf84, `cursor/status-scope-memory-558b`) instead of collecting new asks; it's also top's research night, and memory-accounting is booked for 07:00-08:30Z. Skipped rounds aren't 'nothing new', so the timer stays on. Next round at 08:00Z: memory-accounting (after its window) and network-accounting.
- Round 31 (6 Oct 08:00Z, recorded 09:20Z): skipped. It's the rename move's night: shared machinery is frozen to 14:00Z except train fixes, every lead is on the move's check and the restack wave, and memory-accounting is in its quiet timed window on node 2 until 13:30Z. Round 29's yes items are in flight: the quick tier's warm `.lake` is #1317, and scope memory is on `cursor/status-scope-memory-558b`. Skipped rounds aren't 'nothing new', so the timer stays on. Next round at 16:00Z (12:00Z falls in the freeze): memory-accounting, network-accounting.
- Rounds 32 and 33 (6 Oct 12:00Z, 16:00Z): skipped. At 12:00Z the restack wave and freeze ran to 14:00Z. At 16:00Z memory-accounting and network-accounting were on their 16:30Z, 18:30Z and 22:30Z goal deadlines.
- Round 34 (6 Oct 20:00Z): no announcement. Top's v2 platform review (thread 1791316316.610139, 19:52Z) asked every lead the same questions an hour earlier, and eight leads had answered with what costs them time and what to retire. A separate interview would have been chatter. Infra items from those replies, triaged in the same thread at 20:14Z (ts 1791317274.065829): (1) one booking calendar on node 2 (memory-accounting, compute-accounting): yes, infra, done 20:07Z. Node 2's slots read gpu-lease's `fill/windows`, `slot-windows` is retired, and the `slot-NAME=runs` mark is in #1375 @ 9ab3b6d2f. The calendar in git is later (bookings change within the hour), and so is gating host work outside a lease (one allocator per machine). (2) Infra's idle quick-tier tmux chains: gone (Q14 dropped the mark). (3) A Lean toolchain in workspaces (ci, C19): yes, infra, on the day workspaces exist. (4) The gate computing the Q5 carry (circuits): not infra's, it belongs to the gate's owner. (5) Naming: infra moved its vote to `gate`. Next round 7 Oct 00:00Z: memory-accounting and network-accounting, unless the 22:30Z goals are still open.
- Round 35 (7 Oct 00:00Z): no announcement. Top's "Verity repository" thread (1791331591.766669, 00:06Z) asks every lead what breaks for them by 01:30Z, so a separate interview now would be chatter in their reply window. Infra answered there (1791332483.183659, note:infra/20261007T0030Z-draft-org-proposal-feedback). Items for infra in leads' replies so far: comms (alerts as run-store records, delivered by infra/, which is infra's own answer too), compute-accounting (node-local outputs kept while a ref lives; privileged timed pod on the quiet nodes; a GPU home for hours-long serve that doesn't block the timed queue), lean (the daily cache unit in infra/; per-module replay verdicts signed by a platform run). These go to top's 01:30Z summary for Daniel. Infra triages them once his ruling is out, not before. Next round 04:00Z: memory-accounting and network-accounting (still unasked since rounds 19 and 28).
- Round 36 (7 Oct 04:00Z): @memory-accounting and @network-accounting (announce ts 1791345646.764449). Both were last asked in round 28 or earlier and skipped since round 30. Top's redesign (03:01Z) just asked both to put node-only cited outputs into the store before the nodes stop at 15:00Z, so the questions point at that. Context given: $OUT (#1435), status/inspect resources (#1436), py-spy on both nodes.
