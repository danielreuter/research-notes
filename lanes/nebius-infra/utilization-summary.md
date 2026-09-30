---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Nebius utilization summary: vy-nebius-1 (Verity) and vy-nebius-2 (POUS)

**Draft at 08:37Z; final by 13:30Z.** Steward: nebius-infra (bc-fd19a2fe).

**Sources:**
- node 1: Prometheus (DCGM GPU, node-exporter host, 1 min) and `vy-usage`;
- node 2: POUS's 10 s sampler.

`tools/util_collect.py` reads both and stores them hourly as evidence.

**Definitions:**
- **busy:** utilization above 0 in that minute;
- **held:** at least 1 GiB of GPU memory in use, or a lease;
- **idle:** available minus (held or busy).

## GPU-hours per server, by hour

| Server | Hour (UTC) | GPU-h | busy | held or busy | idle | CPU busy (core-h of 192/h) | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | 05:16–06:00 | 5.9 | 0.03 | 0.05 | 5.8 | 12.0 | 112 GiB |
| vy-nebius-1 | 06:00–07:00 | 8.0 | 0.00 | 0.22 | 7.8 | 23.3 | 149 GiB |
| vy-nebius-1 | 07:00–08:00 (cut over at 07:00:48) | 8.0 | 0.05 | 1.4 | 6.6 | 56.2 | 261 GiB |
| vy-nebius-1 | 08:00–08:32 | 4.3 | 0.05 | 0.75 | 3.5 | 30.3 | 273 GiB |
| vy-nebius-2 | 06:05–07:00 | 7.4 | 0.23 | 1.0 | 6.4 | 18.4 | 515 GiB |
| vy-nebius-2 | 07:00–08:00 | 8.0 | 0.97 | 5.7 | 2.3 | 23.8 | 77 GiB |
| vy-nebius-2 | 08:00–08:32 | 4.2 | 0.80 | 3.2 | 1.0 | 26.5 | 32 GiB |

**Evidence:**
- `art:3dd1acb0f2e735e1bdf84a94a0cb1fda4480b864de07f63987d312f55138ee91` (06:43Z)
- `art:347d695219d8b9c509cecb86f03d6564e950f711999c4bf3ce191d913603352b` (06:47Z)
- `art:041e0c3442c4f1c38b0579441900235146090803b15b84144f177245740edac4` (07:43Z)

**Reading:**
- **Node 2 filled up once POUS's workers started (06:09Z).**
- **Node 1's GPUs are held but hardly busy.**
  - Before the cutover, there was no queued GPU work.
  - Since the cutover, M0's and `flock-v2-design`'s prover jobs spend most of their time building the witness on the host (41%
    of M0's prefill figure, per `flock-v2-design`).
  - Coverage cells fail fast on sm_120 until FA2 (#477) lands.

## Top inefficiencies found

| # | Inefficiency | Cost | Done | Status |
|---|---|---|---|---|
| 1 | **Node 1's GPUs idle or held-idle all night so far:** onboarding, a late cutover, coverage blocked on merges and on templates, prover jobs bound by host work | 99% idle to 07:00Z; 82% idle 07–08Z | Backlog per workstream; two theory lanes launched; coverage fills routed | **open** (see Open) |
| 2 | **Every coverage cell failed in setup:** the uid-1000 job user can't write the synced tree | coverage at 0 cells | Job-private tree copy and `PY` on `infra/nebius` (`4ba30f1e`, `0b12356e`), with the Kueue worker's `--out` and `HOT_ROOT` | **fixed**: cells now pass setup (`BOOTSTRAP-OK`) |
| 3 | **A 15-min capture was evicted twice by resubmitted night-sweep rows** (priority inversion) | the capture never finished; each relaunch repaid a ~5 min bootstrap | `capture` priority 1100; `circuits` preempts nothing by priority (live 07:54Z) | **fixed** |
| 4 | **Train checks took `gpu-lease`** although they're CPU-only | blocked M0's cutover; afterwards every check would fail | Checks moved to slots 32–63 and 64–95 with no `gpu-lease` (root and train-speedup) | **fixed** |
| 5 | **Direct runs touched Kueue's GPUs** (three `pytest` runs on GPU 0 after the cutover), and picked their CPUs from stale notes | GPU contention; noisy benchmarks | `research run` blanks `CUDA_VISIBLE_DEVICES` and starts direct runs on `/etc/vy/direct-cpus` (node 1: 0–95) (`84fb8a7b`, `259acc56`) | **fixed in code**; takes effect as lanes pick up `infra/nebius` |
| 6 | **Pinned benchmarks overlapped:** Build 128–159 and M0 144–191 | noisy points on both lines | Disjoint map: Build 128–159, M0 160–191, build-v2-kv 96–127 | **fixed** |
| 7 | **Three versions of `gpu-lease` in an hour**, plus the #485 × #488 and #485 × `infra/nebius` conflicts | drift, and conflicts in trains | One shared branch, `infra/nebius` (#496, now in RC's queue); hourly drift check | **fixed** |
| 8 | **Tests read the host** (`/etc/research/deadline`, `LEASE_DIR`, `/etc/vy/direct-gpus`) | every train check on node 1 failed | #504, plus `b20aa7e1` and `e5a7fbd2` on `infra/nebius`; reproduced and verified with fake host files | **fixed** on the branch; lands with #496 |
| 9 | **The urgent ping thread died with a merge** | lost pings | PR #494, which never merges | **fixed** |

## Theory lanes launched

| Lane | Agent | Workstream | Why theory-bound | Feeds | Status 08:20Z |
|---|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | one implementing agent against 8–22 agent-days of ranked changes; CPU 91% idle | Build owner bc-47d0a3ed | profiling done; the prefill quadratic is in `Concat.slice` and replay, so it's implementing shared key and value prefixes |
| `flock-v2-design` | bc-37a1971b | 3 Prover | nothing designed after tiles and row 2 | M0 bc-ff572e70 | host witness build found to be 41% of M0's prefill; attempt #4 (line `flock-m0-v3`, byte-identical, noisy) reaches **prefill 8.23e6 and decode 1.81e5 × native**, against M0's baseline run's 3.48e7 and 7.9e5, at the device bound; #5 (prefetching uploads) next |

**Not launched:**
- **Coverage:** its bottleneck is merges (FA2 #477 on main) and infra, not ideas.
- **Security:** it doesn't use the servers.

**Launches stop** once the queues and direct work keep the GPUs and CPUs busy. That's re-checked every 30 minutes.

## Open

- **Node 1 GPU busy time is still near 0.** Queued GPU work is host-bound (prover witness builds) or blocked on merges (coverage).
  Next: FA2 landing, which is RC's; `flock-v2-design`'s faster host evaluation; red-team GPU experiments on the assumptions table
  (`rt-sem-cublas` is running).
- **Coverage is compute-bound at 08:36Z:** 4 cells wait for GPU quota while `provers` leaves 2 GPUs idle, because `circuits` never
  borrows. A rebalance (circuits 5, provers 3) is proposed to the Kueue worker.
- **CPU-only coverage Builds are blocked in code:** vLLM finds no platform on a 0-GPU pod. The frontend fix (force the CUDA
  platform for a declared target) is routed to the vLLM side. Meanwhile each cell holds a GPU through its Build.
- **#496** in a train.
- **`lease.sh` clamp fix (`0ad80ec2`)** not yet deployed on either node. It can't fire tonight.
- **Kueue CPU nominal**, less 64 for the check slots: asked of the Kueue worker.
