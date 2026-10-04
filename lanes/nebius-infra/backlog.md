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

## State at 02:30Z Oct 4 (7:30 PM PDT Oct 3), steward pass

- **Both servers have all 8 GPUs allocated, and neither has a queue.**
  - Node 1 has 8 provers admitted in Kueue, and all 8 GPUs hold about 90 GB. The pacer has nothing in flight; its only
    waiting Commits are the two batch-64 Gemma-2 rows (`cov-n050-2`, `cov-n051-2`) on circuits' keep list, held by design.
  - Node 2's `vy-cluster-agent` holds 8 POUS jobs and its queue is empty. GPU 6 was briefly empty and was granted at
    02:29:55Z. The `pouw-infra-fill` tmux pane there is a dead leftover; the cluster agent does the filling now.
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
