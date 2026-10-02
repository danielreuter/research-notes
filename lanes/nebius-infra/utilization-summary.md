---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Nebius utilization summary: vy-nebius-1 (Verity) and vy-nebius-2 (POUS), Sep 30 05:16–13:59Z

**Final, 14:00Z** (first finalized 12:40Z; the table now runs to 13:59Z). Steward: nebius-infra (bc-fd19a2fe).

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
| vy-nebius-1 | 12:00 | 8.0 | 3.3 | 1.4 | 0.20 | 6.6 | 15% | 199 GiB |
| vy-nebius-1 | 13:00 | 8.0 | 4.6 | 1.1 | 0.03 | 6.9 | 12% | 262 GiB |
| **vy-nebius-1** | **05:16Z–13:59Z** | **69.9** | **42.8** | **9.7** | **0.72** | **60.1** | **18%** | **296 GiB** |
| vy-nebius-2 | 06:00 | 7.4 | – | 1.0 | 0.23 | 6.4 | 10% | 515 GiB |
| vy-nebius-2 | 07:00 | 8.0 | – | 5.7 | 0.97 | 2.3 | 12% | 77 GiB |
| vy-nebius-2 | 08:00 | 8.0 | – | 6.4 | 2.78 | 1.6 | 18% | 105 GiB |
| vy-nebius-2 | 09:00 | 8.0 | – | 6.5 | 5.49 | 1.5 | 13% | 68 GiB |
| vy-nebius-2 | 10:00 | 8.0 | – | 5.9 | 4.29 | 2.1 | 11% | 74 GiB |
| vy-nebius-2 | 11:00 | 8.0 | – | 3.9 | 2.61 | 4.1 | 6% | 44 GiB |
| vy-nebius-2 | 12:00 | 8.0 | – | 6.4 | 5.10 | 1.6 | 13% | 65 GiB |
| vy-nebius-2 | 13:00 | 7.9 | – | 5.6 | 5.09 | 2.3 | 16% | 44 GiB |
| **vy-nebius-2** | **05:16Z–13:59Z** | **63.3** | **–** | **41.4** | **26.54** | **21.8** | **13%** | **515 GiB** |

The 13:00 rows cover 13:00–13:59Z. Node 1's quiet hour, 12:30–13:30Z, spans its 12:00 and 13:00 rows: `circuits` held until
13:17:56Z, and only 0.03 GPU-hours busy in the 13:00 hour.

**Node 1:**
- **Before the 07:00Z cutover:** 99% idle. Onboarding was still in progress, the cutover was pending, and no GPU work was queued.
- **After it:** Kueue kept 3–8 GPUs allocated, 42.8 GPU-hours in all. Only 9.7 GPU-hours held GPU memory and 0.72 were busy.
- **Why:** coverage cells ran on the one-GPU `config-run-row`. Each held its GPU for a ~3 min tap-compiling bootstrap, queued on one
  lock, then a 3–4 min CPU Build, and used it only during a 7–10 min Commit. Prover jobs build their witness on the host (41% of M0's
  prefill figure).
- **CPU:** 19% busy. RAM peaked at 296 of 1,716 GiB.

**Node 2:** 65% held and 42% busy overall; 81% held from 09:00 to 10:00Z, once POUS's workers and fill queue ran. It was kept quiet for
POUS's timed windows by agreement.

**Totals, both servers:** 133.1 GPU-hours available. 51.1 held or busy (38%), 27.3 busy (20%), 81.9 idle.

## Evening, 23:00Z Sep 30 – 04:41Z Oct 1 (4:00–9:40 PM PDT; written at 9:45 PM PDT)

| Server | Hour (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy |
|---|---|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | 09-30 23:00 | 8.0 | 1.7 | 1.1 | 0.25 | 6.9 | 7% |
| vy-nebius-1 | 10-01 00:00 | 8.0 | 7.0 | 3.9 | 1.02 | 4.1 | 19% |
| vy-nebius-1 | 10-01 01:00 | 8.0 | 7.3 | 4.0 | 0.62 | 4.0 | 28% |
| vy-nebius-1 | 10-01 02:00 | 8.0 | 5.6 | 4.5 | 0.55 | 3.5 | 29% |
| vy-nebius-1 | 10-01 03:00 | 8.0 | 0.3 | 0.3 | 0.03 | 7.7 | 10% |
| vy-nebius-1 | 10-01 04:00 | 5.6 | 2.3 | 2.2 | 0.77 | 3.4 | 16% |
| **vy-nebius-1** | **23:00Z–04:41Z** | **45.6** | **24.2** | **16.1** | **3.23** | **29.5** | **18%** |
| vy-nebius-2 | 09-30 23:00 | 8.0 | – | 7.8 | 6.58 | 0.2 | 26% |
| vy-nebius-2 | 10-01 00:00 | 8.0 | – | 7.3 | 4.85 | 0.7 | 27% |
| vy-nebius-2 | 10-01 01:00 | 8.0 | – | 7.4 | 5.16 | 0.6 | 48% |
| vy-nebius-2 | 10-01 02:00 | 8.0 | – | 5.3 | 0.18 | 2.7 | 42% |
| vy-nebius-2 | 10-01 03:00 | 8.0 | – | 1.3 | 0.10 | 6.7 | 18% |
| vy-nebius-2 | 10-01 04:00 | 5.6 | – | 0.6 | 0.03 | 4.9 | 14% |
| **vy-nebius-2** | **23:00Z–04:41Z** | **45.6** | **–** | **29.8** | **16.89** | **15.8** | **30%** |

Source: `art:916bf70f2ab32cb41d983d4508bd747059bebd497d8bcf74afc2b0724862db32` (05:16Z–04:41Z).

**What happened:**
- **4:00–5:30 PM PDT, disk hold.** Node 1's `/workspace` peaked at 81% (3:51 PM PDT, about 1,300 GB/h), from replay bundles and
  proofs' duplicated `circuit.txt` files. `deployments-gpu` was held, 21 circuits Commits were deactivated, and the GPUs sat idle.
  - Fixed: `vy-disk-guard`, which holds every queue at 80%; cancelling `cov-g058` and deleting its 98 GB `.partial` (circuits' yes);
    proofs' dedupe; replays ahead of Builds.
- **From 4:47 PM PDT, paced release.** `~/commit-release/release.py` on node 1 is the one pacer, on circuits' and infra's word.
  - Its limits: the projected bundles under the cap (150 GB, then 300 GB from 6:07 PM PDT; someone has since set 1000 GB, with a
    latch back to 150 GB at 78%), 6 Commits in flight, and 4 of them at batch 8+.
  - Its per-model estimate stays above every bundle measured on Sep 30.
- **After 8:07 PM PDT, out of work.** Both nodes ran out of GPU work: the feeders had nothing queued, and node 2 held 56 unapproved
  CPU jobs for overnight. Alerted at 8:40 PM PDT (`note:20261001T0340Z-alert-from-nebius-infra-both-nodes-out-of-gpu-work`). Work
  resumed on node 1 by 9:40 PM PDT (13 CPU tasks, 3 Commits).
- About 2.2 TB of released weights left node 1 tonight, so `/workspace` is at 29%.

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

| Lane | Agent | Workstream | Why launched | Outcome, 14:00Z |
|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | one implementing agent against 8–22 agent-days of ranked plan changes; node 1's CPU 91% idle | Key and value prefix sharing (plan change 3) as line `build-v2`. Attempt 1: 6 of 6 rows digest-identical, prefill wall 0.55–0.67× the baseline, RSS about 0.6×. Main-vs-tip A/B planned for 13:30Z; no result reported by 14:00Z. Then a merge request through the Build owner |
| `flock-v2-design` | bc-37a1971b | 3 Prover | nothing designed after tiles and row 2; decode overhead undesigned | **Finished at 12:49Z.** Line `flock-m0-v3` has 10 attempts, all byte-identical under M0's statement digests. The lever is a one-pass host evaluation of the deep unit's witness, writing directly into pinned host slots, plus a 16-byte z-transpose fix. Best attempt, #8 (18 vCPU, noisy): **7.91×10⁶ prefill and 1.75×10⁵ decode × native**, against the baseline run's 3.48×10⁷ and 7.9×10⁵. Quiet-hour attempt #10 (48 vCPU): 8.56×10⁶ / 1.91×10⁵, against its same-job control's 8.72×10⁶ / 1.92×10⁵. Branch `cursor/host-unit-eval-c9e2` @ `ce7eb155`; merging is M0's call. Designed but not measured: chunked host-slot upload, predicted −6%; unit-slot slack, a statement change |

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
- **Lessons log:** research-notes `lanes/nebius-infra/lessons.md`, 84 dated entries from both projects.
- **Urgent pings:** [#494](https://github.com/danielreuter/verity/pull/494), which never merges.
- **The plan:** `docs/shared-infra-plan.md`.

## Quiet hour and after, 12:31–13:57Z (addendum, 13:58Z)

| Server | GPU-h observed | Kueue-allocated | Held or busy | Busy | Idle |
|---|---:|---:|---:|---:|---:|
| vy-nebius-1 | 11.6 | 5.4 | 1.7 | 0.15 | 9.9 |
| vy-nebius-2 | 11.6 | n/a | 8.7 | 7.8 | 2.8 |

- **The quiet hour idled node 1.** `circuits` admitted nothing from 12:30Z. The benches that ran were M0's `m0-v3-a11-182` in
  `provers`, 13:02–13:16Z, and the Build lane's re-measure, 12:30–12:56Z. Node 1's GPUs were almost all idle.
- **Released early, twice (root's call once nothing was measuring):**
  - At 13:13:30Z I released while a11 was still in its timed runs. The two captures that started overlapped its last ~2.5 min
    (other processes' cores rose from 4–6 to 15–36), so that tail is noisy.
  - I put the Hold back at 13:16:44Z, then released for good at 13:17:56Z, once `provers` was empty.
  - Lesson logged: before an early release, check that `provers` has no admitted workload.
- **Two-task cells had published no Attempts** since 12:01Z: both tasks ran `row stage` bare.
  - Fixed on `infra/nebius` `763ea668` (13:54Z). Each task is one `research run --tool vllm.build|commit` Attempt, and the Commit
    cites the Build.
  - Proved in the store on SmolLM2: Build `r20260930-133221-34d3`, Commit `r20260930-134308-4d11`.
  - Qwen3-30B-A3B's 13:00Z pass left no run record, so it gets rerun.
  - Config-run Commits still publish no typed `verdict` (`research-outputs write` wants `verdict.json`). Routed to the vLLM
    coordinator.
- **Per-tree Triton and vLLM caches** are in the same revision, for the TP2 lane's 274 s Commit warmup. Its cold-vs-warm test runs
  on `763ea668`.

## Still open

- **Node 1's busy fraction is still near 1%.** Two-task cells are the default again from `763ea668`, so the next hours show whether
  GPU hold falls as measured. Prover jobs stay bound by the host witness until `flock-v2-design`'s lever lands in M0.
- **A bigger SkyPilot jobs controller** (Kueue worker), so waiting cells can't hold every launch slot.
- **#496** in a train; until it lands, #485, #488 and #504 stay open on their own.
- **Node 1's `gpu-lease`** is behind `infra/nebius`. It's unused since the cutover, so this is low priority.
- **Custody multipart uploads stall** on the Nebius hosts: POUS's finding, routed to RC.
- **The steward's GitHub token works again** (13:54Z push). Lanes that can't fetch GitHub take `infra/nebius` from the bundle
  `artifacts/nebius/infra-nebius-763ea668.bundle` (sha256 `33bce048…`, needs `8f777377`).

## Daytime, 14:00–21:33Z (7:00 AM–2:33 PM PDT; update at 2:40 PM PDT)

| Server | Hour (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | 14:00 | 8.0 | 3.0 | 1.5 | 0.22 | 6.5 | 24% | 300 GiB |
| vy-nebius-1 | 15:00 | 8.0 | 3.2 | 1.6 | 0.18 | 6.4 | 33% | 831 GiB |
| vy-nebius-1 | 16:00 | 8.0 | 6.8 | 3.9 | 0.32 | 4.1 | 44% | 1028 GiB |
| vy-nebius-1 | 17:00 | 8.0 | 7.8 | 4.1 | 0.35 | 3.9 | 31% | 1202 GiB |
| vy-nebius-1 | 18:00 | 8.0 | 7.8 | 4.4 | 0.72 | 3.6 | 29% | 943 GiB |
| vy-nebius-1 | 19:00 | 8.0 | 7.2 | 4.4 | 0.30 | 3.6 | 27% | 854 GiB |
| vy-nebius-1 | 20:00 | 8.0 | 8.0 | 5.3 | 0.33 | 2.7 | 25% | 443 GiB |
| vy-nebius-1 | 21:00 | 4.5 | 4.0 | 3.1 | 0.23 | 1.5 | 34% | 807 GiB |
| **vy-nebius-1** | **14:00Z–21:33Z** | **60.5** | **47.8** | **28.2** | **2.65** | **32.3** | **31%** | **1202 GiB** |
| vy-nebius-2 | 14:00 | 8.0 | – | 7.4 | 6.12 | 0.6 | 27% | 70 GiB |
| vy-nebius-2 | 15:00 | 8.0 | – | 5.5 | 1.98 | 2.5 | 12% | 130 GiB |
| vy-nebius-2 | 16:00 | 8.0 | – | 3.5 | 1.67 | 4.5 | 18% | 110 GiB |
| vy-nebius-2 | 17:00 | 8.0 | – | 5.4 | 3.56 | 2.6 | 11% | 109 GiB |
| vy-nebius-2 | 18:00 | 8.0 | – | 7.0 | 4.69 | 1.0 | 18% | 69 GiB |
| vy-nebius-2 | 19:00 | 8.0 | – | 7.6 | 6.71 | 0.4 | 30% | 96 GiB |
| vy-nebius-2 | 20:00 | 8.0 | – | 7.0 | 5.83 | 1.0 | 33% | 179 GiB |
| vy-nebius-2 | 21:00 | 4.6 | – | 4.2 | 3.43 | 0.3 | 46% | 205 GiB |
| **vy-nebius-2** | **14:00Z–21:33Z** | **60.5** | **–** | **47.6** | **33.98** | **13.0** | **23%** | **205 GiB** |

The 21:00 rows cover 21:00–21:33Z. Source: `art:fd2ad8f125943e7f6d4c8e449cd0447d6d5a4c2da4559595edd0909fb5ee7f3e` (05:16–21:33Z).

**Node 1 is allocated but not busy.**
- Kueue kept 6–8 GPUs admitted from 9 AM PDT on. A process held GPU memory for 28.2 of the 47.8 allocated GPU-hours, and the GPUs
  were busy for 2.65 (4.4% of all GPU time).
- Node 2 was busy 56% of the time.
- Daniel's targets (2:06 PM PDT) are node 1 at 60% GPU-busy by 3:30 PM PDT and both nodes at 80% by 6:00 PM PDT.

**Causes, in order, and what was done:**
1. **Dispatched Commits replayed on their GPU.** Node 1's dispatcher ran the 9:20 AM two-task template until node1-fill refreshed
   it to `896d14cd` at 2:15 PM PDT. Now a Commit on a tree with PR B defers its replay to a CPU task.
2. **TP2 rows hold 2 GPUs through their CPU Build.** These are the 91 queued `config-run-row` jobs. The vLLM coordinator made a
   GPU-less 2-rank Build priority 1 and gave it a new lane.
3. **Hung Commits.** Gemma-2-2B Commits held GPUs for 50–90 minutes with no output. Since 2:20 PM PDT, a Commit whose `commit.log`
   is quiet for 15 minutes is stopped and recorded as cancelled (`ac3e0ea51`).
4. **Commits waited behind Builds for CPU and memory.** GPU and CPU work now use separate queues: `deployments-gpu` has a fixed
   4 vCPU and 160 GiB per GPU, and `deployments-cpu` takes Builds and replay. GPU work gets priority 600 over 0-GPU work at 500.
5. **2-GPU TP2 heads starved behind 1-GPU Commits.** `deployments-gpu` has been StrictFIFO since 2:14 PM PDT (node1-fill).
6. **Prover jobs hold 93 GB of GPU memory at about 0% busy.** They build their witness on the host (`backend-sweep-2`, `prover-b`).
   This is open with the prover lanes.

**Also live since 7 AM PDT:**
- Grafana on node 1 (DCGM, Node Exporter Full, busy % per Kueue queue).
- Idle-GPU alerts, written as notes to `lanes/infra/` and `lanes/node1-dispatcher/` with the owning lane named.
- A cap of 4 vLLM deployments and 6 jobs waiting.
- Both servers' hard stop moved to 2026-10-07T15:00:00Z.
- Hourly busy notes, now running through 8 AM PDT Oct 1.

## Evidence

- `art:916bf70f2ab32cb41d983d4508bd747059bebd497d8bcf74afc2b0724862db32`: 05:16Z Sep 30 – 04:41Z Oct 1, both servers, the source of the evening table.
- `art:fd2ad8f125943e7f6d4c8e449cd0447d6d5a4c2da4559595edd0909fb5ee7f3e`: 05:16–21:33Z, both servers, the source of the daytime table.
- `art:48b2eed3fea5d405b696819edceb123442fb5b0ada870f3753d3cfdac6b3d9e0`: 05:16–13:59Z, both servers, the source of the table above.
- `art:b5e8e3e984e8fb34ed2463a40edbebaa21b274a35930307bee455d4db2a27911`: 05:16–12:31Z, the 12:40Z version.
- `art:00e0db82cc9619749b87a46f8db84f58f1bd730f804367ce3698cf858db1f3d5`: 12:31–13:57Z, both servers, the source of the addendum.
- Earlier hourly snapshots:
  - `art:3dd1acb0f2e735e1bdf84a94a0cb1fda4480b864de07f63987d312f55138ee91`
  - `art:347d695219d8b9c509cecb86f03d6564e950f711999c4bf3ce191d913603352b`
  - `art:041e0c3442c4f1c38b0579441900235146090803b15b84144f177245740edac4`
  - `art:9d9bbe64087f0b619801cf1624d4120c4481b5730daae3e7d9e68eaaffa7f3c9`
  - `art:cec8591ae06e2bf396a9574143e6e7d872efd4a190d1dd8230409fa954e13ce2`
  - `art:463ce38085e75dffcf35b3b4efa473a69cd5c25cc5979df8f03259dc797bcf40`
  - `art:4d533cde834684fa505032853396bb9171b36cb3b9ebcaddb288a54f66e248f1`
  - `art:9b793a6870582d0d667b00af5bed5b933468b52b353a8279fdac36d6db744d7e` (1:20 AM PDT Oct 2)
  - `art:4fcccbc1f4027956cce78e2529ea465979079c912cff815862635d27e921b0f1` (2:50 AM PDT Oct 2, the latest)
- **Running totals, Sep 30 05:16Z to 09:50Z Oct 2** (from `art:4fcccbc1…`):
  - Node 1: 420 GPU-h observed, 119 held or busy, 18 busy, 301 idle.
  - Node 2: 413 GPU-h observed, 179 held or busy, 105 busy, 233 idle.
- **Working files in this folder:** `backlog.md` (the CPU map and fills), and `tools/` (`channel_sync.py`, `util_collect.py`,
  `drift_check.py`).
