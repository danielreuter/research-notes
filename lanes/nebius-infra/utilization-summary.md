---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Nebius utilization summary: vy-nebius-1 (Verity) and vy-nebius-2 (POUS), Sep 30 05:16–12:31Z

**Final, 12:40Z.** Steward: nebius-infra (bc-fd19a2fe).

**Sources:**
- node 1: Prometheus (DCGM GPU and node-exporter host metrics, 1 min) and Kueue's `vy-usage` queue samples (5 min);
- node 2: POUS's own 10 s sampler.

`tools/util_collect.py`, in this folder, reads both. No new sampler was added.

**Definitions:**
- **Kueue-allocated:** GPU-hours admitted to jobs.
- **Held:** at least 1 GiB of GPU memory in use, or a lease.
- **Busy:** DCGM utilization above 0 in that minute.
- **Idle:** available minus (held or busy).

## GPU-hours per server

| Server | Hour (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | 05:00 | 5.9 | 0.1 | 0.1 | 0.03 | 5.8 | 9% | 112 GiB |
| vy-nebius-1 | 06:00 | 8.0 | 1.7 | 0.2 | 0.00 | 7.8 | 12% | 149 GiB |
| vy-nebius-1 | 07:00 | 8.0 | 5.2 | 1.4 | 0.05 | 6.6 | 29% | 261 GiB |
| vy-nebius-1 | 08:00 | 8.0 | 5.4 | 1.4 | 0.07 | 6.6 | 23% | 273 GiB |
| vy-nebius-1 | 09:00 | 8.0 | 7.1 | 1.1 | 0.07 | 6.9 | 19% | 181 GiB |
| vy-nebius-1 | 10:00 | 8.0 | 7.8 | 0.6 | 0.10 | 7.4 | 22% | 217 GiB |
| vy-nebius-1 | 11:00 | 8.0 | 7.6 | 2.5 | 0.17 | 5.5 | 20% | 296 GiB |
| vy-nebius-1 | 12:00 | 4.3 | 1.9 | 0.8 | 0.10 | 3.5 | 14% | 199 GiB |
| **vy-nebius-1** | **05:16Z–12:31Z** | **58.1** | **36.8** | **7.9** | **0.58** | **50.2** | **19%** | **296 GiB** |
| vy-nebius-2 | 06:00 | 7.4 | – | 1.0 | 0.23 | 6.4 | 10% | 515 GiB |
| vy-nebius-2 | 07:00 | 8.0 | – | 5.7 | 0.97 | 2.3 | 12% | 77 GiB |
| vy-nebius-2 | 08:00 | 8.0 | – | 6.4 | 2.78 | 1.6 | 18% | 105 GiB |
| vy-nebius-2 | 09:00 | 8.0 | – | 6.5 | 5.49 | 1.5 | 13% | 68 GiB |
| vy-nebius-2 | 10:00 | 8.0 | – | 5.9 | 4.29 | 2.1 | 11% | 74 GiB |
| vy-nebius-2 | 11:00 | 8.0 | – | 3.9 | 2.61 | 4.1 | 6% | 44 GiB |
| vy-nebius-2 | 12:00 | 4.2 | – | 3.2 | 2.32 | 1.0 | 6% | 44 GiB |
| **vy-nebius-2** | **05:16Z–12:31Z** | **51.6** | **–** | **32.6** | **18.67** | **19.0** | **11%** | **515 GiB** |

The 12:00 rows cover 12:00–12:31Z.

**Node 1:**
- **Before the 07:00Z cutover:** 99% idle. Onboarding was still in progress, the cutover was pending, and no GPU work was queued.
- **After it:** Kueue kept 5–8 GPUs allocated, 36.8 GPU-hours in all. Only 7.9 GPU-hours held GPU memory and 0.58 were busy.
- **Why:** coverage cells ran on the one-GPU `config-run-row`. Each held its GPU for a ~3 min tap-compiling bootstrap, queued on one
  lock, then a 3–4 min CPU Build, and used it only during a 7–10 min Commit. Prover jobs build their witness on the host (41% of M0's
  prefill figure).
- **CPU:** 19% busy. RAM peaked at 296 of 1,716 GiB.

**Node 2:** 63% held and 36% busy overall; 81% held from 09:00 to 10:00Z, once POUS's workers and fill queue ran. It was kept quiet for
POUS's timed windows by agreement.

**Totals, both servers:** 109.7 GPU-hours available. 40.5 held or busy (37%), 19.3 busy (18%), 69.2 idle.

## Top inefficiencies: found, and what was done

| # | Inefficiency | Cost | Done | Status |
|---|---|---|---|---|
| 1 | **Coverage cells held a GPU through bootstrap and CPU Build** (the one-GPU `config-run-row`) | the 36.8-allocated / 0.58-busy gap; about 18 min of GPU per small cell | #536, the GPU-less Build (the vLLM side), plus `8f777377`: the Build pod gets the host's `libcuda.so.1`, which vLLM's CUDA platform loads even without a GPU. The smoke test found this. **Measured:** a SmolLM2-135M two-task cell passed end to end, with the Build on no GPU, digests equal, replay 460/460. GPU hold per cell went from about 18 min to about 7.5 min cached, roughly 2.4× more cells per GPU-hour | **fixed**, live since 12:01Z: two-task cells ran in the quiet hour |
| 2 | **Host-wide bootstrap lock**, made worse by my per-pod tree copies, which forced every GPU job to recompile its taps | captures waited 8–14 min; GPU cells held the lock ~3 min each, one after another | One tree copy per content (taps build once per tree), and a stamp that skips a bootstrap that already passed without the lock (`f3e0bf63`). **Measured:** a repeat capture ran 49 s from submit to finish | **fixed** |
| 3 | **Queue settings that idled GPUs:** priority preemption evicted captures; my CPU-quota cut left `provers`' GPUs without CPU quota; cells asked for 192–512 GB against 6–12 GiB used | captures never finished; 2–3 GPUs idle; 4 jobs blocked on memory quota | `capture` priority with no in-queue preemption; CPU 112+64, my cut retracted; memory at the measured peak plus 25% (epoch-run) | **fixed** |
| 4 | **SkyPilot's controller launches at most 8 jobs**, and cells waiting for quota hold those slots | `provers` jobs waited more than 10 min without reaching Kueue | Submitters keep at most 2 cells waiting in Kueue. This also protected the quiet-hour benches | **workaround**; a bigger controller is open |
| 5 | **Every coverage cell failed in setup** (the uid-1000 job user can't write the synced tree) | coverage at 0 cells from about 06:50 to 08:05Z | Job-private tree plus `PY`, later the shared tree (`4ba30f1e`, `f3e0bf63`) | **fixed** |
| 6 | **Train checks blocked the cutover, and short checks queued behind trains:** checks took `gpu-lease`; exclusive slots were only 10–23% busy | a check-wide failure risk after the cutover; short checks waited 10–20+ min | Check slots on CPUs 32–95 with no `gpu-lease`; a shared `--short` slot at `nice 10` (`fb923c3a`) | **fixed** |
| 7 | **Direct runs touched Kueue's GPUs and picked stale CPU blocks** | GPU contention; noisy benches | `research run` blanks `CUDA_VISIBLE_DEVICES` and starts direct runs on `/etc/vy/direct-cpus` (`84fb8a7b`, `259acc56`); a disjoint CPU map | **fixed** |
| 8 | **Drift:** three `gpu-lease` versions in an hour, conflicting infra PRs, live Kueue diverging from the branch | merge conflicts; config nobody had committed | One shared branch, `infra/nebius` (#496), with an hourly drift check. Live Kueue matches the branch since 09:16Z | **fixed** |
| 9 | **Channel gaps** between research-notes and the store | POUS's notes to Verity root went unseen; the Lean lanes' requests reached the red team 80 min late | Every-lane two-way sync every 10 min, holding sensitive files back | **fixed** |
| 10 | **Tests read the host, or the network** (the deadline file, `LEASE_DIR`, `/etc/vy/direct-gpus`, a GitHub fetch) | every train check on node 1 failed; a suite hung for 14 min | #504, plus `b20aa7e1`, `e5a7fbd2` and `9540e031` | **fixed** |

**My own mistakes, each fixed or disclosed to the owner:**
- The per-pod tree copy (07:30Z) that made #2 worse.
- The CPU-quota cut ask (06:27Z).
- The channel sync overwriting RC's store copy of a note (06:38Z).
- My smoke test overwriting the host copy of the coverage lane's SmolLM2 row directory (10:58Z); the published Attempt is intact.
- My smoke test's `provers` pod evicting the Build lane's `cr2-mistral-decode` through a Kueue reclaim (11:29Z).

## Theory lanes launched (Daniel's instruction: launch them when a workstream is theory-bound)

| Lane | Agent | Workstream | Why launched | Outcome, 12:31Z |
|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | one implementing agent against 8–22 agent-days of ranked plan changes; node 1's CPU 91% idle | Key and value prefix sharing (plan change 3) as line `build-v2`. Attempt 1: 6 of 6 rows digest-identical, prefill wall 0.55–0.67× the baseline, RSS about 0.6×. Main-vs-tip A/B at 13:30Z, then a merge request through the Build owner |
| `flock-v2-design` | bc-37a1971b | 3 Prover | nothing designed after tiles and row 2; decode overhead undesigned | Found the host witness build is 41% of M0's prefill figure; host-unit-eval lever, byte-identical: **prefill 8.23×10⁶ and decode 1.81×10⁵ × native**, against the baseline run's 3.48×10⁷ and 7.9×10⁵ (line `flock-m0-v3`, noisy). Quiet-hour re-measure `r20260930-122715-eaf3` running |

**Not launched:**
- **Coverage:** bound by merges and job shape, not ideas.
- **Security:** its Lean work doesn't use the servers.

**Stopped at two:** after 07:00Z, idle GPUs came from job shape and queue settings (#1–#4), which infra fixes addressed, not from missing
ideas.

## Shared infra with POUS

- **`infra/nebius`** ([#496](https://github.com/danielreuter/verity/pull/496), tip `8f777377`) is the one shared branch.
  - 40 commits (merges aside) beyond its base on `main`, from both infra lanes, the Kueue worker, the Nebius owner and RC; all under `tools/research/`. It carries #485,
    #488 and #504.
  - What runs on the servers comes from it.
- **Lessons log:** research-notes `lanes/nebius-infra/lessons.md`, 83 dated entries from both projects.
- **Urgent pings:** [#494](https://github.com/danielreuter/verity/pull/494), which never merges.
- **The plan:** `docs/shared-infra-plan.md`.

## Still open

- **Node 1's busy fraction is still near 1%.** The two-task cells started at 12:01Z, so the next hours show whether GPU hold falls as
  measured. Prover jobs stay bound by the host witness until `flock-v2-design`'s lever lands in M0.
- **A bigger SkyPilot jobs controller** (Kueue worker), so waiting cells can't hold every launch slot.
- **#496** in a train; until it lands, #485, #488 and #504 stay open on their own.
- **Node 1's `gpu-lease`** is behind `infra/nebius`. It's unused since the cutover, so this is low priority.
- **Custody multipart uploads stall** on the Nebius hosts: POUS's finding, routed to RC.
- **The steward's GitHub token is dead since about 09:30Z:** pushes go by bundle through root, and the drift check compares against the
  last `infra/nebius` fetched here.

## Evidence

- `art:b5e8e3e984e8fb34ed2463a40edbebaa21b274a35930307bee455d4db2a27911`: 05:16–12:31Z, both servers, the source of the table above.
- Earlier hourly snapshots:
  - `art:3dd1acb0f2e735e1bdf84a94a0cb1fda4480b864de07f63987d312f55138ee91`
  - `art:347d695219d8b9c509cecb86f03d6564e950f711999c4bf3ce191d913603352b`
  - `art:041e0c3442c4f1c38b0579441900235146090803b15b84144f177245740edac4`
  - `art:9d9bbe64087f0b619801cf1624d4120c4481b5730daae3e7d9e68eaaffa7f3c9`
  - `art:cec8591ae06e2bf396a9574143e6e7d872efd4a190d1dd8230409fa954e13ce2`
  - `art:463ce38085e75dffcf35b3b4efa473a69cd5c25cc5979df8f03259dc797bcf40`
  - `art:4d533cde834684fa505032853396bb9171b36cb3b9ebcaddb288a54f66e248f1`
- **Working files in this folder:** `backlog.md` (the CPU map and fills), and `tools/` (`channel_sync.py`, `util_collect.py`,
  `drift_check.py`).
