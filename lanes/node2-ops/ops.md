---
id: node2-ops-ops
campaign: pouw
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), worker of the infra coordinator (bc-17cc41f1)
---

# node2-ops: operations log for vy-nebius-2 (newest first)

Takes over node-2 ops from pous infra (bc-efe47341). Owns ticks only while `/workspace/pouw/infra/ops-owner` on node 2 reads
`bc-c0738ef6-f6bb-5c95-a44f-8e08ff9f35fd`; otherwise standby. Runs until 2026-10-07T14:55Z (node self-stop).
Timers: hourly `5 * * * *`, alerts `2,17,32,47 * * * *`, final backups 2026-10-07T09:00Z and 13:30Z.

## Hourly (node 2; source `/workspace/pouw/infra/utilization-report.json`, its `node2_ops` block)

Target (proposed): GPU busy ≥95%, useful ≥90% of busy. Filler = a fill job whose header carries `filler=`; unlabeled = useful.
CPU busy is for CPUs 0–127 (the check slots 128–191 excluded), over the window between two hourly `/proc/stat` snapshots.

- 20:00–21:00Z: **86.7% busy** (6.92 of 7.98 GPU-h, no timed windows), useful 100% (no filler). Free-idle 0.68, leased-idle 0.38 (bc-dd22acf8 0.23, bc-ccd30e80 0.10); waiters 36 min. Cause: job churn, not an empty queue: 234 one-GPU fill exits in the hour (bc-2aa33ad8's `hsplit` median 1.3 min per lease), each costing a runner poll (`FILL_POLL_S` 10 s) of idle GPU, spread evenly (4–10 GPU-min per 10 min). Ask sent: chunks back to back inside one lease. CPU 0–127: 43.0% (check slots 26.7%). Disk 32%.
- 19:00–20:00Z: **95.1% busy** (7.61 of 8.00 GPU-h, no timed windows), useful 100% (no filler). Leased-idle 0.24, free-idle 0.15; waiters 20.5 min. Meets the target. CPU 0–127: 29.4% (19:16–20:05Z); check slots 17.5%. At 20:05Z the fill queue had 0 GPU jobs behind the 8 running (20 CPU jobs queued).
- 18:00–19:00Z: **78% busy** (6.27 of 8.00 GPU-h: timed 0.60, kernels 5.67), useful 100% (no filler). Leased-idle 1.13, free-idle 0.60; lease waiters 32 min. Cause: leased-idle, 0.72 GPU-h of it bc-e6a46970's `fp8chain-die{0,1,3,4,5}.sh` fill jobs holding GPUs at 0%; free-idle while a timed window waited. Since the 17:58:46Z waiters fix (to 19:05Z): 79.9%. CPU 0–127: 47.7% (19:09–19:16Z, first window).

## Node 2 layout (read 19:09Z)

NUMA 0 = CPUs 0–95 + GPUs 0–3; NUMA 1 = CPUs 96–191 + GPUs 4–7 + NIC mlx5_0. No NVLink (`NODE` within a socket, `SYS` across).
Fill CPUs 96–127 and check slots 128–191 are on NUMA 1; the held Verity CPUs 48–95 on NUMA 0.

## Deployed on node 2 (`/workspace/pouw/infra/bin/`; rollback copies `*.prev-<stamp>` beside them)

| File | sha256 | Commit (`infra/nebius`) | Since |
|---|---|---|---|
| `gpu-lease` | `49238797…` | `8ba5fc589` (agent mode; usage cap kept) | 23:17:43Z |
| `fill_runner.py` | `fe3bdc8b…` | `ad91739ef` on `cursor/n2-commits-first-558b`, by **infra** at 07:45Z, on top of my `5314b8a34` (Commit guests `gpus=2` TP2, up to 120 min; cpu-sets kept; run with `FILL_VERITY_LEND=0`). Infra's backup: `/workspace/verity-guest/backup/20261001T0745Z/`. Don't restore a `.prev-*` without folding in `ad91739ef` (`note:20261001T0753Z-handoff-from-infra-runner-ad91739ef-gpu7-keep-free`). Infra restarted it at 08:42:41Z with `FILL_CPU_SET=48-91 FILL_VERITY_CPU_SET=48-91` | 2026-10-01 07:45Z |
| `fill_runner.py` (now) | `df9b8baa…` | `main` `a0063d9fe` (by **infra**, `research deploy`), which adds `849a768b6`'s self-service fence: `fill_runner.py fence OWNER --gpu I --cpus LIST --until UTC [--jobs GLOB --max-min M] --why TEXT`, read each tick and ending on its own; `--release` removes it. Runner restarted 04:12:36Z with `FILL_VERITY_LEND=0` and adopted the running series job. Rollback `bin/.deploy-prev/fill_runner.py.20261003T041222Z` (= #778, `62bdf53d`) | 2026-10-03 04:12Z |
| `fill_runner.py` (before) | `62bdf53d…` | `0feb33361` on `cursor/fill-max-min-file-558b` ([#778](https://github.com/danielreuter/verity/pull/778), by **infra**, on top of #701), installed by `research deploy` ([#777](https://github.com/danielreuter/verity/pull/777); the node's log is `/workspace/research/deploy/record.jsonl`). Exceptions to the 30-min GPU cap are lines of `fill/max-min` (glob, minutes, until): today `pous-honest-soak-* 540 2026-10-02T14:45Z`. Rollback `bin/.deploy-prev/fill_runner.py.20261002T062750Z` (= #701, `471cf488`), but not before 14:45Z, since it would cap the soak at 30 min. Infra's deploy put every older `bin/*.prev-*` in `/workspace/research/deploy/attic/20261002T0608*Z/`, so the rollback paths in the rows below now live there | 2026-10-02 06:27Z |
| `fill_runner.py` (before) | `471cf488…` | `d24d734c3` on `cursor/fill-yield-slot-d-35fd` ([#701](https://github.com/danielreuter/verity/pull/701), by me, on `main` `d784c58ee`). While a train check holds `/workspace/research/locks/check-d.lock`, cpu-sets jobs on 0–47 don't start, and running ones pause. A check runs in a session cgroup, so nice 19 can't make them yield to it. Rollback `bin/fill_runner.py.prev-20261001T1738Z` (= #676, `a8c88f3b`) | 2026-10-01 17:38Z |
| `fill_runner.py` (before) | `a8c88f3b…` | `7b9c6c7a7` on `cursor/fill-keep-free-waiters-35fd` ([#676](https://github.com/danielreuter/verity/pull/676), by me, on `main`'s #662): a waiter pinned inside `fill/keep-free` (GPU 7's PoUS `--on 7 --wait`) holds back no fill. Rollback `bin/fill_runner.py.prev-20261001T1312Z` (= #662) | 2026-10-01 13:12Z |
| `fill_runner.py` (before) | `9c9c7d2d…` | `f103d0ffc` on `cursor/fill-no-rerun-558b` (#662, by **infra**; supersedes my #660, closed). Each job's exit status goes to `running/.<job>.rc`. A job that recorded none goes to `fill/held-unknown-exit/`, never back to the queue: file it by its log and tell its owner. Old runner in `/workspace/verity-guest/backup/20261001T0930Z/`. Infra's `release_legacy_held.py` (tmux `legacy-held`, until 17:00Z) files the jobs adopted at 09:29:37Z | 2026-10-01 09:29Z |
| `/workspace/pouw/fill/cpu-sets` | (data) | `bc-e6a46970-… 0-47 <slots> [mem_gb]`: compute accounting's verifies on 0–47 (verity-top, 12:00 AM PDT); delete the line to put them back on 96–127 | 2026-10-01 07:12Z |
| `/workspace/pouw/fill/windows` | (data) | booked timed windows, start UTC + minutes; edit when a booking moves | 2026-10-01 07:02Z |
| `node_ops.py` | `7b8ebe56…` | `6d877a03` (OOM guard prefers `fill-verity-*`) | 20:08Z |
| `/etc/systemd/system/vy-cluster-agent.service` | (unit) | main's `1253f09ec` (`/workspace/research/src/1253f09ec…`), by me with infra's yes (`note:20261002T1515Z-reply-from-infra-drill-and-repin-one-restart-yes`); was `91af9a6bf`, whose unit is in `/workspace/research/deploy/attic/`. Any other pin or restart is @infra's call | 2026-10-02 16:04:17Z |
| `backup.sh` | `e820a1f9…` | `283af0ae7` (retry/skip a changing unit; packs nothing while a window runs or waits) | 00:08Z |
| `publish_pool.py` + `~/.config/systemd/user/infra-pool-publish.{service,timer}` | `01d22db9…` | `8bbc7be21` (infra-pool/v1 to vy-n1 every 5 min; monitors; per-kind table; node 1 merge; delivered_by_hour) | 02:10Z |

Daniel's one-pool rulings (19:12Z, `note:20260930T1915Z-rulings-from-daniel-one-pool`, relayed by infra) approved the guest path and the cutover; nothing is held now.

## Open items

- **Timers:** from 16:14Z `subscribe_timer` returns `invalid_argument` for every new timer. Only the recurring ticks remain (alerts at :02/:17/:32/:47, hourly at :05), plus the two final-backup one-shots on 7 Oct.
- **Pearl-C4's verify re-run** (bc-e8ffd7f2): 48–91 now that window 4's verify is done, or 0–47 at nice 19 with compute accounting's yes (`note:20261001T1650Z-reply-from-node2-ops-pearl-c4-verify-rerun-cores`). No request yet.
- **Inbox on every alerts tick** (from 13:05Z): `~/node2-ops/inbox.sh` lists the notes added on origin since the acked commit that are in `lanes/node2-ops/` or name node2-ops, and `inbox.sh --ack` advances it. I missed pouw-node2's 12:41Z ask for 25 min because the alerts tick read only `alerts.jsonl`.
- **Overnight allowed set adds `pn2h-*`** (owner proofs-n2-hill bc-f0eeea0e, proofs' yes; `note:20261001T0735Z-handoff-from-proofs-n2-hill-pn2h-yes`, `note:20261001T0802Z-ask-from-proofs-allow-pn2h-in-overnight-gate`), until 17:00Z: GPU points through `vy-provers` on 128–191, each names its question, none placed from 20 min before a window. Never sweep them.
- **Overnight allowed set adds memory accounting's `pous-dsweep-*` and `pous-climb-*`** (bc-15ada664), until 17:00Z: top-level 07:41Z, infra says the d-sweep can go through the fill queue (`note:20261001T0752Z-handoff-from-infra-gpu7-and-quiet-cores-live`). GPU 7 is theirs directly (`fill/keep-free`).
- **Where node-2 items go (compute accounting, 09:17Z; bc-2aa33ad8 has stopped):** PoUW's are filed in `lanes/accounting` for their owners: bc-c066b30c (`pouw-node2`: timed windows, fill, GPU 0's verifies), bc-e8ffd7f2 (`pouw-fp4`: FP4 jobs), bc-c62f9726 (`pouw-served`: served jobs). PoUS's go to memory accounting, bc-15ada664 (`lanes/memory-accounting`).
- **Verifies on 0–47 (`fill/cpu-sets`):** 0 slots since 08:58Z, because 0–47 is train-check slot d (top-level 1:52 AM PDT); queued verifies wait, cap 40 GB. Deleting the line puts them back on the runner's `FILL_CPU_SET`. CPU map (read 12:25Z): user.slice and system.slice are back on 0–123 since 09:24:26Z (the drop-ins' mtime; proofs' hill pane shows Terminated). The runner infra restarted at 09:29:36Z carries no `FILL_*CPU*` env, so its defaults hold: Verity CPU jobs 48–95, other CPU fill 96–127 (96–123 in effect, under user.slice). PoUS's quiet cores 124–127 (`vy-pous-quiet`, `pous-quiet.slice`) until 17:00Z. If compute accounting's READY line asks for all 192 CPUs, lift both at the window's drain (`sudo systemctl set-property --runtime user.slice AllowedCPUs=`, same for system.slice), and put back `AllowedCPUs=0-123` afterwards. `held-proofs-pn2g/` is empty; proofs' new GPU jobs go through `vy-provers`.
- **Windows ahead (`fill/windows`):** 18:50Z the quota cutover (15 min). The lines up to 17:25Z (served window 4) are past. Each window: confirm fill is off every GPU once its `gpu-lease --timed` waits (status `window waiting True`, then `timed True`), and that no `scope-residue` was needed.
- **Overnight gate ended 15:00Z; readout sent** (`note:20261001T1510Z-report-from-node2-ops-morning-readout`). bc-8412d697's four `aw-*` CPU jobs stay in `held-overnight/` until their owner or memory accounting asks. History of the rule: each alerts tick swept `fill/queue/` for jobs **newly queued after 9 PM** outside the allowed set (see the 03:50Z log line, plus `verity-commit-*` again from 07:02Z) into `held-overnight/`; jobs running at 9 PM keep their chunks (99 → requeue → restart). A lane's yes moves its jobs back. At 8 AM PDT, give the morning readout inputs (per-hour useful, filler and held-idle GPU %, CPU %, who ran dry, rollbacks).
- **9 PM PDT (04:00Z) overnight gate:** each queued job's lane needs an explicit yes (compute-accounting for PoUW, circuits for Commits), and its header must name a research question. Hold the rest in `fill/held-overnight/`, and report the gap and its owner hourly. Run nothing of PoUS's or network accounting's. The glide path's live-node cutoff is 9 PM PDT.
- **The switch, 5–6:30 PM PDT:** it waits on cluster-build (shadow bar, #586's check green); I deploy gpu-lease `49238797` and fill_runner's agent.lock change together.
- **`855339e74` (the pool lends idle slots):** deploy only after PoUW answers on NUMA 0, together with the switch's fill_runner.
- Job norms, owned by me: the daily top-3 wasters (16:00Z); merge node 1's file into the pool file by T4; announce the kind spec when cluster-build's registry lands; a kind that is on the list two days running becomes a proposed admission check.
- Nebius key rotation: Daniel ruled 18:42Z "not now, rotate later". Open, not urgent; no action from node2-ops until he says so.
- Standing GPU backlog and CPU fill: asked bc-2aa33ad8 via the pouw coordinator (`note:20260930T1925Z-handoff-from-node2-ops-hour-and-backlog`).
- 21 large units are left out of the hourly backup (`large.txt`); check each hour which ones stopped changing and have no `backup_unit.sh` run (never `gpu3-fp8/out`).

## Log

- 2026-10-03 07:12Z hourly (06Z): GPU busy 50.3% (4.03 of 8.00 GPU-h, all useful): 3.98 of it timed, circuits' Qwen3-235B-A22B TP8 window on all 8 GPUs from 06:30Z.
    - **Why below 80%:** fill drained for the window. 3.96 GPU-h sat free from about 06:00Z to 06:30Z (waiting 32 min). CPU 46.1% (65.4% by `/proc/stat`): the window's host side, plus the weight download and the `check` before it.
    - **Backup:** none, the window is on (`timed True`). They resume after 11:30Z. The 06Z backup `r20261003-060931-29eb` is the last.
    - **Disk:** `/` is now 15% used (213 GB free). Both `lean-audit-scratch-*` dirs are gone, the leftover `azkehmu9` too, with no note about it yet. `/workspace` is 58%.
    - **Checks:** daemons are up, and `status.md` was fresh (07:09Z). One runner (`df9b8baa`), no new deploys. The agent is on `1253f09ec` (no restarts). `gh` works again: #494 is still closed.
- 2026-10-03 06:33Z alerts tick: `disk` `/workspace` 60% full (1,989 GiB free, 06:26Z), up from 54% at 06:17Z. That's circuits' Qwen3-235B-A22B weights (118 shards, about 470 GB) landing in `/workspace/jobs/hf` for the window, so it should level off near 63%. Nothing to do. The window is on (`timed True`, 0/8 free, 2 GPU jobs queued). Watermark 06:26:30Z.
- 2026-10-03 06:25Z alerts tick: `disk` `/` 63% full (92 GiB free, 06:07Z), the first root alert.
    - **What's on root:** 120 GB is `~/.cache/verity-check/lean-audit-scratch-*`. The live check (`r20261003-055703-86e3`) has 61 GB. 59 GB (`azkehmu9`) is left from `r20261003-030801-94eb`, a `check` stopped by SIGTERM (rc 143) at 03:10:58Z, whose `finally` never ran. The Qwen3-235B download writes to `/workspace` (2.3 TB free), not root.
    - **Not deleted:** that scratch holds the warm Lake dependencies `WarmDeps` moved into it. Handed to infra (`note:20261003T0625Z-alert-from-node2-ops-killed-check-left-59g-on-root`); I'll delete it or move the dependencies back on their word. Watermark 06:07:09Z.
- 2026-10-03 06:12Z hourly (05Z): GPU busy 13.1% (1.05 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series, plus short leases by bc-4323a347 and `adhoc:network-accounting`.
    - **Why below 80%:** nothing else was queued, so 6.64 GPU-h sat free. Leased-idle 0.31 GPU-h: the series 0.12, bc-4323a347 0.10, network accounting 0.10. Waiters 12.2 min.
    - **CPU:** 19.6% by `/proc/stat` (57.9% so far in 06Z): a `check` run (`r20261003-055703-86e3`, its Lean audit), the Qwen3-235B weight download (`curl`, tmux `qwen3-235b-download`, for the 06:30Z window) and a Pearl-C `verify_run.py`.
    - **Backup:** `r20261003-060931-29eb`, unpinned, before the 06:30Z window. The 05Z backup `r20261003-050912-43ea` is preserved. Backups wait for `timed False` until the windows end (11:30Z).
    - **Checks:** daemons are up, and `status.md` was fresh (06:08Z). One runner (`df9b8baa`). The agent is on `1253f09ec` (no restarts). `gh` returns 401 (its token is invalid), so #494 is unchecked this hour; it was closed at 05:09Z.
- 2026-10-03 06:10Z alerts tick: one `gpu-idle-in-lease` (05:55Z), GPU 2 at 0.5%, an `adhoc:network-accounting` lease since 05:49:32Z. It ended by itself (all 8 GPUs free at 06:02Z). Watermark 05:55:06Z.
    - **Second fill runner (infra's, `note:20261003T0610Z-alert-from-node2-ops-second-fill-runner-orphaned-a-job`):** a second `fill_runner.py` ran beside the tmux one (pid 1580276, up since 04:12:36Z). It adopted the series job `…052345Z` at 05:37:11Z. When that job ended, both runners filed it: `done` at 05:41:37Z, and again as `unknown-exit` at 05:41:41Z (minutes 4.5, measured from its adoption). It then started `…054127Z` at 05:41:51Z and exited before reaping it, so the job sat in `running/` with its wrapper's rc 0 (05:59Z), unknown to the live runner. Its renewed successor `…055948Z` then exited 75 ("another series job is running"). I couldn't see who started the second runner (no login record, nothing in the quota log, no `fences` file). Any `fill_runner.py` argv but `fence` (e.g. `--help`) runs a full second runner.
    - **Mine:** at 06:07:41Z I filed `…054127Z` to `done/` (rc 0, 17.9 min) after checking its process group was gone. I removed its `.pgid`/`.unit`/`.rc` and wrote a `done` event, with `why` naming me, through the runner's own `event()`. `running/` is empty. The successor waits in `queue/`, because its `max_min=30` doesn't clear the booked windows.
    - **Windows booked (infra, 05:58Z and 06:00Z):** 06:30–10:30Z circuits' Qwen3-235B-A22B TP8 on all 8 GPUs (Daniel), then 10:30–11:30Z compute accounting's timed FP8 served pass. Fill drains ahead of them. The hourly backups wait for `timed False`.
- 2026-10-03 05:10Z hourly (04Z): GPU busy 11.1% (0.89 of 8.00 GPU-h, all useful): only memory accounting's vLLM e2e series.
    - **Why below 80%:** nothing else was queued, so 7.00 GPU-h sat free. Leased-idle 0.11 GPU-h, the series' start-ups. CPU 1.0%.
    - **Deploys (infra, from `main` `a0063d9fe`):** `fill_runner.py` at 04:12:22Z (`df9b8baa`, matches `main`; adds the self-service `fill_runner.py fence`, see the table), and `/usr/local/sbin/vy-setup` at 04:16:08Z. The runner restarted at 04:12:36Z with `FILL_VERITY_LEND=0`, adopted the series job (rc 0), and `fill.err` is empty.
    - **Backup:** `r20261003-050912-43ea`, unpinned. The 04Z backup `r20261003-040636-3b78` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (05:06Z). The agent is on `1253f09ec` (no restarts). No windows. #494 is still closed.
- 2026-10-03 04:08Z hourly (03Z): GPU busy 10.6% (0.85 of 8.00 GPU-h, all useful): only memory accounting's vLLM e2e series (four runs, each rc 0 in 17.9 min).
    - **Why below 80%:** nothing else was queued, so 7.00 GPU-h sat free. Leased-idle 0.15 GPU-h, all the series' start-ups. CPU 6.1% (9.0% by `/proc/stat`), none of it fill jobs.
    - **Backup:** `r20261003-040636-3b78`, unpinned. The 03Z backup `r20261003-030606-43f0` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (04:05Z). The runner is still `62bdf53d`, no deploys since 01:56Z. The agent is on `1253f09ec` (no restarts). No windows. No new notes in the lanes I skim. #494 is still closed.
- 2026-10-03 03:08Z hourly (02Z): GPU busy 11.1% (0.89 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series, plus `cov-gm363-l`'s Commit (rc 0 at 02:10:43Z, 27.4 min in its 90-min lease) and replay (rc 0).
    - **Why below 80%:** nothing else was queued, so 6.64 GPU-h sat free. Leased-idle 0.47 GPU-h: 0.36 the Commits', 0.11 the series'. CPU 2.7%.
    - **Backup:** `r20261003-030606-43f0`, unpinned. The 02Z backup `r20261003-020625-2b1a` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (03:04Z). The runner is still `62bdf53d`, no deploys since infra's `n2_commit.sh` at 01:56Z. The agent is on `1253f09ec` (no restarts). No windows. #494 is still closed.
- 2026-10-03 02:08Z hourly (01Z): GPU busy 15.4% (1.23 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series, plus TP2 Commits and their replays.
    - **Why below 80%:** nothing else was queued, so 4.29 GPU-h sat free. Leased-idle 2.48 GPU-h: 2.36 the Commits' TP2 leases (most of it `cov-gm363-l`'s host staging, see the 02:04Z line), the rest the series'. CPU 4.0%.
    - **Backup:** `r20261003-020625-2b1a`, unpinned. The 01Z backup `r20261003-010629-0cde` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (02:05Z). The runner is still `62bdf53d`. New deploy: `n2_commit.sh` at 01:56:09Z by infra (`0bb87726`, `cursor/n2-long-row-max-min-558b`), the long-row `max_min` that gave `gm363-l` its 90-min lease. The agent is on `1253f09ec` (no restarts). No windows. The new GPU-at-0% alert (01:48Z) is node 1's. #494 is still closed.
- 2026-10-03 02:04Z alerts tick: two `gpu-idle-in-lease` (01:50Z), GPUs 5–6 at 6.8–6.9%, the second attempt of bc-698052e1's TP2 Commit `cov-gm363-l` (phi4 B8 I1024 O128), 7 min into its lease.
    - **What it's doing:** both attempts look the same. After `commit staging: window_mb=256 slots=8 retain=host bounded` (minute 1), the scope's memory climbs to 284 GiB by minute 16 (213 GiB of it shmem). The scope's cap is now 386 GiB, so this isn't the 193 GiB OOM. Then nothing more on stdout, while the two TP workers each run one core and the GPUs sit near 10%.
    - **Why it isn't a loop:** the first attempt's lease was 25 min, and it was stopped (`max_min`) at 01:43:20Z. The second has `max_min=90` (lease `--max-min 90`), so its owner's long-row cap now covers it. Nothing to do; I'll check at the hourly that it ended. Watermark 01:50:01Z.
- 2026-10-03 01:33Z alerts tick: six `gpu-idle-in-lease` (01:25Z and 01:30Z) at 1.1–4.2%, three bc-698052e1 TP2 Commits 7–8 min into their leases: `cov-gm363-l` on GPUs 5–6 (since 01:18:19Z), `cov-lw07-gm358` on 2–3 (01:21:19Z) and `cov-lw07-gm357` on 0–1 (01:22:19Z). Same start-up pattern as before, which the hourly counts as leased-idle. Nothing to do; watermark 01:30:06Z.
- 2026-10-03 01:09Z hourly (00Z): GPU busy 12.3% (0.98 of 7.98 GPU-h, all useful): memory accounting's vLLM e2e series, plus TP2 Commits.
    - **Why below 80%:** nothing else was queued, so 5.02 GPU-h sat free. Leased-idle 1.98 GPU-h: 1.83 the Commits' TP2 leases (infra's known waster), 0.15 the series'. CPU 4.3%.
    - **Backup:** `r20261003-010629-0cde`, unpinned. The 00Z backup `r20261003-000608-767a` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (01:04Z). The runner is still `62bdf53d` (`FILL_VERITY_LEND=0`), no deploys since the 21:21Z cpuset drop-in. The agent is on `1253f09ec` (no restarts). No windows. The new GPU-at-0% alert (00:19Z) is node 1's. #494 is still closed.
- 2026-10-03 00:33Z alerts tick: two `gpu-idle-in-lease` (00:25Z), GPUs 5–6 at 6.2–6.9%, a bc-698052e1 TP2 Commit 7 min into its lease (since 00:18:32Z). It's the start-up pattern, which the hourly counts as leased-idle. Watermark 00:25:06Z.
- 2026-10-03 00:18Z alerts tick: two `gpu-idle-in-lease` (00:10Z), `cov-gm367`'s GPUs 5–6 at 0.0%, 10 min in. It resolved itself: the Commit ended rc 0 at 00:14:21Z (14.0 min), and its replay rc 0 at 00:14:51Z. Watermark 00:10:06Z.
- 2026-10-03 00:09Z hourly (23Z): GPU busy 13.0% (1.04 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series, plus TP2 Commits.
    - **Why below 80%:** nothing else was queued, so 6.18 GPU-h sat free. Leased-idle 0.79 GPU-h: 0.68 the Commits' TP2 start-ups, 0.11 the series'.
    - **Backup:** `r20261003-000608-767a`, unpinned. The 23Z backup `r20261002-230625-111e` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (00:05Z). The runner is still `62bdf53d`. The agent is on `1253f09ec` (no restarts). No windows. The new GPU-at-0% alert is node 1's. #494 is still closed.
- 2026-10-03 00:03Z alerts tick: four `gpu-idle-in-lease` (23:55Z and 00:00Z) at 1.7–9.7%, all TP2 Commits of bc-698052e1 in their first 7 min (leases from 23:48Z on GPUs 5–6 and 23:53Z on 2–3). Running now: `gm359` (since 23:53:29Z) and `gm367` (since 00:00:19Z). Same start-up pattern as `gm360` and `gm372-r2`, both rc 0. Nothing to do; watermark 00:00:06Z.
- 2026-10-02 23:09Z hourly (22Z): GPU busy 12.0% (0.96 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series, plus the TP2 Commits `gm360` and `gm372-r2`.
    - **Why below 80%:** nothing else was queued, so 6.53 GPU-h sat free. Leased-idle 0.51 GPU-h: 0.39 the Commits, 0.12 the series' start-ups.
    - **New deploy (infra, 21:21:23Z):** `/etc/systemd/system/user@.service.d/vy-cpuset.conf` from `6ab5f059` (`cursor/cluster-cpuset-pin-558b`). It sets `Delegate=cpu cpuset memory pids`, so a cluster-agent scope's `AllowedCPUs=` takes hold. `user@1001` still has 0–123. No effect on fill or backups.
    - **Backup:** `r20261002-230625-111e`, unpinned. The 22Z backup `r20261002-220628-013d` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (23:05Z). The runner is still `62bdf53d` (no fence PR yet). The agent is on `1253f09ec` (no restarts). No windows. The new GPU-at-0% alert is node 1's. #494 is still closed.
- 2026-10-02 23:03Z alerts tick: two `gpu-idle-in-lease` (22:55Z), GPUs 5 and 6 at 4.1–4.5%. Both are one TP2 Commit, `cov-gm372-r2` (bc-698052e1), 10 min in since 22:45:51Z. Same early-lease pattern as `gm360`, which finished rc 0. Nothing to do; watermark 22:55:06Z.
- 2026-10-02 22:08Z hourly (21Z): GPU busy 11.7% (0.94 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series, plus Commit `cov-gm360`.
    - **Why below 80%:** nothing else was queued, so 6.2 GPU-h sat free. Leased-idle 0.87 GPU-h: 0.73 of it is `gm360`'s TP2 lease waiting on shared memory before it finished rc 0, and 0.13 is the series' start-ups.
    - **Backup:** `r20261002-220628-013d`, unpinned. The 21Z backup `r20261002-210626-5502` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (22:04Z). The runner is still `62bdf53d` (#778; infra's fence PR isn't deployed). The agent is on `1253f09ec` (no restarts). No windows. The new GPU-at-0% alert is node 1's. #494 is still closed.
- 2026-10-02 21:48Z alerts tick: one `gpu-idle-in-lease` (21:35Z), `cov-gm360`'s other GPU (6) at 0.2%. It resolved itself: the Commit ended rc 0 at 21:44:44Z (24.5 min), and its replay ended rc 0 at 21:46:04Z. So the shared-memory waits were slow work, not a hang. Watermark 21:35:06Z.
- 2026-10-02 21:33Z alerts tick: one `gpu-idle-in-lease` (21:30Z), GPU 5 at 6.9%. It's bc-698052e1's TP2 Commit `cov-gm360` (`gpus=2`, since 21:20:12Z).
    - Not the stale-plan rebuild. Its `commit.log` repeats vLLM's "No available shared memory broadcast block found in 60 seconds" from 21:30Z, so one TP rank is busy or stuck.
    - `n2_commit.sh` sends it to node 1 after two stops. I'll watch for repeat alerts. Watermark 21:30:06Z.
- 2026-10-02 21:08Z hourly (20Z): GPU busy 11.0% (0.88 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series.
    - **Why below 80%:** nothing else was queued anywhere (infra's backlog: all 16 GPUs idle), so 7.0 GPU-h sat free. Leased-idle was 0.12 GPU-h (the series' start-ups).
    - **Coming from infra:** a PR by 23:00Z adding `fill_runner.py fence`, one line in node 2's fill dir per timed window (from memory accounting's interview, round 12). When it's deployed, I'll check the runner's sha and env.
    - **Backup:** `r20261002-210626-5502`, unpinned. The 20Z backup `r20261002-200646-96f1` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (21:04Z). The agent is on `1253f09ec` (no restarts). No windows. The new GPU-at-0% alert is node 1's. #494 is still closed.
- 2026-10-02 20:09Z hourly (19Z): GPU busy 11.5% (0.92 of 8.00 GPU-h, all useful): memory accounting's soak rerun until 19:49Z, then their vLLM e2e series.
    - **Why below 80%:** nothing else was queued, so 7.0 GPU-h sat free. Leased-idle was 0.08 GPU-h (the series' start-up).
    - **Infra released the rerun's fence at 20:00Z** (`soak-rerun/FENCE.released-20261002T2000Z`, `fill/keep-free` gone). They respawned the fill loop at 20:00:52Z with `FILL_VERITY_LEND=0` only. The series was restarted then.
    - **Backup:** `r20261002-200646-96f1`, unpinned again. The 19Z backup `r20261002-190654-2736` is preserved. PoUW's `served_debit` run has ended.
    - **Checks:** daemons are up, and `status.md` was fresh (20:04Z). The agent is on `1253f09ec` (no restarts). No windows. #494 is still closed.
- 2026-10-02 20:03Z alerts tick: one `gpu-idle-in-lease` (19:55Z), GPU 7 at 3.5%, 6 min into memory accounting's lease. Their soak rerun ended rc 0 at 19:49:34Z (163.7 min), and they restarted their own vLLM e2e series at 19:49:32Z (`…194932Z`). The alert is its vLLM start-up. Nothing to do; watermark 19:55:06Z.
- 2026-10-02 19:09Z hourly (18Z): GPU busy 12.5% (1.00 of 8.00 GPU-h, all useful): memory accounting's soak rerun on GPU 7.
    - **Why below 80%:** nothing else was queued for a GPU, so 7.0 GPU-h sat free.
    - **CPU 0–127 at 37.2%:** PoUW's Pearl-C `served_debit.py`, 47 processes at nice 19 from 18:17Z, in the agent-placed scope `cluster-r20261002-173355-4eef`. 46 are on 48–95; the launcher is on 0–91. Clear of the rerun's 116–123 fence.
    - **Backup:** `r20261002-190654-2736`, on 48–79,94–95 at nice 19 (sharing those cores with served_debit). The 18Z backup `r20261002-180625-bbd8` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (19:05Z). The agent is on `1253f09ec` (no restarts). No windows. The new infra alerts are node 1's. #494 is still closed.
- 2026-10-02 18:08Z hourly (17Z): GPU busy 12.4% (0.99 of 8.00 GPU-h, all useful): memory accounting's soak rerun on GPU 7.
    - **Why below 80%:** nothing else was queued, so 7.0 GPU-h sat free. CPU 0–127 was at 26.7%: the rerun's server on 116–123, plus PoUW's `served_debit.py` (outside fill, on 85 and 91–93 since 17:34Z).
    - **The rerun:** it exited "more" (rc 99) after 10.7 min at 17:05:54Z and restarted. Fill cleared one `scope-residue` (`gpu-lease-3090890`).
    - **Backup:** `r20261002-180625-bbd8`, on 48–79,94–95 at nice 19 while the fence holds (until 21:00Z). The 17Z backup `r20261002-170639-49df` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (18:04Z). The agent is on `1253f09ec` (no restarts). No windows are booked. #494 is still closed.
- 2026-10-02 17:08Z hourly (16Z): GPU busy 3.6% (0.29 of 8.00 GPU-h, all useful).
    - **Why below 80%:** nothing else was queued, so 7.59 GPU-h sat free. Leased-idle was 0.11 GPU-h.
    - **Memory accounting's series is stopped by them, not me.** Someone touched `vllm-e2e-series.STOP` at 16:09:48Z, 5 min after I removed it. The copy I queued ran clean (rc 0, 892/900, 16:22:59Z) and didn't renew.
    - **GPU 7:** infra handed it to their pinned honest-latency rerun (`pous-soak-rerun-d3d8f4c3`, since 16:55Z). That rerun's fence is cores 116–123 until 21:00Z, and `fill/keep-free` is empty again.
    - **Backup:** `r20261002-170639-49df`, on 48–79,94–95 at nice 19 while the fence holds. The 16Z backup `r20261002-161253-4f31` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (17:04Z). The agent is on `1253f09ec` (no restarts). The new infra notes are node 1's. #494 is still closed.
- 2026-10-02 16:14Z hourly (15Z): GPU busy 6.8% (0.55 of 8.00 GPU-h, all useful).
    - **Why below 80%:** nothing else was queued, and I drained node 2 from 15:36Z for the agent restart. Free 6.56 GPU-h. Leased-idle 0.90 GPU-h, 0.81 of it Commit `gm176`'s two 0% leases.
    - **New from infra at 16:07:57Z:** `fill/keep-free` holds GPU 7 for memory accounting's honest-latency run until 19:20Z (Slack `1790957051.914609`). The fill loop was respawned with `FILL_VERITY_LEND=0 FILL_CPU_SET=96-115`, so other CPU fill is off 116–127.
    - **Backup:** `r20261002-161253-4f31`, on 48–79,94–95 at nice 19 while that run lasts. The 15Z backup `r20261002-150534-69d1` is preserved.
    - **Checks:** daemons are up, and `status.md` was fresh (16:09Z). The agent is on `1253f09ec`. #494 is still closed.
- 2026-10-02 16:15Z alerts (the 15:47Z and 16:02Z ticks): my watermark had stuck at 00:40:06Z, so I went through all 39 alerts since then.
    - 21 `gpu-idle-in-lease` are bc-698052e1's Commits (the known waster in the hourlies).
    - The `fill-failed` alerts are hourly repeats of four failures:
        - `pous-lf-d0-*-edff820f` (04:13Z): memory accounting fixed it, and it ran clean by 04:34Z;
        - the `cov-gm324` replay (04:36Z): the Commits lane's own;
        - `zkk32k-stage-bf16-k32768` (07:40Z): proofs re-queued it as `-b`.
    - The 4 `oom-kill`s are Commits `gm345` and `gm343-to4` at the lease's 193 GiB `MemoryMax`, 185 GiB of it shmem. Fill filed them as `preempted` (137 mapped to 143), and both went to node 1. `/dev/shm` is clean.
    - Added the OOMs to `note:20261002T1607Z-alert-from-node2-ops-gm176-plan-recompute-outlasts-lease`. Watermark advanced to 15:45:06Z.
- 2026-10-02 16:06Z: the drill and the re-pin are done, in one restart, 16:02:40–16:04:17Z (`note:20261002T1606Z-reply-from-node2-ops-agent-healthy-on-main`).
    - Node 2 was empty from 16:01:57Z. gm176 went back to node 1 after its second 25-min stop, both spent at 0% GPU recomputing its plan.
    - Drill: the agent exited 0 with no restart, `agent.lock` was free, and the drill job got GPU 7 from gpu-lease and ended rc 0, with no 75.
    - Pin: active on `1253f09ec`, pid 2749731. The new segment `20261002T160417Z` opens at seq 1935 with `prev` = the old head. `ledger verify`: 1935 records, intact.
    - At 16:05:00Z I removed the series' STOP and queued one identical copy; it started at 16:05:09Z, the first grant through the new agent.
- 2026-10-02 15:36Z drill prep: check `9160` was cancelled at 15:2xZ to free node 2 for this restart (old-circuits-and-proofs, `CANCELLED_MANUAL`), so it counts as done.
    - Memory accounting's vLLM e2e series renews itself 6 s after each chunk ends, so `fill/running/` would never empty on its own. At 15:35:58Z I touched its own documented stop switch, `fill-out/pous/vllm-e2e-series.STOP`. The running chunk `…151908Z` ends normally and doesn't renew.
    - After the restart I'll `rm` STOP and queue one copy of the same script, as its renewal does. Told them (`note:20261002T1536Z-notice-from-node2-ops-vllm-series-paused-for-drill`).
    - Commit gm176 ends by 15:36:23Z at the latest (`max_min=25`).
- 2026-10-02 15:22Z alerts tick: infra said yes to the drill and re-pin in one restart, both done by me, once check `9160` is done and node 2 is empty (`note:20261002T1515Z-reply-from-infra-drill-and-repin-one-restart-yes`).
    - At 15:18Z `9160` was running, fill had 2 jobs (the PoUS e2e series and Commit gm176), and one vLLM process held a GPU. So I only prepared: shipped main `1253f09ec`, diffed the unit, ran `validate` and `ledger verify`. The runbook is in Open items.
    - The GitHub 401 from 15:05Z has cleared (`git fetch` and `gh` work again).
- 2026-10-02 15:09Z hourly (14Z): GPU busy 10.3% (0.83 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7 until 14:45Z; their vLLM e2e series follows from 15:01Z. Leased-idle 0.17 GPU-h (bc-15ada664).
    - **Why below 80%:** nothing else was queued, so 7.0 GPU-h sat free. CPU 0–127 at 6.4%.
    - **Disk** at 39%.
    - **The soak window closed as planned.** `vy-fill-cpu-revert` respawned the loop at 14:44:59Z (runner pid 1966482) with `FILL_VERITY_LEND=0` only, so the Verity CPU pool is back on 48–95. The runner is still #778 (`62bdf53d`). The `fill/max-min` soak line has expired by its own end time.
    - **Backup:** `r20261002-150534-69d1`, unpinned again, packed (542 units, 21.2 GB, 40 large units left out); its custody upload is pending. The 14Z backup `r20261002-140533-e474` is preserved.
    - **This VM's GitHub credential for `danielreuter/verity` is rejected** since about 15:05Z: `gh` returns HTTP 401, and `git ls-remote origin` fails with "Authentication failed". The notes repo (its own token), ssh to node 2 and `research run` still work. It blocks only #494's check and pushes to my PR branches (#701). I'll retry at 16:05Z.
    - **Checks:** daemons and `status.md` (15:04Z) are fine. The 14:12Z alert is node 1's. #494 couldn't be checked (closed at 14:05Z).
- 2026-10-02 15:05Z alerts tick: cluster-build's watch of `vy-cluster-agent` has ended (`note:20261002T1500Z-handoff-from-cluster-build-agent-watch-ended`): `91af9a6bf`, 20 h clean, 73 grants today at 0 s lag. The open items are my rollback drill and infra's re-pin. I proposed doing them in one restart at infra's time (`note:20261002T1505Z-reply-from-node2-ops-drill-and-repin-one-restart`), without the obsolete fill_runner roll back and forward. I won't stop the agent before infra names a time.
- 2026-10-02 14:09Z hourly (13Z): GPU busy 16.6% (1.33 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7, plus bc-698052e1's `-r2` Commits until about 13:30Z. Leased-idle 0.72 GPU-h (bc-698052e1 0.56, bc-15ada664 0.16).
    - **Why below 80%:** nothing else was queued, so 5.95 GPU-h sat free. CPU 0–127 at 7.9%.
    - **Disk** at 38%.
    - **Backup:** `r20261002-140533-e474` packed on 48–79,94–95 at nice 19 (542 units, 20.6 GB, 40 large units left out); its custody upload is pending. The 13Z backup `r20261002-130534-4541` is preserved.
    - **Checks:** daemons and `status.md` (14:05Z) are fine. The runner is still #778 with `FILL_VERITY_CPU_SET=48-79,94-95`; the soak's revert is due at 14:45Z. The new alerts (13:30Z disk-guard release, 13:42Z, gpu-idle) are node 1's. #494 is still closed.
- 2026-10-02 13:09Z hourly (12Z): GPU busy 18.7% (1.50 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7, plus bc-698052e1's `-r2` Commits (gm148, gm228, gm227 from 12:43Z). Leased-idle 1.26 GPU-h (bc-698052e1 1.17, bc-15ada664 0.08).
    - **Why below 80%:** nothing else was queued, so 5.25 GPU-h sat free. The Commits held their GPUs mostly idle again (1.17 GPU-h). CPU 0–127 at 9.9%: proofs' `zkk32k-stage-bf16-k32768-gate`.
    - **Disk** at 38%.
    - **Backup:** `r20261002-130534-4541` packed on 48–79,94–95 at nice 19 (542 units, 20.5 GB, 40 large units left out); its custody upload is pending. The 12Z backup `r20261002-120529-6ffb` is preserved.
    - **Checks:** daemons and `status.md` (13:04Z) are fine. The runner is still #778 with `FILL_VERITY_CPU_SET=48-79,94-95`. Nebius-infra's #819 deploy is node 1's `dispatch.py`. The 12:31Z disk-guard alert is node 1's (80%). #494 is still closed.
    - **Next:** at 14:45Z infra's `vy-fill-cpu-revert` respawns the fill loop without `FILL_VERITY_CPU_SET`, and the `fill/max-min` soak line expires. At the 15:05Z hourly, confirm the pane is back to `FILL_VERITY_LEND=0` only and launch the backup unpinned again.
- 2026-10-02 12:09Z hourly (11Z): GPU busy 11.3% (0.90 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7, plus bc-698052e1's Commits gm138-r2 (19.5 min, then its replay, 11 min on CPU) and gm343-to4. Leased-idle 0.82 GPU-h (bc-698052e1 0.66, bc-15ada664 0.16).
    - **Why below 80%:** nothing else was queued, so 6.28 GPU-h sat free. Most of the leased-idle time was gm343-to4. Twice it held GPU 5 for 13.4 min at 8–10% busy and ended with SIGTERM (rc 143, which fill files as "preempted"). On the third start its `n2_commit.sh` sent it to node 1 ("stopped 2 times on node 2"), so the owner's script handled it. CPU 0–127 at 19.5%.
    - **Disk** at 38%.
    - **Backup:** `r20261002-120529-6ffb` packed on 48–79,94–95 at nice 19 (542 units, 20.4 GB, 40 large units left out); its custody upload is pending. The 11Z backup `r20261002-110528-f913` is preserved.
    - **Checks:** daemons and `status.md` (12:04Z) are fine. The runner is still #778 with `FILL_VERITY_CPU_SET=48-79,94-95`. The 11:29Z alert is node 1's. #494 is still closed.
- 2026-10-02 11:09Z hourly (10Z): GPU busy 10.6% (0.85 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7 alone. Leased-idle 0.15 GPU-h (bc-15ada664).
    - **Why below 80%:** nothing else was queued, so 7.0 GPU-h sat free. CPU 0–127 at 2.6%.
    - **Disk** at 38%.
    - **Backup:** `r20261002-110528-f913` packed on 48–79,94–95 at nice 19 (542 units, 20.3 GB, 40 large units left out); its custody upload is pending. The 10Z backup `r20261002-100534-18c8` is preserved.
    - **Checks:** daemons and `status.md` (11:04Z) are fine. The runner is still #778 with `FILL_VERITY_CPU_SET=48-79,94-95`.
        - Nebius-infra's 10:40Z steward pass says node 2's PoUS soak ended. It hasn't: it is still running in fill (its log was written at 11:02:59Z, chunks preserved), and it holds GPU 7 until 14:45Z. Their point that the other 7 GPUs are free is right, so I sent no correction.
        - The 10:02Z and 10:32Z alerts are node 1's. #494 is still closed.
- 2026-10-02 10:09Z hourly (09Z): GPU busy 11.4% (0.91 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7, plus bc-698052e1's Commit gm345. Leased-idle 0.54 GPU-h (bc-698052e1 0.40, bc-15ada664 0.14).
    - **Why below 80%:** nothing else was queued, so 6.55 GPU-h sat free. CPU 0–127 at 8.2%.
    - **Disk** at 38%.
    - **Backup:** `r20261002-100534-18c8` packed on 48–79,94–95 at nice 19 (542 units, 20.2 GB, 40 large units left out); its custody upload is pending. The 09Z backup `r20261002-090531-3a30` is preserved.
    - **Checks:** daemons and `status.md` (10:05Z) are fine. The runner is still #778 with `FILL_VERITY_CPU_SET=48-79,94-95`. The new infra notes (interviews rounds 8–9, backlog) only restate node 2's state. The 09:32Z alert is node 1's. #494 is still closed.
- 2026-10-02 09:09Z hourly (08Z): GPU busy 11.2% (0.90 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7, plus bc-698052e1's Commit gm345 from 08:54Z. Leased-idle 0.19 GPU-h (bc-15ada664 0.10, bc-698052e1 0.09).
    - **Why below 80%:** nothing else was queued, so 6.91 GPU-h sat free. CPU 0–127 at 5.6%.
    - **Disk** at 37%.
    - **Backup:** `r20261002-090531-3a30` packed on 48–79,94–95 at nice 19 (542 units, 20.1 GB, 40 large units left out); its custody upload is pending. The 08Z backup `r20261002-080635-8145` is preserved.
    - **Checks:** daemons and `status.md` (09:04Z) are fine. The runner is still #778 (up since 06:28:18Z) with `FILL_VERITY_CPU_SET=48-79,94-95`. Nebius-infra's summary has node 2's numbers (one soak, empty queue; 228 of 406 GPU-h idle since Sep 29). The 08:11Z alert is node 1's. #494 is still closed.
- 2026-10-02 08:09Z hourly (07Z): GPU busy 11.0% (0.88 of 8.00 GPU-h, all useful): memory accounting's honest-latency soak on GPU 7, one long chunk since 06:47:40Z. Leased-idle 0.12 GPU-h (bc-15ada664).
    - **Why below 80%:** nothing else was queued for a GPU, so 7.0 GPU-h sat free. CPU 0–127 at 13.2%: proofs' `zkk32k-stage-bf16-k32768` CPU jobs.
    - **Fill's failed count went from 29 to 30:** proofs' `zkk32k-stage-bf16-k32768.sh` failed with rc 1 after 10.5 min (07:40:47Z, 36 GB peak, empty log). It wasn't the node's doing: its owner (bc-973b1d5f) re-queued it at 07:49Z as `-b` on a newer commit (`558eb183c`, adds `MAX_ANDS`).
    - **Disk** at 37%.
    - **Backup:** `r20261002-080635-8145` packed on 48–79,94–95 at nice 19 (542 units, 20.0 GB, 40 large units left out); its custody upload is pending. The 07Z backup `r20261002-070709-59a6` is preserved.
    - **Checks:** daemons and `status.md` (08:05Z) are fine. The runner is still #778 (`62bdf53d`, up since 06:28:18Z) with `FILL_VERITY_CPU_SET=48-79,94-95`. The new infra notes (interviews round 8, nebius-infra backlog) have nothing for node-2 ops. #494 is still closed.
- 2026-10-02 07:10Z hourly (06Z): GPU busy 12.0% (0.96 of 8.00 GPU-h, all useful): bc-698052e1's Commits (gm337–339) and memory accounting's honest-latency soak on GPU 7. Leased-idle 1.45 GPU-h (bc-698052e1 1.30, bc-15ada664 0.15).
    - **Why below 80%:** no other GPU work was queued, so 5.59 GPU-h sat free. The Commits again held their GPUs mostly idle (1.30 GPU-h). CPU 0–127 at 6.2%: 1 kueue-fold Build.
    - **Disk** at 37%.
    - **Infra replaced the fill runner at 06:27:50Z** with #778's head (`0feb33361`, sha `62bdf53d`, on top of #701) through `research deploy`, for the soak's 540-min exception in `fill/max-min`. The loop restarted it at 06:28:18Z and it adopted both jobs. Nothing broke: the soak re-queues itself in 20–27 min chunks (rc 99) and now gets one long chunk from 06:47:40Z. The deploy wasn't posted in `lanes/node2-ops` first; I found it from the runner's new start time. I updated the Deployed table. Infra's `research deploy` cleanup (06:08–06:09Z) also moved every old `bin/*.prev-*` plus `vy-status`, `numa_ab.sh` and `nvml_ab.sh` to `/workspace/research/deploy/attic/`. None of my scripts or the daemons use them.
    - **Backup:** `r20261002-070709-59a6` packed on 48–79,94–95 at nice 19 (542 units, 19.9 GB, 40 large units left out); its custody upload is pending. The 06Z backup `r20261002-060527-35e8` is preserved.
    - **Checks:** daemons and `status.md` (07:05Z) are fine. The fill loop still carries `FILL_VERITY_CPU_SET=48-79,94-95`. #494 is still closed.
- 2026-10-02 06:09Z hourly (05Z): GPU busy 11.9% (0.96 of 8.00 GPU-h, all useful): bc-698052e1's Commits (gm319, gm328, gm331, gm333, then gm337–339) and memory accounting's PoUS jobs, with the honest-latency soak from 05:52Z. Leased-idle 1.70 GPU-h (bc-698052e1 1.54, bc-15ada664 0.16).
    - **Why below 80%:** no other GPU work was queued, so 5.35 GPU-h sat free. The Commits held their GPUs mostly idle (1.54 of the 1.70 leased-idle), infra's known #2 waster. CPU 0–127 at 5.5%: 1 kueue-fold Build.
    - **Disk** at 37%.
    - **Backup:** `r20261002-060527-35e8` packed on 48–79,94–95 at nice 19 (542 units, 19.8 GB, 40 large units left out); its custody upload is pending. The 05Z backup `r20261002-050536-e6ec` is preserved.
    - **Checks:** daemons and `status.md` (06:04Z) are fine. The fill loop still carries `FILL_VERITY_CPU_SET=48-79,94-95`. Nebius-infra's slot-`d` entry (`VY_PROVER_CPUS` 160–191) is about node 1. #494 is still closed.
- 2026-10-02 05:20Z alerts tick: infra's notice (`note:20261002T0510Z-notice-from-infra-verity-pool-off-80-93`) moves the Verity CPU pool off cores 80–93 for memory accounting's soak, 04:45–14:45Z. Checked read-only:
    - The runner (pid 3649474, restarted 05:09:38Z, jobs adopted) carries `FILL_VERITY_LEND=0 FILL_VERITY_CPU_SET=48-79,94-95`.
    - `cov-gm334`'s processes are pinned to 48–79,94–95. `zkk32k-stage-e4m3` had already finished (it is in `fill/done/`).
    - `vy-fill-cpu-revert.timer` fires at 14:45Z. Status: `timed False`.
    - My side: until 14:45Z the hourly backup goes on 48–79,94–95 at nice 19 (about 11 CPU-s and 1 MB written per run, so it's cautious, not needed). No reply sent, since it's a notice and nothing differs from it.
- 2026-10-02 05:09Z hourly (04Z): GPU busy 20.8% (1.66 of 8.00 GPU-h, all useful): memory accounting's PoUS jobs and two of bc-698052e1's Commits (gm319, gm328). Leased-idle 0.75 GPU-h (bc-698052e1 0.41, bc-15ada664 0.34).
    - **Why below 80%:** no other GPU work was queued, so 5.59 GPU-h sat free. CPU 0–127 at 6.4%: 1 kueue-fold Build and proofs' `zkk32k-stage-e4m3`.
    - **Disk** at 37%.
    - **Backup:** `r20261002-050536-e6ec` packed (541 units, 20.3 GB, 40 large units left out); its custody upload is pending. The 04Z backup `r20261002-040544-d66f` is preserved.
    - **Checks:** daemons and `status.md` (05:04Z) are fine. The new nebius-infra backlog entries (the pacer's `deployments-gpu` hold, #767) and the 04:14Z GPU-idle alert are about node 1. #494 is still closed.
- 2026-10-02 04:08Z hourly (03Z): GPU busy 15.9% (1.27 of 8.00 GPU-h, all useful): memory accounting's PoUS jobs (vLLM e2e series, lf-d0-384k and lf-d0-64k), leased-idle 0.27 GPU-h (bc-15ada664).
    - **Why below 80%:** no other GPU work was queued, so 6.46 GPU-h sat free. CPU 0–127 at 7.9%: 3 kueue-fold Builds.
    - **Disk** at 36%.
    - **Backup:** `r20261002-040544-d66f` packed (537 units, 20.3 GB, 40 large units left out); its custody upload is pending. The 03Z backup `r20261002-030541-f1c3` is preserved.
    - **Checks:** daemons and `status.md` (04:04Z) are fine. Resource-steward's `jobs/src` escalation (`lanes/infra/20261001T1015Z-ask-from-resource-steward-jobs-src-copies-unreaped.md`) is about node 1. #494 is still closed.
- 2026-10-02 03:08Z hourly (02Z): GPU busy 10.1% (0.81 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series on GPU 7 (leased-idle 0.19).
    - **Why below 80%:** no other GPU work was queued, so 7.0 GPU-h sat free. CPU 0–127 at 8.7%: 6 kueue-fold Builds, 2 queued.
    - **Disk** at 38%.
    - **Backup:** `r20261002-030541-f1c3` packed (531 units, 40 large units left out); its custody upload is pending.
    - **Checks:** daemons and `status.md` (03:05Z) are fine. Nebius-infra's memory-request and bundle-cap change (`lanes/nebius-infra/memory-requests-and-bundle-cap.md`) is for node 1. The 02:04Z alert is node 1's. #494 is still closed.
- 2026-10-02 02:08Z hourly (01Z): GPU busy 15.7% (1.25 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e series on GPU 7 plus a few of bc-698052e1's Commits. Leased-idle 0.36 GPU-h (bc-15ada664 0.25, bc-698052e1 0.11).
    - **Why below 80%:** no other GPU work was queued, so 6.39 GPU-h sat free. CPU 0–127 at 10.5%: 6 kueue-fold Builds, 7 CPU jobs queued.
    - **Disk** at 37%.
    - **Backup:** `r20261002-020547-08a0` packed (531 units, 20.3 GB, 40 large units left out); its custody upload is pending.
    - **Checks:** daemons and `status.md` (02:04Z) are fine. The new infra alerts (01:34Z, 02:01Z) are node 1's. #494 is still closed.
- 2026-10-02 01:08Z hourly (00Z): GPU busy 3.6% (0.29 of 8.00 GPU-h, all useful): memory accounting's vLLM e2e smoke and its follow-up on GPU 7.
    - **Why below 80%:** no other GPU work was queued, so 7.59 GPU-h sat free. CPU 0–127 at 11.6%: 6 kueue-fold Builds in the Verity pool, 4 queued.
    - **Disk** at 36%.
    - **Backup:** `r20261002-010541-c883` packed (523 units, 19.75 GB, 40 large units left out); its custody upload is pending.
    - **Checks:** daemons and `status.md` (01:04Z) are fine. The 00:45Z infra alert is node 1's, and the interview notes say nothing about node 2. #494 is still closed.
- 2026-10-02 00:48Z alerts tick: one `gpu-idle-in-lease` at 00:40Z. GPU 7 ran at 8.4% for memory accounting's `pous-vllm-e2e-a4eee988-smoke.sh` (bc-15ada664), 6 min into its lease, which is vLLM start-up. No alert followed at 00:45Z, so nothing to do. Backup `r20261002-000556-a56c` is preserved. Watermark advanced to 00:40:06Z.
- 2026-10-02 00:08Z hourly (23Z): GPU busy 6.4% (0.51 of 8.00 GPU-h, all useful).
    - **Why below 80%:** little GPU work was queued: bc-698052e1's Commits (0.65 GPU-h of them leased-idle) and one 10-min PoUS job (bc-f118526f). 6.76 GPU-h sat free, with lease waiters for 20.3 min. CPU 0–127 at 8.7%.
    - **Disk** fell to 41% (2.0 TB) as the replays cleared their bundles.
    - **Backup:** `r20261002-000556-a56c` packed (519 units, 40 large units left out); its custody upload is pending.
    - **Checks:** daemons and `status.md` (00:05Z) are fine, and the loop runs on `FILL_VERITY_LEND=0` alone. The new infra alerts (23:13Z, 23:30Z) are node 1's. #494 is still closed.
- 2026-10-01 23:18Z alerts tick: two more `gpu-idle-in-lease` alerts, for bc-698052e1's Commits on GPUs 7 and 6 at 0.0%. It's the pattern logged at 23:03Z, so nothing new to do. Backup `r20261001-230613-c160` is preserved. Watermark advanced to 23:15:00Z.
- 2026-10-01 23:08Z hourly (22Z): GPU busy 8.0% (0.64 of 8.00 GPU-h, all useful): Pearl-C4's row 16 re-time 0.36 (2.7 min timed), Commits active 0.28.
    - **Commits' idle time:** bc-698052e1's Commits held 1.64 GPU-h, and 1.36 of it was idle (83%).
    - **Why below 80%:** apart from those Commits, no GPU job was queued. 6.0 GPU-h sat free. CPU 0–127 at 7.4%.
    - **Disk 44% → 52%** (2,601 GiB) in the hour: 425 GB of Commit replay bundles (`/workspace/jobs/cov/cov-gm*/…/replay_bundle_p0`, 46–118 GB per Commit). Each bundle goes once its `verity-replay-*` CPU job finishes (gm181 and gm185 are gone), so this is a passing peak.
    - **The guard gap:** fill's 55% disk stop covers only Verity CPU jobs, not Commit GPU guests. A long Commit run could still fill the disk faster than its replays clear it.
    - **Backup:** `r20261001-230613-c160` packed by 23:07:45Z (517 units, 40 large units left out). Disk was back to 50% (2,471 GiB) by 23:08Z.
    - **Checks:** daemons and `status.md` (23:05Z) are fine. #494 is still closed. Infra's 23:00Z alert is node 1's.
- 2026-10-01 23:03Z alerts tick: four more `gpu-idle-in-lease` alerts for bc-698052e1's Commits: GPUs 3 and 4 at 22:50Z, 6 and 7 at 22:55Z, at 0.0–0.1% over 5 min.
    - **Not just start-up:** GPUs 3 and 4 were 8–10 min into their leases. So these Commits hold the GPU at about 0% for most of a 10-min lease. That is the pattern of n2-commits' `verity-commit` in infra's daily top-3 (9.2 idle of 9.7 GPU-h).
    - **Why no note:** no GPU work is queued behind them, so nobody waits. Infra's daily wasters already carry it. The 23:05Z hourly gives the leased-idle figure.
    - Watermark advanced to 22:55:06Z.
- 2026-10-01 22:48Z alerts tick: three `gpu-idle-in-lease` alerts (22:35, 22:40 and 22:45Z, on GPUs 7, 5 and 6, at 0.2–6.9% mean over 5 min). They're all bc-698052e1's Commit guests in their first 5 minutes.
    - **Why it's fine:** each Commit holds a GPU for about 10 min (rc 0), and its replay now runs as a separate `verity-replay-*` CPU job. The low use is each Commit's start-up, not a GPU held through the replay.
    - Nothing to do. Watermark advanced to 22:45:06Z.
- 2026-10-01 22:18Z inbox: infra gave notice of a `22:20Z 10` line (`note:20261001T2212Z-notice-from-infra-window-line-2220z`), for compute accounting: Pearl-C4's re-time of row 16 (bc-e50ef76f), host threads on 48–91, then an untimed verify on 48–123. The line is in, and infra left the loop alone.
    - **Fill:** the 6 Builds running on the Verity pool's 48–95 freeze while it's `timed True` and resume after. No GPU fill is queued. Nothing for me to do.
    - **Backup:** `r20261001-220550-be70` is preserved. No alerts.
- 2026-10-01 22:08Z hourly (21Z): GPU busy 0.0% (0 of 8.00 GPU-h).
    - **Why below 80%:** no GPU job was queued all hour. CPU 0–127 at 8.2%: 6 kueue-fold Builds in the Verity pool, 2 queued.
    - **Backup:** `r20261001-220550-be70` packed by 22:07:21Z (517 units, 40 large units left out).
    - **Checks:** daemons and `status.md` (22:04Z) are fine. Disk 44%. #494 is still closed.
    - **Infra's reply** (`note:20261001T2130Z-reply-from-infra-window-5-hold-was-mine`): the window 5 hold was infra's, for compute accounting. `FILL_CPU_SLOTS=0` in it was a copy mistake. My 20:47:59Z loop is the one infra meant to set. Next time infra says so in `lanes/node2-ops` before it touches fill. Closed.
    - **Inbox bug, fixed:** `inbox.sh` skipped any note whose `origin:` line mentions `node2-ops`, so replies that cite my note ids were dropped. It missed infra's 21:30Z reply and pouw-node2's 19:01Z ask; I'd found the second by reading the lane. Now it skips only `origin: node2-ops…`.
    - **Back-check from 13:00Z** turned up one other missed note: compute accounting's 16:40Z order to pouw-fp4 (`note:20261001T1640Z-order-from-compute-accounting-stop-verifies-before-cutover`, cc me). It belonged to the 17:15Z cutover that was called off, so it's moot now.
- 2026-10-01 21:07Z hourly (20Z): GPU busy 10.6% (0.85 of 8.00 GPU-h, all useful). The busy time was served window 5's timed run (6.4 min).
    - **Why below 80%:** no GPU job was queued, so 7.15 GPU-h sat free. CPU 0–127 at 16.7%.
    - **GPU 0's verifies:** all done, the last at 20:00:46Z. None are queued.
    - **CPU fill:** 6 kueue-fold Builds fill the Verity pool's 6 slots on 48–95, and 5 more wait (`cpus=16`, 64 GB each). Meanwhile 0–47 (slot d is free) and 96–123 sit idle.
    - **Borrowing:** the runner lends idle Verity slots to pous, but it has no reverse path, so a Verity job can't borrow pous's idle 96–123. Infra could weigh that alongside Daniel's 19:12Z "borrowing goes both ways".
    - **Backup:** `r20261001-210554-a3d7` packed by 21:07:30Z (517 units, 40 large units left out); its custody upload was still pending at 21:08Z.
    - **Checks:** daemons and `status.md` (21:04Z) are fine, and the loop runs on `FILL_VERITY_LEND=0` alone. Disk 47%. The new infra alerts (20:32Z, 20:40Z) are node 1's. #494 is still closed.
- 2026-10-01 20:48Z alerts tick: served window 5 has run, with `timed True` at 20:32Z and `timed False` by 20:47Z. No windows are booked ahead.
    - **The hold:** its 20:25Z stop had requeued Builds `gm225` and `gm226` after 80.3 min each. That's lost work, since a Build reruns from the top. With the window over, the hold left 3 queued Builds unable to start.
    - **What I did:** at 20:47:59Z I respawned the loop with `export FILL_VERITY_LEND=0` alone, dropping the hold and its `FILL_VERITY_MEM_TOTAL_GB=1152`. All 3 Builds started.
    - No alerts, inbox empty. No note: infra already has the question of whose hold it was.
- 2026-10-01 20:07Z hourly (19Z): GPU busy 0.0% (0 of 8.00 GPU-h).
    - **Why below 80%:** no GPU job was queued all hour. Node 1 was at 4% too (nebius-infra's 20:00Z reply). CPU 0–127 at 43.9%: the Verity pool and GPU 0's verifies. At 20:05Z the fill queue was empty, and 2 Builds were running.
    - **Disk** is down to 48%, under the 50% that served window 5's run (20:30Z) waits on.
    - **Backups:** `r20261001-190630-5d7f` is preserved (517 units, 18.4 GB, 40 large units left out). `r20261001-200556-1533` is preserved too (518 units, 39 large units left out), done by 20:07:37Z.
    - **Checks:** the window 5 hold (`FILL_CPU_SLOTS=0`, Verity until 20:00Z and stop 20:25Z, mem total 1,152 GB) is still on, with no answer from infra on whose it is. Daemons and `status.md` (20:04Z) are fine. #494 is still closed, and the new alert is node 1's.
- 2026-10-01 19:08Z hourly (18Z): GPU busy 1.4% (0.11 of 7.67 GPU-h, all useful; 0.12 GPU-h leased-idle, mostly bc-698052e1's 10-min Commit `gm170`).
    - **Why below 80%:** no GPU job was queued all hour, and fill was held for the 18:50Z quota cutover. 7.42 GPU-h sat free. CPU 0–127 at 15.9%.
    - **Second restart:** at 19:04:59Z the same other agent respawned the fill loop again, adding `FILL_VERITY_MEM_TOTAL_GB=1152`, and job B's verify `served-verify-de74f334-7` started at 19:05:00Z.
    - **Why window 5 waits:** pouw-served's checkpoint says its window 5 run (`r20261001-185716-6781`) waits on both verifies and on the disk being under 50%. The disk is at 52%.
    - **Backup:** `r20261001-190630-5d7f` started.
    - **Checks:** daemons are up (fill recreated at 19:05:00Z, ops and util at 18:53:32Z) and `status.md` is fresh (19:05Z). Nothing new for me in the watched lanes: the 18:32Z alert is node 1's. #494 is still closed.
- 2026-10-01 19:05Z alerts tick: the quota cutover is done. The daemons were recreated at 18:53:32Z and the `18:50Z` line was dropped at 18:54:01Z. `/workspace` is ext4 with `prjquota`, at 52% space and 10% inodes. There is still no hand-back note from infra.
    - **Alerts:** two `stale` (sampler, fill) at 18:53:32Z, from the daemon stop. Both are fresh since. Watermark advanced to 18:53:32Z.
    - **Inbox:** pouw-node2 saw the line drop and asked for the hold to be lifted and the verifies released (`note:20261001T1901Z-ask-from-pouw-node2-handback-fill-still-held`).
    - **What I did:** at 19:02:56Z I set `cpu-sets` to `bc-e6a46970-… 0-47 4 40` (backup `infra/logs/cpu-sets.bak-20261001T1903Z`), and 4 `fp8gcver` verifies started. Slot d is free. Then I respawned the loop with `FILL_VERITY_LEND=0` alone.
    - **The race:** at 19:03:00Z someone else respawned it with a hold for served window 5 (`20:30Z 30`, added at 19:02:53Z): `FILL_CPU_SLOTS=0 FILL_VERITY_UNTIL=20:00Z FILL_VERITY_STOP=20:25Z`. I left it, and asked infra whose it is.
    - **Fill now:** the runner adopted all 9 jobs: 4 Builds, `served-verify-b959acdf-8` and the 4 verifies. `served-verify-de74f334-7` (31 min lost at the 18:45Z stop) is queued.
    - **Notes:** `note:20261001T1905Z-reply-from-node2-ops-handback-verifies-released` (accounting) and `note:20261001T1905Z-handoff-from-node2-ops-handback-seen-who-holds-fill` (infra).
- 2026-10-01 18:32Z inbox: pouw-node2's note (`note:20261001T1819Z-reply-from-c066b30c-served-window4-on-panel`) puts window 4 on the panel and keeps GPU 0's verifies parked until the hand-back, as planned. It also gives node 2's disk as 51% (2,532 GiB), with 76 GiB left before compute accounting's 52% hold on new passes. Nothing for me to do. No alerts.
- 2026-10-01 18:18Z alerts tick: one alert, `gpu-idle-in-lease` at 18:05:06Z. GPU 7 ran at 8.9% mean over 5 min.
    - **Its job:** bc-698052e1's Commit guest `gm170` (17:59:42Z). It finished rc 0 at 18:09:17Z after 9.6 min, so nothing to do. It fits the Commit pattern already in infra's top-3 wasters. Watermark advanced to 18:05:06Z.
    - **The hold, as designed:** c62f9726's `served-verify-de74f334-7` (max_min 300) started at 18:14:07Z in the Verity pool, so the 18:45Z stop will requeue it and it reruns after the hand-back. The pool doesn't weigh `max_min` against `FILL_VERITY_STOP`. That would be a small runner change for after the cutover.
    - **Backup:** `r20261001-180852-7e76` is preserved (512 units, 18.4 GB, 40 large units left out). At 18:17Z all 8 GPUs were free, with 6 CPU jobs running and 28 queued.
- 2026-10-01 18:10Z hourly (17Z): GPU busy 8.6% (0.62 of 7.27 GPU-h, all useful). The hour has 7.27 GPU-h because the sampler stopped during infra's 17:21Z restart.
    - **Busy time:** served window 4's timed run (4.7 min, 0.62 GPU-h).
    - **Why below 80%:** no GPU work was queued after window 4. The queue held 31 CPU jobs and 0 GPU jobs, so 6.64 GPU-h sat free. CPU 0–127 at 18.6%.
    - **Backup:** `r20261001-180852-7e76` started. The last one took 1.5 min, so it ends long before the 18:45Z Verity stop.
    - **Checks:** daemons (recreated 17:21Z) and `status.md` (18:08Z) are fine. Nothing new for me in the watched lanes; the 17:13Z GPU alert is node 1's. #494 is still closed.
- 2026-10-01 18:08Z alerts tick: the quota cutover I took for done at 17:21Z had been called off. It is now booked for 18:50Z: a `18:50Z 15` line, someone else's, written at 17:35:47Z. Window 4 is verified (c62f9726, 17:57Z).
    - **What I did:** at 18:05:26Z I respawned the fill loop with `FILL_VERITY_LEND=0 FILL_CPU_SLOTS=0 FILL_VERITY_UNTIL=2026-10-01T18:15:00+00:00 FILL_VERITY_STOP=2026-10-01T18:45:00+00:00`. It adopted its 7 jobs: 6 kueue-fold Builds and bc-698052e1's Commit guest `gm170` on 1 GPU.
    - **What stays held:** GPU 0's verifies stay at 0 slots until the hand-back. GPU fill is gated by the line itself.
    - **Notes:** infra (a correction to my 1740Z note, the hold, and an ask for the hand-back time) and compute accounting (the verifies follow the hand-back).
    - **State:** disk 50% (2,488 GiB). No alerts. Watermark unchanged.
- 2026-10-01 17:39Z alerts tick:
    - **Window 4:** its timed run ended before 17:32Z. All 6 grid Builds held through the cutover started at 17:30:00Z (circuits' count, `note:20261001T1731Z-report-from-circuits-grid-models-counts-1030`), filling the Verity pool. Waiting for slots: the BF16 ship build, job B's verify and Builds gm225 and gm404. Disk 50%.
    - **Alert:** `sampler stale` at 17:21:18Z, from the cutover's daemon stop. The sampler is fresh since (17:33Z). Watermark advanced.
    - **Backup:** `r20261001-173340-897a`, the one skipped at 17:05Z, started.
    - **#701:** GPU 0's verifies are due back on 0–47 "yielding to slot d". nice 19 can't make them yield: slot d's checks run in a session scope, fill's in `user@1001.service/app.slice`. So I wrote [#701](https://github.com/danielreuter/verity/pull/701) (cpu-sets jobs on 0–47 pause while `check-d.lock` is held), with a test that fails without it (52 passed, 1 skipped). Deployed at 17:38Z as `471cf488`: the runner adopted its 6 jobs, no errors.
- 2026-10-01 17:29Z after the called-off cutover (I read it as done; it was called off at 17:21Z and moved to 18:50Z):
    - **Infra's restart:** at 17:21:17Z infra recreated the tmux sessions (`pouw-infra-fill`, `-ops`, `-util`, `proofs-n2-hill`, `write-probe`). The fill loop came back with my cutover hold still in its env. `/workspace` is ext4 on `/dev/vdc` (`rw,noatime`).
    - **Window 4:** the cutover line was already out of `fill/windows` (removed without a backup in `infra/logs`). Served window 4 (`r20261001-172141-15d5`, bc-c62f9726) held all 8 GPUs, `timed True`. The `nvidia-smi` running is that run's own telemetry sampler.
    - **What I did:** at 17:29:00Z I respawned the fill loop with `export FILL_VERITY_LEND=0` only, and the runner's env shows just that. I lifted GPU 7's `keep-free`, which ended at 17:00Z (backup `infra/logs/keep-free.bak-20261001T1729Z`). Status reads `kept free -`, with 33 CPU jobs queued: 25 of GPU 0's verifies at 0 slots, plus job B's verify, the BF16 ship build and Builds.
    - The backup waits for `timed False`. No note to infra: nothing is wrong.
- 2026-10-01 17:06Z hourly (16Z): GPU busy 48.3% (3.86 of 8 GPU-h, all useful).
    - Busy time: Pearl-C4's timed re-time (16:00:01–16:25:58Z, 3.47 GPU-h), job B and PoUS's GPU 7 leases.
    - Below 80% because fill is held for the quota cutover and no GPU work was queued after the window: 4.1 GPU-h free. CPU 0–127 at 3.5%.
    - This hour's backup is skipped: 16:32Z's is preserved, and a run now would hold `/workspace` into the 17:15Z cutover. The 17:28Z one-shot runs it after the hand-back.
    - Daemons, `status.md` (17:04Z) and `vy-cluster-agent` fine. Nothing new for me in the watched lanes.
- 2026-10-01 17:03Z inbox: c62f9726's READY for window 4 (`note:20261001T1652Z-ready-from-c62f9726-served-window4-run6-ship`): run 6's ship, `--whole-defer` only. Its launcher starts when the cutover line leaves `fill/windows` or infra posts a hand-back note; after the hand-back, fill runs job B's verify and the BF16 ship build. Infra posted Oct 1's daily top-3 GPU wasters in its report (16:43Z); n2-commits' `verity-commit` is #2 (9.2 idle of 9.7 GPU-h). At 17:02Z: 8/8 GPUs free, nothing in fill running, `keep-free` still `7` (lift it at the hand-back), no hand-back time from infra yet. No alerts.
- 2026-10-01 16:50Z inbox: pouw-node2's READY for window 4 (`note:20261001T1641Z-ready-from-c066b30c-node2-served-4-at-hand-back`).
    - It tells e8ffd7f2 to stop Pearl-C4's running verify at about 17:05Z, so the run is out before the 17:15Z cutover, and asks me to name cores for the re-run. I named 48–91 once window 4's verify ends (about 18:20Z), or 0–47 at nice 19 from 17:55Z with compute accounting's yes (`note:20261001T1650Z-reply-from-node2-ops-pearl-c4-verify-rerun-cores`).
    - Job B is done, and nothing in fill runs. GPU 7's PoUS lease ends at 16:54Z, with no waiters.
    - Backup `r20261001-163236-041e` is preserved (`.custody` reads `preserved: True`): 511 units, 18.4 GB. 40 large units are left out (21 earlier), to check after the cutover.
    - No alerts. Infra hasn't posted the hand-back time yet.
- 2026-10-01 16:36Z inbox and the deferred hourly:
    - **Timeline:** Pearl-C4's 16:00Z lease ended at 16:25:58Z. The kueue-fold Build finished with rc 0 at 16:30:32Z. Job B started at 16:30:02Z, inside its 16:35Z deadline.
    - **Hand-back:** c62f9726 launches window 4's run when the cutover line drops. I asked infra to remove it themselves at the hand-back. Pearl-C4's verifies on 48–91 run until about 17:20Z, so e8ffd7f2 stops the one still running on infra's word. Console's stale `infra-pool.json` was the publisher pausing in the timed windows, by design. Notes: `note:20261001T1636Z-handoff-from-node2-ops-cutover-1015-handback-signal` and `note:20261001T1636Z-reply-from-node2-ops-window4-line-drop`.
    - **Hourly (15Z):** GPU busy 3.9% (0.31 of 8 GPU-h, all useful). Below 80% because almost no GPU work was queued and fill drained for the 16:00Z window (waiters 16.2 min); 7.66 GPU-h sat free. CPU 0–127 at 18.7%. The 16Z hour so far is 78.7% busy (the 26-min timed window). Backup `r20261001-163236-041e` started.
    - No alerts.
- 2026-10-01 16:12Z inbox: the top-level put node 2's quota cutover at 17:00Z, or 17:15Z if node 2 isn't clear, and served window 4 at infra's hand-back, by 17:25Z (compute accounting's order, `note:20261001T1552Z-order-from-compute-accounting-c066b30c-c62f9726-window4-after-cutover`). pouw-node2 asked for the window line and a drained fill (`note:20261001T1555Z-ask-from-pouw-node2-served-4-at-hand-back`).
    - At 16:09Z I added `17:00Z 25` (the cutover) and `17:25Z 30` (served 4); backup `infra/logs/windows.bak-20261001T1609Z`.
    - I restarted the fill loop with no new CPU starts and the Verity stop at 16:55Z (env in Open items). It adopted the paused kueue-fold Build.
    - Job B (1 GPU, 25 min) is the last fill job and must start by 16:35Z.
    - Notes: infra (`note:20261001T1612Z-handoff-from-node2-ops-node2-cutover-fill-drained`), and pouw-node2 and served (`note:20261001T1612Z-reply-from-node2-ops-served-4-booked-fill-held`).
    - The 16:00Z window was running, with `timed True`. No alerts.
- 2026-10-01 15:50Z inbox: pouw-node2 asked compute accounting (second ask) whether GPU 0's 25 parked FP8 verifies can leave 0–47. Its premise was "fill's 48–91", so I replied with the current CPU map: deleting the `cpu-sets` line runs them on 96–123, 4 at a time, under a 128 GB cap; to get 2 at a time under 40 GB, the line would be `bc-e6a46970-… 96-123 2 40` instead. Compute accounting decides; I edit on their word (`note:20261001T1550Z-reply-from-node2-ops-gpu0-verifies-where-they-would-run`). No alerts.
- 2026-10-01 15:08Z hourly (14Z): GPU busy 14.0% (1.12 of 8 GPU-h, all useful). Below 80% because no GPU work was queued. Fill drained for the 14:00Z window from 13:37Z (waiters 22.8 min). Served window 2 held the node 14:00:25–14:04:55Z (0.6 GPU-h). After that the GPU queue was empty, so 6.71 GPU-h sat free. At 15:06Z: 8/8 GPUs free, 0 GPU jobs queued, 25 CPU jobs; only 16:00Z (Pearl-C4) stays booked. #676 merged to `main` at 14:24Z (`d784c58ee`). The deployed `a8c88f3b` is that change. Disk 48%, RAM 1,683 GB available. Daemons, `vy-cluster-agent` and `status.md` fine. No `runner-error`, and `held-unknown-exit/` is empty. Backup `-140627-c112` preserved; `r20261001-150636-3f44` started.
- 2026-10-01 15:10Z morning readout to infra, 9 PM–8 AM PDT: 17.1% GPU busy (15.1 of 88.4 GPU-h), 100% useful, held idle 12.5%, free idle 70.4%, CPU 19.7%; no rollbacks (`note:20261001T1510Z-report-from-node2-ops-morning-readout`). No alerts, inbox empty.
- 2026-10-01 14:48Z inbox: pouw-node2 released the empty 15:00Z slot to fill, since no owner posted READY (`note:20261001T1441Z-ask-from-pouw-node2-drop-1500z-window`). I dropped the line at 14:47:45Z (backup `infra/logs/windows.bak-20261001T1447Z`) and replied (`note:20261001T1448Z-reply-from-node2-ops-1500z-dropped`). Only 16:00Z (Pearl-C4's re-time) is left. At 14:48Z: 7/8 GPUs free, no GPU jobs queued. No alerts.
- 2026-10-01 14:18Z inbox: bc-c62f9726 released served window 3 (15:30Z) (`note:20261001T1408Z-reply-from-c62f9726-served-window-2-timed-window-3-released`). I dropped the line at 14:17Z (backup `infra/logs/windows.bak-20261001T1417Z`) without waiting for pouw-node2's relay, and told compute accounting (`note:20261001T1418Z-reply-from-node2-ops-1530z-window-dropped`). Windows left: 15:00Z and 16:00Z. Backup `-140627-c112` preserved. No alerts; watermark unchanged.
- 2026-10-01 14:07Z hourly (13Z): GPU busy 24.2% (1.94 of 8 GPU-h, all useful). Below 80% because demand ran out: after the 13:06Z refill, the `pn2h-*` points took 1–2 min each, and from about 13:15Z few GPU jobs were queued (pouw-node2's `fp8-715*` repros, `pous-a9-port`). Fill drained for the 14:00Z window from 13:40Z (waiters 18.2 min): 5.8 GPU-h free, 0.26 leased but idle. `pn2h-…-mxf4-k16384` (`max_min=25`, queued 13:36Z) waits for the 14:30–15:00Z gap. Served window 2 held all 8 GPUs 14:00:25–14:04:55Z; its inline verify runs on CPUs 48–123 until 14:55Z. Since the 13:12Z deploy: no `runner-error`, and `held-unknown-exit/` is empty. Disk 48%, RAM 1,622 GB available. Daemons, `vy-cluster-agent` and `status.md` fine. Backup `-131248-6ea7` preserved; `r20261001-140627-c112` started.
- 2026-10-01 13:15Z hourly (12Z): GPU busy 22.1% (1.77 of 8 GPU-h, all useful). Below 80% because of window drains. pouw-ncp held the node 12:05–12:08Z. From 12:20Z fill drained for the 13:00Z 70B window, which compute accounting had released at 11:32Z. pouw-node2 asked me to drop the line at 12:41Z; I read the ask at 13:05Z and dropped it at 13:06Z (backup `fill/windows` in `infra/logs/windows.bak-20261001T1306Z`). Fill refilled 5 GPUs by 13:06:30Z. Also from about 12:20Z, memory accounting's GPU 7 waiters (`--on 7 --wait`) stopped fill from starting anywhere: 5.96 GPU-h free, 0.27 leased but idle, waiters 40.2 min. Fixed in `fill_runner.py` ([#676](https://github.com/danielreuter/verity/pull/676), deployed 13:12:09Z; table above). Replied `note:20261001T1315Z-reply-from-node2-ops-1300z-dropped-gpu7-waiters-fixed`; told infra (`note:20261001T1315Z-handoff-from-node2-ops-fill-runner-keep-free-waiters-676`). Alerts ticks now read this lane's inbox (Open items). Backup `-122731-6b77` preserved; `r20261001-131248-6ea7` started.
- 2026-10-01 12:28Z hourly (11Z), run after the 12:05Z window: GPU busy 9.5% (0.76 of 8 GPU-h, all useful). Below 80% because no GPU fill could start. Before 11:30Z, the drain: the only queued GPU work was Commits at `max_min=40`. Served window 1 held all 8 GPUs for 4m29s (11:30:21–11:34:50Z, 0.6 GPU-h). The runner starts no GPU fill inside a booked window even after its timed lease ends, so the rest of the window sat free. From 12:00Z the 12:05Z window blocked again: 7.17 GPU-h free, 0.07 leased but idle. The three Commits from 10:52Z went back to node 1 at about 11:53Z (`VY_N2_RECLAIM_MIN` 60, `note:20261001T1149Z-report-from-circuits-grid-models-counts-0450`). gm051 and gm149 missed the 12:20–13:00Z gap: no fill tick came at 12:20:00 exactly. pouw-ncp ran 12:05:14–12:08:25Z. Disk 48%, RAM 1,660 GB available. Daemons, `vy-cluster-agent` and `status.md` fine. Backup `-110720-80f4` preserved; `r20261001-122731-6b77` started. Corrected the CPU map under Open items: user/system are back on 0–123 since 09:24Z.
- 2026-10-01 11:10Z hourly (10Z): GPU busy 41.2% (3.29 of 8 GPU-h, all useful). Below 80% because demand ran out between windows. The Pearl-C4 run held all 8 GPUs for 16.7 of its 30 min (2.22 GPU-h). Fill refilled 7 GPUs at 10:30Z, but the four Commits took 4–6 min and PoUS's climbs 0.5–14 min, and nothing else was queued until four more Commits (`max_min=40`) arrived at 10:52Z, too late to clear the 11:30Z window: 4.06 GPU-h free, 0.64 leased but idle. Today's gaps between windows are 5, 40, 30 and 30 min, so those Commits wait until 16:30Z. Told n2-commits, `max_min=25` would fit, their call (`note:20261001T1110Z-handoff-from-node2-ops-commit-max-min-misses-window-gaps`). Disk 47%, RAM 1,669 GB available. Daemons, `vy-cluster-agent` and `status.md` fine. Backup `-103348-d0a3` rc 0, preserved; `r20261001-110720-80f4` started. Large-unit backups done: 21 units preserved. cluster-build's re-pin of `vy-cluster-agent` to main is with infra (`note:20261001T1101Z-handoff-from-cluster-build-repin-agent-to-main`).
- 2026-10-01 10:40Z hourly (09Z), run after the 10:00Z window: GPU busy 23.1% (1.84 of 8 GPU-h, all useful). Below 80% for three reasons. 4.7 GPU-h sat free, mostly the drain before the window: from about 09:30Z no fill job's max_min fits before 10:00Z, and `pn2h-*` place nothing within 20 min of a window. 1.45 GPU-h were leased but idle: circuits' gate Commit on GPU 3 0.58, proofs 0.48, PoUS 0.26. Waiters 46.7 min. The Pearl-C4 window (10:00–10:30Z) ran clean: no GPU fill inside it, no `scope-residue`. At 10:30Z fill refilled all 8 GPUs (n2-commits 4, PoUS 3, GPU 7 PoUS direct with 3 more queued on it). CPU 0–127 37.0%; check slots 1.2%. Disk 42% → 47% (2,333 GB): circuits' 20 grid checkpoints in `jobs/hf` (388 GB, staged 08:38–09:38Z) plus my unit backups; flat at 10:34Z, about 370 GB below the 55% Verity guard. RAM 1,558 GB free. Daemons, `vy-cluster-agent` and `status.md` fine. Backup `-091558` rc 0; `r20261001-103348-d0a3` started. Large-unit backups resumed at 10:31Z: dies 6, 7, 0, 1 and headline-a, b preserved.
- 2026-10-01 09:55Z no new alerts. Infra deployed the exit-status fix as #662 at 09:29:37Z (`note:20261001T0940Z-handoff-from-infra-fill-runner-fix-deployed-662`); I closed #660 as they asked. pouw-fp4 confirmed V-EX stays withdrawn (`note:20261001T0948Z-reply-from-e8ffd7f2-vex-coverage-stays-withdrawn`; its VM covered all 196 tiles); I moved the job to `fill/withdrawn/` and removed my held dir. `held-unknown-exit/` is empty. All 8 GPUs are free for the 10:00Z window. Large-unit backups: dies 6, 7, 0 and 1 preserved; the driver waits until 10:30Z.
- 2026-10-01 09:35Z alerts: `fill-failed` on `pous-climb-s3` (08:59Z): same cause as a3 (its `taskset -c 104-111`), already in memory accounting's note. `gpu-idle-in-lease` on GPU 3 (09:10Z): circuits-commit-phases' gemma2-2b `fix1` gate Commit (`r20261001-090342-83af`), 24 min into its single-core weights step at 2% GPU. Its preemptible lease runs to 11:34Z, so the 10:00Z Pearl-C4 all-GPU window will preempt it. Told the lane, their call (`note:20261001T0935Z-alert-from-node2-ops-gemma2-gate-meets-1000z-window`). Large-unit backups: die6 preserved, die7 uploading; the driver then holds until 10:30Z.
- 2026-10-01 09:25Z hourly (08Z): GPU busy 28.4% (2.27 of 8 GPU-h, all useful). Below 80% for two reasons. 3.62 GPU-h were leased but idle: n2-commits' Gemma-2 Commits 2.56 until infra cancelled them at 08:32Z, proofs 0.64, PoUS 0.19. Another 2.11 GPU-h sat free with nothing approved queued after the cancel. By 09:16Z all 8 GPUs were leased. GPU 3 is circuits' preemptible `fix1` gemma2-2b gate Commit (`r20261001-090342-83af`, launched as `adhoc:ubuntu`), at 0% in its weights step since 09:04Z; it's preemptible, so it doesn't block the 10:00Z window. CPU 0–127 40.3%; check slots 7.1%. Disk 42%, 1,527 GB RAM free; daemons, `vy-cluster-agent` and the pool timer OK; `status.md` fresh. Backup `-080644` rc 0; `r20261001-091558-ffb7` started. I missed item 2 of pouw-node2's 07:41Z ask; the 12:05Z pouw-ncp window was added at 09:20Z (`note:20261001T0925Z-reply-from-node2-ops-ncp-1205z-window-in`). Item routing updated under Open items; memory accounting got its climb-a3 item directly (`note:20261001T0925Z-handoff-from-node2-ops-climb-a3-result-wiped`). Per compute accounting, V-EX stays held: pouw-fp4 finished the 7B coverage elsewhere. Large units: backup.sh leaves out 40 now (21 earlier), and only 8 had a unit backup, the last at 12:26Z yesterday. I had dropped this hourly check. Twenty-one units (about 150 GB raw) have been unchanged for over an hour. `~/node2-ops/large_backup.sh` (copy in my store) backs them up one at a time with `backup_unit.sh`. Each starts only if the unit is unchanged for 60 min and no window runs, waits, or starts within 25 min, and the next starts once custody says preserved. Running in tmux `node2-ops-large-backup`, log `~/node2-ops/large_backup.log`. die6 went first: 13 GB to 6.4 GB in 145 s (`r20261001-092337-ebf6`). Still skipped: `gpu3-fp8/out`, `mvp-e2e/{passes,venv312}`, `pouw-lean-dd9ede96/work`, and dies 3–5 (still changing).
- 2026-10-01 09:15Z alerts: `fill-failed` on `pous-climb-a3` (08:51Z). Cause: infra's 08:42:41Z restart (CPUs 92–123 to proofs until 17:00Z; user/system now 0–91; runner on `FILL_CPU_SET=FILL_VERITY_CPU_SET=48-91`) adopted 9 jobs, and the 8 that ended were re-queued blind as `adopted-exit`. a3 had passed (rc 0, 8.4 min); its re-run `rm -rf`'d the output, then failed on its own `taskset -c 104-111`. s3 failed the same way. I moved four passing `fp8gcver-die4-*` verifies from `queue/` to `done/`. Found and held `pearlc4-vex-coverage.sh` (`fill/held-node2-ops-vex-livelock-20261001T0907Z/`): it had exited 99 every 10 s without progress since about 00:11Z, because the next 7B tile's estimate (694 s) exceeds its 420 s budget. Runner fix `2df218768` (`cursor/fill-exit-status-35fd`: each job's exit status recorded in `running/.<job>.rc`) is for infra to deploy (`note:20261001T0915Z-handoff-from-node2-ops-restart-loses-exit-status-fix`). Owners told via bc-2aa33ad8 (`note:20261001T0915Z-handoff-from-node2-ops-climb-a3-lost-vex-held-verifies-done`).
- 2026-10-01 08:44Z no new alerts. My 08:30Z ask is settled: infra cancelled the five Gemma-2 Commit guests at 08:32Z (rc 143, held in `fill/held-circuits-gemma2-20261001T0832Z/`, per circuits and the top-level). Proofs' `pn2h-*` now hold 2 GPUs, PoUS holds GPU 7, and no GPU work is queued. The runner restarted at 08:42:41Z on the same `fe3bdc8b`; its one `adopted-exit` (`pn2h-…nvf4-k2048`) re-ran and finished rc 0 in 12 s.
- 2026-10-01 08:30Z alerts: `gpu-idle-in-lease` re-alerts on GPU 0 (cg09) and GPU 6 (m001-2). Five Commit guests have sat at 0% for 37–45 min in a single-core step (RSS 24–50 GB, last log line 07:46–07:49Z); no Commit has finished since 07:40Z. This isn't contention (96–123 is 15.7 of 28 busy). Proofs' four `pn2h-*` wait behind them. Asked infra whether to stop new Commit guests on node 2 until the step runs outside the lease (`note:20261001T0830Z-ask-from-node2-ops-commit-guests-hold-gpus-idle-proofs-wait`). Stopped nothing.

- 2026-10-01 08:12Z alerts: two `oom-kill`s in my verify scopes (07:55Z and 08:03Z, `fill-cpuset-*`). The 20 GB cap was too tight: peaks of 19.98 and 20.44 GB sat at the cap, against 16.8 GB under the header's 48 GB. Raised `fill/cpu-sets` to 40 GB, and the 4 running scopes to 40G live (`systemctl --user set-property --runtime`). The killed units requeue (99 or adopted-exit), so nothing failed. Five `gpu-idle-in-lease` alerts on Commit guests (the CPU step; infra monitor log). Memory accounting's `pous-dsweep`/`pous-climb` (bc-15ada664) are allowed until 17:00Z per infra's 07:52Z handoff.

- 2026-10-01 08:10Z hourly (07Z): GPU busy 8.7% (0.69 of 8 GPU-h, all useful). Below 80% for two reasons. n2-commits' Commit guests held 2.84 GPU-h idle in their leases (their single-core "weights of record" step; the cap is now 90 min, `ad91739ef`). Another 4.12 GPU-h sat free with no approved GPU work queued until `pn2h-*` arrived at about 07:50Z. CPU 0–127 36.7%; check slots 6.0%. Disk 38%, RAM 896 GB free; daemons, agent unit and pool timer OK; `status.md` fresh. The 07:05Z backup was missed (VM resets); `-0505` and `-0605` rc 0, `-0805` started. The backup can't take `--queue` (it needs `--source`, and the backup is a node script), so it stays a direct run, the "other way" in infra's goal (a). Replied to proofs: `pn2h-*` allowed until 17:00Z (`note:20261001T0810Z-reply-from-node2-ops-pn2h-allowed`).

- 2026-10-01 07:55Z alerts: `gpu-idle-in-lease` GPU 7 (07:40Z), cg09's previous attempt, moot now. Infra changed node 2 at 07:45Z (`note:20261001T0753Z-handoff-from-infra-runner-ad91739ef-gpu7-keep-free`): runner `ad91739ef` (Commits TP2 and `max_min=90`), `fill/keep-free` = 7 (memory accounting until 17:00Z), windows at 15:00, 15:30 and 16:00Z, and user.slice and system.slice on 0–123. I checked that my cpu-sets code is in the new runner and that all 4 verifies are on 0–47. Dropped the cg09 hold (it fits its lease now) and noted it in n2-commits' note.

- 2026-10-01 07:45Z alerts: `gpu-idle-in-lease` on GPUs 4, 5 and 6 (07:25–07:35Z), n2-commits' Commit guests. Each runs one CPU core on "weights of record" inside its lease; cg09's 07:00Z attempt was capped at 30 min with 2% busy and restarted at 07:30Z. No escaped processes. Sent to n2-commits, cc circuits and infra (`note:20261001T0745Z-alert-from-node2-ops-commit-cpu-step-outlasts-its-lease`); I hold cg09 if it is capped again. Added proofs' `pn2h-*` to the overnight allowed set. kueue-fold moved g080-r1 to `done/` (`note:20261001T0742Z-reply-from-kueue-fold-g080-r1-done`).

- 2026-10-01 07:25Z alerts: `fill-failed` `verity-build-cov-g080-r1` rc 2. Not an OOM: its Build `r20261001-060524-711d` passed at 06:05Z, and my 07:12Z restart's `adopted-exit` led to reruns that found no item and no done marker. Told kueue-fold (`note:20261001T0725Z-alert-from-node2-ops-g080-r1-failed-but-its-build-passed`). The verifies went to 4 slots at 07:25Z with a 20 GB cap (peak 13.3 GB, 10-min units). A second node2-ops thread had written a friction note at 07:12Z (`note:node2-ops/20261001T0712Z-friction-two-node2-ops-threads-at-once`); after the 07:22Z reset no other thread was visible on the VM, and I've updated the note.

- 2026-10-01 07:12Z **verity-top's core map: compute accounting's verifies on 0–47, live.** `5314b8a34` (cpu-sets, 46 nebius tests pass) deployed as `11c4fba4`, runner respawned, all jobs adopted, `fill.err` empty. `fill/cpu-sets` gives bc-e6a46970 0–47 with 1 slot until the first `fp8gcver` unit's peak is measured (4.9 GB at 30 s; header cap 48 GB). Queue order: I touched the `fp8chainver`/`fp8ver2` files so an `fp8gcver` unit is measured first. Checked: affinity 0–47, nice 19, ionice idle; `research run` jobs pin to 48–95. Told compute accounting (`note:20261001T0715Z-reply-from-node2-ops-verifies-on-0-47-live`). After my VM reset at about 07:03Z, I restored from the store bootstrap.

- 2026-10-01 07:12Z alert: GPU 7 idle (0.2%) in the first 5 minutes of n2-commits' Commit guest `cov-cg09`, the known Commit-bootstrap-in-lease pattern. Logged in the infra monitor log; no action. A second node2-ops thread on this VM is mid-change on the core map (`/tmp/n2-infra`, uncommitted), so the alert thread stays read-only until that change lands (`note:node2-ops/20261001T0712Z-friction-two-node2-ops-threads-at-once`).

- 2026-10-01 07:06Z FYI, not node2-ops scope: mps-pack (bc-bf6e7204) made MPS Commit packing live on node 1 at 06:47Z (`note:20261001T0648Z-report-mps-pack-live-on-node1`, addressed to infra and circuits). No Commit is eligible tonight, every pack pod stops by 12:33Z, and node 2 is unaffected. The dispatcher restart came after the 9 PM PDT live-node cutoff, which is infra's call.

- 2026-10-01 07:02Z **infra's four rulings (06:50Z), done.** (1) Hold on new `verity-commit-*` guests lifted 07:02Z. The lease escape is not fixed in `n2_commit.sh` (deployed `17474188`, unchanged since 02:29Z): `research run` starts its workload in a session of its own, so the fill runner's `killpg` and the agent's SIGTERM to `gpu-lease`'s pid both miss it, `gpu-lease` exits and frees the GPU while vLLM runs on inside `gpu-lease-<pid>.scope`. The runner now stops that whole scope and sweeps it when a job ends (`scope-residue` event). Checked on the running `cov-cg09` guest: all its processes are in its scope, none in the job's process group. (2) Window drain: `fill/windows` holds the four booked starts (`note:20261001T0645Z-reply-from-c066b30c-node2-timed-slots-booked`), and no GPU fill starts whose max_min reaches one. A waiting window now drains fill even while the agent holds `agent.lock`; the agent's ledger shows it evicted 7–8 fill leases for each earlier 8-GPU window, but by pid only. (3) `6f0cf0534` on `infra/nebius`: Commits rank first, then pous, then proofs; a queued Commit with no free GPU stops the newest proofs, then pous, GPU fill, never in a window; the deficit order is proofs, pous, Commits. 45 nebius tests pass. Deployed 07:02Z (`68be2cb5`, runner respawned with `FILL_VERITY_LEND=0`, all jobs adopted, `fill.err` empty). (4) Proofs' 11 held jobs went back to `queue/` at 06:49Z; all exited 0 within 12 s with "no research question (PN2G_QUESTION): withdrawn, nothing to do", so proofs must queue fresh jobs to use the empty GPUs (`note:20261001T0705Z-handoff-from-node2-ops-pn2g-released-withdrew`).

- 2026-10-01 06:57Z alert: GPU 1 idle in an `adhoc:ubuntu` lease (commit-gpu-phases gate `r20261001-064902-eb6c`, 4.2%, preemptible, 30 min max, no waiters). Logged in the infra monitor log; no action.

- 2026-10-01 06:56Z +7 h goals to verity-top (`note:20261001T0656Z-report-from-node2-ops-infra-goals-plus7h`). (a) Miss: 49 of 137 jobs on node 2 and 6 of 36 on node 1 went through `--queue` with a question; node 1's Kueue jobs are uncounted (no kubeconfig). (b) Hit: node 1's disk at 31%. (c) Miss: delivered share over 03–06Z was 56% on node 2 and 15% on node 1.

- 2026-10-01 06:38Z released bc-e6a46970's 52 CPU verifies from `held-overnight/` to `queue/`, on compute accounting's 11:26 PM PDT yes relayed by pouw-node2 (bc-c066b30c); their headers now name the question. Still held: the 4 `aw-*` (bc-8412d697). No new alerts.

- 2026-10-01 06:20Z alerts: none new. kueue-fold fixed `n2_build.sh` reruns (`c332e1685`: a `.done` marker makes a rerun a no-op), so runner restarts no longer need a moment without Builds. It moved g084 to `done/` and requeued `cov-g080-r1` with 256 GiB (no OOM since). If g080 is OOM-killed again, hold it.

- 2026-10-01 06:12Z the overnight allowed set adds `pearlc4-bovf-boundary.sh` (bc-e8ffd7f2, PoUW CPU, 24 cores, about 1.6 h), on compute accounting's 10:46 PM PDT order (`note:20261001T0546Z-order-from-compute-accounting-e8ffd7f2-bovf-condition-7`). Running since 06:06Z.

- 2026-10-01 06:08Z hourly (05Z): GPU busy 1.3%; free idle 7.31 GPU-h (no approved GPU work), held idle 0.59 (`adhoc:ubuntu`). CPU 15.6%. Disk 38%; daemons and the agent unit OK; backup `-0505` rc 0, `-0605` started.

- 2026-10-01 06:03Z alerts: `cov-m004-2` failed after a preemption. `n2_build.sh` consumes its item at start, so reruns fail. Appended to kueue-fold's note. Watermark 05:58:43Z.

- 2026-10-01 05:30Z alerts: `adhoc:ubuntu` idle in lease again (GPU 3); appended to the infra monitor log. Watermark 05:25:06Z.

- 2026-10-01 05:15Z alerts: `adhoc:ubuntu` queue-submitted Commit gate jobs (no kind or lane) idle on GPU 1, then failed; reported in the infra monitor log. OOM kill #8, and I held `cov-g080-r1` in `held-overnight/`. Watermark 05:08:06Z.

- 2026-10-01 05:08Z hourly (04Z): GPU busy 11.7% (timed 0.78 GPU-h); free idle 6.64 (no approved GPU work queued); held idle 0.42 (proofs 0.34, `adhoc:ubuntu` 0.09). CPU 16.1%. Disk 38%; daemons and the agent unit OK. Backup `-0405` rc 0, `-0505` started. Queue: only kueue-fold and circuits Builds (allowed).

- 2026-10-01 04:58Z alerts: none new. Rule refined: jobs running at 9 PM keep their chunks (`pearlc4-vex-coverage` cycles 99 → restart within seconds). kueue-fold's Builds (`cov-cg16`, `cg17`, `m004-2`, `m005-2`) run as allowed.

- 2026-10-01 04:42Z alerts, during a timed window (read-only): `pn2g-q-1936-r0` failed, as proofs intends; OOM kill #7 (`cov-g080-r1`'s loop, told kueue-fold). `pearlc4-vex-coverage.sh` (bc-a8466279) is back in the queue and outside the allowed set; sweep it after the window. Watermark 04:31:02Z.

- 2026-10-01 04:28Z alerts: proofs' gate idle in lease again (GPU 7, 3.2%). Proofs answered (`note:20261001T0412Z-reply-from-proofs-gate-1936-stopped`): the gate's selftests are CPU work and its rerun guard was broken (6 starts, 1.6 GPU-h), now fixed; it stops after 9:27 PM. Dropped its max_min exception (`22395f3c9`, never deployed). Nothing to sweep. Watermark 04:10:00Z.

- 2026-10-01 04:10Z alerts: a fourth OOM kill in a `fill-verity-*` scope (04:00:41Z); appended to kueue-fold's note. Nothing to sweep. Watermark 04:00:41Z.

- 2026-10-01 04:10Z hourly (03Z): GPU busy 3.7%; free idle 6.65 GPU-h (no approved GPU work queued), held idle 1.06 (proofs' gate 0.8). CPU 17.7%. Disk 36% (the steward cleaned up from 54%). Daemons, `status.md` and the agent unit OK. Backup `-0405` started. No yes for the held jobs yet.

- 2026-10-01 03:55Z hourly (02Z, late; the VM gap): GPU busy 14.0%, held idle 3.78 GPU-h (n2-commits 3.12, proofs 0.65), free idle 3.10, CPU 42.0%. Hour 03Z so far: 2.8% busy, free idle 5.4 (empty GPU queue). Backup `-0350` started.

- 2026-10-01 03:50Z **overnight gate:** held 56 CPU jobs (bc-e6a46970 52, bc-8412d697 4) in `fill/held-overnight/`, not in compute-accounting's list; asked for a yes. Report: `note:20261001T0350Z-report-from-node2-ops-overnight-gate`.
  - **Allowed overnight:** `f5bf-fp4-coverage-70b-cpu` (bc-f5bf55c8), proofs' `pn2g-q-*` (bc-8416bc72), kueue-fold `verity-build-*`, the per-die divisor baselines and GPU 7's 70B FP4 coverage if queued, and timed windows.
  - **Held:** new `verity-commit-*` (lease escape), everything else.
  - **Each alerts tick tonight:** sweep the queue into `held-overnight/` by that rule. No live-node code change after 9 PM PDT.

- 2026-10-01 03:40Z **after an agent-VM gap (02:20–03:35Z, missed ticks including the 03Z hourly):** three `gpu-unleased` catches, n2-commits' vLLM Commit processes outside their leases, one on proofs' leased GPU 6 (`note:20261001T0340Z-alert-from-node2-ops-commit-processes-outside-their-lease`).
  - Three cgroup OOM kills in `fill-verity-*` scopes, likely `cov-g080-r1`; told kueue-fold.
  - Disk 54%, told the steward.
  - 1 h GPU busy 4%, with no GPU jobs queued.
  - At the gate, I hold new `verity-commit-*` guests until n2-commits explains. Watermark 03:35:06Z.

- 2026-10-01 02:20Z alerts: `gpu-idle-in-lease` ×4, n2-commits' `verity-commit-*` guests (bootstrap inside the GPU lease), and ×1 `pn2g-q` (FYI). `cov-g116` rc=1, item missing (the same rerun pattern as `n2_build.sh`). Relayed to circuits. Disk 48%. Watermark 02:15:06Z.

- 2026-10-01 02:18Z **disk 48%** (39% at 00:10Z): PoUW's `mvp-e2e/passes` holds 800 GB (73 GB a pass, 4 new since 22:12Z), and `gpu3-fp8/out` 737 GB is growing. Alert to resource-steward (`note:20261001T0218Z-alert-from-node2-ops-disk-48-pct-mvp-passes`). Backup `r20261001-000838-916d` PRESERVED.

- 2026-10-01 02:12Z hourly (01Z): GPU busy 86.0%, 100% useful. Held idle 0.70 GPU-h (bc-698052e1 0.18, bc-0f3f8a2f 0.17, bc-8416bc72 0.15) and free idle 0.41. CPU 47.7% (0–127: 57.4%). Delivered share 94% (`delivered_by_hour`).
  - **From about 02:00Z the GPU queue is empty:** 6 of 8 GPUs idle, left idle and reported to the keeper with the cause (PoUW's backlog not queued; circuits gated on `cov-g217`).
  - Backup `-0205` started. Agent unit active. No canary verdict yet.

- 2026-10-01 02:12Z alerts: `pn2g-q-1936-r0` (proofs' gate, approved) idle in lease at 1.2% (staging), FYI.
  - **My miss:** I found five unread handoffs from 22:07–22:31Z. My skims had filtered by time; from now on I read every new file in `lanes/node2-ops/` by name.
  - From those notes:
    - the `pn2g-q` stage job and 3 chunks are approved;
    - circuits' Commits are main fill, gated on `cov-g217` byte-for-byte;
    - the 60-min exception for `pn2g-q-1936-r0` is committed (`7b8318a58`) and goes live with the drill's restart, though the header still asks 30;
    - delivered-output fields are now live (`8bbc7be21`; `note:20261001T0212Z-reply-from-node2-ops-delivered-fields-and-missed-notes`).
  - A window ran 6:46–6:52 PM PDT; waiting for the attempt-67 verdict before the drill. Watermark 01:45:06Z.

- 2026-10-01 01:12Z alerts: `cov-g217-proof` idle in lease again (GPU 0, 0.2% util), its kind's second catch; appended to the circuits note. Watermark 01:05:06Z.

- 2026-10-01 01:10Z hourly (00Z): GPU busy 87.8%, 100% useful. Free idle 0.55 GPU-h (the agent's stuck grant), held idle 0.42 (`cov-g217-proof` 0.34). CPU 27.5% (slots). T2 line and the first top-3 wasters: `note:20261001T0110Z-report-from-node2-ops-t2-and-top-wasters` (GPU met, CPU missed). Backup `-0105` started. Queue 2.63 of 12 GPU-h ready.

- 2026-10-01 00:58Z **INCIDENT, urgent fix:** the live agent granted bc-b139c29c's pinned request (`--on 2,3,4,5,6,7`) GPU 0. `gpu-lease` refused the grant and waited, the agent stopped deciding, and fill holds GPU starts while a waiter is queued, so all 8 GPUs sat free from about 00:52Z. At 00:55:58Z I touched `cluster/live/STOP`: the agent exited, the waiter took GPU 2, and fill refilled 8/8 by 00:57Z (about 5 min idle). Reported in `note:20261001T0058Z-alert-from-node2-ops-agent-stopped-grant-ignored-on`. Node 2 runs on today's rules; `STOP` stays in place.

- 2026-10-01 00:42Z alerts: `gpu-idle-in-lease` on GPU 2. n2-commits' `cov-g217-proof` held it 19.6 min with 10 s busy (a CPU phase in a GPU lease); relayed to `lanes/circuits/`. bc-2aa33ad8 replied that the 0–47 sequencing is fine: measure NUMA 0 as `MemFree + Inactive(file)` (769 GB), log NUMA 0 memory at each freeze, and keep the `mem_gb` caps beside `--membind=1`. Canary window not yet run. Watermark 00:25:02Z.

- 2026-10-01 00:12Z `backup.sh` now waits out timed windows before each unit, and stops with 75 after an hour of windows (`283af0ae7`, sha `e820a1f9`, test added; rollback `backup.sh.prev-20261001T0015Z`). Started the deferred 00Z backup.

- 2026-10-01 00:10Z hourly (23Z): GPU busy 97.6%, 100% useful, 0.17 GPU-h leased-idle (above target). CPU 26.1% (0–127: 35.5%): 55 CPU jobs queue behind 4 slots on 96–127; 0–47 and lending come after the canary.
  - Backup deferred until the 5:00 PM canary window has run (`backup.sh` doesn't check for windows; it should).
  - Agent `r20260930-232102-e6ac` is live and the shadow has stopped; disk 39%; daemons and `status.md` OK.
  - cluster-build: the planner doesn't model fill's CPU jobs, so 0–47 needs no description change.
  - Acked infra's `vy-cluster-agent.service` at about 6:10 PM PDT, with the drill sequence (`note:20261001T0010Z-reply-from-node2-ops-ack-cluster-agent-service`).

- 2026-09-30 23:40Z alerts: `verity-build-vllm-epoch-run-cov-g084.sh` rc=1 is spurious. My 23:17Z runner restart adopted it; the runner requeued it (`adopted-exit`) after its run `r20260930-224925-efaf` had passed; the rerun found its item consumed (`ROW: unbound variable`). Told kueue-fold (`note:20260930T2340Z-handoff-from-node2-ops-g084-spurious-failure-rerun`). **Lesson:** restart the runner only when no Verity Build runs, until `n2_build.sh` reruns as a no-op. The live agent holds `agent.lock` since 23:21Z and grants fill leases. Watermark 23:27:17Z.

- 2026-09-30 23:20Z **switch step 1 done:** deployed by the waiter at 23:17:43Z (4:17 PM PDT), after window 3: gpu-lease `49238797` and fill_runner `5e033072` together, with the runner loop respawned with `FILL_VERITY_LEND=0`. Jobs re-adopted, `fill.err` empty; rollback files `*.prev-20260930T2317Z`; marker `cluster/switch-deployed` written. No `agent.lock` yet, so the live agent is cluster-build's step 2. No alerts; watermark unchanged.

- 2026-09-30 23:10Z hourly (22Z): GPU busy 89.4%, 100% useful, 0.72 GPU-h leased-idle (bc-2aa33ad8 0.31, bc-e6a46970 0.13) and 0.12 free-idle. CPU 40.1%, against T2's 60%: slots are the limit (29 CPU jobs queued, fill has 96–127 with 4 slots). Backup `r20260930-220532-8dc5` rc 0; `-2305` running.
  - **Switch armed:** tmux `node2-ops-switch` on node 2 deploys `8ba5fc589` (gpu-lease `49238797`, fill_runner `5e033072`, runner restarted with `FILL_VERITY_LEND=0`) after window 3 ends, then writes `cluster/switch-deployed` (`note:20260930T2310Z-reply-from-node2-ops-switch-deploy-armed`).
  - **After the 5:00 PM canary:** the rollback drill, then 0–47 fill plus 48–95 lending under bc-2aa33ad8's conditions (freeze on waiting, `numactl --membind=1`); the 6:30 PM repeat is their A/B (`note:20260930T2310Z-handoff-from-node2-ops-numa0-fill-sequencing`).

- 2026-09-30 22:50Z alerts: `gpu-idle-in-lease` ×3, bc-0de2d624's `harness-perdie` (3–6% util, all 8 done, kind 94%), FYI to `lanes/pous/`. `verity-build-cov-n062-r1.sh` rc=10, the second `cov-n06x-r1`, relayed to kueue-fold. Watermark 22:40:05Z.

- 2026-09-30 22:35Z alerts: `gpu-idle-in-lease` on GPU 5, bc-2aa33ad8's `hsplit-w3` (0.8% util, a low-util chunk), relayed to `lanes/pous/`. `verity-build-cov-n061-r1.sh` rc=10 after bootstrap OK (`r20260930-222608-12c0`, validation failed), relayed to kueue-fold. Watermark 22:30:11Z.

- 2026-09-30 22:20Z alerts: the monitor's first `gpu-idle-in-lease` catches were two `kt-e70b` runs (bc-6289d8b0) at <10% util for 5 minutes. They were stopped at `max_min` 8 and passed on retry (about 0.2 GPU-h idle). Relayed to `lanes/pous/`, and a rolling monitor log started at `note:20260930T2220Z-alert-from-node2-ops-job-monitors`. Watermark 22:05:06Z.

- 2026-09-30 22:15Z hourly (21Z): GPU busy 94.6%, 100% useful. CPU 49.3% (0–127: 53.6%, check slots: 40.4%); SM-weighted 1.52 of 8 GPU-h. Under the 95% target by 0.4 points: 0.38 GPU-h leased-idle (top bc-36186951 0.16) and a 4-minute timed window.
  - Backups: `r20260930-210557-16c3` custody PRESERVED; `r20260930-220532-8dc5` rc 0.
  - Daemons up, `status.md` fresh, disk 37%, shadow 584 KB.
  - Queue 8.27 of 12 GPU-h ready (3.7 short; 16 circuits Commits and 3 of bc-2aa33ad8's).
  - Node 1's file is now merged into the pool file as `nodes.n1` (`ec144ba9c`, sha `cb07cc4e`; rollback `publish_pool.py.prev-20260930T2215Z`); node 1 was 1.3% GPU busy.
  - Handoffs read:
    - glide path: the switch at 5–6:30 PM PDT with cluster-build; 15 minutes' notice to bc-2aa33ad8; gpu-lease `49238797` and fill_runner deployed together; canary; drill.
    - the overnight yes rule (from 9 PM PDT); PoUS and network accounting paused; no filler; proofs' `pn2g` held.
    - resource-steward owns cleanup decisions (answered: `note:20260930T2215Z-reply-from-node2-ops-unpublished-runs`).
    - rc=4 closed.
    - kueue-fold's lending `855339e74` waits for PoUW's NUMA 0 answer.

- 2026-09-30 21:52Z alerts: `verity-build-vllm-epoch-run-cov-g019-r1.sh` rc=3 (21:19Z), the same SMOL360 checkpoint not staged, already relayed; kueue-fold's `n2_build.sh` now refuses such Builds (`2068a75c1`). No new relay. GPU queue 1.97 of 12 GPU-h ready, so I added a line to the queue-keeper's note. Watermark 21:19:07Z.

- 2026-09-30 21:55Z bandwidth (for infra, sizing a 90 GB bundle). Both nodes: no local NVMe; `/workspace` is a 4.9 TiB network SSD; root is 247 GiB; `/dev/shm` is 859 GiB tmpfs; eth0 is 400 Gb/s mlx5 Ethernet, MTU 1500. fio on `/workspace` (1 MiB, direct, 4 jobs x iodepth 16, about 10 s, live load): node 2 write 1.54 GiB/s, read 2.37 GiB/s; node 1 write 1.07 GiB/s, read 2.37 GiB/s. Node 2 to node 1 over ssh (aes128-gcm): 1 stream 0.31 GiB/s, 8 streams 2.6 GiB/s, 14 streams about 6.9 GiB/s (2 of 16 were reset by node 1's sshd connection limit). Raw TCP on a high port is filtered between the nodes; only 22 is open.

- 2026-09-30 21:47Z job norms (Daniel 2:14 PM PDT, via infra): node 2's `gpu-idle-in-lease` and `gpu-unleased` monitors and the per-kind table are live in `publish_pool.py` (`6f778a00d`, 0.4 s CPU a run; rollback `publish_pool.py.prev-20260930T2144Z`). Plan and split with cluster-build/kueue-fold: `note:20260930T2140Z-reply-from-node2-ops-job-norms-plan`. From now on the alerts tick relays those two kinds as one note per owning lane per tick. At 01:00Z (6 PM PDT) the T2 line to `lanes/infra/` carries the first top-3 wasters by idle GPU-h, from `nodes.n2.kinds` with `timed:` rows left out; from 1 Oct it's daily at 16:00Z (9 AM PDT). When kueue-fold's `infra-pool-n1.json` exists, merge it in. When cluster-build's registry lands, announce the spec to every handle.

- 2026-09-30 21:27Z publisher live: `infra-pool-publish.timer` writes vy-nebius-1 `/workspace/usage/infra-pool.json` every 5 min (first `generated_at` 21:25:04Z, 0.19 s CPU a run); schema `note:20260930T2127Z-reply-from-node2-ops-infra-pool-schema`. Watermark: 1.47 of 12 GPU-h ready, pinged queue-keeper bc-829aa649 (`note:20260930T2127Z-handoff-from-node2-ops-gpu-queue-below-watermark`). Rollback: `systemctl --user disable --now infra-pool-publish.timer`.

- 2026-09-30 21:18Z alerts: two more kueue-fold Builds rc=3 at bootstrap (SMOL360, TINYLLAMA not staged); added to the 21:05Z note. Watermark 21:16:04Z.

- 2026-09-30 21:15Z hourly: backup `r20260930-210557-16c3` rc 0, 396 units, 0 skipped. Shadow alive, 340 KB. Daemons up, status.md fresh, disk 32%. Asks answered: CPUs 128–191 for fill declined (merge checks run there); 0–47 proposed to bc-2aa33ad8 (freeze-list change, their yes needed); agent-mode question answered for cluster-build (`note:20260930T2115Z-reply-from-node2-ops-agent-mode-and-shadow`). From now on, prose times are Pacific (contract 2.7 §5a).

- 2026-09-30 21:05Z alerts: six kueue-fold `verity-build-cov-*` Builds rc=3 at bootstrap (20:54–21:00Z), MISTRAL7B / QWEN3_30B_A3B weights not staged (HF offline); job-side, relayed (`note:20260930T2105Z-handoff-from-node2-ops-cov-builds-missing-weights`). Disk 32% (27% at 20:17Z; `/workspace/jobs` 13 GB). Watermark 21:00:37Z.

- 2026-09-30 20:33Z alert: `gpu1-pearlc-forms-r2a.sh` rc=4 (20:21:35Z), same pattern (GPU 7); all four bc-18346d9c `forms` jobs now failed; relay note updated. Watermark 20:21:35Z.

- 2026-09-30 20:20Z alerts: `gpu1-pearlc-forms-a.sh` rc=4 on GPU 7 (duplicate line from the node_ops restart), same exit-4 pattern, so it isn't GPU 5 (relay note updated); first Verity guest `verity-build-n2proof-g188.sh` (kueue-fold) rc=2 after its Build passed (`/home/research/uv.toml: Permission denied`, job-side), relayed (`note:20260930T2020Z-handoff-from-node2-ops-first-guest-build-rc2`). Backup rerun `r20260930-201231-7911` custody preserved. Watermark 20:16:29Z.

- 2026-09-30 20:19Z backup `r20260930-200549-d07f` failed (rc 1) at `fill-out/harness-split/state`, which running hsplit jobs rewrite (tar race); every unit after it was lost for that hour. Rerun `r20260930-201231-7911` rc 0, 397 units. Fix `d06d14b5` (retry 3x, then `skipped.txt`) tested locally, deployed 20:19Z.
- 2026-09-30 20:10Z **deployed the one-pool guest path** (table above), outside a window, commit first. Fill runner restarted 2086891 -> 2347098 and adopted its jobs; node_ops restarted by its pane's loop (2005811 -> 2346989). Smoke job `node2ops-verity-smoke.sh` ran in `fill-verity-*.scope`, CPUs 48–95, nice 19, rc 0. Told kueue-fold, infra, nebius-infra. Shadow `r20260930-195806-59f3` (cluster-build, 8 h) running; shadow dir 76K.
- 2026-09-30 20:05Z hourly: 19–20Z 95.1% busy, 100% useful; daemons up, status.md fresh, disk 27%.

- 2026-09-30 19:33Z alert: `gpu1-pearlc-forms-r2b.sh` rc=4 (19:29:45Z), same pattern as `forms-b`, both on GPU 5; added to the 19:20Z relay note. Watermark 19:29:45Z.

- 2026-09-30 19:20Z alerts: `gpu1-pearlc-forms-b.sh` rc=4 (19:12:31Z) and `fp4-recheck2-verify-d3b846cf.sh` rc=1, `RECHECK VERIFY FAILED` (19:13:31Z); both inside the jobs, relayed (`note:20260930T1920Z-handoff-from-node2-ops-alert-two-fill-failures`). Watermark 19:13:31Z.

- 2026-09-30 19:27Z cutover step 1: GRANT WITH CONDITIONS, and the NUMA map (`note:20260930T1926Z-reply-from-node2-ops-numa-map-and-cutover-step-1`). Hourly report now carries `node2_ops` (useful/filler, CPU 0–127).
- 2026-09-30 19:20Z committed on `infra/nebius`: `7f3e59e6` (gpu-lease cap + test) and `964c6423` (live `node_ops.py` cb706e88, `gpu_util_sampler.py` 1f15688e, `backup.sh` b6b58bc0, `backup_unit.sh` 368f1c75, `restart_fill_after_window.sh` 5117f4af, byte for byte); pushed. Nothing deployed.
- 2026-09-30 19:11Z hourly backup `r20260930-190718-208d`: 395 units, 17.7 GB, custody preserved. Daemons util/fill/ops up; status.md fresh; disk 25%; no timed window.
- 2026-09-30 19:05Z hourly report written to node `/workspace/pouw/infra/utilization-report.json` (18–19Z 78%). Alerts watermark 18:30:59Z (last relayed by pous infra); nothing new.
- 2026-09-30 19:02Z **took over node-2 ops**: owner file names bc-c0738ef6 (written 18:57Z). Adopted `/workspace/pouw/infra/lane/` (copies in my VM's `~/node2-ops/lane/`). Hand-back read (`note:20260930T1856Z-handoff-from-pous-infra-hand-back`).
- 2026-09-30 18:52Z verity-top's two items (node-1 Grafana alerts; Verity-side infra agents) relayed to infra (`note:20260930T1852Z-handoff-from-node2-ops-verity-top-items`). Not node2-ops scope.
- 2026-09-30 18:49Z recorded Daniel's 18:42Z ruling: no Nebius key rotation now (open item above).
- 2026-09-30 18:47Z agent VM was reset (home and /workspace wiped); restored with an idempotent bootstrap kept in my agent store (`internal/node2-ops/bootstrap.sh`, no secrets). Owner file still absent -> standby.
- 2026-09-30 18:50Z armed: 4 timers on bc-c0738ef6; ssh, uv, research CLI (`vy-nebius-2` resolves) OK. Owner file absent -> standby.
