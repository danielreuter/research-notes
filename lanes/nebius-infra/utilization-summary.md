---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Nebius utilization summary: vy-nebius-1 (Verity) and vy-nebius-2 (POUS)

**Draft at 11:55Z; final by 13:30Z.** Steward: nebius-infra (bc-fd19a2fe).

**Sources:**
- node 1: Prometheus (DCGM GPU, node-exporter host, 1 min) and `vy-usage`;
- node 2: POUS's 10 s sampler.

`tools/util_collect.py` reads both and stores them hourly as evidence.

**Definitions:**
- **busy:** utilization above 0 in that minute;
- **held:** at least 1 GiB of GPU memory in use, or a lease;
- **idle:** available minus (held or busy).

## GPU-hours per server, by hour

| Server | Hour (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | 05:00 | 5.9 | 0.083 | 0.05 | 0.03 | 5.8 | 9% | 112 GiB |
| vy-nebius-1 | 06:00 | 8.0 | 1.667 | 0.22 | 0.00 | 7.8 | 12% | 149 GiB |
| vy-nebius-1 | 07:00 | 8.0 | 5.25 | 1.42 | 0.05 | 6.6 | 29% | 261 GiB |
| vy-nebius-1 | 08:00 | 8.0 | 5.417 | 1.38 | 0.07 | 6.6 | 23% | 273 GiB |
| vy-nebius-1 | 09:00 | 8.0 | 7.083 | 1.07 | 0.07 | 6.9 | 19% | 181 GiB |
| vy-nebius-1 | 10:00 | 5.2 | 5.167 | 0.37 | 0.07 | 4.8 | 25% | 217 GiB |
| **vy-nebius-1** | **total to 10:38Z** | **43.1** | **24.667** | **4.5** | **0.28** | **38.6** | **20%** | **273 GiB** |
| vy-nebius-2 | 06:00 | 7.4 | – | 1.00 | 0.23 | 6.4 | 10% | 515 GiB |
| vy-nebius-2 | 07:00 | 8.0 | – | 5.72 | 0.97 | 2.3 | 12% | 77 GiB |
| vy-nebius-2 | 08:00 | 8.0 | – | 6.43 | 2.78 | 1.6 | 18% | 105 GiB |
| vy-nebius-2 | 09:00 | 8.0 | – | 6.49 | 5.49 | 1.5 | 13% | 68 GiB |
| vy-nebius-2 | 10:00 | 5.2 | – | 4.44 | 2.99 | 0.8 | 10% | 72 GiB |
| **vy-nebius-2** | **total to 10:38Z** | **36.6** | **–** | **24.1** | **12.45** | **12.5** | **13%** | **515 GiB** |

- **Kueue-allocated:** GPU-hours admitted to jobs (node 1 only, from `vy-usage`), whether or not a job used them.
- **The gap is the night's biggest waste:** from 09:00 to 10:00Z, 7.1 GPU-hours were allocated, 1.1 held GPU memory and 0.07 were busy.

**Evidence:**
- `art:3dd1acb0f2e735e1bdf84a94a0cb1fda4480b864de07f63987d312f55138ee91` (06:43Z)
- `art:347d695219d8b9c509cecb86f03d6564e950f711999c4bf3ce191d913603352b` (06:47Z)
- `art:041e0c3442c4f1c38b0579441900235146090803b15b84144f177245740edac4` (07:43Z)
- `art:9d9bbe64087f0b619801cf1624d4120c4481b5730daae3e7d9e68eaaffa7f3c9` (08:43Z)
- `art:cec8591ae06e2bf396a9574143e6e7d872efd4a190d1dd8230409fa954e13ce2` (10:37Z)

**Reading:**
- **Node 2** filled up once POUS's workers started (06:09Z): 69% busy and 81% held from 09:00 to 10:00Z.
- **Node 1's GPUs are allocated, not used.**
  - Before the cutover (07:00Z), there was no queued GPU work.
  - Since then Kueue has kept 5–7 GPUs admitted, almost all to coverage cells on the one-GPU `config-run-row`.
  - Each cell holds its GPU through a ~3 min tap-compiling bootstrap, queued behind the other cells on one lock, and a 3–4 min CPU
    Build. It uses the GPU only in a 7–10 min Commit. The prover jobs build their witness on the host (41% of M0's prefill figure).
  - **Fixes in flight:** the bootstrap cache (#14, bundle with root); the GPU-less Build (with the vLLM side), which moves Builds off
    GPUs; and memory requests at the measured peak plus 25% (epoch-run), so more cells fit at once.

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
| 10 | **Live Kueue drifted from the branch** (09:00Z): the CPU nominal was cut to 80+24, so `provers`' 3 GPUs sat idle for lack of CPU quota while the node ran at 19–29% CPU; in-queue preemption came back, and captures evicted coverage cell `cov-k09-3` twice | 2–3 idle GPUs; lost Builds | Retracted my earlier CPU-cut ask; the Kueue worker applied CPU 112+64 and no in-queue preemption, committed to `infra/nebius` `4e96ed05` (09:16Z); the drift check now diffs live Kueue against the branch hourly | **fixed** |
| 11 | **vLLM's per-machine manifest pool lock serializes lanes** on the shared host | build-v2-kv waited more than 20 min | Routed to the Build owner (budget per run, not per machine) | **open** |
| 12 | **Coverage cells hold a GPU through their bootstrap and CPU Build** (the one-GPU `config-run-row`) | GPU held 16m48s–22m56s per small cell, about 18 min typical; 24.7 GPU-h allocated to 10:38Z, 0.28 busy | #536 (the GPU-less Build) plus `8f777377`: the build task gets the host's `libcuda.so.1`, which vLLM's CUDA platform loads even without a GPU (found by the smoke test). **Measured:** a SmolLM2-135M two-task cell PASSed end to end on node 1: Build 5m52s with no GPU, digests equal to the GPU-visible reference; Commit 440 s; replay 460/460. The GPU was held 15 min for this first cell of its tree (7m35s of it the one-time GPU bootstrap), about 7.5 min cached, against about 18 min before: roughly 2.4× more cells per GPU-hour | **fixed**; live once `8f777377` is pushed and lanes switch |
| 13 | **Coverage cells over-request memory**: 192–512 GB each, while the node uses 110 GiB with 6 running; memory quota then blocks 4 jobs, a GPU capture among them | 2 GPUs idle at 09:30Z | Routed to epoch-run: request the measured peak plus ~25% (pods have no memory limit, so there's no OOM risk) | **open** |
| 14 | **vLLM jobs queue on one host-wide bootstrap lock**, made worse by my 07:30Z per-pod tree copy: every GPU cell recompiled its native taps (~3 min) under the lock, so a 7 s capture bootstrap waited behind them | **before:** jobs 110, 111 and 119 waited 8–14 min before running for seconds; GPU cells held the lock 2m46s–2m57s each, one after another (jobs 124, 120, 121) | One copy of the tree per content (taps build once per tree), and a stamp per tree, arguments and venv that skips a passed bootstrap without the lock (`f3e0bf63`, in bundle `9540e031` in the store's `artifacts/nebius/`, for root to push). **After:** test captures on node 1 took 1m05s from submit to finish for the first job (a real bootstrap, 8 s) and 49 s for the second (cached, lock skipped) | **fixed**; live for each lane once it merges `infra/nebius` |
| 15 | **Short lane checks queue behind trains:** three trains held all three exclusive check slots for long pytest runs, so the GEMM lane's NVFP4 circuit-check rerun (`r20260930-100544-7226`) waited on `check-b`; the slots were 10–23% busy | a minutes-long check waits a whole train (10–20+ min) | Two shared short slots, `check-s1` and `check-s2`, on the check CPUs 8–95 at `nice 10` (usable now with a raw `flock` line; `check_slot.sh --short` in `fb923c3a`, same bundle); node 1's `check-slots` file written; GEMM lane told | **fixed** |
| 16 | **The notes-to-store channel gap, twice:** POUS's notes to Verity root, and the Lean lanes' #514 and #519 pin-grant requests to red-team-flock-3, sat in research-notes while their recipients read the store | found 80 min late, or not at all | `channel_sync.py` mirrors every `lanes/<lane>/` both ways every 10 min (48 h window; never overwrites; holds sensitive-looking and red-team store-to-notes files) | **fixed** |
| 17 | **SkyPilot's jobs controller launches at most 8 jobs at once**, and a job waiting for Kueue quota still holds a slot, so 7 cells queued for `circuits` blocked jobs bound for `provers`, which had free GPUs | a `provers` job waited more than 10 min without reaching Kueue | Submitters keep at most 2 cells waiting in Kueue (epoch-run told); a bigger controller is proposed to the Kueue worker | **open**, workaround in place |
| 18 | **My test evicted another lane's job:** a one-GPU test pod in `provers` triggered Kueue's reclaim of a GPU `circuits` was borrowing, killing the Build lane's `cr2-mistral-decode` mid-run | one lost Build-lane attempt | Build lane told; lesson logged: tests go to `circuits`, which never preempts | **mine, not repeatable** |

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
- **The steward's VM lost GitHub auth at 09:30Z** (invalid token). Pushes to `verity` would go through a bundle in the store's `artifacts/`; nothing is pending.
