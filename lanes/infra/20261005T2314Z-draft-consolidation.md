---
id: infra/20261005T2314Z-draft-consolidation
campaign: finished-state
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: bc-17cc41f1-6227-5fab-bc64-3fa2f224558b (@infra coordinator, for Daniel's finished-state ask, thread 1791241620.537329)
---

# Infra's code: consolidation (duplication, fragile APIs, dead code, ranked changes)

Scope: what infra owns. That is `tools/research/src/research/pods/` (the RunPod side, and `nebius/`: 60 files, about 11,100 lines
of Python and shell), `tools/research/src/research/pods/sh/` (`gpu_lease.sh`, `lease.sh`, `pod_guard.sh`), `tools/cluster/`, check's
slot files (`tools/check/slot.py`, `lean_slot.py`, `pod_setup.sh`, `train.sh`), and `research queue` (`queue.py`). It also covers
what runs outside the repository: tmux loops on the control VM and helper scripts under `/tmp` on agent VMs. Read on the Lean
move's head `b87eeef64`. Tonight's PRs on that base: #1243 (one `machines.d` for `register` and `run --on`) and #1244 (paths in
`pods/` and `deploy.toml`).

## 1. Duplication, and which copy survives

| What | Copies | Survivor | Why |
|---|---|---|---|
| GPU schedulers on the two nodes | `gpu_lease.sh` (FCFS, backfill, preemption, agent mode), `n1_lease.py` (node 1's Kueue-backed pool), `fill_runner.py` (node 2's fill queue), `dispatch.py` (node 1's Kueue dispatcher), `keeper.py` (standing targets), `tools/cluster` agent (shadow mode, decides nothing) | `gpu_lease.sh` as the only request API. The `tools/cluster` agent is the only policy, once it leaves shadow mode. `fill_runner`, `keeper` and `dispatch` become its clients | Five places now decide who gets a GPU. Each new rule (timed windows, preemptible, `--max-min` backfill) has to be written two or three times, and the copies drift (tonight: node 1's pool grows for a waiter without recording who it was). |
| Custody | `n1_custody.sh` (445 lines), `n2_custody.sh` (408); the scripts differ in 763 lines once `n1`/`n2` are normalised | One `vy-custody` with a `--via node1` mode for node 2's rsync-then-Job path | The publish/verify/reconcile logic is the same. Only the transport differs. |
| GPU utilisation | `gpu_util_sampler.py` (node 2, 10 s JSONL), `util_collect.py` (console, Prometheus/DCGM for node 1), `resource_probe.py`, `node_ops.py`, `publish_pool.py` and `pool_n1.py` each read utilisation their own way | One per-node JSONL in the sampler's format. On node 1, a shim converts Prometheus DCGM to that JSONL (no new NVML polling, because proofs time there). Every reader reads the JSONL. | Node 1 has no sampler, so `gpu-lease`'s end-of-lease line there reads "busy 0m00s of 0m00s sampled" and never prints the hint to prepare outside the lease (tonight's idle provers-pool leases). |
| Alerts | `n1_alerts.py`, `node_ops.py` (node 2), `gpu_stray.py` (writes `blocked`), the tmux loops `idle-alerts`, `gpu-idle-tracker`, `n1-alerts`, `n2-window-watch`, `n2-unit-watch` and `control-disk-alert` on the control VM | One `vy-alerts@NODE` unit per node, posting through `research msg` | The tmux loops die with the VM, aren't in `deploy.toml`, and nobody else can see or restart them. |
| Machine tables | `~/.research/machines.toml` (laptop, hand-edited), `<notes>/machines.d` (registry), `/etc/vy` files on the nodes | `machines.d` alone. Retire `machines.toml` once `registry import --apply` has copied every live entry | After #1243 both are read everywhere, which is correct but leaves two sources of truth and a refusal path for every name they disagree on. |
| `gpu_lease.sh` copies | the repository's own; `/workspace/verity-guest/bin/gpu-lease` on each node (installed by `deploy.toml`); two frozen copies as `tools/cluster/tests/fixtures/gpu-lease-*` | The repository's own plus the deploy. The frozen fixtures are fine (they pin replays) | No action needed; listed so nobody "dedupes" the fixtures. |
| Slot status and helpers | `tools/check/slot.py`, `check_slot.sh`, `check_slot_d.sh`; on my VM `/tmp/slot_status.py`, `/tmp/one_slot.sh`, `/tmp/pod_cuda.sh` (CUDA 13.0.1 install), `/tmp/atop_start.py` | `slot.py` gains `status` and `one-slot` subcommands. The CUDA package list goes into `pod_setup.sh`. The `/tmp` scripts are deleted | The `/tmp` scripts vanish with my VM and are how slot status and pod CUDA actually work today. |

## 2. Awkward or fragile APIs, the better form, and every caller

- **`research run --on` extends a pod's lease only with `--timeout`.** A long run without one can outlive its pod (I misstated this
  to architecture tonight). Better: extend by the declared `--timeout` when given, else by the machine's `guard` idle minutes plus a
  floor. Callers: `remote.py` (the run launcher), `pods/lease.py`, and every `research run --on POD` across lanes; no caller changes.
- **`registry_dir(machines_toml, environ)`** takes a `machines_toml` it no longer reads after #1243. Better: `registry_dir(environ)`.
  Callers: `registry.py` (5), `remote.resolve_machine`, `doctor.registry_unread`. Mechanical.
- **`gpu_lease.sh` is a 400-line bash script with inline Python heredocs** (usage report, backfill arithmetic, agent mode). Better:
  a small Python module with the same CLI, with `gpu_lease.sh` left as a five-line wrapper. Callers: every lane's job script on both
  nodes (`gpu-lease N --wait ...`), `fill_runner.py`, the `tools/cluster` agent's grant files, tests in `test_nebius*.py` and
  `test_keeper.py`. The CLI stays, so callers don't change. The risk is in timed windows and preemption, which the tests pin.
- **`n1_lease.py`'s `grow` event has no waiter identity.** It logs `waiting: N` only, so finding who held an idle pool GPU tonight
  needed atop and `lease-usage.jsonl`. Better: log the waiters' `who`, `run` and `cmd` (from the `wait.*` owner fields `waiters()`
  already parses). Callers: none outside the pool. A one-line change.
- **Pod helpers that match their own command line.** `pkill -f` / `pgrep -f` with a pattern the ssh command contains killed my shell
  twice. `research pods ssh` could offer `--stop-guard` / `--start-guard` instead of each agent hand-writing `pkill`. Callers: me and
  architecture's pod handling; `pod_guard.sh` already has a pidfile to use.
- **`queue.py`'s rules path switch** (`ci/queue.toml` on main, else `tools/check/queue.toml`, `RULES_BEFORE_MOVE`). Once the move
  lands and the file moves, drop the fallback. Callers: `research queue`, `research merge`'s gate, `test_queue.py`,
  `test_merge_gate.py`.

## 3. Dead code to remove

- `nebius/lean_cache_daily.sh`, the stub "publisher not installed". It goes when lean's #1006 publisher lands. Until then the timer
  stays off (standing order).
- `node_sweep.sh`'s `LK_NEW`, if no tree with `security_proofs/flock/*` exists on either node. Those paths never existed on main
  (#1244 keeps them until a sweep shows no such tree).
- `registry import` and the `machines.toml` merge, once `machines.toml` is retired (row 5 of §1).
- `check_slot_d.sh` (slot d's special case) once `slot.py` covers it. Check `deploy.toml` first.
- The control VM's tmux loops listed in §1, once their units exist.
- `RULES_BEFORE_MOVE` in `queue.py` (§2).

## 4. Ranked: value against risk, and whose code it touches

| # | Change | Value | Risk | Touches |
|---|---|---|---|---|
| 1 | #1243 (one `machines.d`) and #1244 (Lean move paths) land in the first post-move train | high: pods registered from any VM resolve everywhere; the `.lake/packages` sweep sees post-move trees | low | infra only |
| 2 | `n1_lease.py` logs waiter identity on `grow`; `gpu-lease` usage records name the lease's pool holder | high for attribution, a few lines | low | infra |
| 3 | Node 1's DCGM-to-JSONL utilisation shim, so `gpu-lease`'s hint works on node 1 | high: the self-correcting signal for idle leases | low–medium (a new unit; reads Prometheus only) | infra; console reads the same JSONL later |
| 4 | Control VM's tmux loops become `deploy.toml` units on the nodes (alerts, watches) | medium–high: survive VM loss, visible to all | medium (alerts can go quiet if a unit is wrong; run both a day) | infra; circuits and proofs receive the alerts |
| 5 | The `/tmp` helpers go into the repository: CUDA in `pod_setup.sh`, `slot.py status/one-slot` | medium | low | infra; ci uses `pod_setup.sh` |
| 6 | One custody script for both nodes | medium (one place for publish and reconcile bugs) | medium: custody preserves results, so it needs dry runs on both nodes before switching | infra; console reads custody's records |
| 7 | `run --on` lease extension without `--timeout` | medium | low | infra; every lane benefits, no caller change |
| 8 | Retire `machines.toml` | medium (one truth) | low after #1243, but it touches the laptop's habits | infra; Daniel's laptop |
| 9 | `gpu_lease.sh` as a Python module behind the same CLI | medium (testability; it's the API every GPU job uses) | medium–high: preemption and timed windows | infra; every GPU lane's scripts stay the same |
| 10 | One scheduler: the `tools/cluster` agent goes live and `fill_runner`, `keeper` and `dispatch` become its clients | high in the long run | high: it decides who runs on both nodes, and timed PoUW windows depend on it | infra, circuits (dispatch templates), compute accounting (timed windows), proofs (provers pool) |

## 5. What needs Daniel's ruling

1. **Make the `tools/cluster` agent live** (row 10). It has run in shadow mode on node 2. Going live hands GPU decisions on both
   nodes to one planner. My recommendation: node 2 first, behind a day of shadow agreement at least 99% with what `gpu-lease`
   decided, then node 1's pool.
2. **Retire `~/.research/machines.toml` on the laptop** (row 8). It's his file. My recommendation: yes, after
   `research pods registry import --apply` copies every live entry and `research pods registry` shows no refusals.
3. **A sampler or shim on node 1** (row 3) adds a reader beside proofs' timed runs there. My recommendation: the Prometheus shim,
   which adds no NVML queries, rather than `gpu_util_sampler.py`. Proofs should confirm it doesn't affect their timings.
