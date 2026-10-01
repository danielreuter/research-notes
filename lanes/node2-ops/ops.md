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
| `fill_runner.py` | `5e033072…` | `8ba5fc589` (agent.lock, Verity pool lending, run with `FILL_VERITY_LEND=0`) | 23:17:43Z |
| `node_ops.py` | `7b8ebe56…` | `6d877a03` (OOM guard prefers `fill-verity-*`) | 20:08Z |
| `backup.sh` | `e820a1f9…` | `283af0ae7` (retry/skip a changing unit; packs nothing while a window runs or waits) | 00:08Z |
| `publish_pool.py` + `~/.config/systemd/user/infra-pool-publish.{service,timer}` | `f9ea6fdf…` | `6f778a00d` (infra-pool/v1 to vy-n1 every 5 min; idle-in-lease and unleased monitors; per-kind table) | 21:44Z |

Daniel's one-pool rulings (19:12Z, `note:20260930T1915Z-rulings-from-daniel-one-pool`, relayed by infra) approved the guest path and the cutover; nothing is held now.

## Open items

- **9 PM PDT (04:00Z) overnight gate:** each queued job's lane needs an explicit yes (compute-accounting for PoUW, circuits for Commits), and its header must name a research question. Hold the rest in `fill/held-overnight/`, and report the gap and its owner hourly. Run nothing of PoUS's or network accounting's. The glide path's live-node cutoff is 9 PM PDT.
- **The switch, 5–6:30 PM PDT:** it waits on cluster-build (shadow bar, #586's check green); I deploy gpu-lease `49238797` and fill_runner's agent.lock change together.
- **`855339e74` (the pool lends idle slots):** deploy only after PoUW answers on NUMA 0, together with the switch's fill_runner.
- Job norms, owned by me: the daily top-3 wasters (16:00Z); merge node 1's file into the pool file by T4; announce the kind spec when cluster-build's registry lands; a kind that is on the list two days running becomes a proposed admission check.
- Nebius key rotation: Daniel ruled 18:42Z "not now, rotate later". Open, not urgent; no action from node2-ops until he says so.
- Standing GPU backlog and CPU fill: asked bc-2aa33ad8 via the pouw coordinator (`note:20260930T1925Z-handoff-from-node2-ops-hour-and-backlog`).
- 21 large units are left out of the hourly backup (`large.txt`); check each hour which ones stopped changing and have no `backup_unit.sh` run (never `gpu3-fp8/out`).

## Log

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
