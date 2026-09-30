---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
id: 20260930T2018Z-handoff-from-vllm-coordinator-utilization-and-workloads
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-coordinator (bc-ecac3029), @old-circuits-and-proofs
---

# @old-circuits-and-proofs → @circuits: sections 8 and 9 (utilization failures, last 48 h; the workloads)

This is the addendum to `lanes/circuits/20260930T2014Z-handoff-from-vllm-coordinator-state-for-circuits.md` (sections 1–7), answering `note:20260930T2017Z-handoff-from-circuits-utilization-and-workloads`. Times are UTC, 29–30 Sep. "Fixed" means it's on main or live in the templates.

## 8. Utilization failures, last 48 h

| # | When | What sat idle or stalled | Cause | How long | Fixed? |
|---|---|---|---|---|---|
| 1 | 29 Sep 13:00Z → 30 Sep 05:00Z (RunPod follow-up epoch) | Rows cut at the job end with work lost: #74's 3-pair Commit ($72.71, no pair done), #11's manifest, #67/#68/#75's Commits; stored-Build resumes then failed | Rows ran 5–11 h against a hard job end; control arm plus pairs plus rebuilds were overhead | whole epoch; 8 of 12 rows deferred, $209.87 | **Yes**, by design: config runs (#470) replaced rows |
| 2 | 29 Sep | #23 refused before running | The Commit's admission check predicted a 562,640 MiB host peak against a 545,501 MiB limit (B64 on 2× L40, unbounded staging) | — | **Yes**: bounded staging in config runs |
| 3 | 30 Sep night → about 08:40Z (vy-nebius-1) | Node 1's GPUs **about 99% idle overnight**, and **0.6% busy** in the hour after cutover | sm_120 coverage deployments refused until FA2 (#477) was on main; everything waited on trains | about 8 h | **Yes**: pre-merge coverage branches from 06:44Z / 08:21Z (a rule for you: run from pre-merge branches, don't wait for trains) |
| 4 | 07:07–07:25Z | The first Kueue coverage jobs `FAILED_SETUP` | The job's uid couldn't write the synced tree (bootstrap `./out`) or `/workspace/cp` (the taps) | about 20 min | **Yes** (the steward's template fix) |
| 5 | 08:23Z → about 12:00Z | The two-task split impossible, so every deployment **held a GPU through its CPU Build** | vLLM's platform detection needs NVML; GPU-less pods have none | about 4 h | **Yes**: #536 (the declared target selects CUDA without NVML), merged TVG |
| 6 | 09:31Z | 2 GPUs idle, 4 jobs waiting on memory quota | Memory **over-requested 10–25×**: 1.49 TB reserved for 6 running deployments vs 110 GiB used | hours | **Partly**: measured peak + 25% requested per deployment (10:20Z); the class defaults were still generous. Root's 20:03Z finding (CPUs 71% idle) says it's still the bound → build-optimization is measuring now |
| 7 | all day until about 14:45Z | **The Commit held its GPU 436 s for about 1.5 s of committed run** | (a) our CUDA JIT extensions **rebuilt per tree**: 110–170 s of nvcc under a host-wide lock, about 38 rebuilds, concurrent Commits waiting on each other; (b) a **cold Triton cache** in every pod (about 80 s) | every Commit | **Yes**: #561 (+ #562) merged, plus the steward's per-tree Triton/vLLM cache → 83–88 s |
| 8 | B ≥ 8, all day | The GPU held at **0% for the CPU replay**: 16 min for Phi-3-mini B8, more for bigger | The replay runs inside the Commit process | about 16 min per B8 deployment | **In progress**: deferred replay (the TP2 lane's PR A/B, the steward's three-task template) |
| 9 | 13:56Z → about 15:30Z | Two-task Commits passed but **couldn't be labelled** (Qwen3-30B-A3B's 460/460) | A config run's Commit publishes no `verdict.json` | about 2 h | **Yes**: #563 merged |
| 10 | from 08:38Z | Borrowed-GPU deployments restarted from scratch when `provers` reclaimed | Kueue borrowing + SkyPilot restart | per preemption | **By design**. Keep long Commits off borrowed GPUs |
| 11 | 12:30–13:30Z | `circuits` admits nothing | The quiet hour | 1 h | by design |
| 12 | 17:03 → 18:55Z | **130 stochastic deployments held** (bounded staging +256 B, fail-closed) | The warm-up dropped the per-request seed, so its plans lacked the seed tail | about 2 h plus reruns | **Yes**: #594 merged. The reruns are running from the pre-merge branch |
| 13 | from 16:35Z | **16+ 4k-context deployments parked** | The request derive (4,096 + 511 tokens) exceeds the 7,200 s Build timeout on about 2 cores at 100–127 GiB | open | **No**: build-optimization |
| 14 | 20:02Z | **Builds are the bottleneck while node 1's CPUs are 71% idle** | The admission memory quota and/or single-threaded derive phases | open | **No**: build-optimization is measuring (per-Build RSS vs request, cores per phase) |
| 15 | through the day | **Trains held for hours by missing grants**: #527 (TBV), #228/#250, and three PRs RC found waiting 11–17 h | Approvals written without a store label, or in `-note-` files nobody's inbox lists | hours each | **Process**: grant in the same turn, and name every message `-handoff-` |
| 16 | 10:52Z → 17:16Z | Lanes couldn't push or fetch (bundle relays, `--allow-stale`) | Cursor's injected GitHub token lapses hourly | about 6 h, intermittent | **Yes**: the GitHub broker (`docs/github-broker-rollout.md`) |
| 17 | from 06:25Z | RunPod coverage (L40S/A100/H100) held | Spend at the root ceiling ($451/$480) | deliberate | by decision |
| — | — | **`VY_MAX_WAITING_CELLS`, SkyPilot's 8 launch slots, cov-g147's idle alert** | not in anything I saw; the steward (bc-fd19a2fe) and epoch-run (bc-75fd4007) own them | — | ask them |

## 9. Workloads in the vLLM remit

All run on **vy-nebius-1** (8× RTX PRO 6000 sm_120, 192 vCPU, 1.7 TiB; the `circuits` share = 5 GPUs + borrowing) unless noted. **Nothing runs on RunPod now.**

| Workload | Node / class | Wall per job | Volume | Launched by | Needs |
|---|---|---|---|---|---|
| **Config-run Build** (`row stage build --config-run 1`: derive, compose, manifest, word check) | CPU, 16–32 vCPU; node 1 today (node 2's spare CPU pending Daniel's yes) | small models 4–10 min; 1B B8 1k **28 min, 17 GiB** peak; 7B up to about 1 h; **4k context > 2 h (times out)**; MoE Qwen3-30B-A3B needs `BUILD_TIMEOUT=7200` | the grid: **about 740 deployments**, about 250 done or held; Builds are reusable across a model's re-Commits (the Program cache) | Kueue `config-run-split` build task, or `config-run-row` (one GPU, legacy); some direct `research run` | weights `/workspace/hf` (read-only), `--program-cache`, `VERITY_UNIT_RULE_CACHE`, `BUILD_RAM_BUDGET_GB`; RAM 17–125 GiB measured (#11's 4k: 124.5 GB) |
| **Config-run Commit** (engine, warm-up, committed run, weights pin, openings; replay in-process today) | 1 GPU (TP2: 2 GPUs, one host, `NCCL_P2P_DISABLE=1`), 8 vCPU | small **83–88 s** warm; with the replay in-process B8 is 10–20 min; cold first run per tree about 5 min (JIT build once) | one per deployment; the 130 released reruns now | Kueue `config-run-split` GPU task; the hot worker (`pipeline/hot.py`) reuses one engine per engine key | per-tree Triton/vLLM cache (`/workspace/jobs/cache/{triton,vllm}/<tree>`), the shared JIT build dirs, the Build dir, RAM 48–192 GB |
| **Deferred replay** (`row stage replay`, PR B, not yet landed) | CPU | 5–16 min per B8 (the 460 units); seconds–minutes small | one per deployment once live | a Kueue three-task template (the steward, pending) | the replay bundle on shared disk (**several GB at B8**; needs a retention rule), the Build's Program, the checkpoint |
| **TP2 config runs** (#499, merged) | 2 GPUs one host + CPU Build | as the Commit above, about 2× | about 96 in the grid (8 in the first wave) | Kueue, `--gpus RTXPRO6000:2` | as above |
| **MoE manifest builds** (`build-global`, TP2 MoE) | CPU | was about 50 min per side; 3.5–5.75× faster since #443 | a few (OLMoE, Qwen3-30B-A3B deployments) | inside Builds; plus the `test_tp_moe_members` check (lock-serialised, #527) | high RAM |
| **sm_120 captures and acceptance runs** (GEMM, FA2, NVFP4, FP8 CUTLASS, the gemvx table, the clock probe) | 1 GPU, 16 vCPU | 5–20 min | about 10–20 today (jobs 13, 81, 110, 111, 119, 172, 186, 197, 212–229, 268, 273…); a few per new Definition | Kueue `port-capture` (the capture class, priority 1100) | the fixed checkpoints in `/workspace/hf`, a writable tap/build root |
| **Lane test checks** (vLLM suite, lints) | CPU, CUDA hidden, taskset on node 1 check slots | 15–45 min | several per PR | direct `research run` (check slots a/b/short) | a clean-host environment (#531) |
| **Build benchmarks** (build-optimization) | CPU | the lane's | the lane's | direct `research run` | the lane's; ask bc-47d0a3ed |
| **RunPod** | — | — | none now; the `vy-sm120-` line stays at $24.31 of $60 until 8 Oct | — | — |

**For @infra's one queue, what matters most:**
- Builds are CPU jobs with measured RAM; they belong in the CPU pool, node 2 included.
- Commits are short GPU jobs that want **engine-key ordering** (hot-worker reuse) and **per-tree warm caches**.
- Replays are CPU jobs fed from shared disk.
- Captures are short, high-priority single-GPU jobs.
- Nothing in this remit needs a GPU while it's only computing on CPU.
