---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Ready backlog for vy-nebius-1 (and node 2's spare CPU): per workstream

The nebius-infra steward keeps this. Newest state first, and each item names its owner, what fills it, and its status. Fills route
through the owning lane: the research coordinator (bc-8ece7cde) or the vLLM coordinator (bc-ecac3029).

**Standing ruling (11:30 PM PDT Oct 1):** whenever #767's head moves, tell the research coordinator (bc-8ece7cde, Slack
`research slack ask --to @old-circuits-and-proofs`) directly, since #767 is in a train.

**Standing ruling (6:16 PM PDT Oct 1):** a small fix to infrastructure the steward runs goes straight to the merge queue once its
tests pass, without asking: take it out of draft, run `research queue ready N --by nebius-infra`, and ask @ci on Slack to stack
it. In Slack posts, put the mentions first, then `steward:`. The top-level forwards a post that tags a handle anywhere, but
the doorbell wakes only the names at the start.

**Standing ruling (root, 06:33Z Oct 4, Daniel's rule):** GPU work runs only for owner-approved items that each name their
research question. There is no filler, and GPUs may idle when approved work runs out. The steward doesn't offer idle GPUs
as backfill; it reports them idle and lets @top route approved work. Preemptible leases remain the way approved backfill
runs. (Also in the infra report `20260930T1845Z-report-infra`: every job names its research question.)

**Fallback (14:33Z Oct 4):** node 1's `vy-steward-watch.timer` writes a read-only state line every 15 min to
`/workspace/verity-guest/steward-watch.jsonl` (flags disk-72, disk-78, pacer-stale, dispatcher-stale; a copy is in
`tools/vy-steward-watch`). It keeps running when this VM is suspended. After a gap, read it from the last pass on. My passes
are the cron timer `nebius-infra-steward-pass-v2` plus `nebius-infra-steward-fallback` (every 45 min), which runs a full pass
when `/tmp/steward-pass.last` is over 40 min old.

**Subscriptions (root, 16:34Z Oct 4: they expire 7 days after creation; renew any expiring within 2 days).**
- `nebius-infra-steward-pass-v2` (cron `*/30`, `sub_bbdccb40…`) and `nebius-infra-steward-fallback` (every 2,700 s,
  `sub_35ad9975…`): both expire 2026-10-11T14:33Z.
- A one-shot reminder, `nebius-infra-renew-subscriptions-oct9`, fires about 2026-10-09T14:00Z to renew them.
- To renew: unsubscribe, then re-subscribe with the same args under a **new name** (`-v3`). Re-subscribing a just-closed name
  returns `created: false` and leaves no timer (seen 14:33Z Oct 4). Confirm with `list_subscriptions`.

## Open asks

1. **[@infra] Hourly eviction covers `/workspace/research/src`** (root, 04:02Z Oct 4; asked in the disk thread,
   `1791086539.319899`).
   - Use the same conditions as root's 03:48Z yes: the tree's commit is on origin; no running or queued run, check slot or
     Lean slot uses it; no run record holds it as its source's only copy.
   - Why: nothing prunes `src/`, check runs add up to 24 GB each, and node 1 lost about 300 GB in the hour to 03:11Z.
     The one-off cleanup removed 205.6 GB+ (see "State at 04:02Z").
   - Once it's on main, bump the `tool-1028.conf` pin on both `vy-store-evict` units. Then check one hourly run prunes
     `src/` and leaves trees in use alone.
   - Status: asked. Nothing is needed from me unless @infra declines.
   - **21:45Z Oct 4: #1115 landed on main `16749a0ff`** (`store_evict.sh` with `VY_EVICT_SRC`, the
     `store_evict_src.conf` drop-in, `evict.py`'s `evict_src` via `--src-dir`). It's **not live on node 1**: the wrapper
     is the old one, the `src.conf` drop-in isn't installed, and `tool-1028.conf` pins `e307a849` (no `--src-dir`).
     - Main's tool snapshot is `2babac2063726d4c`, already on node 1.
     - Asked @infra (`1791150252.250029`) whether the pin should move there. The deploy of the wrapper and drop-in is
       theirs, unless they hand it to me.
   - **Done, 22:14Z Oct 4: live on node 1, deployed by @infra.**
     - The new wrapper, `vy-store-evict-research.service.d/src.conf`, and `tool-1028.conf` on both units now pin
       `2babac2063726d4c` (main `16749a0ff`).
     - The first research run (22:14:54Z) deleted 23 src trees (32.8 GB, 427k inodes) and kept 63 (condition 1: 7,
       condition 2: 20, condition 3: 18, recent: 38).
     - Confirmed in the thread (`1791153079.691869`). From now on the disk-72 flag needs no nudge for `src/`; the pin now tracks
       main's `2babac20` and needs a bump with the next eviction change.
2. **[@infra] The control pod's notes checkout is on a detached HEAD** (root, 16:09Z Oct 6; told @infra once,
   `1791303016.287849`).
   - `vy-control:/workspace/steward/research-notes`: a sync's rebase started at 16:05:41Z and never finished. HEAD is
     `3acaf610e` (origin/main), with no rebase state left. Local `main` is `12203a957`, 1 ahead and 2 behind. Every sync
     fails with "HEAD is detached".
   - It's @infra's checkout: don't touch its git state. Each pass, read that post's replies and run
     `git -C … branch --show-current`. **When @infra acks or it's back on `main`, send root one line.**
   - 16:13Z: no reply yet. Syncs keep committing on the detached HEAD (`6cad6de70`, 16:10:19Z, on no branch); added
     in-thread (`1791303214.257379`) that a plain checkout of `main` would orphan it.
   - 16:41Z: still detached, no reply. The detached HEAD is now `220251cf7` (sync commits through 16:40Z, plus a
     16:26Z cloud mirror commit).
   - Root, 16:42Z: if @infra hasn't acked by 17:15Z, reply once in the thread copying @top: notes haven't reached GitHub
     since 16:06Z, and list the unpushed sync commits on the detached HEAD. Still hands off its git state. One-shot timer
     `nebius-infra-notes-detached-1715` (`sub_fdd5426a…`) fires at about 17:15Z.
   - 17:16Z: no ack, still detached (HEAD `c4bfdeefd`, 8 commits above origin/main plus `main`'s `12203a957`). Replied
     once in the thread copying @top (`1791306973.522099`). Next: one line to root when @infra acks or it's on `main`.
   - **Fixed by 17:23Z (no ack in the thread).** On `main` `f0fcde1d7`, equal to origin/main. The 16:05–16:49Z syncs
     were rebased and pushed; the 16:58Z mirror's file is in HEAD. The 17:22Z sync `8edf83992` had committed conflict
     markers into `lanes/coordinator/20260925T1614Z-report-coordinator.md`, and the 17:23Z reset dropped it. The likely
     cause is that the 16:05Z rebase conflicted on that file and was quit. Posted as FYI (`1791307940.694999`); told root.
     My 17:31Z check ran one `git fetch origin main` there (it only moves the tracking ref).

## State at 22:30Z Oct 6 (3:30 PM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 67.0% (1,654 GiB free); 0 admitted, all 8 idle (reported); pacer and dispatcher
  clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 70%. The next hourly is loop tick 156.

## State at 22:01Z Oct 6 (3:01 PM PDT), steward pass (cron on time)

- The 21:44Z "pod holds a GPU at 0%" alert (GPUs 1 and 6) is the known pool pattern. Pool holders were created at
  21:32Z for proofs' `85-rec-reprice.sh STEP=oprove` (`k4096t67`, `r20261006-213154-250d` and `-83f6`), which now lease
  only around GPU calls (last leases 38 s and 13 s, rc 0). They sat unused about 10 min and then went. The alert is the
  infra and dispatcher lanes', who own the pool, and it went to both. Not re-posted.
- Node 1 (watch, no flags): 68.4% (1,585 GiB free); 0 admitted, all 8 idle (reported); pacer and dispatcher clean.
- Node 2: 0 of 8 and no queue: fully idle (reported), 70%. No new hourly.

## State at 21:43Z Oct 6 (2:43 PM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 68.7% (1,570 GiB free). GPU work again since 21:31Z: `provers` 2 admitted, 2 leases
  (`adhoc:ubuntu`, GPUs 1 and 6), 6 idle (reported). Pacer and dispatcher clean.
- Node 2: 0 of 8 and no queue: fully idle (reported), 70%.
- Hourly snapshot `art:40630b07…` (about 21:30Z; utilization-summary updated).

## State at 21:14Z Oct 6 (2:14 PM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 68.0% (1,604 GiB free), a slow climb from 64.1% at 19:14Z with no GPU work (check runs).
  All 8 idle since about 11:53Z (reported); pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 70%. The next hourly is loop tick 150.

## State at 20:43Z Oct 6 (1:43 PM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 67.3% (1,643 GiB free); no GPU work since about 11:53Z, all 8 idle (reported);
  pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 70%. The next hourly is loop tick 150.

## State at 20:13Z Oct 6 (1:13 PM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 66.1% (1,699 GiB free); no GPU work since about 11:53Z, all 8 idle (reported); pacer and
  dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported). `/workspace` at 70%, up from 68% (node 2's disk is @infra's and
  node2-ops'; no flag of mine).
- Hourly snapshot `art:decf3636…` (about 19:50Z; utilization-summary updated).

## State at 19:43Z Oct 6 (12:43 PM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 65.8% (1,715 GiB free); no GPU work since about 11:53Z, all 8 idle (reported); pacer and
  dispatcher clean.
- Node 2: 2 of 8 (a fill job on 7, a `pouw-service-draw` session job on 4 since 19:40Z), 6 idle (reported), 68%. The
  next hourly is loop tick 144.

## State at 19:14Z Oct 6 (12:14 PM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 64.1% (1,804 GiB free); no GPU work since about 11:53Z, all 8 idle (reported);
  pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%. The next hourly is loop tick 144.

## State at 18:45Z Oct 6 (11:45 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 65.1% (1,753 GiB free); no GPU work since about 11:53Z, all 8 idle (reported); pacer and
  dispatcher clean.
- Node 2: 2 of 8 (fill jobs on 7 and on 4, the latter compute-accounting's bc-1beaff8e since 18:38Z), 6 idle
  (reported), 68%. No new hourly.

## State at 18:14Z Oct 6 (11:14 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 65.5% (1,729 GiB free), up from 62.9% at 17:45Z. Writers: `cp -a` of a Lean tree with its
  Mathlib build into `research/lanes/vbridge-5a30/check/`, and check runs' Lean audits. No action at this level. No GPU
  work since about 11:53Z, all 8 idle (reported). Pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%.
- Hourly snapshot `art:6efd165e…` (about 18:10Z; utilization-summary updated).

## State at 17:45Z Oct 6 (10:45 AM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 62.9% (1,863 GiB free); no GPU work since about 11:53Z, all 8 idle (reported);
  pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%. The next hourly is loop tick 138.
  The notes checkout is fixed (open ask 2).

## State at 17:14Z Oct 6 (10:14 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 64.8% (1,765 GiB free). No GPU work since about 11:53Z, all 8 idle (reported). Pacer and
  dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%. No new hourly.
- The notes checkout is still detached (HEAD `c4bfdeefd`), and @infra hasn't replied; the 17:15Z timer sends the follow-up.
- The 16:44Z entry below was lost when something rewrote this file at 16:49:30Z; re-added.

## State at 16:44Z Oct 6 (9:44 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 63.0% (1,857 GiB free). No GPU work since about 11:53Z, all 8 idle (reported). Pacer and
  dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%.
- The loop's 16:28Z hourly failed (`ssh n2` exit 255, transient; n2 answers now). Reran by hand:
  `art:7b88bd2f…` (utilization-summary updated).

## State at 16:13Z Oct 6 (9:13 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 63.0% (1,857 GiB free). Compute-accounting's passes are all gone
  (`jobs/pouw-mvp-e2e/passes/` empty), so the 76% trigger for B2's passes is moot. Still no GPU work since about
  11:53Z, all 8 idle (reported). Pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%. No new hourly (next at loop tick 132).
- The notes checkout on `vy-control` is still detached (open ask 2).

## State at 15:42Z Oct 6 (8:42 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 66.5% (1,682 GiB free); two pass windows left (B1's 3, B2's 3). Still no GPU work since
  about 11:53Z, all 8 idle (reported). Pacer and dispatcher clean.
- Node 2: 2 of 8 (a fill job on 7, a research session job on 4 since 15:40Z), 6 idle (reported), 69%. No new hourly.

## State at 15:15Z Oct 6 (8:15 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 67.0% (1,655 GiB free), three pass windows left. No GPU work since about 11:53Z: 0 admitted,
  no leases, all 8 idle (reported). Pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%.
- Hourly snapshot `art:5358bd51…` (about 15:00Z; utilization-summary updated).

## State at 14:44Z Oct 6 (7:44 AM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 66.2% (1,697 GiB free), three pass windows left; all 8 GPUs idle since about
  11:53Z (reported); pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%. The next
  hourly is loop tick 126.

## State at 14:13Z Oct 6 (7:13 AM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 66.3% (1,691 GiB free), three pass windows left; all 8 GPUs idle since about
  11:53Z (reported); pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 67%. No new hourly.

## State at 13:42Z Oct 6 (6:42 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 66.7% (1,670 GiB free). The verifies freed two more windows; three are left (about 220 GB:
  B1's window 3 and B2's 2–3). All 8 GPUs idle since about 11:53Z (reported); pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 67%.
- Hourly snapshot `art:bba10bb5…` (about 13:30Z; utilization-summary updated).

## State at 13:12Z Oct 6 (6:12 AM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 70.2% (1,498 GiB free), passes unchanged; all 8 GPUs idle since about 11:53Z
  (reported); pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 67%. The next hourly is
  loop tick 120.

## State at 12:42Z Oct 6 (5:42 AM PDT), steward pass (cron on time)

- Unchanged. Node 1 (watch, no flags): 69.9% (1,510 GiB free), passes unchanged; all 8 GPUs idle since about 11:53Z
  (reported); pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 67%. No new hourly.

## State at 12:12Z Oct 6 (5:12 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 70.9% (1,460 GiB free), up 1.7 points since 11:43Z. The passes are unchanged (five window
  dirs, B1's verify on window 2). `provers` 0 admitted, no `gpu-lease` holders: all 8 GPUs idle and fenced (reported).
  Pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 67%. No new hourly since `art:918b9600…`.

## State at 11:43Z Oct 6 (4:43 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags since 11:15Z): 69.2% (1,546 GiB free). B1's verify freed window 1's passes (439 to 366 GB;
  five window dirs left). The 76% trigger for B2's passes stands. `provers` 3 admitted; GPUs 0, 1 and 5 leased, the rest
  fenced for Kueue. Pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 67%.
- Hourly snapshot `art:918b9600…` (about 11:37Z; utilization-summary updated).

## State at 11:12Z Oct 6 (4:12 AM PDT), steward pass (cron on time): disk-72 on node 1

- Node 1: the watch flagged `disk-72` at 11:00Z (72.0%); `df` reads 72.2% (1,396 GiB free). `research/src` eviction is
  live, so no @infra nudge. The 30 min growth is check runs' Lean scratch (`research/scratch` 227 GB, five check dirs of
  about 22 GB each since 10:36Z), not the passes (439 GB, unchanged).
- @compute-accounting answered (`1791283389.461089`): no more GPU phases. The passes only shrink as B1's verify
  (`r20261006-094525-d77f`) and B2's relaunched verify finish. Near 78% they approve deleting B2's passes
  (`jobs/pouw-mvp-e2e/passes/r20261006-100722-c6cb.*`, about 220 GB). **At 76%, ask @infra in the disk thread to remove
  those under `retention rm --approved-by @compute-accounting --ref slack:1791283389.461089`.** Tell root at 78%.
- `provers` 3 admitted; pacer and dispatcher clean. Node 2: 1 of 8 (a fill job on 7), 7 idle (reported), 68%.

## State at 10:43Z Oct 6 (3:43 AM PDT), steward pass (cron on time)

- Node 1: 69.7% (1,519 GiB free; the passes ask below is open, no reply yet). `provers` 3 admitted; GPUs 0, 1 and 5 leased
  (memory-accounting's keeper on 0–1), 2–4 and 6–7 fenced for Kueue. Pacer and dispatcher clean.
- Node 2: 2 of 8 (a timed research job on 7, a fill job on 1), 6 idle (reported). `/workspace` 67%. No new hourly.

## 10:42Z Oct 6: node 1 at 69.5%, compute-accounting's passes (fallback poll)

- The watch read 68.8% at 10:30Z, and `df` reads 69.5% (1,531 GiB free) now. A second `arms.sh` GPU phase
  (`r20261006-100722-c6cb`) added 220 GB, so 440 GB of passes sit in `jobs/pouw-mvp-e2e/passes/`. Their CPU phases
  (`r20261006-094525-d77f`, `r20261006-103435-106e`) delete passes after each verify, but the first has been on window
  1's verify since 09:45Z. Asked @compute-accounting in the disk thread, copying @infra (`1791283302.853189`), how many
  more GPU phases are planned and whether the next can wait for freed passes. Nothing deleted. Tell root at 78%.

## State at 10:12Z Oct 6 (3:12 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 65.3% (1,739 GiB free), flat since 09:45Z. Compute-accounting's 220 GB of passes are still
  in `jobs/pouw-mvp-e2e/passes/`, awaiting their CPU phase. `provers` 6 admitted; all 8 GPUs taken (6 leases, 2 fenced
  for Kueue). Pacer and dispatcher clean.
- Node 2: 1 of 8 (a fill job on GPU 1); a second fill job (bc-15ada664's `pous-vllm-e2e-series`) is starting on GPU 7.
  6 idle (reported). `/workspace` 67%.
- Hourly snapshot `art:d9568d02…` (about 10:01Z; utilization-summary updated).

## 09:58Z Oct 6: node 1's disk jump, 61.4% to 64.7% (09:30–09:45Z), attributed

- Compute-accounting's `arms.sh` GPU phase (`r20261006-091845-6504`, bc-1beaff8e) wrote 220 GB to
  `jobs/pouw-mvp-e2e/passes/` (three windows, about 70 GB each, 09:28–09:42Z), then stopped. By design its CPU phase
  verifies each window and then deletes the passes. Node 1 is at 65.3% (1,739 GiB free) and flat. No flags, no post.

## State at 09:42Z Oct 6 (2:42 AM PDT), steward pass (cron on time)

- The 09:17Z idle-lease alert (GPU 7) was compute-accounting's `r20261006-090402-0325` (bc-1beaff8e,
  `cursor/pouw-h3-sha512-e3fa`, `pearl_c_vllm/h3_window.sh`): a ship build and a 7 min CPU screen check inside its
  `gpu-lease`. It exited 0 at 09:16Z. Told @compute-accounting once (`1791279930.620769`), FYI.
- Node 1 (watch, no flags): 61.4% at 09:30Z, `research/src` 94 trees, `provers` 4 admitted; GPUs 0–2 and 4 leased
  (memory-accounting's keeper on 1, 2 and 4; bc-1beaff8e on 0), 3 and 5–7 fenced for Kueue. Pacer and dispatcher clean.
- Node 2: 3 of 8 (a session job on 0, a fill job on 6, a timed quiet job on 7), 5 idle (reported). `/workspace` 67%.
- No new hourly snapshot; latest is still `art:80559fcc…`.

## State at 09:12Z Oct 6 (2:12 AM PDT), steward pass (cron on time)

- Node 1 (watch, no flags): 61.3% at 09:00Z (`df` 62% now), `research/src` 116 trees, `provers` 6 admitted; all 8 GPUs
  taken (6 leases, 2 fenced for Kueue). The pacer and dispatcher are clean.
- Node 2: a timed quiet job (`gl-14594`, research, GPU 7, 900 s) since 09:07Z, with three more timed jobs queued for
  GPU 7, plus a fill job and a session job held behind the window (POUS policy). 7 GPUs idle (reported). `/workspace` 68%.
- No new hourly snapshot (next at loop tick 108); latest is still `art:80559fcc…`.

## State at 08:42Z Oct 6 (1:42 AM PDT), steward pass (cron arrived 12 min late)

- Node 1 (watch, no flags): 60.1% (2,001 GiB free), `research/src` 102 trees, `provers` 4 admitted (2 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: node2-ops alerted @infra that it was unreachable from 08:32Z. It was a planned reboot: at 08:30:12Z the research
  user ran `grub-reboot vy-device-cores` and a delayed reboot, after adding a 08:30Z quiet line for memory-accounting to the
  schedule. Up since 08:36Z, `vy-cluster-agent` active, `/workspace` 68%. Told @infra (`1791276204.019549`). Now 1 of 8
  leased (research, GPU 7), 7 idle (reported), no queue.
- Hourly snapshot `art:80559fcc…` (utilization-summary updated).

## State at 08:12Z Oct 6 (1:12 AM PDT), steward pass (cron arrived 12 min late)

- Node 1 (watch, no flags): 62.5% (1,880 GiB free), `research/src` 104 trees, `provers` 5 admitted (3 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: 0 of 8 leased and no queue; fully idle, reported. The next hourly snapshot is loop tick 102.

## State at 07:43Z Oct 6 (12:43 AM PDT), steward pass (cron arrived 13 min late)

- Unchanged. Node 1 (watch, no flags): 61.6% (1,926 GiB free), `research/src` 94 trees, `provers` 8 admitted (7 GPUs
  held); the pacer and dispatcher are clean. Node 2: 1 of 8 (served-zk on GPU 0), 7 idle (reported), and no queue.

## State at 07:15Z Oct 6 (12:15 AM PDT), steward pass (cron arrived 14 min late)

- Node 1 (watch, no flags): 61.4% (1,936 GiB free), `research/src` 86 trees, `provers` 8 admitted (6 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: 1 of 8 leased (served-zk on GPU 0); 7 idle (reported), and no queue. node2-ops told @infra that node 2's root
  disk is 53% with 80 GB of leaked test dirs in `/tmp` (`20261006T0655Z-alert-from-node2-ops-…`); that's @infra's.
- The latest hourly snapshot is `art:6bd762df407abe6bedb3e8ef24b47f44c0a4b3736239e2b66a0c9e6b9e5841f1` (about 07:05Z).

## 06:47Z Oct 6: node 2's queued jobs behind the timed window ran (root's ask)

- All 8 queued at 06:13Z were granted 06:04–06:14Z: circuits' keeper ×4, research ×4, served-zk, @top's `p2decode`, and
  the fill job. The noise sweep's evicted run `r20261006-052256-d3f8` was regranted at 05:48Z and ended `done` at 05:49Z.
- The only unrun waiters withdrew themselves ("handle dropped", reason "node is quiet"): `p2decode` `gl-1013798` at
  06:10Z, and `gl-1911871` and research `gl-2037206` (both submitted at 06:35Z) at 06:41Z. None was dropped by the
  scheduler, so nobody was told.

## State at 06:44Z Oct 6 (11:44 PM PDT Oct 5), steward pass (cron arrived 14 min late)

- Node 1 (watch, no flags): 60.7% (1,972 GiB free), `research/src` 78 trees, `provers` 4 admitted (4 GPUs held); the
  pacer and dispatcher are clean. The 06:17Z idle-lease alert is the already-reported pattern, so not re-posted.
- Node 2: 0 of 8 leased and no queue; the timed window ended and its queued jobs are gone. Idle, reported.

## State at 06:13Z Oct 6 (11:13 PM PDT Oct 5), steward pass (cron arrived 13 min late)

- **Node 1 down to 57.2% (2,146 GiB free):** circuits' `free_values_after.sh` deleted the second GLM capture
  (`r20261006-001155-ac92/capture/values`, 245,216,372 KiB) after its Match step, as designed and as circuits expected.
  - `research/src` 91 trees, `provers` 5 admitted (3 GPUs held); the pacer and dispatcher are clean.
- Node 2 is still in the PoUS timed window (1 lease, `timed` on GPU 7, since about 05:28Z), with 8 jobs queued behind
  it. That's POUS's design.

## State at 05:43Z Oct 6 (10:43 PM PDT Oct 5), steward pass (cron arrived 12 min late)

- Node 1 (watch, no flags): 62.1% (1,903 GiB free), `research/src` 87 trees, `provers` 4 admitted (2 GPUs held); the
  pacer and dispatcher are clean.
- **Node 2 is in a PoUS timed window:** 1 of 8 leased (the `timed` job `gl-415333`, run `r20261006-052744-7177`, on GPU
  7, about 05:28Z).
  - The scheduler evicted 5 fill jobs (including the noise sweep's) and keeps the rest free for clean timing. The fill
    runner reports "timed True", with 3 fill jobs queued until the window ends.
  - The 7 idle GPUs are by POUS's design, so there's nothing to route.
- The latest hourly snapshot is `art:dfdefd19d058576dad226da138a32dad4fcc094a6a571787aef3329a34152250` (about 05:30Z).

## State at 05:11Z Oct 6 (10:11 PM PDT Oct 5), steward pass (cron arrived 11 min late)

- Node 1 (watch, no flags): 64.8% (1,764 GiB free), `research/src` 98 trees, `provers` 4 admitted (3 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: 5 of 8 leased (@top's `p2decode` ×2, 1 `research`, 1 `adhoc:ubuntu`, a fill job). GPUs 2, 4 and 5 are idle
  (reported), and there's no queue. The next hourly snapshot is loop tick 90.

## State at 04:40Z Oct 6 (9:40 PM PDT Oct 5), steward pass (cron arrived 9 min late)

- Node 1 (watch, no flags): 66.1% (1,701 GiB free), `research/src` 95 trees, `provers` 4 admitted (2 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: 8 of 8 leased, 2 queued. Leases: circuits' `commit-sweep`, @top's own `bc-7f347b4b-p2decode`, the noise sweep
  ×2, 2 `research` runs, `adhoc:ubuntu`, and a fill job.
  - node2-ops told @infra (`20261006T0435Z-alert-from-node2-ops-node2-workspace-down-190-gib-overnight`) that node 2's
    `/workspace` lost 192 GiB in 4 h, unattributed. It's at 67% now, not urgent, and node 2 retention is @infra's.

## State at 04:09Z Oct 6 (9:09 PM PDT Oct 5), steward pass (cron arrived 8 min late)

- Node 1 (watch, no flags): 65.3% (1,742 GiB free), `research/src` 110 trees, `provers` 5 admitted (2 GPUs held); the
  pacer and dispatcher are clean. Another idle-lease alert at 03:27Z; proofs already told once, so not re-posted.
- Node 2: 8 of 8 leased (the noise sweep on 5–7, 3 `research` runs, 1 `adhoc:ubuntu`, a fill-runner job), and no queue.
- The latest hourly snapshot is `art:7bad833da704d9a87edb4e255783665fe00b4dfc76681e740eb88bf425424ba8` (about 03:55Z).

## State at 03:37Z Oct 6 (8:37 PM PDT Oct 5), steward pass (cron arrived 6 min late)

- Node 1 (watch, no flags): 64.2% (1,794 GiB free), `research/src` 93 trees, `provers` 2 admitted (2 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: 6 of 8 leased (compute-accounting's noise sweep `bc-113f8c4c` on 1–5, a fill-runner job on 7). GPUs 0 and 6
  are idle (reported), and there's no queue. The next hourly snapshot is loop tick 84.

## State at 03:16Z Oct 6 (8:16 PM PDT Oct 5), steward pass (cron arrived 15 min late)

- Node 1 (watch, no flags): 63.7% (1,821 GiB free), `research/src` 94 trees, `provers` 2 admitted (2 GPUs held); the
  pacer and dispatcher are clean.
- Node 2: 8 of 8 leased (compute-accounting's noise sweep `bc-113f8c4c` on 0–2, 5 and 6; 2 `research` runs on 3–4; a
  fill-runner job on 7), and no queue. The served-zk lease (`bc-7a8095f9`) finished.

## 03:12Z Oct 6: disk watch lifted

- An hour under 72% since the check-run removal (63.4%, 1,835 GiB free), so `node1-disk-watch-78e` is off. Circuits'
  `jobs/cov` and `jobs/q235-gate` are still held for 78%. The 30-min passes and node 1's watch carry on.

## 02:55Z Oct 6: node 2's two new leases checked against Daniel's rule (root's ask)

- Both are compute-accounting's workers. Their branches end `-e3fa`, the compute-accounting coordinator
  `bc-e90634dd-…-97abfd87e3fa`. Both serve @top's 02:12Z assignment (`1791252777.081129`; compute-accounting's plan
  `1791252953.650169`).
  - The question: can one served Pearl-C request's commitment (hm96-sha512 rows) be opened by the hidden_zk proof, and
    what does serving in that format cost on sm120 by 14:00Z?
  - `bc-7a8095f9` on GPU 5: served-zk, `r20261006-023348-3018` (`benchmarks/pouw/served_zk/serve.sh`).
  - `bc-113f8c4c` on GPUs 0–3 and 6: `r20261006-023458-d2bb` (`pearl_c_vllm/noise_sweep.sh`, branch
    `pouw-noise-sweep-e3fa`), untimed preemptible screens of that decode overhead until 13:58Z. They're widened under
    @top's 02:23Z call for one bigger preemptible lane per lead.
  - Approved. Nothing to tell root.

## State at 02:45Z Oct 6 (7:45 PM PDT Oct 5), steward pass (cron arrived 13 min late)

- Node 1 (watch, no flags): 62.4% (1,888 GiB free), `research/src` 84 trees, `provers` 1 admitted (1 GPU held); the pacer
  and dispatcher are clean.
- Node 2: 8 of 8 leased (agent `bc-113f8c4c` on 0–3 and 6, `bc-7a8095f9` on 5, a `research` run on 4, a fill-runner job on
  7), and no queue.
- The latest hourly snapshot is `art:36041b8e11cd9385e0d988b9ddba2d73c2f77bc37df76441f71d3a99336df8f5` (about 02:30Z).

## State at 02:12Z Oct 6 (7:12 PM PDT Oct 5), steward pass: check runs removed

- **@infra removed the ci-approved check runs**, 02:11–02:12Z. `rm --approved-by @ci` first refused (implicit owner
  @runner), so @infra wrote `research keep … --owner @ci` sidecars on @ci's yes (`1791252322.579119`; scope: check.py
  runs, ended more than 12 h ago, preserved). Then 422 deletions, all `@ci`, all under `research/runs`, about 611 GiB, all
  logged.
  - The four live check slots' run dirs are intact.
- **Node 1 is now 64.4% (1,785 GiB free).** Circuits' `jobs/cov` and `jobs/q235-gate` are still held for 78%.
  `node1-disk-watch-78e` comes off after an hour under 72% (about 03:12Z).
- Node 2: 1 of 8 (a fill-runner job). The coordinator lane's new merge-queue conflict handoffs aren't mine.

## 02:03Z Oct 6: asked @infra to remove ci-approved check runs now (root's ask)

- Node 1 is at 73.6% (1,323 GiB free), climbing about 157 GiB/h. Asked @infra in the relief thread (`1791252129.787529`)
  to delete, via `retention rm --approved-by @ci --ref slack:1791247233.203489`, the finished check runs that ended more
  than 12 h ago and are preserved in the store (105 runs, about 517 GB). @ci offered explicit sidecars if rm refuses on
  implicit owners. Circuits' `jobs/cov` and `jobs/q235-gate` stay for 78%. Tell root only if @infra can't.

## State at 01:40Z Oct 6 (6:40 PM PDT Oct 5), steward pass (cron arrived 9 min late)

- The idle-lease alert recurred at 01:25Z (GPU 7) on zk-gateway's `r20261006-010844-c628` (tree `e0b25b4423`): still
  `gpu-lease … --preemptible -- bash 85-rec-reprice.sh STEP=oprove` around the whole step, so proofs' fix isn't in that
  launch. Its stdout has two flock panics. Told proofs once in the thread (`1791250870.620509`), as they asked.
- Node 1 (watch, no flags): 71.4% (1,434 GiB free), `research/src` 73 trees; the pacer and dispatcher are clean. Node 2:
  1 of 8 (a fill-runner job), and no queue.
- Tick 72's hourly ran through the gzip fix and stored
  `art:c078194b5b6eb21ffd6cd3f6ee62581a427bb513bb7ef3c8b1e2505ed573fad5` (about 01:10Z).

## State at 01:07Z Oct 6 (6:07 PM PDT Oct 5), steward pass (cron arrived 6 min late)

- Node 1 (watch, no flags): 70.5% (1,480 GiB free) after proofs' 159 GiB went; `research/src` 63 trees. 0 of 8 GPUs and
  nothing in Kueue (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
- The loop's next hourly is tick 72 (about 01:10Z), the first with the gzip fix. The `TimeoutExpired` line still in the
  log is tick 66's.

## 01:02Z Oct 6: the owners answered; relief ready for 78%

- **@proofs:** yes, and @infra already deleted 159 GiB via `retention rm --approved-by @proofs` (`jobs/e2e-integrate`,
  `rec-v0`, `proofs-flock-fp`, `proofs-zk-k32k`; logged). Node 1 is at 70.5% (1,480 GiB free) at 01:00Z.
- **@ci:** yes. Preserved finished check runs already have implicit records (gc takes them past 48 h), and ci approves
  deleting preserved finished check runs that ended more than 12 h ago (`1791247233.203489`).
- **@circuits** (`1791247292.233679`):
  - yes to `jobs/q235-gate` (111 GB, the Oct 3 gate) and `jobs/cov` (653 GB, 946 rows, grid paused since Oct 3), as
    low-priority retention for gc at 78%;
  - no claim on DeepSeek-V3-0324-NVFP4; Qwen1.5-MoE and gemma-2-9b can go if needed;
  - `glm47-match` stays (row 1's recapture; values go about 5 h after the capture).
- So at 78% about 1.2 TB is ready on owners' yes. Still unclaimed: the DeepSeek-V3 weights (424 GB).

## 00:40Z Oct 6: relief for 78% lined up (root's ask), awaiting owners

- Asked @ci, @circuits and @proofs, with @infra copied (`1791247165.325479`), what each could free on request with a
  retention record. On offer, to be confirmed:
  - check's 105 finished run dirs older than 12 h (517 GB);
  - circuits' `jobs/cov` (653 GB, partly) and `jobs/q235-gate` (111 GB, Oct 3, owner unconfirmed);
  - proofs' `jobs/{proofs-flock-fp,e2e-integrate,proofs-zk-k32k,rec-reprice}` (181 GB);
  - `hf` models no run named in 3 days: DeepSeek-V3-0324-NVFP4 (424 GB, fetcher unknown) plus about 108 GB of small ones.
  - `research/scratch` (147 GB) is live, so it isn't on offer. Nothing is deleted.

## State at 00:35Z Oct 6 (5:35 PM PDT Oct 5), steward pass

- **Node 1 jumped from 68.6% to 74.1% (00:15–00:30Z):** circuits' second GLM-4.7-Flash capture (`m1-capture`, run
  `r20261006-001155-ac92`, direct lease on GPU 6 until 00:57Z) wrote 235 GB into
  `glm47-match/…/r20261006-001155-ac92`. It finished at 00:30:36Z, and the disk is flat at 75% (1,280 GiB free).
  - Like yesterday, its CPU Match leg (about 13 h) and `free_values_after.sh` will delete `capture/values` afterwards.
    Until then about 177 GiB is left before 78%.
  - Re-armed `node1-disk-watch-78e` (every 15 min) to tell root at 78%. No disk-72 nudge, since src eviction is live.
- The 00:25Z "pod holds a GPU at 0%" alert came in, likely around this capture's lease; circuits', and the pattern is
  already reported.
- The `TimeoutExpired` line in the loop log is tick 66's. Tick 68 isn't an hourly tick; the next hourly, tick 72, uses
  the gzip fix. Node 2: 1 of 8 (a fill-runner job), and no queue.

## State at 00:20Z Oct 6 (5:20 PM PDT Oct 5), steward pass (cron arrived 16 min late)

- **The hourly util_collect at tick 66 (23:32Z) failed:** `ssh n2 'cat /workspace/pouw/infra/util/*.jsonl'` timed out at
  300 s. That's 140 MB of node 2 sampler JSONL, growing about 25 MB a day, probably slow during a VM pause.
  - Fixed in `/tmp/util_collect.py` (copy in `tools/`): node 2 is read through `ssh_gz` (`| gzip -1` on node 2, 600 s
    timeout).
  - A run by hand took 2 min 20 s and stored `art:cc609351e836511c83cb7f2a3fbae9350e6eb006013c76bcda712ba598fe2f0b`.
- Node 1 (watch, no flags): 68.6% (1,574 GiB free), `research/src` 51 trees, `provers` 1 admitted (1 GPU briefly held at
  00:15Z); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
- Drift: node 1's `gpu-lease` now matches main (`0d477644`), so @infra deployed it. @infra hasn't answered on
  `vy-custody`.
- The cron passes are arriving later each time (4, 9, 13, 16 min) as this VM pauses; node 1's watch covers the gaps.

## State at 23:43Z Oct 5 (4:43 PM PDT), steward pass (cron arrived 13 min late)

- **@proofs fixed the idle-lease cause** (`1791242426.676669`): `rec-step2` held a lease across a whole `85-rec-reprice`
  step. It now takes `gpu-lease` only around each GPU prove call (preemptible where it can), and `zk-gateway` follows the
  same rule.
- Node 1 (watch, no flags): 67.8% (1,614 GiB free), `research/src` 46 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't answered
  on `vy-custody`. Loop tick 66 (23:32Z) is taking the hourly snapshot.

## 23:15Z Oct 5: the idle `provers` lease alert, attributed

- The five alerts (04:25, 08:26, 20:31, 21:12, 22:26Z) are `n1_lease.py` growing one pool holder per `gpu-lease` waiter. The
  waiters: circuits' `glm47-flash` `r20261005-041419-e27e` (04:14Z, failed 04:18), then proofs' recursion `flock` runs
  (`cursor/rec-step2-95d4` / `rec-reprice-95d4`, `85-rec-reprice.sh STEP=oprove`) that lease a GPU but spend the lease in
  the CPU prover. Not ours. Posted once to @infra and @proofs (`1791242004.526059`); node1-dispatcher has no Slack handle.

## State at 23:09Z Oct 5 (4:09 PM PDT), steward pass (cron arrived 9 min late)

- Unchanged. Node 1 (watch 22:30–23:00Z, no flags): 67.1% (1,652 GiB free), `research/src` 45 trees, 0 of 8 GPUs and
  nothing in Kueue (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
  @infra hasn't answered on `vy-custody`.
- A fifth "pod holds a GPU at 0%" alert today (22:27Z), the same brief `provers` pool lease pattern, for the infra and
  dispatcher lanes.

## State at 22:35Z Oct 5 (3:35 PM PDT), steward pass (cron arrived 4 min late)

- Unchanged. Node 1 (watch 22:00–22:30Z, no flags): 66.8% (1,667 GiB free), `research/src` 43 trees, `provers` 1 admitted
  and 0 GPUs held; the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't
  answered on `vy-custody`.

## State at 22:00Z Oct 5 (3:00 PM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 66.8% (1,663 GiB free), `research/src` 47 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't
  answered on `vy-custody`.
- The latest hourly snapshot is `art:88d775cce9a4444a3a2cfe25e61364e10b27630ac9d83c6a656f04304f5e2cd1` (about 21:55Z).

## State at 21:30Z Oct 5 (2:30 PM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 66.8% (1,663 GiB free), `research/src` 46 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't
  answered on `vy-custody`.
- Pattern: "pod holds a GPU at 0%" alerts at 04:26, 08:27, 20:32 and 21:13Z today, each a brief `provers` pool lease that
  sat unused about 10 min and then went. They go to the infra and dispatcher lanes, who own the pool. Not acted on.

## State at 21:00Z Oct 5 (2:00 PM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 67.2% (1,646 GiB free), `research/src` 46 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't
  answered on `vy-custody`.
- The 20:32Z Grafana "pod holds a GPU at 0%" alert (the brief `provers` lease) is moot: no GPU is held now.

## State at 20:30Z Oct 5 (1:30 PM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 66.9% (1,661 GiB free), `research/src` 45 trees, `provers` 1 admitted and 0 GPUs
  held; the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't answered on
  `vy-custody`.
- The latest hourly snapshot is `art:83a145c45e097f2f60b69b6fb90ba0e595afe7da8238d71c40a5530a66d65853` (about 20:20Z).

## State at 20:00Z Oct 5 (1:00 PM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 67.1% (1,648 GiB free), `research/src` 48 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't
  answered on `vy-custody`. The next hourly snapshot is loop tick 54.

## State at 19:30Z Oct 5 (12:30 PM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 66.5% (1,682 GiB free), `research/src` 41 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. @infra hasn't
  answered on `vy-custody`.

## State at 19:00Z Oct 5 (12:00 PM PDT), steward pass

- **@circuits confirmed (`1791226624.473259`)** that `replay_a.json` from `8267` is complete and valid: tier a, pass,
  316/316 specs, 3,382/3,382 instances. The replay finished before writing it, and the INCOMPLETE verdict is expected (G5's
  wiring run hit its cap, holdouts not run). So the deleted capture isn't lost and needs no GPU rerun. @infra hasn't
  answered on `vy-custody` yet.
- Node 1 (watch, no flags): 66.5% (1,682 GiB free), `research/src` 51 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
- The latest hourly snapshot is `art:74d4a676ec0b62114f784606d12d73dc0bb8be7e3ade610294fa0e9dd4c9d0ea` (about 18:50Z).

## State at 18:55Z Oct 5: the 18:30–18:45Z drop attributed

- **The about 233 GiB freed at 18:30:29Z was circuits' own cleanup.** Run `r20261005-054511-d219` (`glm47-flash`,
  `free_values_after.sh`) deleted `glm47-match/…/r20261005-041934-6dad/capture/values` (245,093,644 KiB). It did so after the
  Match CPU leg `r20261005-054111-8267` wrote `replay_a.json` (18:25Z), the script's designed condition ("needed by no stage
  after replay_a"), and logged it in its `out/freed.json`. Not resource-steward's sweep (18:30Z: `/tmp` pytest only), not
  the src eviction (18:11Z: 6.2 GB), and no retention record. The Match leg itself ended `failed` at 18:29Z, which is
  circuits'. Separately, @infra's `vy-custody` exits 1 every 10 min (18:26, 18:36, 18:47Z) while still publishing runs.
- 19:00Z: asked @circuits (`1791226523.807879`) to confirm `replay_a.json` is valid after Match `8267`'s INCOMPLETE exit 1
  (G5/G7/G8 skipped for missing inputs), or else the 245 GB capture needs a GPU rerun; I suggested deleting only after
  Match exits 0. Asked @infra (`1791226524.628149`) whether `vy-custody`'s exit 1 (27 record-less attempts held) is a
  deliberate flag or a partial failure. Tell root only if circuits says the capture is lost.

## State at 18:30Z Oct 5 (11:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 71.1% (1,449 GiB free), `research/src` 51 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies. The
  next hourly snapshot is loop tick 48.

## State at 18:00Z Oct 5 (11:00 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 71.3% (1,441 GiB free), `research/src` 60 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies or
  inbox items for me.

## State at 17:30Z Oct 5 (10:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 71.2% (1,446 GiB free), `research/src` 57 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:fbc01e5df457939fc749b011916cbb635eb30f89e4f94bea90a93fee7997b281` (about 17:25Z).

## State at 17:00Z Oct 5 (10:00 AM PDT), steward pass

- Node 1 (watch, no flags): 71.4% (1,433 GiB free), `research/src` 58 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean.
- Node 2: back to 1 of 8 (a fill-runner job); circuits' bench and memory accounting's timing loop finished. No queue, and
  no replies.

## State at 16:30Z Oct 5 (9:30 AM PDT), steward pass

- Node 1 (watch, no flags): 71.1% (1,451 GiB free), `research/src` 53 trees, `provers` 1 admitted and 0 GPUs held. The
  pacer and dispatcher are clean.
- Node 2: 5 of 8 leased (circuits' `pu-commit-bench` on GPUs 0, 4 and 5; memory accounting's `timing-loop` on 6; a
  fill-runner job on 7), and no queue. No replies.

## State at 16:00Z Oct 5 (9:00 AM PDT), steward pass

- Node 1 (watch, no flags): 71.2% (1,445 GiB free), `research/src` 62 trees, `provers` 1 admitted and 0 GPUs held. The
  pacer and dispatcher are clean.
- Node 2: 2 of 8 leased (circuits' `pu-commit-bench` on GPU 4, and a fill-runner job on GPU 7), and no queue. No replies.
- The latest hourly snapshot is `art:87ad458070a151621c462e81c38f11199d24c4b94cf982596790d0d2cfebbfb6` (about 15:50Z).

## State at 15:46Z Oct 5: disk watch lifted

- An hour under 72% (70.8% at 14:46Z, now 71.1%, 1,449 GiB free), so `node1-disk-watch-78d` is off. The 30-min passes and
  node 1's watch (disk-72, disk-78) carry on.

## State at 15:30Z Oct 5 (8:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 71.2% (1,443 GiB free), `research/src` 56 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
  Loop tick 36 (15:29Z) is running the hourly snapshot.

## State at 15:00Z Oct 5 (8:00 AM PDT), steward pass

- Node 1 (watch, no flags): 70.9% (1,458 GiB free), under 72% since 14:46Z; `research/src` 61 trees. 0 of 8 GPUs and nothing
  in Kueue (idle, reported). The pacer and dispatcher are clean. `node1-disk-watch-78d` comes off at about 15:46Z if it
  stays under.
- Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.

## State at 14:30Z Oct 5 (7:30 AM PDT), steward pass

- Node 1: 72.8% (1,365 GiB free), easing from 73.9% at 14:15Z (disk-72, no nudge since src eviction is live);
  `research/src` 60 trees. 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and dispatcher are clean.
  `node1-disk-watch-78d` is on.
- Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:4d7dc3623d24a7033724270de12008588ab8ea316f08cbe96b2201bec41907a4` (about 14:25Z).

## State at 14:05Z Oct 5 (7:05 AM PDT), steward pass

- **Node 1 climbing again:** 70.9% (13:15Z), 72.0% (13:30Z), 73.6% (13:45Z), 74.0% (14:00Z; 1,304 GiB free). That's about
  150 GiB/h, reaching 78% in about 80 min.
  - No single writer: the probe shows only about 1 GB of vLLM integration logs per check. `research/runs` went from 540 to
    565 GB, `research/scratch` from 59 to 79 GB, and `research/cache` is 291 GB; `research` is 1,389 GB in all, `jobs`
    1,165 GB and `hf` 1,128 GB (steady).
  - No nudge for disk-72, since src eviction is live. Re-armed `node1-disk-watch-78d` (every 15 min) to tell root at 78%.
- 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner
  job), and no queue. No replies.

## State at 13:30Z Oct 5 (6:30 AM PDT), steward pass

- The quiet hold was released on schedule (`vy-quiet-release`, 13:30Z).
- Node 1: the watch flagged disk-72 (72.0%, 1,405 GiB free; 70.9% at 13:15Z). No nudge, since src eviction is live;
  `research/src` 58 trees. 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and dispatcher are clean.
- Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.

## State at 13:00Z Oct 5 (6:00 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 70.6% (1,475 GiB free), `research/src` 50 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean, and the quiet hold runs until 13:30Z. Node 2: 1 of 8 (a fill-runner
  job), and no queue. No replies.
- The latest hourly snapshot is `art:66aa3193434e12c60df3b24c825df60112758fc74ada794ce2dc589d5ead04b9` (about 12:50Z).

## State at 12:30Z Oct 5 (5:30 AM PDT), steward pass

- Node 1's quiet hold started at 12:30Z (`vy-quiet-hold`: circuits' admissions held until 13:30Z).
- Node 1 (watch, no flags): 69.3% (1,538 GiB free), `research/src` 44 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.

## State at 12:05Z Oct 5 (5:05 AM PDT), steward pass

- Unchanged. Node 1 (watch 11:30–12:00Z, no flags): 69.5% (1,529 GiB free), `research/src` 49 trees, 0 of 8 GPUs and
  nothing in Kueue (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
  No replies.
- This VM seems to pause briefly at times. The cron pass arrived 5 min late (12:05Z), and tick 20's sync (11:41Z) spanned
  about 16 min of wall clock, as tick 3's did at 07:07Z, more than `timeout -k 30 480` allows. The steps still finish
  normally, and node 1's watch covers the gaps.

## State at 11:30Z Oct 5 (4:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 69.4% (1,537 GiB free), `research/src` 47 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:b7ef95b9686c921f91a8fd2e9d8b46e05aa5f1960ffd9fb40105354460d15633` (about 11:15Z).

## State at 11:00Z Oct 5 (4:00 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 69.8% (1,513 GiB free), `research/src` 56 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies. The
  next hourly snapshot is loop tick 18 (about 11:05–11:15Z).

## State at 10:30Z Oct 5 (3:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 69.7% (1,519 GiB free), `research/src` 51 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.

## State at 10:00Z Oct 5 (3:00 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 70.8% (1,467 GiB free), `research/src` 61 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:b7b5f42f92bad3accc980033d38d464523603299efc107557145f5244598622f` (about 09:35Z).

## State at 09:30Z Oct 5 (2:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 70.7% (1,468 GiB free), `research/src` 59 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies. The
  next hourly snapshot is loop tick 12 (about 09:30–09:40Z).

## State at 09:00Z Oct 5 (2:00 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 70.6% (1,476 GiB free), `research/src` 75 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The 08:27Z Grafana "pod holds a GPU at 0%" alert (the brief `provers` lease) is moot: no GPU is held now.

## State at 08:30Z Oct 5 (1:30 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): 70.5% (1,478 GiB free), `research/src` 71 trees, `provers` 1 admitted and 0 GPUs
  held; the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:07ad4f0d572195b57b47d55095498db5a4ef311fc496d5e180c3071981528f8b` (about 08:00Z).

## State at 08:00Z Oct 5 (1:00 AM PDT), steward pass

- Node 1 (watch, no flags): 70.7% (1,470 GiB free), `research/src` 73 trees. `provers` has 1 workload admitted, and no GPU
  is held yet. The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- Loop ticks 4 (07:32Z) and 5 (07:43Z) were on schedule, so the 07:07Z stretch was a one-off.

## State at 07:30Z Oct 5 (12:30 AM PDT), steward pass

- Node 1 (watch, no flags): 70.6% (1,474 GiB free), `research/src` 68 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- Loop: tick 3's sync (07:07Z) ended normally ("to store 1") but spanned about 15 min of wall clock before the sleep began
  (07:22:45Z), longer than `timeout -k 30 480` allows. That's probably a brief VM pause, not a hang. Watch for a repeat.

## State at 07:00Z Oct 5 (12:00 AM PDT), steward pass

- Node 1 (watch, no flags): 71.3% (1,442 GiB free), `research/src` 78 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The restarted loop's ticks 0–2 ran cleanly under `timeout -k`. Tick 0's util_collect stored
  `art:dbaa7ad955fe459166f66eb092f2205deb69568c55c2ce3a8744294b4a1b29ac`, and drift reads Kueue "same".

## State at 06:30Z Oct 5 (11:30 PM PDT Oct 4), steward pass

- Node 1 (watch, no flags): 70.5% (1,477 GiB free), `research/src` 67 trees, 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- Steward loop: tick 398's channel sync hung from 05:45 to about 06:22Z with no output. `timeout 480` kills python, but the
  `| tail` waits on any child still holding the pipe.
  - **Fixed 06:33Z, at root's ask:** `/tmp/steward_loop.sh` now runs each step's whole pipeline under
    `timeout -k 30 N sh -c '…'` (channel sync 480 s, util_collect 900 s, drift_check 300 s). timeout signals its process
    group, so a hung child can't keep `tail` waiting. A failed or timed-out step logs a line.
  - Swapped in by atomic `mv` and restarted in tmux `steward-loop` (new pid 1438107, tick 0 at 06:33Z). A copy is in
    `tools/steward_loop.sh`.

## State at 06:00Z Oct 5 (11:00 PM PDT Oct 4), steward pass

- Unchanged. Node 1 (watch, no flags): 70.4% (1,484 GiB free), `research/src` 80 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies or
  inbox items for me.

## State at 05:30Z Oct 5 (10:30 PM PDT Oct 4), steward pass

- Unchanged. Node 1 (watch, no flags): 70.2% (1,497 GiB free), `research/src` 75 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:c4ab2e118332552a9b460866c42d5e36dc601db8ddc7bd4a6df239df9d0918c3` (about 05:20Z).

## State at 05:00Z Oct 5 (10:00 PM PDT Oct 4), steward pass

- Node 1 (watch, no flags): 70.3% (1,491 GiB free), `research/src` 84 trees. 0 of 8 GPUs and nothing in Kueue (idle,
  reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The 04:26Z Grafana "pod holds a GPU at 0%" alert (infra and dispatcher lanes) is moot: node 1 holds no GPU now.

## State at 04:30Z Oct 5 (9:30 PM PDT Oct 4), steward pass

- Node 1 (watch, no flags): 67.9% (1,609 GiB free; 65.2% at 04:15Z), `research/src` 73 trees. 1 of 8 GPUs held (`provers` 1
  admitted). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.

## State at 04:00Z Oct 5 (9:00 PM PDT Oct 4), steward pass

- Node 1 (watch, no flags): 65.5% (1,729 GiB free), down from 69.0% at 03:45Z (about 174 GiB freed), `research/src` 84
  trees. 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a
  fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:5f9b6b0a09fe789a8eb8b8bd39c5fc9dc6c45627d185b07656b524ec8f0cb886` (about 03:55Z).

## State at 03:30Z Oct 5 (8:30 PM PDT Oct 4), steward pass

- Unchanged. Node 1 (watch, no flags): 69.0% (1,557 GiB free), `research/src` 75 trees, 0 of 8 GPUs and nothing in Kueue
  (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies or
  inbox items for me.

## State at 03:10Z Oct 5: disk watch lifted

- An hour under 72% (69.3% at 02:09Z, 69.1% now, 1,550 GiB free), so `node1-disk-watch-78c` is off. The 30-min passes and
  node 1's watch (disk-72, disk-78) carry on. The @top pause line isn't needed. The @proofs and @ci questions stay open in
  the thread.

## State at 03:00Z Oct 5 (8:00 PM PDT Oct 4), steward pass

- Node 1 (watch, no flags): 69.0% (1,557 GiB free), `research/src` 79 trees. 0 of 8 GPUs and nothing in Kueue (idle,
  reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No replies.
- The latest hourly snapshot is `art:610da91933fc0f412a1a8fe383a5a24937cf0c925b49012cb164b17115875f89` (about 02:55Z).

## State at 02:30Z Oct 5 (7:30 PM PDT Oct 4), steward pass

- Node 1 (watch, no flags): 68.8% (1,564 GiB free), `research/src` 73 trees. 0 of 8 GPUs and nothing in Kueue (idle,
  reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. No new replies or inbox
  items for me.

## State at 02:10Z Oct 5: owners freed about 220 GiB, node 1 at 69.3%

- 69.3% (1,539 GiB free) at 02:09Z, from 73.7% at 02:00Z. Owners cleared their own data (no retention-log entries):
  - `glm47-match` 240 to 6 GB (circuits' GLM capture);
  - `cache/pouw-hidden-zk` 180 to 138 GB, and `pouw-hidden-zk-replay2` 80 to 70 GB;
  - `cache/verity-check` 159 to 104 GB (a finished audit's scratch).
- The @top pause line isn't needed unless the disk climbs back to 78%. `node1-disk-watch-78c` comes off after an hour under
  72% (about 03:09Z). The @proofs and @ci questions stay open for the record.

## State at 02:00Z Oct 5 (7:00 PM PDT Oct 4), steward pass

- Node 1: 73.7% (1,319 GiB free), `research/src` 82 trees. 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and
  dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
- No reply from @proofs or @ci. The @top pause line is held for 78%. The latest hourly snapshot is
  `art:10047c3e01f33e04981b20547abcbcc066a8c25a2d984fd39bcfadd4c5fdbebd` (about 01:50Z).

## State at 01:30Z Oct 5 (6:30 PM PDT Oct 4), steward pass

- Node 1: 73.0% (1,353 GiB free). The 01:11Z src eviction took `research/src` from 91 to 71 trees (74 now). 0 of 8 GPUs and
  nothing in Kueue (idle, reported). The pacer and dispatcher are ticking and clean. Node 2: 1 of 8 (a fill-runner job),
  and no queue.
- No reply from @proofs or @ci. The @top pause line is held for 78%.

## State at 01:00Z Oct 5 (6:00 PM PDT Oct 4), steward pass

- Node 1: 72.2% (1,395 GiB free), easing from 75.5% at 00:30Z; `research/src` 91 trees. 0 of 8 GPUs and nothing in Kueue
  (idle, reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
- No reply from @proofs or @ci. The @top pause line is held for 78%. `node1-disk-watch-78c` is on until the disk is an hour
  under 72%.

## State at 00:30Z Oct 5 (5:30 PM PDT Oct 4), steward pass

- Node 1: 75.5% (1,229 GiB free), flat since 00:13Z; `research/src` 85 trees. The pacer's cap is 0 GB at this level (its
  75% room target), with nothing waiting but the 2 kept rows. 0 of 8 GPUs and nothing in Kueue (idle, reported). The
  dispatcher is clean.
- Node 2: 1 of 8 (a fill-runner job), and no queue.
- No reply yet from @proofs (replay) or @ci (`verity-check`). The @top pause line is held for 78%.
- Infra's node-side move audit (`20261004T2359Z-report-node-side-move-audit`) lists resource-steward's `vy-node-sweep`, not
  my units.
- The latest hourly snapshot is `art:b60917a0e01013953ad14e05234a94007469e6939747f09e5bcb9c7e20b62bf9` (about 00:25Z).

## State at 00:12Z Oct 5: root's two asks (pause at 78%, the verity-check cache)

- **At 78% with no @proofs answer:** one line in the disk thread to @top, copying @proofs, to pause the K=14,336 replay
  (branch `cursor/pouw-c4-k14336-replay-b5fc`) until @proofs says how much more it writes. Draft: `/tmp/top-pause.txt`.
  Then report to root.
- **`research/cache/verity-check` is 159 GB.** Asked @ci, copying @infra (`1791159060.789029`): who owns it, and can any of
  it be evicted under a retention record?
  - 122 GB is two `lean-audit-scratch-*` directories (59 and 63 GB), in use right now by running Lean audits (pouw, pous,
    level3 cwds, files written 00:09Z), so not freeable yet. I asked whether check removes them when an audit finishes.
  - The rest: `lean-deps` 18 GB (warm deps, leave alone), `lean-records` 13, `circuit-check` 7, `lean-audit` and
    `lean-builds` about 1 each.
  - I found no @circuits statement on clearing circuit-check caches after #1126, so there's nothing to fold in.
- Disk 77% (1,185 GiB free) at 00:11Z. Nothing deleted.

## State at 00:08Z Oct 5: node 1 at 77%, the pouw-hidden-zk replay is filling it

- 77% (1,193 GiB free) at 00:06Z, down 41 GiB in 6 min.
  - `research/cache/pouw-hidden-zk-replay2` went from about 1 to 80 GB since 23:06Z, from four new runs
    (`r20261004-2304{45,55}`, `-2305{01,06}`, `cut_a_{head,form5,form6,first}-k14336`). `pouw-hidden-zk` is still
    180 GB.
  - A check copying `lean-records` into scratch adds about 7 GB.
- Followed up in one line to @proofs and @infra (`1791158845.092659`): answer, or pause the replay. A one-shot
  `node1-disk-78-soon` at about 00:12Z tells root at 78%. Nothing deleted.

## State at 00:00Z Oct 5 (5:00 PM PDT Oct 4), steward pass

- Node 1 (watch, disk-72, no nudge since src eviction is live): 75.4% (1,234 GiB free; 75.6% at 23:45Z), short of 78%.
  `research/src` 94 trees. 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and dispatcher are clean.
  @infra's `n1-lease` `VY_POOL_BORROW_UNTIL` expired at 00:00Z.
- Node 2: 1 of 8 (a fill-runner job), and no queue.
- No reply from @proofs or @infra on the `pouw-hidden-zk` cache. The coordinator lane's new friction note (`research merge`
  and stale PR heads) isn't for me.

## State at 23:30Z Oct 4 (4:30 PM PDT), steward pass

- Node 1 (watch, disk-72, no nudge since src eviction is live): 74.8% (1,266 GiB free), flat since 23:15Z; `research/src`
  83 trees. 0 of 8 GPUs and nothing in Kueue (idle, reported). The pacer and dispatcher are clean.
- Node 2: 1 of 8 (a fill-runner job), and no queue.
- No reply yet from @proofs or @infra on the `pouw-hidden-zk` cache (`1791155309.642929`). `node1-disk-watch-78c` is on.
- The latest hourly snapshot is `art:c29ca68baf75f5689fb5cd9cc81e4556d677673e405b00a50d28884f99feb95d` (about 23:20Z).

## State at 23:15Z Oct 4 (4:15 PM PDT): asked the pouw-hidden-zk owner, at root's ask

- **Root (23:02Z):** don't wait for 78%, since the pacer's cap drop slows merge trains. Ask the owner of the three
  `pouw-hidden-zk` `cut_a_form*-k14336` runs how much more they'll write and whether finished stages can be published out
  of `runs/`. Copy @infra, and delete nothing.
- **Correction to my 23:00Z read:** each of the three run directories is only about 1 GB (two done, one running). The
  probe's "about 10 GB each" was write traffic, not growth. The campaign's disk is its cache instead.
- **Where the disk went** (`du` at 23:10Z, against earlier):
  - `research/cache` grew from 157 to 342 GB: `pouw-hidden-zk` 180 GB, new `pouw-hidden-zk-replay2` since 23:06Z, and
    `verity-check` 148 GB.
  - `research/trees` is 84 GB (`lean-*` worktrees, about 12 GB each).
  - `research/scratch` grew from 13 to 59 GB, and `research/runs` from 521 to 540 GB.
  - `glm47-match` shrank to 240 GB.
- **Owner:** @proofs. The runs come from branch `cursor/pouw-c4-k14336-replay-b5fc`, a replay of #1034's `hidden_zk`
  driver (C-Flock `--zk`), and #1034 names proofs.
- **Asked** in one line in the disk thread, to @proofs with @infra copied (`1791155309.642929`): how much more it will
  write, and whether finished stages can be published out of `runs/` and the cache.
- Disk at 23:13Z: 75% (1,271 GiB free). `node1-disk-watch-78c` tells root at 78%.

## State at 23:00Z Oct 4 (4:00 PM PDT), steward pass

- **Node 1 disk is climbing with src eviction live:** 72.4% (22:30Z), 74.1% (22:45Z), 74.5% (23:00Z; 1,277 GiB free).
  `research/src` is steady at about 80 trees.
  - Writers over 10 MB/s since 22:25Z: three `pouw-hidden-zk` runs (`r20261004-2134{06,11,16}-*`, `cut_a_form*-k14336`
    stages) at about 10 GB each into `research/runs/*/out/`, plus about 1 GB of vLLM integration logs per check.
  - That's about 34 GB of the 105 GiB lost; the rest is slower writers.
  - Re-armed `node1-disk-watch-78c` (every 15 min) to tell root at 78%, about 50 min away at this rate. No nudge for disk-72
    (src eviction is live).
- GPUs idle, reported: node 1 0 of 8 and nothing in Kueue; node 2 1 of 8 (a `research` lease), no queue. The pacer and
  dispatcher are clean.
- The latest hourly snapshot is still `art:e9fe80bd…`.

## State at 22:30Z Oct 4 (3:30 PM PDT), steward pass: #1115 live

- **#1115 is live** (open ask 1, done; see Open asks). The watch still flags disk-72 (72.4%, 1,382 GiB free), but src
  eviction is live, so there's no nudge. The rest of the disk is the GLM capture and `research/runs`.
- GPUs idle, reported: node 1 0 of 8 and nothing in Kueue; node 2 0 leases and no queue. The pacer and dispatcher are clean.

## State at 22:00Z Oct 4 (3:00 PM PDT), steward pass

- **The watch flagged disk-72 at 22:00Z** (72.0%, 1,404 GiB free; `research/src` 84 trees). #1115 isn't live (old
  wrapper, no `src.conf`, pin still `e307a849`), and @infra hasn't answered the 21:44Z pin question. I added a one-line
  nudge under it (`1791151269.030879`), not a new ask.
- GPUs idle, reported: node 1 0 of 8 and nothing in Kueue; node 2 1 of 8 (a `research` lease), no queue. The pacer and
  dispatcher are clean.
- The latest hourly snapshot is `art:e9fe80bd5c6fc03b31bdc52e47415d6b213c9466f1c07746c2f2a528baf9279f` (about 21:55Z).

## State at 21:30Z Oct 4 (2:30 PM PDT), steward pass

- Both nodes' GPUs are fully idle, reported: node 1 0 of 8 and nothing in Kueue; node 2 0 leases and no queue.
- Node 1 (watch, no flags): disk 70.9% (1,458 GiB free), `research/src` 75 trees. The pacer and dispatcher are clean.
- In the infra lane: node2-ops' `20261004T2125Z-reply-from-node2-ops-runner-lock-on-main-not-deployed`. Node 2's fill runner
  lacks main's one-runner lock (`4c56e60a9b`); deploying it is @infra's. Not mine.
- #992 is still open, and @circuits' GLM footprint answer is still open.

## State at 21:15Z Oct 4 (2:15 PM PDT): disk watch lifted

- The disk has been under 72% for an hour (71.4% at 20:15Z, now 70.7%, 1,470 GiB free), so `node1-disk-watch-78b` is off.
  The 30-min passes and node 1's watch (disk-72, disk-78) carry on. @circuits' GLM footprint answer is still open.

## State at 21:00Z Oct 4 (2:00 PM PDT), steward pass

- Node 1 (watch, no flags): disk 71.7% (1,422 GiB free), `research/src` 81 trees. 0 of 8 GPUs and nothing in Kueue (idle,
  reported); the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue.
- No answer from @circuits on the GLM footprint, and #992 is still open. The latest hourly snapshot is
  `art:36e153cae0fc7956e7e365014ca3010d133a64f04bf47cc72e29fe088d68f75d` (about 20:50Z).

## State at 20:35Z Oct 4 (1:35 PM PDT), steward pass

- Node 1 (watch, no flags): disk 71.6–72% (1,426 GiB free), `research/src` 73 trees. 0 of 8 GPUs held, nothing in Kueue
  (idle, reported). The pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner job), and no queue. #992 is still
  open.
- The @top src ask is withdrawn (resource-steward's sweep prunes `src/`), and @circuits' GLM footprint question is open.
  The watch is now `node1-disk-watch-78b` (every 15 min: tell root at 78%, delete nothing).

## Friction: an unrecorded deletion under the shared `research` user (filed 20:05Z Oct 4, at root's ask)

- **What:** between 19:02 and 19:30Z on Oct 4, about 143 of node 1's `/workspace/research/src` trees were deleted, from 220
  to 77. Nothing is in `/workspace/research/retention/deletions.jsonl`, `src/.trash` is empty, and no sudo `rm` was
  involved. Nobody claimed it in the disk thread (asked at 19:33Z, `1791142428.245139`) by the 20:00Z full pass.
- **Why it matters:** retention exists so data you don't own is deleted only with its owner's recorded yes; its README's
  named failure is a bare `rm` on 3 Oct. Every agent logs into node 1 as `research` with one key, so neither sshd nor the
  journal says who.
  - No running check lost its tree this time (checked 19:36Z, including `f68a`). That was luck, not a guard.
- **Possible fixes (not mine to make):**
  - #992's gc with `src/.trash` and the retention log, so pruning is recorded;
  - per-agent SSH keys or a required `--by` on node-side deletes, so an actor is attributable;
  - making `research/src` deletable only through `research retention`.
- Status: open, for @infra (node 1's access and retention tooling).
- **Update 20:35Z: almost certainly resource-steward's `node-sweep.sh`,** so authorized. Its delete-without-asking list
  covers `research/src/<sha>` older than 6 h that nothing live references (Daniel's ruling on card `01933aa8`;
  `note:20260930T2205Z-report-resource-steward` §1). It renames through `src/.trash` before deleting.
  - It matches: 16 more trees went 20:02–20:15Z, all from my unused list and none in use, `.trash` empty, no retention log.
  - The friction narrows to: no retention record and no actor under the shared user. Posted in the disk thread
    (`1791145928.972449`), withdrawing the @top src ask.

## State at 20:05Z Oct 4 (1:05 PM PDT): disk at 75%, ask sent to @top and @circuits

- **Disk at 75% at 20:00Z** (1,292 GiB free at 20:02Z), from 69.8% at 19:45Z.
  - The writer was circuits' GLM-4.7-Flash `m1-capture` (`r20261004-194051-8f66`, direct GPU lease), which wrote about 246 GB
    from 19:40 to 19:57Z into `/workspace/research/glm47-match/` (that run 235 GB, the directory 354 GB). Its capture is
    done, and the disk is flat since.
  - The pacer's 78% latch can't slow a direct lease.
- `research/src`: 83 trees, 122 GB. 66 unused trees free 107 GB net
  (`art:4e752ca6fc4cf87420feba1f8d8ae43e18ac9b7933434f88b8a79789df381e37`).
- **Sent the ask** (root's 75% trigger) to @top and @circuits in the disk thread (`1791144236.471529`): circuits is to give
  the GLM run's further footprint and when the capture is preserved and evicted, and @top to approve the src cleanup
  (@infra owner).
- **On @top's yes, I run it:**
  1. re-scan with `/tmp/src_candidates.py`;
  2. keep trees whose 40-hex name is a commit in a fresh `git fetch origin`;
  3. `research keep PATH --owner @infra --priority low --expires now`;
  4. `research retention rm PATHS --approved-by @infra --ref <yes>`, dry first and then `--apply`.
- Watch: `node1-disk-watch-78` (every 15 min) tells root at 78%. The 10-min watch is retired.
- Node 1: 2 of 8 GPUs held (`provers` 2, the GLM work), and the pacer and dispatcher are clean. Node 2: 1 of 8 (a fill-runner
  job). New in the dispatcher lane: a 19:56Z "pod holds a GPU at 0%" alert (not mine). The latest snapshot is
  `art:d276acd724e0449c9edf5a2935b6032752f7a7d180da6ae60d45956be85f9dc7`.

## State at 19:35Z Oct 4 (12:35 PM PDT): research/src pruned by someone, unlogged

- **`research/src` went from 220 trees (19:02Z) to 160 (19:15Z) to 77 (19:30Z).** The disk fell from 73% (19:06Z) to 70.6%
  (1,476 GiB free, 19:30Z).
  - Nothing is in `deletions.jsonl` since 04:01Z, `src/.trash` is empty, and no sudo `rm` was involved (the trees are
    `research`'s). No Slack post claims it, and every agent logs in as `research`, so I can't tell who.
  - Asked in the disk thread for whoever pruned it to say so and how (`1791142428.245139`).
- **The @top ask is on hold:** the disk is under 72% and the trees are pruned. At the 19:50Z deadline, send it only if the
  disk is back at 75%, or if @infra says it wasn't involved and the trees regrow. I told root.
- Node 1: 1 of 8 GPUs held (`provers` 1). Node 2: 1 of 8 (a fill-runner job). The pacer and dispatcher are clean, and #992
  is still open.
- **Root (19:34Z):** hold the @top ask (send only at 75%, or if the trees regrow and @infra says it wasn't involved). Keep the
  "who pruned it" question open. If nobody claims it by the 20:00Z full pass, file a friction item: an unrecorded deletion
  under the shared `research` user.
- **No running check lost its tree** (checked 19:36Z):
  - `f68a` (`r20261004-184459-f68a`, check slot c and Lean check slot 1, mid Lean audit) is on `525e5c32…`, which exists.
  - So do the other live holders: check-b `6cfd99db…` and check-d `3f048ece…`.
  - Every running run's tree exists, except two Oct 1 runs whose pids are dead (stale records).
  - So I sent nothing to RC.

## State at 19:08Z Oct 4 (12:08 PM PDT): escalation path to @top, at root's ask

- **Root (19:05Z):** if @infra hasn't acted by 19:50Z or 75% disk, whichever comes first, ask @top in the disk thread to
  approve a repeat of this morning's cleanup under the same three conditions, with @infra as owner, naming who runs it.
  Delete nothing without that approval. Tell root at 78%.
- Timers: `node1-disk-watch-75` (every 10 min) and `node1-disk-top-deadline` (one-shot, 19:50Z). Draft:
  `/tmp/top-ask.txt`, sent with `--file`.
- On @top's yes, the runner is me:
  1. re-scan;
  2. keep only trees whose name is a 40-hex commit present in a fresh `git fetch origin` (condition 1, and condition 3
     follows for git-sourced trees);
  3. `research keep` each one (owner @infra, low, expires now);
  4. `retention rm --approved-by @infra --ref <@top's yes>`, dry first and then `--apply`.

## State at 19:05Z Oct 4 (12:05 PM PDT), steward pass: disk at 72%, @infra nudged

- **Node 1 reached 72% at 19:01Z** (1,416 GiB free), up from 69.2% at 18:45Z. A 24 GB Lean source tree landed at 19:00Z,
  and `research/runs` is 517 GB.
- `research/src` has 220 trees. 195 are unused by this morning's scan, and they free 162 GB net
  (`art:732c49efbaf0078b48b533086378a018142d90efed16b96f73583378c0830f29`).
- **Nudged @infra** in the disk thread (`1791140606.471969`, wording fix `1791140660.133439`): land #992's src-tree rule or
  run another `retention rm` under root's three conditions. #992 is still open. Next: tell root at 78% (the pacer's latch).
- Lesson: backticks inside a double-quoted `--text` run as shell commands. Post from `--file`.
- Node 1 GPUs: 1 of 8 held, `provers` 2 admitted. Node 2: 1 of 8 (a fill-runner job), and no queue. The pacer and
  dispatcher are clean. The latest hourly snapshot is `art:a33673c936681a6d553b691ba2ebe02996ef3f179543aece1ea00eb857367b6c`.

## State at 18:30Z Oct 4 (11:30 AM PDT), steward pass

- Node 1 (watch, no flags): disk 68.9% (1,561 GiB free; 41 GiB down since 18:15Z), `research/src` 207 trees. 0 of 8 GPUs
  and nothing in Kueue (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 GPUs (a fill-runner job), and no
  queue.
- #992 is still open, with no reply from @infra. Loop tick 342 (the hourly snapshot) started at 18:30Z; the latest stored is
  still `art:206177f4…`.

## State at 18:00Z Oct 4 (11:00 AM PDT), steward pass

- Unchanged. Node 1 (watch, no flags): disk 68.0% (1,606 GiB free), `research/src` 198 trees, 0 of 8 GPUs and nothing in
  Kueue (idle, reported); the pacer and dispatcher are clean. Node 2: 1 of 8 GPUs (a fill-runner job), and no queue.
- #992 is still open, with no reply from @infra. The next hourly snapshot is loop tick 342 (about 18:00–18:10Z).

## State at 17:30Z Oct 4 (10:30 AM PDT), steward pass

- Node 1 (watch, no flags): disk 67.3% (1,638 GiB free), `research/src` 194 trees, 0 of 8 GPUs held and nothing in Kueue
  (idle, reported). The pacer and dispatcher are clean.
- Node 2: 1 of 8 GPUs held (a fill-runner job), and no queue. #992 is still open, with no reply from @infra.
- node2-ops' note to @infra (`20261004T1715Z-reply-from-node2-ops-wasters-oct4-circuits-tp8-was-match-and-commit`): an
  8-GPU lease on node 2 is unmeasured, not idle. I added that caveat to the summary's day-three node 2 numbers. Nothing is
  for me to do.

## State at 17:00Z Oct 4 (10:00 AM PDT), steward pass

- Node 1 (watch, no flags): disk 68.0% (1,604 GiB free), `research/src` 186 trees. 0 of 8 GPUs held and nothing in Kueue
  (idle, reported). The pacer and dispatcher are ticking, and the dispatcher is clean.
- Node 2: 1 of 8 GPUs held (a fill-runner job), and no queue.
- #992 is still open, with no reply from @infra. The latest hourly snapshot is
  `art:206177f4cae09411bfac4dac40d6ff6b50a8d131563ab911c79c9021d701b0a7` (about 16:40Z).

## State at 16:30Z Oct 4 (9:30 AM PDT), steward pass

- **Node 1 disk never reached 72%.** It peaked at 71.4% (1,435 GiB free) at 16:15Z, then fell to 67.3% (1,641 GiB) by
  16:30Z: about 206 GiB freed outside retention (no decisions) and eviction, probably a run's own cleanup. `research/src`
  kept growing (177 trees). No nudge was needed. #992 is still open.
- Node 1 GPUs: 1 of 4 `provers` leases is a live `pr-1057` run (GPU 3), and the GPUs hold no memory now; the rest are idle.
  @infra restarted `n1-lease` on #1075 at 15:20Z (`VY_POOL_BORROW=6` until 00:00Z Oct 5: preemptible waiters may borrow
  circuits' GPUs), and `n1-lease-circuits` at 15:29Z. The pacer (cap 418 GB) and dispatcher are clean.
- Node 2: 1 of 8 GPUs held (a fill-runner job), and no queue.

## State at 16:00Z Oct 4 (9:00 AM PDT), steward pass

- **Node 1 disk is near the 72% nudge point:** 70.7% (1,471 GiB free) at 16:00Z, against 69.9% at 15:45Z; `research/src`
  has 159 trees. At this rate it crosses 72% around 16:30Z. If the 16:15 or 16:30Z watch line flags disk-72 and #992 (still
  open) isn't live, nudge @infra in the disk thread.
- Node 1 GPUs: 4 of 8 held, all preemptible `pr-1057` runs started 15:49Z (GPUs 1, 3, 4 and 7; `provers` has 4 admitted).
  GPUs 0, 2, 5 and 6 are idle. The pacer and dispatcher are ticking, and the dispatcher is clean.
- Node 2: 1 of 8 GPUs held (a fill-runner job on GPU 7), and no queue.

## State at 15:30Z Oct 4 (8:30 AM PDT), steward pass

- Node 1 (watch, no flags): disk 69.8% (1,515 GiB free), `research/src` 144 trees. The pacer and dispatcher are ticking,
  and the dispatcher is clean.
- GPUs idle, reported: node 1 0 of 8, nothing admitted or pending; node 2 1 of 8 (a `research` lease), no queue.
- #992 is still open, with no reply from @infra on open ask 1. The latest hourly snapshot is
  `art:9c8df68ccd2594bc86537826366a0972e77d0a35ee2058e90e36b58428fb0e12` (tick 330, about 15:15Z).

## State at 15:00Z Oct 4 (8:00 AM PDT), steward pass

- Node 1 (watch, no flags): disk 69.6% (1,525 GiB free), `research/src` 133 trees (126 at 14:32Z). That's about 85 GB an
  hour, which reaches the 72% nudge point around 16:30Z unless `src/` eviction goes live first. The pacer and dispatcher are
  ticking, and the dispatcher is clean.
- GPUs idle, reported, not offered: node 1 holds 0 of 8, with nothing admitted or pending. Node 2 has 1 of 8 (one
  `research` lease), an active agent and no queue.
- No reply from @infra on open ask 1. The next hourly snapshot is loop tick 330 (about 15:05Z); the latest is still
  `art:0c2f6f60…`.

## State at 14:35Z Oct 4 (7:35 AM PDT): recovery pass after the 07:02–14:26Z gap

- **The gap:** my agent VM was suspended from about 07:13Z to 14:20Z (the loop's `timeout` and `sleep` didn't advance). The
  research coordinator's timers stopped too. The 13:30Z utilization summary was missed, and I finalized it at 14:45Z.
- **Node 1 disk:** 69% (1,589 GiB free), flat since 07:00Z (1,605). It never reached the 72% nudge point or the 78% latch.
  - `research/src` has 121–126 trees and 276 GB.
  - **`src/` eviction isn't live:** no retention decisions since 04:01Z, and the 13:11 and 14:11Z hourly evictions freed 0 GB.
    #992 (open, updated 06:13Z) carries a `src-tree` rule (@infra, 6 h).
- **Quota:** the 10:30Z revert ran on time (`provers` 2, `deployments-gpu` 6). Its patch wrote `6` as a number, so drift read
  "DIFFER" on `"6"` vs `6` only. I re-applied `infra/nebius`'s `kueue.yaml` at 14:30Z (`kubectl diff` showed only that
  line), and drift reads "same" (logged in `quota-changes.log`).
- **Node 1:** 0 of 8 GPUs held, no workloads admitted or pending, and GPU busy at 0% over the last hour. The dispatcher and
  pacer are clean and ticking. Reported idle, not offered.
- **Node 2:** 1 of 8 GPUs held (a fill-runner job). Both queues are empty, the cluster agent is active, and the disk is at 55%.
- **Drift, also:** node 1's `/usr/local/bin/gpu-lease` is behind main (it's `cdcab7126`'s); node 2's matches main. That's
  @infra's deploy, so I only report it.
- **Settled during the gap:** network-accounting's 06:54Z seeds name their question: do chunks without the 5-s memory
  sampling, and 40-min chunks, keep more windows (calibration pass 3 input). @top approved it at 05:23Z, and it's now the
  `question` label on seeds 237–240 (`1791097457.393389`, after root asked in @top's thread).
- The 07:07Z Grafana alert (pool holder `gpu-pool-1791096899979` at 0% on GPU 2) is moot: node 1 holds no GPUs now.

## State at 07:00Z Oct 4 (12:00 AM PDT Oct 4), steward pass

- Node 1: 7 of 8 GPUs held, all preemptible leases through the pool. GPU 4 is idle.
  - Four are network-accounting's network-trace seeds (`benchmarks/network_traces/run.sh --seed N`, 45 min each). Two
    started 06:32–06:33Z, before my 06:34Z amendment, and two at 06:54Z.
  - Three are `pr-1057` runs (06:54Z).
  - The run records carry no research-question label, so whether these are approved items is for network-accounting and
    @top, not me. I reported it to root and posted nothing more.
- Node 2: 8 of 8 GPUs leased (4 memory-accounting `erase-calib`, 4 fill-runner jobs), and no queue.
- Node 1 disk: 69% (1,605 GiB free), `research/src` 106 trees, still below the 72% nudge point. No reply from @infra on
  open ask 1.
- The latest hourly snapshot is `art:0c2f6f604a61703c9e5ed49d7e3c3a3e7e126ba9b63c75bbc7472fd836e85586` (tick 324,
  about 06:40Z).

## State at 06:30Z Oct 4 (11:30 PM PDT Oct 3), steward pass

- **Network-accounting's sweep is done** (`1791093815.201609`). @top released node 1 at 05:23Z for circuits' GLM work, and
  the cancelled waiters were deliberate. Network-accounting runs only as backfill on GPUs I name, and does calibration on
  CPU.
- **Node 1: 2 of 8 GPUs held.** GPUs 6–7 have two `adhoc:ubuntu` leases since 06:15Z (one is `pr-1057`, preemptible).
  GPUs 0–5 are fenced and idle, and circuits' GLM work hasn't started (its one run was 05:46–05:52Z).
  - I named GPUs 0–5 for network-accounting's backfill, preemptible leases only through the pool, so any non-preemptible
    lease from circuits or RC preempts them (`1791095485.354199`).
  - **Amended at 06:34Z, at root's ask** (`1791095647.485629`): only for owner-approved items that each name their
    research question, otherwise leave them idle. The node 2 note got the same line (`1791095648.487279`). From now on I
    report idle GPUs and don't offer them as backfill (standing ruling at the top).
- **Node 2: 4 of 8 GPUs free since about 06:00Z.** The other four are memory-accounting's fill jobs, and both queues are
  empty. node2-ops has no Slack handle, so I told @memory-accounting and @compute-accounting directly
  (`1791095517.627029`), with no reply needed.
- Node 1 disk: 68% (1,637 GiB free), `research/src` 93 trees. The 72% nudge point isn't reached. No reply from @infra on
  open ask 1.
- The steward loop's tick 323 sync took about 16 min. Tick 324, with the hourly snapshot, comes at about 06:35Z.

## State at 06:00Z Oct 4 (11:00 PM PDT Oct 3), steward pass

- **Node 1: 0 of 8 GPUs held since 05:54Z.** The pool (`n1_lease.py`) released its 8 holders from 05:36 to 05:54Z because
  no runs were waiting.
  - Network-accounting's 04:04Z batch (non-preemptible trace chunks in `provers`) finished 05:34–05:47Z. Three of its
    waiters exited with SIGTERM (143) at 05:24Z while still queued, which looks deliberate rather than a lease fault.
    No top-up followed.
  - Routed in one Slack post to @network-accounting (top up, or say the sweep is done) and @old-circuits-and-proofs (other
    GPU work until the 10:30Z quota revert): `1791093768.014119`.
  - Quotas until 10:30Z: `provers` 6, `deployments-gpu` 2. The pacer has no Commits waiting except the 2 kept Gemma-2 b64
    rows. The CPUs are busy with check slots and builds.
- Node 1 disk: 69% (1,604 GiB free), `research/src` 79 trees, still about 55 GB per 30 min. The 72% nudge point isn't
  reached.
- Node 2: 4 of 8 GPUs leased (4 leases, both queues empty), another gap between top-ups. Recheck at 06:30Z.
- The steward loop's ticks have stretched to 10–26 min, so the next hourly snapshot (tick 324) is around 06:15Z. No reply
  from @infra on open ask 1.

## State at 05:30Z Oct 4 (10:30 PM PDT Oct 3), steward pass

- **Node 1's `research/src` is growing back**, as expected until open ask 1 lands. It has 71 trees and 228 GB, against 50
  trees right after the cleanup. `/workspace` is at 68% (1,631 GiB free): about 85 GB more used since 04:15Z, roughly
  70 GB an hour, so 74% is about 4 h away.
  - If it reaches 72% before @infra's hourly src eviction is live, nudge @infra in the disk thread.
  - The pacer's cap is 408 GB. 8 of 8 GPUs are held (8 provers), and the dispatcher is clean.
- Node 2 is refilled: 8 of 8 GPUs leased, with 2 `research` runs, 2 `adhoc:ubuntu` and 4 fill-runner jobs, and no queue.
  The 05:00Z gap closed by itself, so there was nothing to route.
- No reply from @infra on open ask 1. The latest hourly snapshot is still `art:99e0c0a5…`.

## State at 05:00Z Oct 4 (10:00 PM PDT Oct 3), steward pass

- Node 1: `/workspace` 66% (1,710 GiB free), `research/src` 61 trees, the pacer's cap 492 GB. 8 of 8 GPUs are held (8
  provers), and the dispatcher is clean.
- **Node 2: 4 of 8 GPUs held** (GPUs 0, 3, 4 and 7 empty), and neither the agent's queue nor the fill runner's has work.
  - Three one-hour POUS chunks (plain `research` submitter, 48 GiB, max 3,600 s) ended at 04:58Z. Their submitter tops up
    about hourly (02:54, 03:08 and 04:04Z), so this is the gap between top-ups that #1044 (standing campaign targets) is
    for. The four running jobs are the fill runner's.
  - Recheck at 05:30Z. If still idle, tell the POUS owners through node2-ops (bc-c0738ef6).
- The latest hourly snapshot is `art:99e0c0a5963bd2673ccf09b21c7added5cc4799a1b8907f6baca6a2a1194e931` (about 04:35Z).
  No reply from @infra on open ask 1.

## State at 04:30Z Oct 4 (9:30 PM PDT Oct 3), steward pass

- Node 1: `/workspace` 67% (1,694 GiB free); `research/src` is back to 52 trees. The pacer's cap is 474 GB, and the
  dispatcher is clean. 8 of 8 GPUs are held (8 provers).
- The 04:11Z hourly evictions ran on the pinned `e307a849`, at the 2,500 GB mark, and freed 3.9 GB.
- Node 2: 8 of 8 GPUs held, three of them fill-runner jobs started 04:24–04:28Z.
- No reply from @infra on open ask 1. The next hourly snapshot comes at loop tick 318 (about 04:31Z); the latest is
  `art:7e73e229…`, from about 03:30Z.

## State at 04:15Z Oct 4 (9:15 PM PDT Oct 3): research/src cleanup done, disk watch lifted

- @infra's `retention rm` finished at 04:01:19Z: 159 trees deleted (224.7 GB), all under root's three conditions.
  `research/src` now has 50 trees (@infra's "done", disk thread `1791086571.769439`).
- Disk: 66%, 1,715 GiB free, settled since 04:00Z. The pacer's cap is 500 GB. I lifted the 15-min watch
  (`node1-disk-watch`); the :00 and :30 passes keep checking the disk. Open ask 1 (hourly src eviction) is with @infra,
  with no decline so far.

## State at 04:02Z Oct 4 (9:02 PM PDT Oct 3): @infra is cleaning up research/src

- **@infra (bc-17cc41f1) is running `research retention rm`** as owner @infra, on root's yes relayed at 03:48Z. Root's three
  conditions: the commit is on origin; no running or queued run or slot uses the tree; no run record holds it as its
  source's only copy. Each decision is logged in `/workspace/research/retention/deletions.jsonl`.
  - By 04:01Z it had deleted 69 trees (205.6 GB), all from my candidate list (`art:bd3cf373…`) and none from the 20 I
    excluded. `research/src` is down from 201 trees to 170, and it is still running.
  - Disk at 04:00Z: 67% (1,690 GiB free); the pacer's cap is back to 465 GB.
- My 15-min disk watch stays through 04:15Z to confirm the end state, then comes off. The :00 and :30 passes keep checking.
- Node 1 has 8 of 8 GPUs held (8 provers), and the dispatcher is clean. Node 2 has 7 of 8 held, with the fill runner
  starting jobs.

## State at 03:30Z Oct 4 (8:30 PM PDT Oct 3): disk watch at root's ask

- **Root's ask (03:17Z):** check node 1's disk every 15 min (timer `node1-disk-watch`, at :15 and :45, plus the :00 and :30
  passes). If @infra hasn't acted by 74% or 03:47Z (one-shot timer `node1-disk-escalation-deadline`), whichever comes first,
  escalate to @infra and @top in the disk thread with an owner-approvable `research/src` cleanup through
  `research retention rm`. Delete nothing without approval. Tell root at 78% or if merges stall.
- **Cleanup prepared** (`art:bd3cf3736ce1712e2ab208a20eea55ca9868c8fcf48242eaeab4c935654279bd`; draft post in
  `/tmp/src-escalation.txt`):
  - 178 of 198 trees are unused, 219 GB net of hard links into `/workspace/cache` (uv) and the kept trees. 71 trees of
    1 GB or more hold 201 GB.
  - 20 trees (152 GB) are excluded: each has a live process, a running run's `job.json`, a live slot holder, or a change
    within the last hour.
  - No retention record covers `research/src`, so `retention rm` refuses them all today (dry run on `4e6cef7e`). The
    proposed owner is @infra, since this is `research run`'s machine-side cache.
  - Steps on approval: re-scan (`/tmp/src_candidates.py` on n1), `research keep` each tree (owner @infra, low,
    expires now), then `retention rm --approved-by @infra --ref <yes>`, dry first and then `--apply`.
- Disk at 03:23Z: 69%, 1,566 GiB free. Growth slowed to about 40 GB an hour after 03:11Z.
- 03:30Z pass: disk 69% (1,567 GiB free), and no reply from @infra on the src cleanup. Node 1 has 8 of 8 GPUs held (8
  provers) with the pacer's cap at 338 GB. Node 2 has 8 of 8 leased; GPUs 2 and 6 were starting fill-runner jobs. The
  dispatcher is clean, and the latest hourly snapshot is `art:7e73e229…`. Drift shows only the planned quota swap, which
  reverts at 10:30Z.
- **03:47Z: escalated** to @infra and @top in the disk thread (`1791085669.650279`), since nobody had acted on
  `research/src` by the deadline. The disk was 69% (1,573 GiB free), flat since 03:11Z. I'm waiting for the owner's yes;
  nothing is recorded or deleted.

## State at 03:15Z Oct 4 (8:15 PM PDT Oct 3): #1028 installed on node 1, eviction pause lifted

- **Done at root's ask** (root's Slack thread `1791083016.896119`, closed; reported in the disk thread `1790807092.688879`).
  - Main `59438bab7`'s tool snapshot is `e307a849d2b709e1`. It was already on node 1 and the newest, shipped at 02:17Z, so
    the 02:35Z and 02:51Z eviction runs already had `TREE_KEEP_S`.
  - Both units have a `tool-1028.conf` drop-in pinning `VY_RESEARCH_TOOL` to that snapshot, because the wrapper's default,
    the newest snapshot, can be an older branch's. Bump the pin when a later eviction fix lands.
  - **@infra had already done the install at 03:07Z, in parallel** (root's thread, `1791083313.080789`). It pinned the
    same snapshot, removed both `pause-until-1028.conf` drop-ins, stopped the 6 Oct auto-unpause timer, and ran the
    research store's eviction by hand: all 5 trees kept, 16.3 GB of preserved blobs and run files evicted. My 03:11Z
    `tool-1028.conf` replaced its pin with the same value, so there is one pin; my `rm -f` of the pause drop-ins was a
    no-op.
  - A dry run, then a second run by hand of each unit at the 2,500 GB mark: the research store's 5 trees (all fetched
    within 2.5 h) were kept with identical contents (`trees_kept 5`, `trees_removed false`). No process had a tree open.
    These runs freed 0.1 GB and 0 GB, since @infra's 03:07Z run had already freed what was evictable. The next hourly runs
    are at 04:11Z.
- **Eviction won't slow the disk.** `/workspace` is at 69% with 1,574 GiB free, down about 300 GB from 02:35 to 03:11Z.
  - The writes are check runs' source trees. `/workspace/research/src` holds 197 trees (356 GB, 39 of them since 00:00Z);
    three of 24–29 GB with Lean `.lake` builds appeared since 02:46Z. Another 48 GB is in `research/scratch`.
  - Nothing in the research tool prunes `src/`. Disk policy is resource-steward's (bc-b154b9ef), so I left the routing to
    @infra in the disk thread.
  - The pacer's cap drops at 78%, about 470 GB from here; resource-steward's writer pause is at 82%, and my guard at 90%.

## State at 02:30Z Oct 4 (7:30 PM PDT Oct 3), steward pass

- **Both servers have all 8 GPUs allocated, and neither has a queue.**
  - Node 1 has 8 provers admitted in Kueue, and all 8 GPUs hold about 90 GB. The pacer has nothing in flight; its only
    waiting Commits are the two batch-64 Gemma-2 rows (`cov-n050-2`, `cov-n051-2`) on circuits' keep list, held by design.
  - Node 2's `vy-cluster-agent` granted all 8 GPU leases, and its own queue was empty. GPU 6 was briefly empty and was
    granted at 02:29:55Z.
  - **Correction (03:35Z, from node2-ops' note `20261004T0321Z-alert-from-node2-ops-fill-pane-is-live-not-a-leftover`):**
    the `pouw-infra-fill` tmux pane is live; don't kill it. Its fill runner launches jobs under the agent's leases and keeps
    its own queue, which the agent can't see until a job asks for a lease. At 03:31Z two of the 8 leases were fill-runner
    jobs (GPUs 2 and 6), six were `research` runs, and two more fill jobs were queued.
- Node 1's `/workspace` is at 66% with the pacer's cap at 521 GB, and the dispatcher is clean. With the eviction pause at
  1,500 GB free, eviction starts again near 69%. The disk has climbed about 1.5% an hour since 23:05Z (61% to 66%), which
  reaches 69% around 04:30Z, and #1028 is still open. If the disk is at 68% or more and #1028 hasn't merged by then, raise
  it with @infra in the disk thread before eviction runs on the unfixed code.
- Running totals since Sep 30 05:16Z: node 1 is 103 of 746 GPU-h busy and node 2 is 169 of 739. The latest hourly snapshot is
  `art:54aa06e7f4a18d69f9836802cff75e55bc0d502ef7408c020c4eb322cac4eaa8`.

## State at 22:07Z Oct 2 (3:07 PM PDT Oct 2), steward pass

- **TP2 work is back on node 1** (in @top's thread `1790958343.711109`):
  - @circuits resumed the stochastic phi4 TP2 rows after fixing its staging bug.
  - @top approved 4 qwen3-14b TP2 greedy rows (`gm349`/`351`/`353`/`359`) on the new tree, unleased under the two-at-a-time TP2
    cap, switching to leased once the TP-lease change deploys.
- Node 1: 1 Commit in flight, disk 54%, and dispatcher and pacer are clean. Node 2: 1 GPU busy.
- The steward loop resumed after a pause, with tick 221 at 21:53Z; the next hourly snapshot is due on tick 222.
- 01:25Z Oct 4: **@infra paused both of my evictions (#780) at 00:14Z.** It added drop-ins
  `/etc/systemd/system/vy-store-evict{,-research}.service.d/pause-until-1028.conf` setting `VY_EVICT_FREE_GB=1500`, because
  eviction emptied fetched trees under running suites.
  - Since free space is 1.86 TB, above the 1.5 TB mark, they evict nothing until about 69%.
  - Node 1's disk crept from 61% to 65% (23:05–01:16Z); `jobs` is about 1,161 GiB (was about 1,050), and the pacer's cap is
    593 GB.
  - The drop-ins say "remove after #1028". **#1028 is the right PR**, though I first misread it: it bundles the eviction fix
    with the vLLM regression work.
    - `store/evict.py` adds `TREE_KEEP_S` (24 h), so `stale_trees()` only removes entries not fetched within it.
    - `store/local.py` has `fetch()` refresh the entry's mtime on every fetch.
    - I corrected my post in the disk thread, and won't open a duplicate PR.
  - **When #1028 merges:** check that the newest `/workspace/research/tool/*/` snapshot on node 1 (what `vy-store-evict` runs)
    has `TREE_KEEP_S`. Then remove both `pause-until-1028.conf` drop-ins, run `systemctl daemon-reload`, and check one hourly
    run keeps fresh trees (`trees_kept` in its report).
- 17:20Z Oct 3: **node 1's Lean audit cap (#947, main `0d4e61d5d`) is live.** `/workspace/research/locks/lean-slots` is
  `check 2` + `audit 2` = 4.
  - @infra wrote it at 16:52Z, the split @infra and @proofs agreed at 16:25Z.
  - Verified with main's `lean_slot.py`: `--pool check` took `check/0`, `--pool audit` took `audit/0`, and an unlisted pool is
    refused. Check's lean-audit step takes a `check` slot when its audit misses the cache.
  - Confirmed with real checks at 17:45Z: `check/0` and `check/1` are held by two checks' Lean audits (trees `21ae2464…` and
    `1d06cc08…`), taken at 17:40Z and 17:41Z.
  - My slip: at 17:15Z I wrote `any 4` over it without reading it first, and restored `check 2`/`audit 2` at 17:16:35Z. No slot
    was taken meanwhile; no `lean-*.lock` existed.
  - Told @proofs and RC in @infra's thread.
  - Lesson: read a node setting file before writing it, since another lane may own the current value.
- 16:10Z Oct 3: **the GPU quota is back at `provers` 6 / `deployments-gpu` 2.** A `kubectl patch` at 15:07:46Z did it, after
  @infra's 14:30Z restore to 2/6. I asked once in the allocation thread.
  - **Answered:** it is @infra's own move with circuits' OK, posted in that thread at 15:07Z (reply `1791040121.426949`); I had
    missed it.
  - A timer on node 1 reverts it at 10:30Z Sun Oct 4. The drift check's "DIFFER" is expected until then.
- 14:45Z Oct 3: **#925 and #931 merged at 14:39:33Z.** `check` now runs the six PyYAML test modules; it's test-only, so nothing
  deploys on node 1.
  - @infra restored the GPU quota on time (`deployments-gpu` 6, `provers` 2).
  - The drift check still flagged `deployments-gpu`'s GPU `nominalQuota`: the number `6` from @infra's patch, against `"6"` in
    the YAML. I patched it to the string form, so the drift check reads "same".
- 13:12Z Oct 3: **#925's train failed twice on node 1** (`r20261003-115617-1bb8`, `r20261003-121548-b4f2`) in
  `test_nebius_dispatch_pin.py`, one of the modules it stops skipping. Importing `dispatch.py` loaded node 1's real
  `/workspace/jobs/dispatch/dispatch.env`, with provers on 160-191, into `os.environ`.
  - @infra fixed it in [#931](https://github.com/danielreuter/verity/pull/931): `conftest.py` points `VY_DISPATCH_ROOT` at an
    absent dir. RC stacks #925 on it, and #925's head stays `d6a77c1e6`.
  - It's the same class of host leak as #701 and the bundle-sizes one; #925 surfaced it, as intended.
- 11:55Z Oct 3: **[#925](https://github.com/danielreuter/verity/pull/925)** (`d6a77c1e6`, ready) puts `pyyaml>=6` in the root
  dev group, so `check` runs the 6 Nebius test modules that skipped on `importorskip("yaml")` (81 tests, all pass). `research`
  stays stdlib-only; `uv lock` adds only `pyyaml 6.0.3`. The research and repository suites pass (research: 2 skipped, was 8).
  I told RC directly, and @ci in the disk thread. The next `check` reruns every suite once, since `uv.lock` is an input of all.
- 10:20Z Oct 3: the drift check reports node 1's live Kueue differs from `infra/nebius` (GPU nominal quotas). It's intentional
  and temporary. @infra's agent moved 2 GPUs from `deployments-gpu` to `provers` at 09:08Z for memory accounting's HBM check and
  network accounting's seeds (6/2 to 4/4; 3/5 at 09:14Z; `kubectl patch` back to 4/4 at 09:59:56Z). It will put them back at
  14:30Z (Slack `1791018655.389699`). Leave `kueue.yaml` alone; after 14:30Z, check the drift line is "same".
  - Update: at 10:37Z @infra raised `provers` to 6 (`deployments-gpu` 2), for network accounting's 5 concurrent trace chunks,
    still until 14:30Z (Slack `1791023955.632189`).
  - The #925 and #931 train's check `8512` was cancelled at 13:45Z (#905 landed) and restacked by RC. #931 still needs its
    author's ready label.
- 07:25Z Oct 3: node 1's `research` area swings: about 733 GB at 06:10Z, about 1,030 GB, then shrinking (-44 GiB in 2.5 min, at
  985 GB). Check runs and scratch build up between the hourly `vy-store-evict-research` passes (:50) and the cleanups, so the
  disk moves between 54% and 64% and the pacer's cap with it (649 GB at the peak). The latch is at 78%, so no action; watch it.
  On node 2 the same kind of scratch filled `/` (two Lean audit trees of about 60 GB each); @infra freed it to 213 GB at about
  06:52Z.
- 06:10Z Oct 3: node 1's disk went from 54% to 60% between 05:35 and 06:05Z, roughly 300 GB, and none of it was bundles (2 GB).
  - `research` is now about 733 GB: `runs` 364, `src` 194, `trees` 84. It was 854 GB a few minutes earlier and is shrinking about
    16 GiB/min, so it's being cleaned up.
  - The pacer's cap fell to 819 GB as designed. Nothing is growing now (`jobs` and `hf` are flat). No action.
- 02:40Z Oct 3: node 1's disk reached 64% with no Commit in flight, while 3 replays wrote. It's falling again (-9 GiB in 2 min).
  `jobs/cov` is 1,124 GB, against 553 GB of bundles the pacer counts, so about 570 GB is kept replay output or leaves. Worth
  asking circuits whether that can be preserved and evicted if the disk climbs. Latest hourly:
  `art:335dbf600cd702bac28e96f7f239eeb71dee1484034cf3f270294e3a7d21c73b`.
- 01:10Z Oct 3: node 1's disk went from 54% to 62% in 33 min (bundles 144 to 531 GB). The pacer has 2 in flight, projected at
  771 GB against a 1,206 GB cap, and holds `cov-gm190-rb` and `cov-gm175-rb` for room; the latch and pause are at 78% and 80%.
  The TP Commit lease has been live on node 1 since 00:30Z (circuits). Watch the disk next pass.
- 00:36Z Oct 3: the pacer has 4 in flight, all batch 8+, projected at 1,189 GB against a 1,297 GB cap, with 144 GB of bundles
  on disk; the disk is at 54%. Latest hourly: `art:6e4ee310c5131f6813c2bd38dc7b09402800183969bbe8082f99790096d8acf4`.
- 22:40Z: a TP2 Commit holds GPUs 2 and 3 (62 GB each), with 1 in flight. Latest hourly:
  `art:3553580273a6e527ad4feca55c9b8522c3352e31fe0536242413e797ffc16525`. The drift check is clean.

## State at 20:12Z Oct 2 (1:12 PM PDT Oct 2), steward pass

- **All 16 GPUs are idle, with nothing queued anywhere:** no ready files on node 1, an empty fill queue on node 2, and 0 Commits in
  flight. I told the research coordinator at 10:36Z that the queues are open, and haven't pinged again, to keep chatter low.
- Node 1's disk is at 53%. Dispatcher and pacer are clean. Latest hourly:
  `art:a1b652b8234d0b818e705a019309c5ed7edf9908085896cddd5b03125fc2dab5`.

## State at 19:17Z Oct 2 (12:17 PM PDT Oct 2), steward pass

- Dispatcher and pacer are clean on the `a2d9b48ba` code: no `tick failed` or `item-failed` in the pane.
- **Both nodes are idle with nothing queued:**
  - Node 1: 0 Commits in flight, CPU 23%, disk 54%, and nobody waiting for a check slot.
  - Node 2: 1 GPU busy, and the fill queue is empty.
- Latest hourly: `art:6d5d3e931d51da431de8c47da87a0cf585041f1e998a25a38208dba254019707`.

## State at 18:48Z Oct 2 (11:48 AM PDT Oct 2): tool-fix train `a2d9b48ba` deployed on node 1

- **#839's three node files** are installed from `a2d9b48ba` at 18:45:12Z: `dispatch.py`, `sky/release.py` and
  `sky/commit_pack.py`. Each live copy had equalled the pre-train main. Backups: `*.bak-20261002T1845Z-pre-839`.
  - **Dispatcher:** no restart needed (#819 runs each tick fresh). Clean ticks at 18:45:44Z and 18:46:46Z, and no `item-failed`.
  - **Pacer:** tmux `commit-release` restarted after a tick and has run since 18:45:38Z. The mirror
    `/workspace/jobs/dispatch/bundle-sizes.json` (mode 664) is identical to `~research/commit-release/bundle-sizes.json`.
  - **Pack pilot:** new pack pods read the new `commit_pack.py`.
- **Nothing else to deploy on node 1:**
  - `slot.py` runs from each check's own tree.
  - #836 (`research` CLI BLAS caps), #826 (custody) and #837 (`research merge`) are tool code that each run or client ships
    itself.

## State at 18:45Z Oct 2 (11:45 AM PDT Oct 2), steward pass

- **#695 merged at 18:10:42Z.** Main contains `4e18ac694`, and `nebius_auth` reads `NEBIUS_SA_PRIVATE_KEY_B64`, falling back to
  the old multi-line `NEBIUS_SA_PRIVATE_KEY` while `_B64` is unset. I told root, so root can ask Daniel to rotate the key.
  - Daniel's part: store the new key as `NEBIUS_SA_PRIVATE_KEY_B64` (`base64 -w0 key.pem`) and delete `NEBIUS_SA_PRIVATE_KEY`.
  - Nothing to deploy on the nodes: `common.sh` runs from the checkout that runs `launch.sh` and `teardown.sh`.
- #839 is still open and ready.

## State at 18:12Z Oct 2 (11:12 AM PDT Oct 2), steward pass

- **#695 is not in main yet.** Its combined train `bb4ed6605` passed (`r20261002-164824-6c2b`, done rc 0 at 17:42Z). Before it
  merged, main moved to `d407f982e`, @ci's 24-PR combined train, and that doesn't contain `4e18ac694`.
  - I asked the research coordinator directly to re-land it on the current main (Slack `1790964624.303819`).
  - Tell root when it merges.
- #839 is still open and ready.
- **Both nodes are idle with nothing queued:** node 1 has 0 Commits in flight and disk at 53%; node 2 has 1 GPU busy (PoUS).

## State at 17:37Z Oct 2 (10:37 AM PDT Oct 2), steward pass

- **#695** is still open. The coordinator cancelled its quick train at 16:48Z as superseded (#806 had landed) and rebuilt it as
  `bb4ed6605` (`cursor/train-prep-695-on-combined-f628`). That check is `r20261002-164824-6c2b` on node 1, slot `a`, still
  running at 17:35Z. Tell root the moment #695 merges.
- **#839** is open and ready.
- **Confirmed:** the first prover after the 15:00Z revert (`nd-proofs-vllm-mo-f6e0641252`) runs on `taskset -c 160-191`.
- **Circuits fixed the `cov-gm176` lease waste in #840:** `submit` checks the plan's code key, and a stale row stays on node 1 and
  derives its plans before taking a GPU.
- **Both nodes:**
  - Node 1 has 0 Commits in flight, CPU at 12%, and disk at 54%; nothing is queued.
  - Node 2 has 1 GPU busy, a PoUS soak rerun.
- Latest hourly: `art:c6ce73624458625b57f414664eed6515254f826c022774d9a86c901b7a11df55`.

## State at 16:50Z Oct 2 (9:50 AM PDT Oct 2): #695 and the friction pass

- **[#695](https://github.com/danielreuter/verity/pull/695)** (@infra's Nebius key fix), at root's ask after the sixth leak at
  09:37Z.
  - Merged main into it (`4e18ac694`). The one conflict: main's "rerun from a fresh tmux login shell" message, kept for the IDs
    and extended to the key under either name, with a test case.
  - Checked without printing or decoding the value. Both auth tests use explicit dummy environments, and a dummy `env -i` demo
    shows the multi-line form leaking its body lines while the base64 form prints only its name. Suites were run with the Nebius
    secrets unset.
  - Out of draft and marked ready. The research coordinator is checking it on its own quick train: `68b9d547e`, check
    `r20261002-163340-bbf1` on node 1, slot `a`, running since 16:34Z.
  - **When it merges, tell root**, so root can ask Daniel to rotate the key and store it as `NEBIUS_SA_PRIVATE_KEY_B64`.
- **[#839](https://github.com/danielreuter/verity/pull/839)** (`ed0d92b53`, ready), the three friction items, one commit each:
  - per-Job `try` in `tick()`, with `item-failed` and `tick failed: N Job(s) left unseen`;
  - `commit_pack.py` reads the pacer's learned rates from the `$VY_BUNDLE_SIZES` mirror, which `release.py` writes to
    `/workspace/jobs/dispatch/bundle-sizes.json`;
  - `slot.py`'s skip names `/etc/vy/direct-cpus`.
  - Deploy after it lands: the dispatcher needs nothing (#819). Restart tmux `commit-release` for the mirror, and check that
    `/workspace/jobs/dispatch/bundle-sizes.json` appears.
- **Gap found:** PyYAML isn't in the locked environment, so `check` skips every `importorskip("yaml")` test module (most dispatch
  and commit-pack tests). I told the research coordinator.

## State at 16:15Z Oct 2 (9:15 AM PDT Oct 2): node 2 agent restart done

- **Outcome** (`note:20261002T1606Z-reply-from-node2-ops-agent-healthy-on-main`): one restart, 16:02:40–16:04:17Z, with the agent
  stopped for 96 s.
  - The drill passed: a clean exit 0, `agent.lock` freed, and gpu-lease granted the drill job on GPU 7 with no `no-gpu` exit.
  - Re-pinned from `91af9a6bf` to main's `1253f09ec`; the old unit is in `/workspace/research/deploy/attic/`.
  - The ledger is one chain: seq 1935's `prev` is the old head, and `cluster ledger verify` reports 1,935 records intact.
  - To drain node 2, node2-ops paused memory accounting's vLLM e2e series with its stop switch at 15:35:58Z and restored it at
    16:05Z. It told memory accounting.
  - Commit `cov-gm176` went back to node 1 by itself at 16:01:38Z. It had held GPU 6 at 0% for two 25-min leases, recomputing
    its plan ("plan key differs"). That's circuits' `n2_commit.sh`, noted by node2-ops.
- I told the research coordinator that node 2 checks can resume, and @infra in the disk thread. Nothing else is open from this yes.
- **Still to verify:** the next node 1 prover gets `taskset` 160-191.

## State at 15:45Z Oct 2 (8:45 AM PDT Oct 2), steward pass

- **Node 2 restart:**
  - The research coordinator cancelled `9160` at 15:33Z (rc 143). Its custody runner, pid 1997360, has exited, and it starts
    nothing on node 2 until I say the agent is healthy.
  - Still blocking: the fill job `verity-commit-vllm-epoch-run-cov-gm176.sh` in `fill/running/`.
  - The agent is active, with no `STOP` yet. Waiting for node2-ops' reply in `lanes/infra/`.
- **On 2 Oct I asked @infra in the thread** to give node2-ops a Slack handle or have it watch the thread, at root's ask.
- **Circuits' overlap analysis** (`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/circuits/overlap-slowdown-analysis.md`):
  - Five leased `-to4` Commits pinned 1,284 GB of shared memory while each requested 170 G, so Commits slowed 5–12×.
  - Circuits will size gm-feed's B8+ requests from the predicted pool.
  - My call: no pacer memory rule for now, since Kueue's memory quota then caps pinned pools. If they still overlap after the
    resize, add the Shmem rule.
  - The vmstat collector is @infra's call. I replied in the thread.
- **Still to verify:** the next prover after 15:00Z gets `taskset` 160-191. None has been submitted since.

## State at 15:20Z Oct 2 (8:20 AM PDT Oct 2): node 2 agent restart approved, on @infra's behalf

- **Root asked** me to answer node2-ops' request for infra. I said yes to one restart of node 2's `vy-cluster-agent`, covering the
  rollback drill and the re-pin to main (`ef6a3e748` or later). node2-ops does both steps in one sitting.
  - Reply: `note:20261002T1515Z-reply-from-infra-drill-and-repin-one-restart-yes`, in `lanes/node2-ops/`, synced to the notes repo.
  - Posted in the disk thread for @infra (Slack `1790954030.024529`).
- **Conditions:**
  - check `r20261002-150400-9160` (#757, #806) on node 2 has finished; it started 15:05Z;
  - no prover, check or fill job runs on node 2. At 15:10Z a PoUS fill job and a GPU process were running;
  - the research coordinator was asked at 15:10Z to start no node 2 check until node2-ops reports healthy (Slack
    `1790953858.466389`).
- **Next for me:** when node2-ops' "healthy" reply lands in `lanes/infra/`, tell the research coordinator directly that node 2
  checks can resume, and record the drill's results here.
- **Not covered:** a second restart, a `fill_runner` rollback, or a pin other than main's head. Those go to @infra.

## State at 15:12Z Oct 2 (8:12 AM PDT Oct 2), steward pass

- **The lend revert ran at 15:00:00Z** (`slot-d-lend/log`): `VY_PROVER_CPUS=160-191`, and slot `d` is open with no `windows=`.
  Holder 333071 ended. All 4 slots are free, and nobody is waiting.
  - No prover has been submitted since. Next pass: check that a new prover's `taskset` is 160-191 (#819 rereads `dispatch.env`).
- **#830 merged at 15:03:05Z.** Node 1's deployed `sky/kueue.yaml` is now main's (backup `kueue.yaml.bak-20261002T1510Z-pre-830`).
  `kubectl diff -f kueue.yaml` shows no spec change; only the last-applied annotation was stale, from the 14:25Z `patch`. Live,
  `infra/nebius`, main and the deployed copy all agree.
- **Waiting on infra (bc-17cc41f1), not me:** node2-ops wants infra's yes and a time for node 2's `vy-cluster-agent` rollback drill
  plus a re-pin to main in one restart (`note:20261002T1505Z-reply-from-node2-ops-drill-and-repin-one-restart`). Cluster-build's
  watch has ended (`note:20261002T1500Z-handoff-from-cluster-build-agent-watch-ended`).
- The steward loop looks suspended again: its log stopped at 14:47Z, and its `sleep` reads as started at 15:00Z. It resumes by
  itself.

## State at 14:42Z Oct 2 (7:42 AM PDT Oct 2), steward pass

- **#824 merged at 14:17:34Z and has been live since 14:38:41Z.** Node 1's `sky/release.py` is main's (backup
  `release.py.bak-20261002T1440Z-pre-824`), and tmux `commit-release` was restarted right after a tick.
  - First tick: "a Commit of qwen3-8b (no size yet) is admitted: holding the deployments-gpu LocalQueue". 3 in flight, 1,144 GB
    projected against a 1,303 GB cap.
  - I told @circuits.
- **#830** is in check `r20261002-142145-d407` on node 2, and the coordinator merges it on the pass.
- **Slot `d` lend:** the revert timer fires at 15:00Z, and holder 333071 ends then too. Check `slot-d-lend/log`, then that the next
  prover gets 160-191 (#819 rereads `dispatch.env`) and that a check takes `d`.
- Node 1 disk at 53%. Node 2: 1 GPU busy. Latest hourly:
  `art:70a4c6d0a7fc43b340d9c856ebec9a785091c3b00c0d1f1a59d439c23d5b4af5`.

## State at 14:30Z Oct 2 (7:30 AM PDT Oct 2), steward pass

- **CPU quota was capping Commits on node 1.** `deployments-gpu` had 24 vCPU nominal plus 8 borrowing, fully used. Leased Commits
  request no GPU but up to 16 vCPU each, so only two fit.
  - `cov-gm192` (gemma2-9b b8, released at 14:13Z) sat `Pending` on "insufficient unused quota for cpu… 16 more needed", with
    8 GPUs idle and about 124 vCPU of unused nominal quota in the cohort.
  - Live at 14:25Z: the CPU `borrowingLimit` went from 8 to 72, and `cov-gm192` was admitted at once. Backup on node 1:
    `/tmp/cq-deployments-gpu.bak-20261002T1425Z.yaml`.
  - `infra/nebius` `e35d87346`; the drift check reads live and `infra/nebius` as the same.
  - [#830](https://github.com/danielreuter/verity/pull/830) (`1217592f7`, ready) syncs main's `sky/kueue.yaml` to `infra/nebius`.
    Main had also missed the 2 Oct memory moves.
  - I told the research coordinator directly, and @circuits and @ci in the disk thread.
- **Correction (14:35Z): the "GPU idle while work is waiting" alert was real, not false.**
  - Kueue's `pendingWorkloads`, which is `vy_exporter.py`'s `vy_queue_pending`, already leaves out deactivated workloads. Live
    now: the 2 held Gemma-2 Commits are unadmitted, and `deployments-gpu` reports pending 0.
  - Prometheus: `vy_queue_pending{deployments-gpu}` was 2–3 from 13:20 to 13:55Z, while the queue's CPU use was 20 and then 32 of 32.
    `sum(vy_ready_jobs)` was 0 throughout.
  - So the 13:52Z alert counted 2 active Commits waiting on CPU quota, the cap raised at 14:25Z. No exporter change is needed. I
    told root.
- **#824** is in train `2f5787e59`. #819 is live.
- **Slot `d`:** holder 333071 has it until 15:00Z.

## State at 13:43Z Oct 2 (6:43 AM PDT Oct 2), steward pass

- **The quiet hour and the disk guard both let go at 13:30Z.** Every ClusterQueue is at `None`, and the guard's `held` is empty.
- **Node 1:** the pacer has 4 in flight against a 541 GB projection and a 1,301 GB cap. Disk at 55%. GPUs are filling as those
  Commits start.
- **Node 2:** 1 GPU busy, and the fill queue is empty.
- **#824 is in the research coordinator's train:** `2f5787e59`, check `r20261002-132105-4f0d` on node 1, third in line. Deploy
  once it lands.

## State at 13:25Z Oct 2 (6:25 AM PDT Oct 2), steward pass

- **Node 1 recovered.** Replays drained the bundles from 1,437 to 182 GB, and the disk is at 54%.
  - `cap-150` is gone; someone else deleted it. The pacer's cap is 1,316 GB, with 2 Commits in flight.
  - Circuits says the pacing is fine. `gm343-to4` was llama32-3b, and no gemma2-9b b32 row is queued.
- **Holds:** every ClusterQueue is on Hold for the quiet hour, until 13:30Z.
  - The disk guard has also held `provers` and `backfill` since 12:31Z (80%; `/var/lib/vy-disk-guard/held`).
  - It releases them itself on its first check after the quiet hour, since the disk is under 75%.
- **Slot `d`:** `e2ef` finished. Holder 333071 now holds `check-d.lock` and lets go at 15:00Z.
- #824 is open in the queue. Latest hourly: `art:76124ad90524d77a4218bc4b88beebd7b591b61d6dff8174465fac9ff212749a`.

## State at 13:25Z Oct 2 (6:25 AM PDT Oct 2)

- **Correction to 12:40Z:** the six `-to4` Commits weren't gemma2-9b.
  - `gm340`–`342` are qwen25-3b b32, at 168–175 GB each. `gm346`–`348` are yi15-6b b32, at 274–287 GB each.
  - Only `gm347` went through the pacer's release, estimated at 205 GB. Kueue admitted the other five on arrival through the open
    gate; for example, `gm340` was created and admitted at 12:00:00Z.
  - The gemma2-9b rate came from `cov-gm138-r2` (b8, estimated at 76 GB).
  - I corrected it to @circuits.
- **[#824](https://github.com/danielreuter/verity/pull/824)** (`cursor/pacer-probe-unmeasured-e910`, `9d48127bd`), at root's ask:
  - `sized(row)` means a learned rate, or a row of `HIDDEN_X_LAYERS`.
  - A model without one has one Commit unfinished at a time.
  - While one is admitted, the gate holds the LocalQueue.
  - Two tests; removing either half fails both. The `research` and `repository` suites pass (`--quick`).
  - Marked ready. I told the research coordinator directly, and @ci in the disk thread.
  - When it lands: back up `sky/release.py`, install the merged file, and restart tmux `commit-release` between ticks.
- **#819 merged at 12:39:40Z and is live.** Someone else installed `dispatch.py` at 12:59Z and restarted the loop with
  `restart_loop.sh` at about 13:00Z. Its per-tick child is `dispatch.py loop --once`, with no `VY_PROVER_CPUS` in its environment.
  - The restart step is out of `slot-d-lend/revert.sh`; it's back to its author's version. My version is in
    `revert.sh.bak-20261002T1320Z-with-restart`.
- `cap-150` is still in place, since the disk is at 80%. Delete it once the disk is under 70%.

## State at 12:40Z Oct 2 (5:40 AM PDT Oct 2), steward pass

- **Node 1's disk: 61% at 12:09Z, 80% at 12:35Z** (3,994 GB used, 1,023 GB free, flat since).
  - Six gemma2-9b b32 `-to4` Commits (`cov-gm340`–`348`) wrote 168–287 GB each, 1.35 TB in all. The pacer had no gemma2-9b rate,
    and the formula estimate (Phi-3 scaling) was far too low.
  - The latch file `~research/commit-release/cap-150` was written at 12:28:49Z, at 78.0%. The cap is now 150 GB, and releases are
    paused at 80%.
  - Learned: `gemma2-9b` at 0.0263 GB per (batch × token). That's about 970 GB at the peak of one bundle while it was written; a
    b32 Commit is now estimated at 1,213 GB, so they go one at a time.
  - Replays: 5 running (`60b6`, `761f`, `9136`, `c533`, `eea8`). `d4f3`'s (gm340) waits for the quiet hour to end.
  - All 5 ClusterQueues are on Hold for the daily quiet hour (12:30–13:30Z); that hold isn't the disk guard's, which is at 90%.
  - I told @circuits in the disk thread.
- **Next:** delete `cap-150` once the disk is under 70%.
- **Slot `d`:** `e2ef` still runs on it, and holder 333071 is still queued. #819 is still open in train `bdaa8d28c`.

## State at 12:15Z Oct 2 (5:15 AM PDT Oct 2), steward pass

- **#819 is in the research coordinator's train:** `bdaa8d28c`, check `r20261002-114823-665c` on node 2, fourth in line. Deploy
  once `665c` lands.
- **Node 1:** 6 Commits in flight from the Builds that finished. Disk at 61%; the cap is 1,133 GB against a 1,061 GB projection.
  Node 2's GPUs are all idle.
- **Slot `d`:** `e2ef` still runs on it, and the steward holder (pid 333071) is queued behind it. The 10:48Z head waiter took
  slot `a`.
- **`utilization-summary.md` is finalized for the last 24 hours** (to 12:11Z), from
  `art:e928a60a5356cb83407ca00ad60900ec44c91b853023d30672279ecae768d932`:
  - Node 1: 166 of 192 GPU-h idle.
  - Node 2: 158 of 191 GPU-h idle.

## State at 11:52Z Oct 2 (4:52 AM PDT Oct 2), steward pass

- **A check got onto slot `d` during the lend:** `r20261002-104712-e2ef`, at about 11:45Z. Its pre-#789 `slot.py` read the slots
  file once, at 10:48Z, before the `windows=` was added at 10:59Z. Left running; I told @proofs.
- **The head of the line (pid 3558373, from 10:48Z, no reread) has the same blind spot.** So I queued a holder:
  - pid 333071, `flock -o -w 11501 check-d.lock`, which ends at 15:00Z. Its pid is in `slot-d-lend/d-holder.pid`, and it logs to
    `slot-d-lend/log`.
  - It takes `d` the moment `e2ef` ends and releases it by itself at 15:00Z. `/proc/locks` shows it queued behind 3555784.
- **Both nodes:** node 1's GPUs are idle, with 1 Commit in flight, replays being submitted, and the ready queue empty. Node 2 has
  1 GPU busy, and its fill queue is empty.
- #819 is open at `906215a04`, in the queue.
- Latest hourly: `art:c66263bcfccafc9b20000beb0102115338f692d58ed4e32a0e2b780744fc0a91`. Idle since Sep 30 05:16Z:
  - Node 1: 315 of 434 GPU-h.
  - Node 2: 246 of 427 GPU-h.
- **Before 13:30Z:** add an Oct 1–2 overnight section to `utilization-summary.md`.

## State at 11:47Z Oct 2 (4:47 AM PDT Oct 2)

- **[#819](https://github.com/danielreuter/verity/pull/819)** (`cursor/dispatch-reread-env-e910`, `906215a04`), at root's ask: the
  dispatcher loop runs each tick as a fresh `loop --once` process from `CALLER_ENV`, the environment captured before
  `load_settings`. So it reads `dispatch.env` as it is now, and removed keys drop out.
  - Test: `test_nebius_dispatch_settings.py`. It fails against main's loop and against a loop that passes its loaded `os.environ`.
  - `suites.py --quick` passes (22 suites).
  - It's marked ready. I told the research coordinator directly, and @ci in the disk thread.
- **When it lands:**
  1. Back up node 1's `/workspace/jobs/dispatch/infra/nebius/dispatch.py` (identical to main now), and install the merged file.
  2. Restart the loop once with `restart_loop.sh`.
  3. Check that the next prover's `taskset` matches `dispatch.env`.
  4. Then drop the restart step from `/home/research/slot-d-lend/revert.sh`; it's only needed while the old loop runs.
  - If it hasn't landed by 15:00Z, the revert's restart is what moves provers back to 160-191.

## State at 11:20Z Oct 2 (4:20 AM PDT Oct 2), steward pass

- **Slot `d`'s cores are lent to provers until 15:00Z.** Someone posting as @infra set this up at 11:01Z, at @proofs' ask (thread
  `1790937423.181889`): `VY_PROVER_CPUS=128-191` in `/workspace/jobs/dispatch/dispatch.env`, and slot `d` with
  `windows=/workspace/research/locks/slot-d-windows`, which opens 11:00Z for 240 min. `vy-slot-d-lend-revert.timer` undoes both at
  15:00Z (`/home/research/slot-d-lend/revert.sh`). While it lasts, node 1 has 3 check slots.
- **The lend only took effect at 11:16Z.** The dispatcher loop reads `dispatch.env` once, at start, so provers submitted at 11:05Z
  still got 160-191.
  - I added `/workspace/jobs/dispatch/restart_loop.sh` (copy in `tools/`). It restarts the loop 20 s after a tick, without the
    `dispatch.env` keys, in a login shell, and with `KUBECONFIG=/home/research/.kube/config`.
  - My first restart, at 11:13Z, came up without `KUBECONFIG`: 3 ticks failed and nothing was submitted. Fixed at 11:16Z.
  - Since then the zk-k32k BF16 K=32768 serve job (`nd-proofs-zk-k32k-2b534a426f`) runs on 128-191.
  - `revert.sh` now ends by running the helper (backup `revert.sh.bak-20261002T1120Z`). `tmux` reaches `node1-dispatch` from a
    systemd service as research; I tested that.
  - I told @proofs in the thread.
- **Both nodes:** GPUs are still idle apart from the provers. Circuits resent the 9 gemma2-9b Builds that failed on a grid-branch
  import bug.
- **At 15:00Z:** check `slot-d-lend/log` for the revert and the restart, and that the next prover gets 160-191.

## State at 10:40Z Oct 2 (3:40 AM PDT Oct 2), steward pass

- **#767, #783 and #789 merged at 09:40:58Z.** Node 1's live `sky/release.py` matches main. #780 and circuits' #805 are still
  open.
- **All 16 GPUs are idle, with nothing queued.**
  - Node 1: the dispatcher's ready queue is empty, and 7 Builds run on CPU. Bundles are down to 2 GB (from 306), and the disk is
    at 54%.
  - Node 2: the PoUS soak ended, and the fill queue is empty.
  - I told the research coordinator once that the queues are open.
- The 4 checks in slots, and the 7 in the line, predate #789's merge. The first check of main to take `d` is the end-to-end
  confirmation.

## State at 10:20Z Oct 2 (3:20 AM PDT Oct 2), steward pass

- **Node 1, all 8 GPUs idle, between waves:**
  - No Commit in flight. The dispatcher's ready queue is empty. 7 Builds started 09:38–09:53Z; their Commits follow.
  - The two Gemma-2 b64 Commits stay held by ruling.
  - CPU is 17–28% busy, at load 72.
- **Failures in the last 39 `vllm-epoch-run` jobs: 12.**
  - 9 `cov-gm34x` Builds exited with rc 10 (08:06–08:56Z). Their owner re-ran them as `-to4` items, which are running now with no
    deadline.
  - 7 `qwen3-30b-a3b` b8 `-to4` Builds were ended on purpose at 10:08Z: someone set each Job's `activeDeadlineSeconds` to 1.
    Not mine to chase.
- **Node 2:** one PoUS soak on GPU 7, and the fill queue is empty.
- **Slots:** all 4 are busy, with 8 checks in the line. `d` is held by `r20261002-082647-af3d`, whose code is from before #789.
- Latest hourly: `art:4fcccbc1f4027956cce78e2529ea465979079c912cff815862635d27e921b0f1` (09:48Z tick). Idle since Sep 30 05:16Z:
  - Node 1: 301 of 420 GPU-h.
  - Node 2: 233 of 413 GPU-h.

## State at 09:45Z Oct 2 (2:45 AM PDT Oct 2), steward pass

- **Correction to 09:12Z:** the two `gemma2-2b` b64 i1024 Commits (`cov-n051-2`, `cov-n050-2`) aren't waiting on the disk
  cap. The pacer's `kept()` holds them: it never releases b64+, and the top-level ruled at 1:30 AM PDT that Gemma-2 at b16+
  with i1024 stays held. #805 won't release them. I corrected it to @circuits in the disk thread.
- **Node 1:** GPUs are 0–6% busy.
  - 2 Commits in flight, 4 provers, and 14 Builds and replays on CPU. The dispatcher's ready queue is empty.
  - GPU work is waiting on the CPU Builds upstream, not on a limit.
  - Disk at 58%; the cap is 1,204 GB against a 525 GB projection.
- **Node 2:** one PoUS soak on GPU 7, and the fill queue is empty.
- **The steward loop paused, then resumed.** Its log stopped at 09:18Z, and its `sleep` reads as started at 09:38Z, which fits a VM
  suspension of about 20 minutes. Nothing needed restarting; the next tick runs the hourly utilization put.
- All 4 check slots are busy, with 7 checks in the line.

## State at 09:12Z Oct 2 (2:12 AM PDT Oct 2), steward pass

- **The pacer's batch-8+ limit is 6** (was 4), which @circuits okayed at 2:04 AM PDT. It's live on node 1 since 09:08:41Z
  (backup `sky/release.py.bak-20261002T0910Z-pre-big6`), and in #767 at `42b47d190`, re-marked ready. I told the research
  coordinator directly, and @ci and @circuits in the disk thread.
- **Commits:** 1 in flight. The two `gemma2-2b` b64 Commits now wait on the disk cap, about 37 GB short (687 + 585 GB against
  1,235 GB).
  - Circuits' #805 (queued) makes `evict --runs` see run outputs, about 453 GB on node 1, which raises the cap once it lands.
- **Slot `d` works end to end:** `r20261002-070557-a8e6` passed on it (rc 0, 08:44–09:02Z), and `r20261002-071347-cf2b` took
  it next. A check running #789's code hasn't taken `d` yet.

## State at 08:58Z Oct 2 (1:58 AM PDT Oct 2), steward pass

- **Node 1:** 4 Commits in flight, all batch 32, with GPUs filling as their pods start (4–32% at 08:52Z). 2 provers started
  at 08:50Z. Disk at 56%, and the cap is 1,251 GB against a 747 GB projection.
  - **What binds:** the pacer's batch-8+ limit of 4 (circuits, 6:09 PM PDT), not the disk. All 3 waiting Commits are batch 32–64.
  - I asked @circuits whether to raise it to 6. It stays at 4 until they answer.
- **Node 2:** one PoUS soak on GPU 7 (2 h so far). The fill queue is empty, so the other 7 GPUs have no work queued.
- **Totals since Sep 30 05:16Z:**
  - Node 1: 295 of 413 GPU-h idle.
  - Node 2: 228 of 406 GPU-h idle.
- Latest hourly: `art:9b793a6870582d0d667b00af5bed5b933468b52b353a8279fdac36d6db744d7e`.

## State at 08:50Z Oct 2 (1:50 AM PDT Oct 2)

- **Slot `d` is live again**, so node 1 has 4 check slots. `r20261002-074151-42ac` passed on 128–159, and the watcher re-added
  `d` at 1:18 AM PDT.
- **Two things kept checks off it:**
  - The watcher killed the `flock` parent (3423154), but its `sleep` child (3423156) kept `check-d.lock`. `flock` without `-o`
    hands the locked descriptor to the child. I released it at 1:44 AM PDT, and the head of the line, `r20261002-070557-a8e6`,
    took `d` within a minute.
  - `research run` starts every direct run on `/etc/vy/direct-cpus` (`remote.direct_cpus`), which said `0-95`. #789's guard
    compares a slot's cores with `os.sched_getaffinity(0)`, so it skipped `d` on the hedge train (`r20261002-083432-6142`).
- **Node change:** `/etc/vy/direct-cpus` is now `0-95,128-159`; 96–127 stays the dispatcher's. Backup:
  `/var/backups/vy-allowedcpus/direct-cpus.20261002T0845Z`. A fresh run, `r20261002-084614-911c`, starts on those 128 cores, and
  #789's `usable()` there lists c, a, b and d.
- **Rule for the CPU map:** `direct-cpus` must cover every check slot's cores, or #789's guard skips that slot.
- I told the research coordinator directly, and told @infra and @ci in the disk thread (the lander needs no change).
- #701's fill-runner failure is not from the cpuset: root dropped that question at 1:48 AM PDT, since the test also failed on
  node 2.

## State at 08:00Z Oct 2 (1:00 AM PDT Oct 2)

- **Non-bundle growth measured** from two full `du -d 2 /workspace` snapshots 26 min apart (06:45Z and 07:11Z): about
  50–55 GB/h in all.
  - `jobs/runs` ~23 GB/h (circuits' runs, mostly not preserved), `research/runs` ~16 GB/h (check runs), `jobs/store`
    ~14 GB/h, `hf` flat.
- **A second eviction, `vy-store-evict-research`** (User=research, hourly, on `/workspace/research/{store,runs}`), has run
  since 12:55 AM PDT. Its first run freed 106.7 GB from preserved copies, including files of 527 finished check runs.
  - It's in #780 at `02849d996`, re-marked ready. I told @ci and @infra.
  - I asked @circuits to push `jobs/runs` outputs so the eviction can take them.
- Slot `d` test `r20261002-074151-42ac` is still running on 128–159.

## State at 07:50Z Oct 2 (12:50 AM PDT Oct 2)

- **The host cpuset was widened to 0–159** at 12:37 AM PDT, per root: `systemctl set-property user.slice AllowedCPUs=0-159`,
  and the same for `system.slice`.
  - Old value: `AllowedCPUs=0-127` on both, set at 11:39 PM PDT Sep 30. The old drop-ins are in `/var/backups/vy-allowedcpus/`.
    Roll back with `set-property … AllowedCPUs=0-127`.
  - No running pod was pinned onto 128–159 at the time. The running checks kept their pinning (8–31, 32–63, 64–95), and a
    new ssh session gets 0–159.
- **My mistake, fixed at 12:29 AM PDT:** the 05:35Z narrowing of provers never reached the dispatcher loop. Its pane shell
  exported `VY_PROVER_CPUS=128-191` (and the other `dispatch.env` keys), which override `dispatch.env`. The loop was
  restarted after `unset VY_PROVER_CPUS VY_DISPATCH_CPUS VY_DISPATCH_DEPTH VY_LEASE_HOSTDIRS PACK_COMMITS PACK_PODS`, and now
  reads 160–191.
- **Slot `d` test:** `r20261002-074151-42ac` checks main `b8c9dd478` through
  `research run --tool check -- env CHECK_SLOTS=/workspace/research/locks-dtest/slots python3 tools/check/slot.py -- …`, with
  its own lock dir. It has been pinned to 128–159 since 12:42 AM PDT.
  - `/workspace/research/locks/slot_d_retest.sh` (pid 3917596) re-adds `d` to `locks/slots` and `check-slots` and kills the
    `check-d.lock` holder (pid 3423154) only on `done`/`rc 0`. The marker is `slot-d-readded`, or `slot-d-test-failed`.
  - Next pass: read the marker, post that `d` is back or stays out, and tell the research coordinator directly.

## State at 07:30Z Oct 2 (12:30 AM PDT Oct 2)

- **Slot `d` is out again** since 12:22 AM PDT. A `research run` session on node 1 is held to cores 0–127 (`AllowedCPUs` on
  `user.slice` and `system.slice`, set with `systemctl set-property` at 11:39 PM PDT Sep 30). So `slot.py`'s affinity call
  onto 128–159 failed with "Invalid argument", killing c37e, 5fc6 and 2ac5.
  - I removed `d` from `locks/slots` and `check-slots` (backups `*.bak-20261002T0722Z`) and disabled the watcher
    (`slot_d_waiter.sh.disabled-20261002T0722Z`).
  - I hold `check-d.lock` (pid 3423154, `flock … sleep`) so checks already waiting with `d` in their list can't take it.
    Release it once no waiter in `check-line/` is older than 07:22Z.
  - I told the research coordinator directly.
- **The fix is in #789**, now at `35beb61c9` and re-marked ready: `slot.py` skips any slot outside `os.sched_getaffinity(0)`,
  and a test fails without that filter. I told @ci.
- **Re-adding `d` needs @infra's yes** to `systemctl set-property user.slice AllowedCPUs=0-159`, and the same for
  `system.slice`. Then one check is run on `d` by hand, and `d` goes back only after it passes. Asked at 12:25 AM PDT.

## State at 07:20Z Oct 2 (12:20 AM PDT Oct 2)

- **Slot `d 128-159` is live** since 11:58 PM PDT, in `locks/slots` and `check-slots`, so node 1 has 4 check slots. I told the
  research coordinator and @ci that the lander needs no change.
- **It sat free with 9 checks in the line.** `slot.py` read the slots file once, before waiting, and the head of the line was
  a priority train ticket from 11:56 PM PDT, older than `d`. That clears when `a`–`c` frees.
  - The fix is [#789](https://github.com/danielreuter/verity/pull/789), stacked on #783: every retry rereads the slots file.
    It's marked ready at `3b1da247a`, and I told the research coordinator and @ci.
- #783 is reviewed and approved on @infra's behalf; I posted it to the research coordinator because I found no review-ask
  thread. #767 at `90b6cc699` and #780 at `e02e4359d` are open in the queue.
- Node 1: disk at 55%, inodes at 39%, the pacer's cap at 1,326 GB, and 2 Commits in flight. A second full `du` is running
  into `/tmp/du-snap/all-*` (the first was at 06:45Z); compare them next pass.
- Latest hourly utilization: `art:b5609bef810c9dfb06e141b04ac31e01ec93194fccb8cf53f80fafd68dd222f2` (12:00 AM PDT).

## State at 06:50Z Oct 2 (11:50 PM PDT Oct 1)

- **Correction to the 06:35Z block:** the non-bundle growth is *not* mostly circuits' run dirs. Two `du -d 2` snapshots 10 min
  apart (06:12Z and 06:22Z) showed:
  - `/workspace/jobs/runs` grew from 446 to 447 GB, about 6 GB/h, not about 68 as I claimed;
  - `/workspace/research/cache/verity-check` grew from 45 to 65 GB, from `lean-audit-scratch-*` dirs of 13–20 GB each, one
    per running Lean audit and none older than 30 min, so transient;
  - `/workspace/jobs/src` shrank from 91 to 19 GB, a cleanup.
  - `hf` (847 GB of models) wasn't in those snapshots.
  - I told @circuits and @infra that no change is needed on circuits' side.
- A full `du -x -d 2 /workspace` is running into `/tmp/du-snap/all-*`. Next: a second one about an hour later, then the
  diff, before asking anyone for anything.
- Learned estimates so far, in GB per batch × token: danube3-500m 0.0018, pleias-350m 0.0021, qwen3-06b 0.0035. So qwen3-06b
  b32 is now about 161 GB, against 480.
- Slot `d` is still waiting on 1 prover pod. Node 1 has no Commit in flight or waiting except the keep-list ones, and its
  GPUs are idle on Build supply.

## State at 06:45Z Oct 2 (11:45 PM PDT Oct 1)

- **The hourly eviction is live** since 11:35 PM PDT: `vy-store-evict.timer` and `.service` on node 1, running as ubuntu at
  idle I/O, with `/usr/local/bin/vy-store-evict`. It runs `research data evict --runs` until 2,500 GB are free, dropping only
  local copies the remote holds.
  - Its first run freed 125 GB, taking the disk from 57% to 55%. Each run logs a line to `journalctl -u vy-store-evict`.
  - It's in the repo as [#780](https://github.com/danielreuter/verity/pull/780), marked ready at `e02e4359d`; I asked @ci to
    stack it and told @infra.
- I told the research coordinator #767's head (`90b6cc699`) directly.

## State at 06:35Z Oct 2 (11:35 PM PDT Oct 1)

- **The cap was binding before the disk because the estimates ran 4–9x high.**
  - The formula sized every model it doesn't list as Phi-3-mini. qwen3-06b and r1-distill-qwen-15b b32 bundles came in at 51
    and 107 GB against 480 each.
  - Unfinished bundles already counted only what was left to write, and bundles on disk cancel out of the release test, so
    the estimates were the cause.
  - Since 11:25 PM PDT the pacer learns each model's size from the Commits it watches succeed: the largest written ×1.25, in
    `~/commit-release/bundle-sizes.json`, tracked in `bundle-track.json`. That's #767 at `90b6cc699`, marked ready, with @ci
    told. The previous file is `sky/release.py.bak-20261002T0625Z-pre-learn`.
- **Non-bundle growth, about 87 GB/h, is mostly circuits' run directories.** `/workspace/jobs/runs` gained 409 runs in 6 h at
  about 1 GB each (Build `outputs/build`, replay `replay_slim_p0`). Only 7 of its 2,936 run dirs are preserved on the
  remote, so they can't be safely evicted. I asked @circuits to push them (`research data push --pending`) or drop what
  finished chains don't need.
- **Pruned 184.6 GB** of local blobs in `/workspace/jobs/store` whose artifacts are preserved on the remote, oldest first. I
  used `research data evict --target-free-gb 2500`, run as ubuntu (which owns the blobs), with the shipped tool
  `/workspace/research/tool/e1e97b1dec5f6d11`. Disk went from 57% to 54% and the cap from 1,120 to 1,291 GB. About 120 GB
  more is evictable. I suggested to @infra an hourly `evict` on node 1, at a free-space mark of its choosing.
- Second `du -d 2` snapshot running in `/tmp/du-snap/` on node 1; compare next pass with the 06:12Z one.

## State at 06:15Z Oct 2 (11:15 PM PDT Oct 1)

- Slot `d` is still waiting: the waiter reports 1 running pod pinned onto 128–159, probably the prover-d pod running since
  9:13 PM PDT.
- **The pacer's cap is shrinking** with everything on `/workspace` that isn't a bundle: about 3.03 TB at 11:07 PM PDT against
  2.64 TB at 6:37 PM, roughly 87 GB/h. The cap went from 1,402 GB to 1,013 GB, and at this rate it reaches 0 in about 12 h,
  after which Commits stop.
  - The pacer holds `deployments-gpu` for `cov-gm437`, the next eligible Commit, whose estimate doesn't fit. All 8 GPUs on
    node 1 are idle.
  - A quick `du` timed out after `hf` (847 GB of models). A full `du -d 2` of jobs, research, verity-guest, cp and pouw is
    running on node 1 into `/tmp/du-snap/`. Next pass: compare it with a second snapshot to find the growers, then route
    the cleanup to their owner.
- Since 10:16 PM PDT Sep 29, node 1 has been 4.3% GPU-busy (16.5 of 387.5 GPU-hours) and node 2 26.7% (101.5 of 379.9)
  (`art:3136fbeb12c14b63a25dc36ff29c3b6170fcd9dba00ec8e48988ac235041e76f`, 10:41 PM PDT).

## State at 05:40Z Oct 2 (10:40 PM PDT Oct 1)

- **Slot `d` is on its way.** `VY_PROVER_CPUS` is 160–191 in `dispatch.env` since 10:35 PM PDT; the backup is
  `dispatch.env.bak-20261002T0535Z`, and the dispatcher was restarted. New prover jobs land on 160–191.
  - 7 prover pods created earlier still run pinned to 128–191, the oldest since 9:13 PM PDT.
  - `/workspace/research/locks/slot_d_waiter.sh`, under setsid on node 1 and logging to `slot-d-waiter.log`, adds
    `d 128-159` to `locks/slots` and ` 128-159` to `check-slots` once no running pod is pinned onto 128–159. It then writes
    `locks/slot-d-added`.
  - Next pass: if that marker exists, post in the disk thread that `d` is live, and tell @ci the lander needs no change.
    The only lander that locked `check-a.lock` directly was the research coordinator's, which launches through `slot.py`
    since #773 (`tools/check/train.sh`). Slot `a`'s holder since 10:01 PM PDT is still a direct flock, from before that
    change.

## State at 05:05Z Oct 2 (10:05 PM PDT Oct 1)

- **The pacer's hold gates only Commits, by construction**, since 9:59 PM PDT; nobody held the change.
  - Circuits' lease-pool holders queue on their own LocalQueue `deployments-gpu-pool`, on ClusterQueue `deployments-gpu` with
    the same quota. That is n1_lease.py's new `VY_POOL_LOCAL_QUEUE`. The circuits controller restarted in tmux
    `n1-lease-circuits`, and its 16 fences survived.
  - The pacer holds the `deployments-gpu` LocalQueue, not the ClusterQueue, which the quiet hour and the disk guard keep.
    The old ClusterQueue hold was released at the switch. The holder window is gone.
  - The repo has it in #767 at head `a8fa60289`, marked ready, with @ci told. `infra/nebius` has `kueue.yaml` as `c2cad7073`.
  - Backups: `n1_lease.py.bak-20261002T0500Z-pre-local-queue` and `sky/release.py.bak-20261002T0500Z-pre-local-queue`.

## State at 04:40Z Oct 2 (9:40 PM PDT Oct 1)

- **My `deployments-gpu` hold deadlocked two Commits from 9:09 to 9:32 PM PDT.** n1_lease.py's GPU holders
  (`gpu-pool-circuits-*`) queue in `deployments-gpu`, so the hold kept them out, and two admitted Commits waited for a lease
  with all 8 GPUs empty. Their projection then kept the hold on.
  - Fixed at 9:32 PM PDT: a pending pool holder opens the gate until it's admitted. Both Commits got their GPUs (0 and 7).
  - #767's head is now `2f96d7c57`, marked ready, with a test. Node 1 runs it, and I told @ci, @circuits and @infra.
  - The previous file is `sky/release.py.bak-20261002T0435Z-pre-holders`.
- `/workspace` is at 60%, and the pacer's cap at 1,194 GB.
- Since 10:16 PM PDT Sep 29, node 1 has been 4.3% GPU-busy (16.4 of 377.2 GPU-hours) and node 2 27.1% (100.1 of 369.7)
  (`art:5b20bce7f316b8281eac3dff62fe79afa860ca89c78f4aaea7d1ff9e2aec4e9a`, 9:24 PM PDT).

## State at 04:10Z Oct 2 (9:10 PM PDT Oct 1)

- **The pacer bypass is closed.** From 8:30 to 9:00 PM PDT `/workspace` went from 58% to 67%, about 860 GB/h. Kueue had
  admitted 4 big Commits past the pacer, falcon3-1b b32 ×2 and yi15-6b b16 ×2, projecting 2.1 TB against the 1.2 TB cap.
  Since 9:03 PM PDT the pacer holds `deployments-gpu` itself while the projection is at the cap or the disk at 80%, and
  releases its own hold under both; see `memory-requests-and-bundle-cap.md`. The disk eased to 64–65% as replays drained.
  I told @circuits and @infra.
- **The pacer is now in the repo:** [#767](https://github.com/danielreuter/verity/pull/767),
  `tools/research/src/research/pods/nebius/sky/release.py` beside `kueue.yaml`. Its tests cover the hold at the cap, the hold
  at 80% disk, and releasing only its own hold. The PR is marked ready at `63573a12c`; I asked @ci to stack it and told @infra.
  - Since 9:09 PM PDT node 1 runs that file from the deployed `sky/`, in tmux `commit-release`.
  - `~/commit-release/release.py` is a symlink to it; the old file is `release.py.pre-repo-20261002T0410Z`.
  - State stays in `~/commit-release`, configurable as `VY_PACER_DIR`.
  - The store copy `tools/commit_release.py` matches the repo.
  - Root's refinement, added at 9:15 PM PDT; the head is now `9372a3ccc`, marked ready, and @ci was told. The hold opens only
    when the admitted Commits' projection plus the next Commit's fits under the cap: the next released or waiting one, else
    the largest admitted. With none in flight the gate opens and one Commit goes even over the cap, outside the 78% latch.
    Node 1 runs it; the previous file is `sky/release.py.bak-20261002T0418Z-pre-next-fits`.

## State at 03:35Z Oct 2 (8:35 PM PDT Oct 1)

- **@infra confirmed the slot plan** at 8:19 PM PDT, choosing option (b) of proofs' two. At 10:30 PM PDT `VY_PROVER_CPUS`
  narrows to 160–191 and slot `d 128-159` follows, as planned. Until 7 AM PDT, proofs may run up to 4 untimed GPU fill jobs
  on node 2. Node 2 already shows 5 GPUs in use.
- Node 1: `/workspace` at 58%, the pacer's cap at 1,265 GB with 3 Commits in flight, and the dispatcher ticking.

## State at 03:05Z Oct 2 (8:05 PM PDT Oct 1)

- Since 10:16 PM PDT Sep 29, node 1 has been 4.4% GPU-busy (16.0 of 364.1 GPU-hours) and node 2 27.4% (97.9 of 356.6)
  (`art:06ae12704ec1a3ffdf273397cb5ab4015d897a0d4e0959a904ee185fc361207c`, 7:46 PM PDT).
- `/workspace` went from 57% to 62% between 7:30 and 8:00 PM PDT, about 200 GB of it outside counted bundles. The writers
  are two big Commits, cov rows at llama32-3b b16 and falcon3-1b b32, each writing about 20 GB/min, most of it not kept.
  The pacer's cap followed the disk down to 1,169 GB.
- The dispatcher ticks fine, all 3 check slots are busy, no lease pool is blocked, and nobody has replied about slot `d`.

## State at 02:45Z Oct 2 (7:45 PM PDT Oct 1)

- **A 4th check slot, due after 10:30 PM PDT (05:30Z).** Trains wait 25+ minutes for node 1's 3 slots (`c 8-31`, `a 32-63`,
  `b 64-95`).
  - Over the last 12 hours the slots averaged 36 of 88 cores busy (90th percentile 65). Builds and replays averaged 15 of 32,
    peaking at 32. Provers averaged 8 of 64 cores, peaking at 21. Checks use 5–41 GB of RAM each.
  - Plan: slot `d 128-159` from provers' range, with provers narrowed to 160–191. Builds and replays keep 96–127.
  - @proofs asked to hold until 10:30 PM PDT, because Daniel asked for 24 timed `--zk` points that need all of 128–191.
- Steps on the first pass after 05:30Z:
  1. Set `VY_PROVER_CPUS=160-191` in `dispatch.env` and restart the dispatcher (tmux `node1-dispatch`, as research).
  2. Wait until no running provers pod is pinned to 128–159.
  3. Append `d 128-159` to `/workspace/research/locks/slots`, and add ` 128-159` to the first line of
     `/workspace/research/check-slots`.
  4. Post in the disk thread that `d` is live.
- `slot.py` checks pick up `d` by themselves. The lander that flocks `check-a.lock` with its own `taskset` needs `d` added to
  its list; I asked @ci. `check_slot.sh` names slots a–d, so 4 is its ceiling without a code change.

## State at 02:32Z Oct 2 (7:32 PM PDT Oct 1)

- **Node 1's dispatcher was redeployed from `main` at 7:27 PM PDT.** It's `main` at `63ce2ea1d`, which carries #732, #745 and
  #746, plus #713's `dispatch.py` changes. #713 adds the pack-pod fit check, live since 1:09 PM PDT and still unmerged.
  - The previous copy is `dispatch.py.bak-20261002T0230Z-pre-main`. Settings come from `dispatch.env`, unchanged.
  - The loop runs as `python -u dispatch.py loop --every 60 | tee -a /workspace/jobs/dispatch/loop.log`, in tmux
    `node1-dispatch` as research.
  - The ticks at 7:28 and 7:29 PM PDT succeeded. Root asked for the redeploy, and I told @circuits.
- I asked @circuits to have the hiding-commitments worker submit through the dispatcher's ready files instead of creating a
  chain's later Jobs itself.

## State at 02:25Z Oct 2 (7:25 PM PDT Oct 1)

- Since 10:16 PM PDT Sep 29, node 1 has been 4.4% GPU-busy (15.6 of 355.6 GPU-hours) and node 2 27.8% (96.7 of 347.9)
  (`art:75742f63c00a0d224ad68b268f97ff63cf441901e2a59882dc5f05024a5e1115`, 6:41 PM PDT).
- #732 and #746 merged, at 6:21 and 7:09 PM PDT. The relay asked @circuits to redeploy node 1's `dispatch.py` from main at
  7:10 PM.
- **The dispatcher stalled again from 6:55 to 7:20 PM PDT, 26 failed ticks.** `cov-hide-gm392-c`'s replay Job was created
  out of band at 6:54 PM, so routing its Commit's end hit AlreadyExists. The relay alerted @circuits and @infra at 7:00 PM
  (5 failed ticks). At 7:20 PM I labelled the Commit Job `seen=1`, and the next tick submitted two replays and a Commit.
  Until node 1 runs #732, each out-of-band submission of a chain's next task can stall it again.
- Node 1 has no GPU in use. 2 Commits are admitted, `deployments-cpu` has 17 admitted and none pending, and the pacer's cap
  is 1,332 GB. `/workspace` is at 60%. Node 2 is idle.

## State at 02:20Z Oct 2 (7:20 PM PDT Oct 1)

- Backlog item 2 (memory per class) and the bundle cap are done; see `memory-requests-and-bundle-cap.md`.
  - gm-feed's Build and replay requests now come from measured peaks plus a margin (applied 7:15 PM PDT).
  - 160Gi of guaranteed memory moved from the GPU queue to the CPU queue (`19003d0c1`).
  - The pacer's cap follows the disk: 1,335 GB at 7:16 PM PDT.
- Still open: leased Commits bypass the pacer, because Kueue admits them before its tick can hold them.

## State at 01:35Z Oct 2 (6:35 PM PDT Oct 1)

- #732 merged at 6:21 PM PDT; #746 is ready and with @ci. The relay sends the redeploy ask to @circuits once both have
  merged.
- The live `VY_LEASE_HOSTDIRS` default works: all 4 leased `deployments-gpu` Commit Jobs created since 6:14 PM PDT mount
  `/run/gpu-lease-circuits`.
- On node 1, 7 of 8 GPUs are empty, `provers` admits nothing, and `deployments-cpu` has 6 Builds and replays pending on its
  384Gi limit. The pacer projects 947 of its 1,000 GB cap, with 479 GB of bundles waiting for replay. So Commits are limited
  by how fast replays clear bundles and by Build quota, both already recorded at 00:45Z. Node 2 is running on 3 GPUs.
  `/workspace` is at 58%.

## State at 01:20Z Oct 2 (6:20 PM PDT Oct 1)

- The circuits lease pool was blocked twice, at 5:49 and 5:58 PM PDT. Both strays were circuits' hiding-commitments retries
  (cov-hide-gm392-b and -b2) on a tree without `gpu_lease.py`, submitted through lease-pilot scripts that circuits has since
  guarded. The relay's new check posted both to @infra within a minute. Circuits cleared the pool at 5:58 and 6:09 PM.
- **Circuits' Commits leasing from proofs' pool, found and fixed.** Five rows whose Build was moved to node 2 (cov-gm290,
  gm291, gm295, gm302 and f6f9d7d87d's) had their Commits submitted by `n2_build.sh`'s hand-back. It runs `dispatch.py submit
  --task 1` over ssh without `VY_LEASE_HOSTDIRS`, so the Commits fell back to `/run/gpu-lease`. The fix is
  [#746](https://github.com/danielreuter/verity/pull/746), still a draft: `dispatch.py` defaults the variable to
  `deployments-gpu=/run/gpu-lease-circuits` for every caller. I patched the same default into node 1's deployed copy at
  6:14 PM PDT (backup `dispatch.py.bak-20261002T0120Z`). The loop wasn't restarted, since it already has the variable. The
  relay's redeploy ask for #732 now tells circuits to keep this default.
- Those moved Builds' node-1 Jobs are deleted when they move, so their hand-back can't cause the AlreadyExists stall.

## State at 00:45Z Oct 2 (5:45 PM PDT Oct 1)

- Since 10:16 PM PDT Sep 29, node 1 has been 4.4% GPU-busy (15.2 of 347.5 GPU-hours) and node 2 28.2% (95.9 of 339.8)
  (`art:49d408d5a71fb8b6b22548c5a9f91f29962a641a94428d8fee46e41feb7c60b8`). The 5:25 PM PDT hourly collection failed on a
  one-off ssh error (exit 255), and the rerun at 5:42 PM worked.
- The limit is still 384Gi, the drift check shows live Kueue matching `infra/nebius`, the dispatcher's ticks succeed, and #732
  is open, not yet merged.
- `deployments-cpu` is full again at 849 of 864Gi, with 4 Builds and 2 replays pending, while node 1 has 1.18 TB of RAM free.
  I'm not raising the limit further. The cohort has 1,365 of its 1,664Gi booked, so 128Gi more borrowing would leave room
  for only about one more 170 GB Commit before Commits start evicting borrowing Builds, which restart from scratch. The
  pacer allows 6 Commits in flight. The lasting fix is right-sizing requests: booked memory is about 2.5× what's in use
  (539 GB). That's backlog item 2, memory per class, owned by epoch-run and resource-steward.

## State at 00:10Z Oct 2 (5:10 PM PDT Oct 1)

- `deployments-cpu` still borrows up to 384Gi (no flip-flop).
- **The dispatcher failed every tick from 2:42 to 5:05 PM PDT.** `cov-gm390`'s Commit Job was created by another path at 2:38
  PM PDT, before its Build's end was routed. From then on, each tick's `kubectl create` of that Job raised AlreadyExists and
  aborted the tick before the Build got its `verity.dev/seen` label, about 140 times. Everything after it was skipped:
  - two finished Builds' Commits (cov-gm183 since 3:19 PM, cov-gm297 since 4:58 PM);
  - cov-gm390's replay;
  - two item ends;
  - the pack, node-2 spill and ready-item steps, while node 2 sat idle.
- At 5:05 PM PDT I labelled the Build Job `seen=1` by hand, which is what the tick would have done. The next tick submitted
  all of the above, plus two new Builds. The fix is [#732](https://github.com/danielreuter/verity/pull/732): `submit()` counts
  an existing Job of the same item, task and try as submitted. Node 1 runs an older, unmerged copy of `dispatch.py`, so it
  gets the fix only when redeployed. I told @infra and @circuits in the disk thread.
- 5:15 PM PDT: #732 is out of draft, marked ready at `d7110aa31` (`research queue ready 732`), and @ci was asked on Slack to
  stack it. The steward's relay (`tools/alert_pull.sh`) now does two more things:
  - it posts the redeploy ask to @circuits once, when #732 merges (`/tmp/merge-watch.tsv`);
  - it reads the dispatcher's ticks from its tmux pane (`tools/dispatch_ticks.py`), because `loop.log` has been silent since
    1:10 PM PDT. It posts one line to @circuits and @infra, at most once an hour, when 5 or more ticks fail in a row. It also
    posts when the ticks are unreadable or absent for 10 minutes on 3 checks in a row, so it doesn't fail open.
- Otherwise node 1's GPUs are idle by design. Circuits' late-lease Commits hold a GPU only for their 2–4 min GPU work pair,
  then finish on CPU. The two held Commits (cov-n050-2, cov-n051-2) are batch-64 Gemma-2 rows on circuits' keep list.

## State at 23:35Z (4:35 PM PDT)

- Since 10:16 PM PDT Sep 29, node 1 has been 4.4% GPU-busy (14.7 of 334.8 GPU-hours) and node 2 29.1% (95.4 of 327.2)
  (`art:48a5ab1757c60b5a6d4268f7177219e0b5429c581297354e9682bd40c994d7e2`).
- At 4:31 PM PDT node 1 had 7 of 8 GPUs empty. The chain started with `deployments-cpu`, at its memory limit (128Gi of
  borrowing, 637 GB booked), where 3 replays and a Build waited with 1.29 TB of RAM free. Because the replays waited, 743 GB of
  bundles stayed on disk, which held the Commit pacer at its 1 TB cap (2 Commits held, 1 in flight). @infra's 9:59 AM PDT
  raise to 256Gi had reverted itself at 10:14 AM PDT when `provers` admitted a workload, and circuits' 11:00 AM ask to size it
  again went unanswered.
- At 4:34 PM PDT I raised the limit to 384Gi, live and on `infra/nebius` (`49f235f8b`), and told @infra and @circuits in
  circuits' thread. Kueue admitted all 4 at once. The cohort's 1,664Gi nominal stays under node 1's 1,716 GiB, and Commits
  (600) reclaim from borrowing Builds (500) but not replays (600). To revert, set it back to 128Gi.
- At 4:37 PM PDT the limit is still 384Gi. @infra's `cpu-borrow-watch` on node 1 exited after its 10:14 AM PDT revert, and its
  tmux pane now only runs `sleep 86400`. Root's instruction: check the limit on every pass. If it's back at 128Gi, don't
  re-apply it; ask @infra on Slack to retire or adjust the revert rule under Daniel's 12:12 PM PDT one-pool ruling, and tell
  root. The hourly drift check would also flag a revert, because live Kueue would then differ from `infra/nebius`.

## State at 23:10Z (4:10 PM PDT)

- Node 1 was 0% GPU-busy from 3:00 to 4:00 PM PDT, because both of its lease pools were blocked. `gpu_stray.py` wrote `blocked`
  in `/run/gpu-lease-circuits` at 2:42 PM PDT and in `/run/gpu-lease` at 2:48 PM PDT, so no new leases were granted. Kueue
  still admitted 8 Commits, and their pods sat on `gpu-lease --wait` for up to an hour. Meanwhile one GPU-mode bootstrap held
  the host-wide bootstrap lock while it waited on the pool, so every other bootstrap queued behind it.
- Cause: circuits' late-lease Commits released the lease while the driver still listed the process for 5–9 s, and the probe
  caught it in that window. The fix is `dd92caa8a` (`cursor/commit-lease-late-b3b0`), live since 3:42 PM PDT. @circuits
  asked @infra to clear the files at 3:50 PM PDT. The circuits pool granted again at 3:56 PM PDT and the provers pool at
  4:05 PM PDT. Circuits owns the bootstrap-lock fix and is watching both files, since the 7 gpu pods started before the fix
  can still trip the probe on exit.
- At 4:08 PM PDT the circuits pool leases 5 GPUs (0, 2, 3, 4, 6), nothing waits, and `/workspace` is at 51%.
- Nobody saw the blocks for 68 minutes, because the hourly idle-GPU alerts reach only lane notes. Since 4:10 PM PDT the
  steward's alert relay (`tools/alert_pull.sh`) checks node 1 for `/run/gpu-lease*/blocked` every 2 minutes and posts one
  Slack line per file to @infra in the disk thread. The idle-GPU alerts themselves stay off Slack: there have been 28.

## State at 21:35Z (2:35 PM PDT)

**Utilization:**
- From 7:00 AM to 2:33 PM PDT, node 1 was 4.4% GPU-busy: 2.65 of 60.5 GPU-hours, with 47.8 allocated by Kueue and 28.2 holding
  GPU memory. Its CPUs were 31% busy.
- Node 2 was 56% GPU-busy (`art:fd2ad8f125943e7f6d4c8e449cd0447d6d5a4c2da4559595edd0909fb5ee7f3e`).

**At 2:31 PM PDT on node 1:**
- All 8 GPUs are allocated: `deployments-gpu` has 5 (three Commits and one TP2 `config-run-row`), and `provers` has 3
  (`backend-sweep-2` `prover-b`). All 8 read 0% at that instant.
- 29 jobs wait in `deployments-gpu` (StrictFIFO) and 4 in `deployments-cpu`, on memory.

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 2 Coverage | **job shape** | TP2 rows (91 queued) run on `config-run-row` and hold 2 GPUs through their CPU Build. Dispatched Commits replayed on their GPU until node1-fill's 2:15 PM PDT template refresh. | The GPU-less 2-rank Build is the vLLM coordinator's priority 1, in a new lane. Deferred replay is live for trees with PR B. The Commit hang-kill has been live since 2:20 PM PDT (`ac3e0ea51`). |
| 3 Prover | **host witness** | `prover-b` pods hold 93 GB of GPU memory each at about 0% busy. | With the prover lanes (`backend-sweep-2`); nothing for infra. |
| Dispatcher | latent bug | `dispatch.py` `task_resources` raises for any item with a `class` now that `config-run` has three tasks, which would abort every tick. No item sets one yet. | Sent to node1-dispatcher (`note:20260930T2123Z-note-from-nebius-infra-dispatch-class-three-tasks`). |
| Replay memory | waiting on a measurement | The replay task asks for 64 GB, and bundles reach about 90 GB. | Waiting for the TP2 lane's measured peak, sent after the Phi-3 B8 probe. |

## State at 14:05Z

**Utilization:** 05:16–13:59Z, node 1 was 1% GPU-busy (0.72 of 69.9 GPU-h, 42.8 allocated by Kueue) and 18% CPU-busy. Node 2 was
42% GPU-busy (`art:48b2eed3fea5d405b696819edceb123442fb5b0ada870f3753d3cfdac6b3d9e0`).

**At 14:03Z on node 1:** `circuits` has 5 of 5 GPUs allocated, but only one holds memory, at 0%. `provers` has 0 of 3 and nothing
queued. The CPU load is about 106 of 192.

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 2 Coverage | **job shape**, fixed at 13:54Z | Four cells were submitted on the one-GPU `config-run-row` while two-task published no Attempts, and hold their GPUs through the Build. | Two-task publishes since `infra/nebius` `763ea668`; epoch-run and the Build lane were told to switch at 13:56Z (bundle for no-GitHub lanes). |
| 3 Prover | **nothing queued** | M0's a12 was the last `provers` job. `flock-v2-design` finished at 12:49Z, leaving a designed, unmeasured lever (chunked host-slot upload, −6% predicted) and M0's merge call on `cursor/host-unit-eval-c9e2`. | Routed to RC (14:06Z): queue M0's next attempts; otherwise `circuits` can borrow 2 GPUs if coverage keeps cells waiting. |
| 1 Build | CPU benches | Build-optimization Builds are running on the host. | None. |

## State at 06:40Z

**Utilization:** node 1 was 0.4% GPU-busy (of 9.2 GPU-h) and 8.8% CPU-busy from 05:16 to 06:25Z. Node 2 was 1.6% GPU-busy and
6.8% CPU-busy from 06:05 to 06:25Z (evidence: `util_collect.py`, stored hourly).

**Why node 1 is idle, per workstream:**

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 1 Build | **theory/engineering** | One implementing agent. Its plan ranks 4–5 changes worth 8–22 agent-days. Each attempt is CPU-only at 32 vCPU. | Launched `build-v2-kv` (bc-57ddc507): plan change 3, key and value prefixes (the tokens² term). |
| 2 Coverage | **pipeline + merges**, not ideas | The sweep started at 06:10Z with 0 cells. `config-run` holds 1 GPU for a 5–11 h row whose Build is CPU. `circuits` fits only 2 rows at 512 GB each. FA2, MoE and FP8 cells wait on #477/#486/#481/#469/#487. | Route: split the template, memory per class, replay on node 2's CPU (below). |
| 3 Prover | **theory** after tiles | M0 is one agent; tiles, then row 2, and nothing is designed after that. Its direct run ended at 06:13Z and it waits on the cutover. | Launched `flock-v2-design` (bc-37a1971b): the next overhead lever, decode shapes first. |
| 4 Security | agents (Lean) | Doesn't fill the server's GPUs. Lean builds and audits could use spare CPU. | Offer only: `lake build` or audits on node 1 CPUs 0–95. |
| Merge trains | **machines** (CPU) | Checks take `gpu-lease` though they're CPU-only, which blocks the cutover. | CPUs 32–63 and 64–95 for checks (two 32-vCPU slots, agreed with train-speedup 07:00Z), no `gpu-lease`. |

## vy-nebius-1 CPU map (root's decision 07:13Z, updated 2:42 PM PDT; pinned ranges are disjoint)

NUMA nodes are 0–95 and 96–191. Hyperthread siblings are adjacent pairs, so even-aligned ranges share no cores.

| CPUs | For | How |
|---|---|---|
| 0–7 | k3s, the system, unpinned Kueue pods | |
| 8–31 | merge-train check slot `check-c` (RC, 08:09Z) | `check-c.lock`, `8-31` |
| 32–63 | merge-train check slot `check-a` | `flock /workspace/research/locks/check-a.lock taskset -c 32-63 env UV_PYTHON=3.14.7 … check.py`, no `gpu-lease` |
| 64–95 | merge-train check slot `check-b` | the same with `check-b.lock`, `64-95` |
| 8–95, shared | **short lane checks** (a circuit-check rerun, one suite: minutes), which never wait on a train: `check-s1`, `check-s2` on the train slots' CPUs at `nice 10` (10:15Z) | `flock /workspace/research/locks/check-s1.lock nice -n 10 taskset -c 8-95 <cmd>` (or `check-s2`); `check_slot.sh --short <cmd>` once `infra/nebius` has `fb923c3a`; `/workspace/research/check-slots` = `32-63 64-95 8-31` |
| 96–127 | **node 1's dispatcher's Kueue tasks** (Builds, replays, Commits) | `VY_DISPATCH_CPUS=96-127` in `/workspace/jobs/dispatch/dispatch.env` (#745) |
| 128–159 | check slot `d`, being tested (2 Oct 07:42Z); host sessions may use 0–159 since 07:37Z | `user.slice`/`system.slice` `AllowedCPUs=0-159` (was 0-127) |
| 160–191 | **`provers` tasks** (proofs' prover-benches) | `VY_PROVER_CPUS=160-191` in `dispatch.env` (since 05:35Z Oct 2) |

- The dispatcher pins its pods to 96–159. Kueue pods from other submitters aren't pinned and can burst onto any core. Pinned results outside the quiet hour carry `ov.noisy=true`.
- `flock-v2-design` shares M0's range by arrangement with M0, or runs unpinned with `ov.noisy=true`.

## Ready fills

1. **[vLLM coordinator / epoch-run] Split config runs into a CPU job and a GPU job.**
   - Today: one `config-run` job holds a GPU through `row run` (Build, then Commit, then replay), 5–11 h. The Build is CPU work on
     1–4 cores.
   - Fill: `row chain` / `row stage build` as a CPU-only Kueue job (0 GPU, `--build-jobs` for parallel derives, memory per class),
     then `row stage commit` with 1 GPU.
   - Effect: the GPUs are held only for capture and Commit, and 4 GPUs could serve many rows' commits at once. Builds pack the
     144-vCPU `circuits` CPU quota.
   - Owner of the template: Kueue worker (bc-c445c55b).
2. **[vLLM coordinator / epoch-run] Memory per class.**
   - The template's `--memory` overrides (small dense, B ≤ 16: 192 GB) let `circuits` run 6 small rows at once instead of 2.
   - The measured Build peak is 124.5 GB (#11), not 486 (`docs/build-optimization-plan.md`).
3. **[vLLM coordinator] Replay on node 2's CPUs.**
   - POUS offers node 2's 192 vCPU for Verity's CPU-only replay (the gate's 460 random units), at `nice 19`, paused during timed
     windows, through their fill queue `/workspace/pouw/fill/`. The format comes in `lanes/nebius-infra/` within the hour.
   - Use it once the sweep has Commits to replay.
4. **[M0] Provers queue from cutover.**
   - `prover-bench` runs for the `flock-m0-v1` line, and `flock-v2-design`'s prototypes, on GPUs 4–7.
5. **[Build owner] Parallel attempts.**
   - The node-1 CPU map gives Build benches 96–127 (build-v2-kv) and 128–159 (the owner), each pinned at 32 vCPU and labelled `ov.noisy=true` outside the quiet hour.
6. **[research coordinator] More check slots if trains queue.**
   - With two check slots on 32–95 and every pinned range assigned, a third slot would come from 0–31. Ask here.

## Launched theory lanes

| Lane | Agent | Workstream | Why | Feeds |
|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | theory-bound: 1 agent against 8–22 agent-days of ranked changes | Build owner bc-47d0a3ed |
| `flock-v2-design` | bc-37a1971b | 3 Prover | theory-bound after tiles and row 2; decode overhead undesigned | M0 bc-ff572e70 |

Stop rule: no more launches once the queue plus the direct work keep GPUs and CPUs busy. That's re-checked hourly with
`util_collect.py`.
