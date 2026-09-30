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

- 18:00–19:00Z: **78% busy** (6.27 of 8.00 GPU-h: timed 0.60, kernels 5.67), useful 100% (no filler). Leased-idle 1.13, free-idle 0.60; lease waiters 32 min. Cause: leased-idle, 0.72 GPU-h of it bc-e6a46970's `fp8chain-die{0,1,3,4,5}.sh` fill jobs holding GPUs at 0%; free-idle while a timed window waited. Since the 17:58:46Z waiters fix (to 19:05Z): 79.9%. CPU 0–127: 47.7% (19:09–19:16Z, first window).

## Node 2 layout (read 19:09Z)

NUMA 0 = CPUs 0–95 + GPUs 0–3; NUMA 1 = CPUs 96–191 + GPUs 4–7 + NIC mlx5_0. No NVLink (`NODE` within a socket, `SYS` across).
Fill CPUs 96–127 and check slots 128–191 are on NUMA 1; the held Verity CPUs 48–95 on NUMA 0.

## Held for the next approved deploy (committed on `infra/nebius`, not live)

- `7f3e59e6` `gpu-lease` usage report caps busy/sampled at held time (repo sha256 `58e2474c…`; live `0d172cf3…`).
- The held Verity CPU-pool edits (`fill_runner.py`, lane copy `86f3d1d5…`) and OOM-guard preference (`node_ops.py`, lane copy `7b8ebe56…`): need Daniel's yes.

## Open items

- Nebius key rotation: Daniel ruled 18:42Z "not now, rotate later". Open, not urgent; no action from node2-ops until he says so.
- Standing GPU backlog and CPU fill: asked bc-2aa33ad8 via the pouw coordinator (`note:20260930T1925Z-handoff-from-node2-ops-hour-and-backlog`).
- 21 large units are left out of the hourly backup (`large.txt`); check each hour which ones stopped changing and have no `backup_unit.sh` run (never `gpu3-fp8/out`).

## Log

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
