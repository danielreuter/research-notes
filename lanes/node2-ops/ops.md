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
| `fill_runner.py` | `fe3bdc8b…` | `ad91739ef` on `cursor/n2-commits-first-558b`, by **infra** at 07:45Z, on top of my `5314b8a34` (Commit guests `gpus=2` TP2, up to 120 min; cpu-sets kept; run with `FILL_VERITY_LEND=0`). Infra's backup: `/workspace/verity-guest/backup/20261001T0745Z/`. Don't restore a `.prev-*` without folding in `ad91739ef` (`note:20261001T0753Z-handoff-from-infra-runner-ad91739ef-gpu7-keep-free`) | 2026-10-01 07:45Z |
| `/workspace/pouw/fill/cpu-sets` | (data) | `bc-e6a46970-… 0-47 <slots> [mem_gb]`: compute accounting's verifies on 0–47 (verity-top, 12:00 AM PDT); delete the line to put them back on 96–127 | 2026-10-01 07:12Z |
| `/workspace/pouw/fill/windows` | (data) | booked timed windows, start UTC + minutes; edit when a booking moves | 2026-10-01 07:02Z |
| `node_ops.py` | `7b8ebe56…` | `6d877a03` (OOM guard prefers `fill-verity-*`) | 20:08Z |
| `backup.sh` | `e820a1f9…` | `283af0ae7` (retry/skip a changing unit; packs nothing while a window runs or waits) | 00:08Z |
| `publish_pool.py` + `~/.config/systemd/user/infra-pool-publish.{service,timer}` | `01d22db9…` | `8bbc7be21` (infra-pool/v1 to vy-n1 every 5 min; monitors; per-kind table; node 1 merge; delivered_by_hour) | 02:10Z |

Daniel's one-pool rulings (19:12Z, `note:20260930T1915Z-rulings-from-daniel-one-pool`, relayed by infra) approved the guest path and the cutover; nothing is held now.

## Open items

- **Overnight allowed set adds `pn2h-*`** (owner proofs-n2-hill bc-f0eeea0e, proofs' yes; `note:20261001T0735Z-handoff-from-proofs-n2-hill-pn2h-yes`, `note:20261001T0802Z-ask-from-proofs-allow-pn2h-in-overnight-gate`), until 17:00Z: GPU points through `vy-provers` on 128–191, each names its question, none placed from 20 min before a window. Never sweep them.
- **Overnight allowed set adds memory accounting's `pous-dsweep-*` and `pous-climb-*`** (bc-15ada664), until 17:00Z: top-level 07:41Z, infra says the d-sweep can go through the fill queue (`note:20261001T0752Z-handoff-from-infra-gpu7-and-quiet-cores-live`). GPU 7 is theirs directly (`fill/keep-free`).
- **Verifies on 0–47 (`fill/cpu-sets`):** 4 at a time since 07:25Z, cap 40 GB since 08:11Z (20 GB OOM-killed 2 units whose peaks sat at the cap); delete the line to put them back on 96–127. Until 14:50Z, user.slice and system.slice are on 0–127 (infra); if compute accounting's READY line asks for all 192 CPUs, lift both at the window's drain (`sudo systemctl set-property --runtime user.slice AllowedCPUs=`, same for system.slice) and put back `AllowedCPUs=0-127` after. `held-proofs-pn2g/` is empty; proofs' new GPU jobs go through `vy-provers`.
- **Windows tonight (`fill/windows`):** 10:00Z Pearl-C4, 11:30Z served 1, 13:00Z 70B, 14:00Z served 2, 30 min each. If c066b30c's 09:40Z line says BLOCKED, or bc-e8ffd7f2's 09:05Z checkpoint slips, add the fallback `2026-10-01T11:00Z 30`. Each window: confirm fill is off every GPU once its `gpu-lease --timed` waits (status `window waiting True`, then `timed True`), and that no `scope-residue` was needed.
- **Overnight, until 8 AM PDT (15:00Z):** each alerts tick sweeps `fill/queue/` for jobs **newly queued after 9 PM** outside the allowed set (see the 03:50Z log line, plus `verity-commit-*` again from 07:02Z) into `held-overnight/`; jobs running at 9 PM keep their chunks (99 → requeue → restart). A lane's yes moves its jobs back. At 8 AM PDT, give the morning readout inputs (per-hour useful, filler and held-idle GPU %, CPU %, who ran dry, rollbacks).
- **9 PM PDT (04:00Z) overnight gate:** each queued job's lane needs an explicit yes (compute-accounting for PoUW, circuits for Commits), and its header must name a research question. Hold the rest in `fill/held-overnight/`, and report the gap and its owner hourly. Run nothing of PoUS's or network accounting's. The glide path's live-node cutoff is 9 PM PDT.
- **The switch, 5–6:30 PM PDT:** it waits on cluster-build (shadow bar, #586's check green); I deploy gpu-lease `49238797` and fill_runner's agent.lock change together.
- **`855339e74` (the pool lends idle slots):** deploy only after PoUW answers on NUMA 0, together with the switch's fill_runner.
- Job norms, owned by me: the daily top-3 wasters (16:00Z); merge node 1's file into the pool file by T4; announce the kind spec when cluster-build's registry lands; a kind that is on the list two days running becomes a proposed admission check.
- Nebius key rotation: Daniel ruled 18:42Z "not now, rotate later". Open, not urgent; no action from node2-ops until he says so.
- Standing GPU backlog and CPU fill: asked bc-2aa33ad8 via the pouw coordinator (`note:20260930T1925Z-handoff-from-node2-ops-hour-and-backlog`).
- 21 large units are left out of the hourly backup (`large.txt`); check each hour which ones stopped changing and have no `backup_unit.sh` run (never `gpu3-fp8/out`).

## Log

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
