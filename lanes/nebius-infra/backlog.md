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
