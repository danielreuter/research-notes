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
| `gpu-lease` | `58e2474c…` | `7f3e59e6` (usage cap) | 20:08Z |
| `fill_runner.py` | `4a122904…` | `ce30461ac` (Verity guest pool, max_min 360, scope freeze) | 20:08:40Z |
| `node_ops.py` | `7b8ebe56…` | `6d877a03` (OOM guard prefers `fill-verity-*`) | 20:08Z |
| `backup.sh` | `914dd687…` | `d06d14b5` (retry/skip a changing unit) | 20:19Z |
| `publish_pool.py` + `~/.config/systemd/user/infra-pool-publish.{service,timer}` | `242707c4…` | `a8978a241` (infra-pool/v1 to vy-n1 every 5 min) | 21:25Z |

Daniel's one-pool rulings (19:12Z, `note:20260930T1915Z-rulings-from-daniel-one-pool`, relayed by infra) approved the guest path and the cutover; nothing is held now.

## Open items

- Nebius key rotation: Daniel ruled 18:42Z "not now, rotate later". Open, not urgent; no action from node2-ops until he says so.
- Standing GPU backlog and CPU fill: asked bc-2aa33ad8 via the pouw coordinator (`note:20260930T1925Z-handoff-from-node2-ops-hour-and-backlog`).
- 21 large units are left out of the hourly backup (`large.txt`); check each hour which ones stopped changing and have no `backup_unit.sh` run (never `gpu3-fp8/out`).

## Log

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
