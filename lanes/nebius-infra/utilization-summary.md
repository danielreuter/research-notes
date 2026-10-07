---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Nebius utilization summary: vy-nebius-1 (Verity) and vy-nebius-2 (POUS), Sep 30 05:16–13:59Z

**Final, 14:00Z** (first finalized 12:40Z; the table now runs to 13:59Z). Steward: nebius-infra (bc-fd19a2fe).

**Latest:** the section "Third 24 hours, to 14:00Z Oct 4", finalized late at 14:45Z Oct 4 after a VM suspension, covers
Oct 3–4. Before it, "Next 24 hours, to 11:39Z Oct 3" covers Oct 2–3, and "Last 24 hours, to 12:11Z Oct 2" covers Oct 1–2.

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

## Last 24 hours, to 12:11Z Oct 2 (5:10 AM PDT Oct 1 – 5:11 AM PDT Oct 2; finalized 5:15 AM PDT)

| Server | Hours (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | Oct 1 12:10–16:00 (5:10–9 AM PDT) | 30.7 | 8.5 | 5.2 | 1.10 | 25.5 | 21% | 416 GiB |
| vy-nebius-1 | Oct 1 16:00–20:00 (9 AM–1 PM PDT) | 32.0 | 14.2 | 6.3 | 2.07 | 25.7 | 29% | 1543 GiB |
| vy-nebius-1 | Oct 1 20:00–24:00 (1–5 PM PDT) | 32.0 | 7.2 | 4.2 | 0.78 | 27.8 | 29% | 1015 GiB |
| vy-nebius-1 | Oct 2 00:00–04:00 (5–9 PM PDT) | 32.0 | 8.2 | 4.9 | 1.40 | 27.1 | 40% | 869 GiB |
| vy-nebius-1 | Oct 2 04:00–08:00 (9 PM–1 AM PDT) | 32.0 | 9.9 | 3.0 | 0.73 | 29.0 | 40% | 1041 GiB |
| vy-nebius-1 | Oct 2 08:00–12:11 (1–5:11 AM PDT) | 33.3 | 9.1 | 2.9 | 0.67 | 30.5 | 32% | 1546 GiB |
| **vy-nebius-1** | **24 h** | **192.0** | **57.1** | **26.3** | **6.75** | **165.7** | **32%** | **1546 GiB** |
| vy-nebius-2 | Oct 1 12:10–16:00 (5:10–9 AM PDT) | 30.7 | – | 5.7 | 4.25 | 24.9 | 15% | 212 GiB |
| vy-nebius-2 | Oct 1 16:00–20:00 (9 AM–1 PM PDT) | 30.9 | – | 4.8 | 0.46 | 26.2 | 14% | 230 GiB |
| vy-nebius-2 | Oct 1 20:00–24:00 (1–5 PM PDT) | 32.0 | – | 4.1 | 0.64 | 27.9 | 7% | 472 GiB |
| vy-nebius-2 | Oct 2 00:00–04:00 (5–9 PM PDT) | 32.0 | – | 4.5 | 3.43 | 27.5 | 7% | 225 GiB |
| vy-nebius-2 | Oct 2 04:00–08:00 (9 PM–1 AM PDT) | 32.0 | – | 8.5 | 4.14 | 23.5 | 5% | 537 GiB |
| vy-nebius-2 | Oct 2 08:00–12:11 (1–5:11 AM PDT) | 33.6 | – | 5.5 | 3.53 | 28.0 | 6% | 283 GiB |
| **vy-nebius-2** | **24 h** | **191.2** | **–** | **33.1** | **16.46** | **158.1** | **9%** | **537 GiB** |

**GPU-hours used and idle:**
- Node 1: 26 of 192 GPU-h held or busy, and 166 idle (86%). Kueue allocated 57 GPU-h, more than twice what was held. Most
  likely, admitted provers and GPU-pool holders keep their GPU quota through CPU phases; I haven't measured this per job.
- Node 2: 33 of 191 GPU-h held or busy, and 158 idle (83%). Its CPUs were 91% idle.

**Top inefficiencies found, and what was done:**
1. **Dispatcher stall:** every tick failed for 2 h 20 min on a Job that already existed. #732 (merged) makes `submit` idempotent.
   The relay now alerts @circuits and @infra after 5 failed ticks.
2. **Lease-pool fallback:** a node 2 hand-back dropped `VY_LEASE_HOSTDIRS`, so Commits took the provers' pool. #746 (merged)
   makes the default the circuits pool.
3. **Over-booked memory:** Builds and replays booked about 2.5 times their measured peak. Their requests were right-sized, and
   `deployments-cpu` got 640 Gi nominal plus 384 Gi borrowing.
4. **The pacer held Commits with GPUs idle and the disk at 55–60%.** Now in #767 (merged):
   - the cap follows the disk, instead of a fixed 1 TB;
   - bundle estimates are learned from Commits that succeeded (the formula ran 4–9 times high for small models);
   - GPU-pool holders moved to their own LocalQueue, so the pacer's hold never blocks them;
   - the batch-8+ limit went from 4 to 6, which circuits okayed.
5. **Disk:**
   - Hourly evictions of local copies the remote holds: #780 (open; live on node 1). The first research-store pass freed 107 GB.
   - Circuits' #805 lets the eviction see run outputs, about 453 GB more.
6. **Trains waited for check slots.**
   - Slot `d` (128–159) was added, so node 1 has 4 slots.
   - #789 (merged): `slot.py` rereads the slots file on every retry, and skips a slot outside its own cores.
   - The host cpuset was widened to 0–159, and `/etc/vy/direct-cpus` to `0-95,128-159`.
7. **Settings changes never reached the dispatcher loop.** It read `dispatch.env` once, at start, which caught two agents.
   #819 (in a train) reads it fresh every tick.

**Still open:**
- **Feed-bound:** for most of the night, nothing was queued for either server's GPUs.
  - Node 1's GPU work is Commits, which follow hours-long CPU Builds.
  - Node 2's fill queue was empty after the PoUS soak.
  - I told the research coordinator at 3:36 AM PDT that the queues are open.
- **Held by ruling:** the two Gemma-2 b64 i1024 Commits.
- **Kueue-allocated GPU-hours well above held:** see above.
- **Open PRs:** #780, #805 and #819.
- **Disk spike just after this window:** 12:09–12:35Z (5:09–5:35 AM PDT), from 61% to 80%.
  - Six b32 Commits wrote 1.35 TB of bundles: three qwen25-3b and three yi15-6b. The pacer had no size for either model, so the
    formula guessed both low.
  - Five of the six were admitted on arrival through the open gate.
  - The 78% latch and 80% pause held, and the replays are draining the bundles.
  - [#824](https://github.com/danielreuter/verity/pull/824) paces a model with no size one Commit at a time.

**Theory lanes launched:** none in these 24 hours. No workstream was theory-bound: the idle time was feed-bound (work waiting on
upstream Builds or not yet queued by its lane), which goes to the owning coordinator.

## Next 24 hours, to 11:39Z Oct 3 (5:11 AM PDT Oct 2 – 4:39 AM PDT Oct 3; finalized 4:45 AM PDT)

| Server | Hours (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | Oct 2 12:11–16:00 (5:11–9 AM PDT) | 30.5 | 4.3 | 2.8 | 0.32 | 27.8 | 22% | 1574 GiB |
| vy-nebius-1 | Oct 2 16:00–20:00 (9 AM–1 PM PDT) | 32.0 | 2.1 | 1.5 | 0.32 | 30.5 | 24% | 507 GiB |
| vy-nebius-1 | Oct 2 20:00–24:00 (1–5 PM PDT) | 32.0 | 4.5 | 4.0 | 0.57 | 28.0 | 18% | 559 GiB |
| vy-nebius-1 | Oct 3 00:00–04:00 (5–9 PM PDT) | 32.0 | 2.3 | 2.1 | 0.42 | 29.9 | 23% | 768 GiB |
| vy-nebius-1 | Oct 3 04:00–08:00 (9 PM–1 AM PDT) | 32.0 | 4.6 | 4.3 | 2.73 | 27.7 | 27% | 924 GiB |
| vy-nebius-1 | Oct 3 08:00–11:39 (1–4:39 AM PDT) | 29.3 | 11.9 | 10.9 | 8.83 | 18.4 | 17% | 1423 GiB |
| **vy-nebius-1** | **window** | **187.9** | **29.8** | **25.6** | **13.18** | **162.2** | **22%** | **1574 GiB** |
| vy-nebius-2 | Oct 2 12:11–16:00 (5:11–9 AM PDT) | 30.5 | – | 7.0 | 3.30 | 23.5 | 5% | 273 GiB |
| vy-nebius-2 | Oct 2 16:00–20:00 (9 AM–1 PM PDT) | 32.0 | – | 3.4 | 3.17 | 28.6 | 15% | 154 GiB |
| vy-nebius-2 | Oct 2 20:00–24:00 (1–5 PM PDT) | 32.0 | – | 6.1 | 3.52 | 25.9 | 6% | 399 GiB |
| vy-nebius-2 | Oct 3 00:00–04:00 (5–9 PM PDT) | 32.0 | – | 9.0 | 3.61 | 23.0 | 4% | 400 GiB |
| vy-nebius-2 | Oct 3 04:00–08:00 (9 PM–1 AM PDT) | 32.0 | – | 14.4 | 1.82 | 17.6 | 23% | 214 GiB |
| vy-nebius-2 | Oct 3 08:00–11:39 (1–4:39 AM PDT) | 29.3 | – | 14.6 | 1.01 | 14.8 | 29% | 573 GiB |
| **vy-nebius-2** | **window** | **187.9** | **–** | **54.4** | **16.44** | **133.4** | **14%** | **573 GiB** |

**GPU-hours used and idle:**
- Node 1: 26 of 188 GPU-h held or busy, and 162 idle (86%).
  - Kueue allocated 30 GPU-h, now close to what was held (26). The day before, it allocated more than twice what was held.
  - The last block was the busiest: 11 of 29 GPU-h held, and 9 busy. That came from @infra's temporary move of 2 GPUs of quota
    to `provers` (09:08Z to 14:30Z), for memory accounting's HBM check and network accounting's seeds.
- Node 2: 54 of 188 GPU-h held or busy, and 133 idle (71%). Its CPUs were 86% idle.

**Top inefficiencies found, and what was done:**
1. **The disk filled from Commits of unmeasured models.** Six b32 qwen25-3b and yi15-6b Commits took node 1 from 61% to 80% in
   26 min; five were admitted on arrival through the pacer's open gate. #824: one Commit at a time of a model the pacer has no
   size for, with its LocalQueue held while it runs. Live 14:38Z.
2. **CPU quota capped Commits at two.** Leased Commits request up to 16 vCPU each; `deployments-gpu` had 24 plus 8. Its borrowing
   went to 72 vCPU (live 14:25Z), and #830 brought main's `kueue.yaml` in line.
3. **Settings changes never reached the dispatcher loop.** #819: each tick runs fresh. Live about 13:00Z, and confirmed by a
   prover on 160–191 after the 15:00Z revert.
4. **Friction pass (#839, live 18:45Z):**
   - one Job's error no longer stops a tick;
   - the pack pilot uses the pacer's learned bundle sizes;
   - `slot.py`'s skip names `/etc/vy/direct-cpus`.
5. **Slot `d` sat idle, then was lent to provers.**
   - It was blocked by `direct-cpus` and an orphaned lock; I fixed both.
   - A pre-#789 check leaked onto the lent cores; a time-bounded lock holder kept the rest off until 15:00Z.
6. **Circuits' fixes for its own Commits:**
   - A node 2 Commit held a GPU at 0% for two 25-min leases while recomputing its plan; fixed in #840.
   - Overlapping leased Commits pinned more memory than they requested, so circuits is sizing those requests to the real pool.
7. **Node 2's root disk filled with Lean audit scratch, so it refused checks.** @infra freed it to 213 GB at about 06:52Z
   (node2-ops' machine).
8. **The Nebius key leaked a sixth time.** #695 merged at 18:10Z: the key is now read from one line of base64. Daniel's rotation
   is pending.

**Still open:**
- **Feed-bound:** most hours had nothing queued for either node's GPUs. The phi4 and qwen3 TP2 rows came back only once circuits
  had fixed its TP2 staging bug. `gm364` waits on the B8 top-p=1 fix.
- **Node 1's research area swings** about 300 GB an hour (checks' runs and scratch) between cleanups, so the disk moves between
  54% and 64% and the pacer's cap with it.
- **`jobs/cov`** held about 570 GB beyond the bundles the pacer counts (02:40Z).
- **PyYAML isn't in the locked environment,** so `check` skips most dispatch and commit-pack tests.
- **node2-ops has no Slack handle;** asked of @infra.

**Theory lanes launched:** none. The idle time was feed-bound or waiting on fixes in the owning lanes (TP2 staging, B8 top-p=1),
not on open questions.

## Third 24 hours, to 14:00Z Oct 4 (4:39 AM PDT Oct 3 – 7 AM PDT Oct 4; finalized late, 14:45Z)

Due at 13:30Z, but my agent VM was suspended from about 07:13Z to 14:20Z, so no pass ran and this was written afterwards. The
research coordinator's timers stopped over the same span. Source: `art:17d591ed1b4ae0044b2c1a1350c274c3b65a8833f80eabdc11fe743a83e0532c`.

| Server | Hours (UTC) | GPU-h | Kueue-allocated | held or busy | busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | Oct 3 11:39–16:00 (4:39–9 AM PDT) | 34.8 | 10.2 | 9.4 | 8.27 | 25.4 | 23% | 427 GiB |
| vy-nebius-1 | Oct 3 16:00–20:00 (9 AM–1 PM PDT) | 32.0 | 22.3 | 21.2 | 19.18 | 10.8 | 24% | 273 GiB |
| vy-nebius-1 | Oct 3 20:00–24:00 (1–5 PM PDT) | 32.0 | 30.8 | 30.1 | 27.00 | 1.9 | 32% | 389 GiB |
| vy-nebius-1 | Oct 4 00:00–04:00 (5–9 PM PDT) | 32.0 | 31.3 | 30.5 | 27.32 | 1.5 | 32% | 545 GiB |
| vy-nebius-1 | Oct 4 04:00–08:00 (9 PM–1 AM PDT) | 32.0 | 19.5 | 19.1 | 16.13 | 12.9 | 34% | 631 GiB |
| vy-nebius-1 | Oct 4 08:00–12:00 (1–5 AM PDT) | 32.0 | 0.0 | 0.0 | 0.00 | 32.0 | 3% | 99 GiB |
| vy-nebius-1 | Oct 4 12:00–14:00 (5–7 AM PDT) | 16.0 | 0.0 | 0.0 | 0.00 | 16.0 | 1% | 34 GiB |
| **vy-nebius-1** | **window** | **210.8** | **114.1** | **110.3** | **97.90** | **100.5** | **23%** | **631 GiB** |
| vy-nebius-2 | Oct 3 11:39–16:00 (4:39–9 AM PDT) | 34.8 | – | 19.7 | 9.99 | 15.1 | 24% | 538 GiB |
| vy-nebius-2 | Oct 3 16:00–20:00 (9 AM–1 PM PDT) | 32.0 | – | 16.4 | 0.49 | 15.6 | 6% | 842 GiB |
| vy-nebius-2 | Oct 3 20:00–24:00 (1–5 PM PDT) | 32.0 | – | 23.2 | 18.36 | 8.8 | 15% | 555 GiB |
| vy-nebius-2 | Oct 4 00:00–04:00 (5–9 PM PDT) | 32.0 | – | 30.3 | 26.59 | 1.7 | 14% | 272 GiB |
| vy-nebius-2 | Oct 4 04:00–08:00 (9 PM–1 AM PDT) | 32.0 | – | 23.6 | 18.69 | 8.4 | 19% | 394 GiB |
| vy-nebius-2 | Oct 4 08:00–12:00 (1–5 AM PDT) | 32.0 | – | 4.7 | 3.91 | 27.3 | 8% | 546 GiB |
| vy-nebius-2 | Oct 4 12:00–14:00 (5–7 AM PDT) | 16.0 | – | 2.0 | 1.63 | 14.0 | 1% | 28 GiB |
| **vy-nebius-2** | **window** | **210.8** | **–** | **120.0** | **79.66** | **90.8** | **13%** | **842 GiB** |

**GPU-hours used and idle:**
- Node 1: 110 of 211 GPU-h held or busy (52%), 98 of them busy, and 100 idle. The day before, it held 26 of 188.
  - From 16:00Z Oct 3 to 04:00Z Oct 4 nearly every GPU was busy. `provers` had 6 GPUs of quota (15:07Z to 10:30Z) for
    network accounting's non-preemptible trace chunks, run through the GPU pool.
  - The sweep ended at 05:54Z, and @top released node 1 for circuits' GLM work. From 08:00Z to 14:00Z node 1 ran no GPU work,
    and its CPUs were 1–3% busy. No owner-approved GPU work was queued, and Daniel's rule (below) is no filler.
- Node 2: 120 of 211 GPU-h held or busy (57%), 80 busy, and 91 idle. It was busiest 00:00–08:00Z (POUS's research chunks and
  memory accounting's fill and `erase-calib` jobs). It held only 7 GPU-h from 08:00 to 14:00Z.
  - **Busy is undercounted on node 2 when one lease holds all 8 GPUs.** POUS's sampler then records only the lease, with no
    NVML or DCGM query, so those hours read as 0%.
  - That's the 16:00–20:00Z Oct 3 block (16.4 held, 0.49 "busy"): circuits' `circuits-tp8` Match (`match PASS` 17:29Z) and
    Commit (`commit PASS` 19:23Z) were working, not idle.
  - Source: node2-ops, `note:20261004T1715Z-reply-from-node2-ops-wasters-oct4-circuits-tp8-was-match-and-commit`. Its fix,
    `"measured": false` on such records, waits on @infra.

**Top inefficiencies found, and what was done:**
1. **`research/src` grew without bound, so node 1's disk filled.** Every check run ships a source tree of up to 24 GB, and
   nothing pruned them. The disk lost about 300 GB in the hour to 03:11Z.
   - I listed the trees no live process, run or slot used (`art:bd3cf373…`) and escalated at 03:47Z.
   - Root approved deleting them on three conditions: the commit is on origin; no running or queued use; not the only copy.
   - @infra deleted 159 trees (224.7 GB) through `research retention rm` by 04:01Z, and the disk went from 69% to 66%.
2. **Eviction was paused, because it emptied fetched trees under running suites.** #1028 (keep a tree fetched within 24 h) was
   installed by @infra at 03:07Z, and I verified it at 03:11Z: all trees kept.
   - Both eviction units are pinned to main's snapshot (`tool-1028.conf`). Their default, the newest snapshot, could be an
     older branch's code.
3. **Idle GPUs were offered as backfill (my mistake, corrected 06:34Z).** Daniel's rule: GPU work runs only for owner-approved
   items that each name their research question, with no filler. I report idle GPUs and @top routes approved work.
4. **PyYAML wasn't in the locked environment, so `check` skipped the dispatch and commit-pack tests** (day 2's open item).
   #925 fixed it, merged at 14:39Z. Its train surfaced a host leak in the pin tests, which #931 fixed.
5. **Node 1's Lean audits were uncapped.** #947 made `check 2` plus `audit 2` live at 17:20Z.
6. **Kueue drift read "DIFFER" after each quota patch,** because the patch scripts write `nominalQuota` as the number `6`
   while `kueue.yaml` has the string `"6"`.
   - It happened at 14:45Z Oct 3 and again after the 10:30Z revert. I re-applied `kueue.yaml` at 14:30Z Oct 4, and drift
     reads "same".
7. **Steward passes stopped from 07:02Z to 14:26Z** while my agent VM was suspended.
   - Node 1 now runs `vy-steward-watch.timer`, a read-only state line every 15 min to
     `/workspace/verity-guest/steward-watch.jsonl`, flagging disk-72, disk-78 and stale pacer or dispatcher.
   - My passes also have an interval-based fallback timer beside the cron one.

**Still open:**
- **Hourly eviction of `research/src`** is asked of @infra, and #992 (open) has a `src-tree` rule. Until it lands the trees
  grow back: 126 trees and 276 GB at 14:30Z, with the disk at 69%.
- **Node 1's `gpu-lease` is behind main.** It's at `cdcab7126`'s version, while node 2 runs main's; that's @infra's deploy.
- **Feed-bound:** from 08:00Z both nodes sat almost idle, because no owner-approved GPU work was queued.
- **Quota patch scripts write integers,** so every temporary quota move shows as drift until someone re-applies `kueue.yaml`.
- **node2-ops still has no Slack handle.**

**Theory lanes launched:** none. The idle time was feed-bound (approved work ran out), not theory-bound, and the rule is no
filler.

## Evidence

- `art:17d591ed1b4ae0044b2c1a1350c274c3b65a8833f80eabdc11fe743a83e0532c`: 11:39Z Oct 3 – 14:34Z Oct 4, both servers, the
  source of the third 24-hours table.
- `art:bd3cf3736ce1712e2ab208a20eea55ca9868c8fcf48242eaeab4c935654279bd`: node 1's `research/src` cleanup candidates at
  03:20Z Oct 4, with net sizes and the scan script.
- `art:716bbdff08031a6615b0640838fe3a7c5d77eee1a0e403b938d1075314596962`: 12:11Z Oct 2 – 11:39Z Oct 3, both servers, the source
  of the next-24-hours table.
- `art:e928a60a5356cb83407ca00ad60900ec44c91b853023d30672279ecae768d932`: 12:10Z Oct 1 – 12:11Z Oct 2, both servers, the
  source of the last-24-hours table.
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
  - `art:4fcccbc1f4027956cce78e2529ea465979079c912cff815862635d27e921b0f1` (2:50 AM PDT Oct 2)
  - `art:c66263bcfccafc9b20000beb0102115338f692d58ed4e32a0e2b780744fc0a91` (4:45 AM PDT Oct 2)
  - `art:54aa06e7f4a18d69f9836802cff75e55bc0d502ef7408c020c4eb322cac4eaa8` (about 02:00Z Oct 4)
  - `art:7e73e22990487a8d62b893ddc29700c81fc11c8cdbb6aab30c2db2f420ffebdf` (about 03:30Z Oct 4)
  - `art:99e0c0a5963bd2673ccf09b21c7added5cc4799a1b8907f6baca6a2a1194e931` (about 04:35Z Oct 4)
  - `art:0c2f6f604a61703c9e5ed49d7e3c3a3e7e126ba9b63c75bbc7472fd836e85586` (about 06:40Z Oct 4)
  - `art:9c8df68ccd2594bc86537826366a0972e77d0a35ee2058e90e36b58428fb0e12` (about 15:15Z Oct 4)
  - `art:206177f4cae09411bfac4dac40d6ff6b50a8d131563ab911c79c9021d701b0a7` (about 16:40Z Oct 4)
  - `art:a33673c936681a6d553b691ba2ebe02996ef3f179543aece1ea00eb857367b6c` (about 18:45Z Oct 4)
  - `art:d276acd724e0449c9edf5a2935b6032752f7a7d180da6ae60d45956be85f9dc7` (about 19:50Z Oct 4)
  - `art:36e153cae0fc7956e7e365014ca3010d133a64f04bf47cc72e29fe088d68f75d` (about 20:50Z Oct 4)
  - `art:e9fe80bd5c6fc03b31bdc52e47415d6b213c9466f1c07746c2f2a528baf9279f` (about 21:55Z Oct 4)
  - `art:c29ca68baf75f5689fb5cd9cc81e4556d677673e405b00a50d28884f99feb95d` (about 23:20Z Oct 4)
  - `art:b60917a0e01013953ad14e05234a94007469e6939747f09e5bcb9c7e20b62bf9` (about 00:25Z Oct 5)
  - `art:10047c3e01f33e04981b20547abcbcc066a8c25a2d984fd39bcfadd4c5fdbebd` (about 01:50Z Oct 5)
  - `art:610da91933fc0f412a1a8fe383a5a24937cf0c925b49012cb164b17115875f89` (about 02:55Z Oct 5)
  - `art:5f9b6b0a09fe789a8eb8b8bd39c5fc9dc6c45627d185b07656b524ec8f0cb886` (about 03:55Z Oct 5)
  - `art:c4ab2e118332552a9b460866c42d5e36dc601db8ddc7bd4a6df239df9d0918c3` (about 05:20Z Oct 5)
  - `art:dbaa7ad955fe459166f66eb092f2205deb69568c55c2ce3a8744294b4a1b29ac` (about 06:35Z Oct 5)
  - `art:07ad4f0d572195b57b47d55095498db5a4ef311fc496d5e180c3071981528f8b` (about 08:00Z Oct 5)
  - `art:b7b5f42f92bad3accc980033d38d464523603299efc107557145f5244598622f` (about 09:35Z Oct 5)
  - `art:b7ef95b9686c921f91a8fd2e9d8b46e05aa5f1960ffd9fb40105354460d15633` (about 11:15Z Oct 5)
  - `art:66aa3193434e12c60df3b24c825df60112758fc74ada794ce2dc589d5ead04b9` (about 12:50Z Oct 5)
  - `art:4d7dc3623d24a7033724270de12008588ab8ea316f08cbe96b2201bec41907a4` (about 14:25Z Oct 5)
  - `art:87ad458070a151621c462e81c38f11199d24c4b94cf982596790d0d2cfebbfb6` (about 15:50Z Oct 5)
  - `art:fbc01e5df457939fc749b011916cbb635eb30f89e4f94bea90a93fee7997b281` (about 17:25Z Oct 5)
  - `art:74d4a676ec0b62114f784606d12d73dc0bb8be7e3ade610294fa0e9dd4c9d0ea` (about 18:50Z Oct 5)
  - `art:83a145c45e097f2f60b69b6fb90ba0e595afe7da8238d71c40a5530a66d65853` (about 20:20Z Oct 5)
  - `art:88d775cce9a4444a3a2cfe25e61364e10b27630ac9d83c6a656f04304f5e2cd1` (about 21:55Z Oct 5)
  - `art:cc609351e836511c83cb7f2a3fbae9350e6eb006013c76bcda712ba598fe2f0b` (about 00:20Z Oct 6; the 23:32Z hourly failed
    on a node 2 read timeout, since fixed)
  - `art:c078194b5b6eb21ffd6cd3f6ee62581a427bb513bb7ef3c8b1e2505ed573fad5` (about 01:10Z Oct 6; the loop's first hourly
    with the fix)
  - `art:36041b8e11cd9385e0d988b9ddba2d73c2f77bc37df76441f71d3a99336df8f5` (about 02:30Z Oct 6)
  - `art:7bad833da704d9a87edb4e255783665fe00b4dfc76681e740eb88bf425424ba8` (about 03:55Z Oct 6)
  - `art:dfdefd19d058576dad226da138a32dad4fcc094a6a571787aef3329a34152250` (about 05:30Z Oct 6)
  - `art:6bd762df407abe6bedb3e8ef24b47f44c0a4b3736239e2b66a0c9e6b9e5841f1` (about 07:05Z Oct 6)
  - `art:80559fcc69b85bfc00bf57343a0a0a18414d9a3a6684dbbad33f9b93fafa0dc9` (about 08:35Z Oct 6)
  - `art:d9568d020609237c591779bf536bc75af53e934bfaeb3b029d86be316f6d1c13` (about 10:01Z Oct 6)
  - `art:918b96009fad3b6c0a8bdc89e88fb5c5246ac84fe28f05c37fc40558b23cf060` (about 11:37Z Oct 6)
  - `art:bba10bb5a29d18b9faebc5a1e71f23832ab08038561b0d1d359a36e2f47845a9` (about 13:30Z Oct 6)
  - `art:5358bd51cc59aa29ab34cc78fdc1222418d6a32d63da4cd6afeb826f86a3a0f6` (about 15:00Z Oct 6)
  - `art:7b88bd2f3d6143d4391e8651bfaca49f6aafd1fac6a8e5336f60a237fb340aac` (about 16:45Z Oct 6; run by hand after the
    loop's 16:28Z hourly failed on a node 2 ssh error)
  - `art:6efd165e5380feecfcfef8bbf8aea966c5f92a8cc1195f9ae5af3f409f0d5bba` (about 18:10Z Oct 6)
  - `art:decf363676d65ac67d1aa7c3c2fdc75667785266bd5d9ef2e3ed229a3e0acf43` (about 19:50Z Oct 6)
  - `art:40630b0708982efe7ac90d3761bdfca948cda55705e64847c97f1dfbf133ff3e` (about 21:30Z Oct 6)
  - `art:b0df0ace503328aff610ea21be583be83732e4c9bcd10e451512044091aefd40` (about 23:15Z Oct 6)
  - `art:528cdaca22954bf0055dacbf994b0c3612d5b01ce8d05dcbae34ef9b2a6d66bf` (about 00:55Z Oct 7)
  - `art:d80061e4dba92eea1628668bd553a457f6499ed18b721ee6bf5729870aba9871` (about 02:25Z Oct 7)
  - `art:fdaadf9a1a79f0c18b5bd625e2183874e6b5f2aa799c13bad0dcc61b0248b439` (about 04:00Z Oct 7)
  - `art:2d603fcc0ccf985257173aca63ce7eb845b8e595e6f40f9d96b24b10cc8beda7` (about 06:00Z Oct 7)
  - `art:3eace3e328963c27d84504569fd26979a9a3da3b19089bce9397511ff8a5eb48` (about 07:20Z Oct 7)
  - `art:c3315559b6e7551db73091708defc9a8fbbcad39a3a9c5d0d30cf83aa3812736` (about 09:05Z Oct 7)
  - `art:ba3e45f7cd5a1bef502ab80df32e939f624bbe883b9f2eb21944fca9e1595cad` (about 10:45Z Oct 7)
  - `art:e2ff41f78645fdb6aedd17a80e0bcdec5e89a21263b2335073989cbe09974494` (about 12:20Z Oct 7)
  - `art:79b0a41dc55b050a6f24f615a9c944baa1a5adfe85fb14be49ed9005e5c8c30c` (about 14:10Z Oct 7; the last before both
    nodes stopped at their 15:00Z deadline, and the best pre-stop record)
  - `art:686a1c7f6ff30be35a8ab1ac61388b39600317b7d0a4be183f618f8e8958602c` (about 16:50Z Oct 7, after both came back with
    a new deadline of 2026-10-14T15:00Z). It reads node 1 at 1,410 / 323 / 167 / 1,087 and node 2 at 1,412 / 462 / 266 /
    951 (observed / held or busy / busy / idle). Node 1's totals are about 5 GPU-h *below* the 14:10Z snapshot, so some of
    its sampler history before the stop is missing. Running totals below stay on `art:79b0a41d…` until a later snapshot
    passes them.
  - `art:1e85ba289fdcd210f55e60b95f391b8705824fd8fc0695fa5cf61581b2d35c9a` (about 18:15Z Oct 7, the latest). Node 1:
    1,421 observed, 323 held or busy, 167 busy, 1,098 idle. Observed has passed the pre-stop snapshot, but held or busy
    and busy are still about 2 GPU-h below `art:79b0a41d…` (the lost sampler history). Node 2: 1,412 / 462 / 266 / 951,
    the same as at 16:50Z: its GPU sampler (`pouw-infra-util`) hasn't run since the restart, so its totals are frozen at
    the 14:55Z stop.
  - `art:1b53303089a6036b95082f847c281f7e8965a7d9d01650c1fe00b91e6c24272d` (about 20:05Z Oct 7, the latest).
    - Node 1: 1,436 observed, 323 held or busy, 167 busy, 1,113 idle (no GPU work since the restart).
    - Node 2: 1,425 / 462 / 266 / 963. It advances again since its sampler restarted at 18:36Z, with a hole from 14:55 to
      18:36Z that includes its 14:55–16:42Z stop.
- **Running totals, Sep 30 05:16Z to about 14:10Z Oct 7** (from `art:79b0a41d…`, the pre-stop record; later snapshots
  undercount node 1's held and busy hours by about 2 GPU-h and don't advance node 2):
  - Node 1: 1,415 GPU-h observed, 325 held or busy, 169 busy, 1,090 idle. Held or busy barely moved from about 11:53Z
    Oct 6 to 02:31Z Oct 7. Since then it's mostly circuits' 8-GPU Qwen-235B load-time variants (02:31Z on), held mostly
    through load and little of it busy, plus network-accounting's 1-GPU `active_live_cells` lease on GPU 4 from 05:44Z.
  - Node 2: 1,406 GPU-h observed, 462 held or busy, 266 busy, 944 idle.
  - From about 00:00Z Oct 4 into Oct 5 both servers had all 8 GPUs allocated (node 1: 8 provers in Kueue; node 2: 8 jobs
    from its cluster agent). Since about midday Oct 6 both have run mostly idle: node 1 with 0–1 GPU in use apart from
    circuits' load-time runs, node 2 with 1 fill job.
- **Working files in this folder:** `backlog.md` (the CPU map and fills), and `tools/` (`channel_sync.py`, `util_collect.py`,
  `drift_check.py`).
