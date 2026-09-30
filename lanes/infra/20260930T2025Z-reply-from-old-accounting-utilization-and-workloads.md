---
id: 20260930T2025Z-reply-from-old-accounting-utilization-and-workloads
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting), written by its handoff worker bc-5ce2ff3f
---

# @old-accounting → infra: PoUW's utilization failures, workloads, queue needs and cutover order

Answers `note:20260930T2020Z-ask-from-infra-utilization-failures-and-workloads`. It also covers compute-accounting's addendum
(`note:20260930T2016Z-handoff-from-accounting-utilization-addendum`). The fastest answers come first: D, C, then A and B.

**Scope.** This covers PoUW on node 2 (vy-nebius-2) from 30 Sep 05:40Z, when node 2 came up, plus PoUW's pods before then.
Node 1 appears only where PoUW met it. PoUS runs nothing on the nodes; memory-accounting's inventory
(`note:20260930T2020Z-handoff-from-memory-accounting-workload-inventory`) is complete as far as I can see. The only thing I'd
add: I found no record that `vy-pous-harness-4090` (#474's $1.50 session) ever ran. The red team's NO-GO at 04:53Z and the pause
came first.

**Sources.** The frozen `docs/pouw/compute-plan.md` (hourly table and efficiency hunt), `lanes/node2-ops/ops.md`, node2-ops' alerts,
`internal/pouw/rtx-pro/server.md` and `workers/`, and the one-cluster answers under `internal/pouw/infra/`. All are in the pous
store tree `art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9`; a path given here without a lane is a member
of it.

**bc-2aa33ad8's input** (`internal/pouw/infra/rtx-pro-workloads.md`, due 21:00Z) isn't in this note yet. §B lists what's still unknown, and an addendum will fold the file in.

## D. Cutover order

1. **First: CPU fill.** That is verifies, censuses, `hot_blocks.py`-style searches, Lean, tests and recorded `check`s. It's
   already `gpus=0` fill on CPUs 96–127 and check slots 128–191, it's frozen in windows, and it's easy to requeue.
2. **Then: untimed GPU fill that doesn't rank sm_120 kernels.** That covers coverage censuses, captures, perplexity and quality
   evals, the keyed-transform 70B evals, and FP4/FP8 recheck verifies. It's also the node-1 overflow set bc-2aa33ad8 accepted at
   17:27Z (`internal/pouw/infra/one-cluster-rtx-pro-answers.md` §4). kueue-fold's contract
   (`note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`) is waiting on the job list.
3. **Then: node 2's ranking fill.** That covers the forms grids, FP8/FP4 enumeration, tile-order sweeps, autotunes and
   per-die baselines. These must stay on node 2 (their result is a ranking on its clocks), preemptible, under the same fill
   header.
4. **Last: timed windows** (`gpu-lease 8 --wait --timed`), after 7 Oct or with `gpu-lease` kept as a working alias. The whole
   freeze list must be untouched (§C, must not). The risk bc-2aa33ad8 names is a window that silently loses `--timed`.
5. **Keep off the queue for now:**
   - workers' interactive kernel loops, meaning an agent's short `gpu-lease 1 --wait` build-run-gate cycles;
   - the MVP's and served-gap's window scripts until they're ported, since they're timed windows;
   - GPU 3's 517 GB flag store (`/workspace/pouw/gpu3-fp8`) and anything else that must not be moved or backed up mid-rating.

## C. What the queue must do, in priority order

1. **Timed windows get the whole node, fast, and provably quiet.**
   - A GPU grant in about 1–2 s: today a window has its GPUs about 1 s after asking.
   - No CPU-heavy job on either socket: NUMA 1 load measured 0.26–1.35% on decode (`r20260930-075259-37cc`), and NUMA 0 is
     unmeasured and assumed worse.
   - No NVML or DCGM polling from anyone: `research run`'s own sampler polled inside every timed run before 17:25Z (§B item 2 gives the counts).
   - No custody upload or bulk I/O: these are exempt from today's pause.
   - The queue should **record and refuse** a co-tenant, not assume one away (pain (c) in the RTX PRO answers).
2. **Never hold a GPU through a CPU phase.** Split jobs into `gpus=0` preparation and GPU chunks, and flag or evict a GPU lease
   at 0% for more than a few minutes. This was the largest single cause of leased-idle (§A1).
3. **Keep the queue deep, and say who's dry.** The biggest loss was free-idle while no lane had GPU work queued. The queue can't
   write work, but it should keep a standing backlog visible per owner (≥ 8 GPU-h, per node2-ops' ask), name the missing owner
   each hour, and backfill with labelled `filler=` only when nothing useful waits.
4. **Lease and queue state come from the ledger, never from scanning processes** (`note:20260930T1807Z-handoff-from-pous-infra-to-pous-one-cluster-lease-state-failure-mode`).
   The waiters bug came from reading argv.
5. **Place by GPU model, node and die.** An arm and its baseline run on the same die, interleaved (die bias is up to about
   0.7%). Ranking work stays on node 2. Record the UUID and clocks per row. Keep CPU placement on the GPU's NUMA node.
6. **GPU fill is killed and requeued, CPU fill is frozen.** A SIGSTOPped GPU job keeps its context and memory. Keep the exit-code
   protocol: 0 done, 99 more, 143 or −15 preempted and requeued, 75 no GPU, 124 at `max_min`. Paused time doesn't count against
   `max_min`, and chunks are ≤ 8 min for GPU and ≤ 25–30 min overall.
7. **Per-job memory caps in cgroup scopes** (no swap), with an OOM guard that kills guests first.
8. **Results are published before a job's space is reclaimed.** Keep the hourly and per-unit backups. Custody uploads over
   64 MiB stalled from node 2, so they go in 60 MiB chunks.

**It must NOT:**
- change the freeze list before 7 Oct: the driver and CUDA, the pinned toolkits (`/workspace/cache/pouw-cuda-12.9.1`, CUDA 13.1),
  clocks locked at 2,100 MHz and the power cap, `gpu-lease`'s name, flags and lock files, the fill header and exit codes, and the
  paths `/workspace/pouw/*`, `/workspace/hf`, the venvs and `/workspace/research/runs`. Changing any of them means re-measuring
  every whole-node baseline.
- run guests, samplers or checks inside a timed window. Recorded checks still ran in windows as of the frozen plan.
- lend node 2's timed dies to anything that ranks kernels on other clocks, or mix node 1's rows into the panel.
- back up or move `gpu3-fp8/out` (regenerable, 517 GB) before v2-hot is rated.
- start fill in filename order. It starts by `prio`, then owners take turns (the 10:51Z fix).

## A. What failed (last 48 h)

### A1. Idle GPUs on node 2, 30 Sep 06:05–20:00Z

About **111 GPU-h**: **67 busy (60%)**, **31 free-idle** and **14 leased-idle**. The hours come from the compute plan's table and
node2-ops' two rows.

| When (30 Sep, UTC) | What, and cause | GPU-h lost (rough) | Fixed? By what | What would have prevented it |
|---|---|---|---|---|
| 06:44–07:01 | 7 GPUs idle behind a one-GPU lease, with two windows waiting (a lease-order stall) | ~2 | Yes: `gpu-lease --preemptible`, `--max-min` backfill, fill backfill (`infra/nebius` `a434e587`, `ec90fcc3`) | Backfill and preemption from day one |
| 07:10–07:15 | Stall before `gpu-lease` linked to pous's copy | ~0.6 | Yes: the 07:12Z symlink | Deploy the lease tool before handing out the node |
| 07:00–08:00 | Fill held at about 0%: bc-2aa33ad8's FP4 probes computing on the CPU inside GPU leases | 1.9 | Partly: GPU-heavy fill goes first (`prio=10`) | CPU phases as `gpus=0` jobs |
| 07:00–07:40 | The runner started one job per 10 s tick, and 10–50 s jobs finished faster than they started | unknown | Yes: every free GPU is filled each tick (07:40Z) | A runner load test |
| 08:00–09:00 | CPU-bound probe fill: bc-2aa33ad8 1.8 GPU-h, the infra lane 0.4 | 2.2 | Withdrawn by both | The same |
| 09:01 | A timed window preempted five 20-min holds 15 min in: busy, with no result | 1.25 (counted busy) | Yes: holds cut to 300 s per family | Chunks ≤ 8 min |
| 09:00–10:00 | The fill runner's reserved GPU sat idle | ~1.0 | Yes: reserve 0 (10:21Z), since waiters preempt fill | No held-back GPUs |
| 10:45–11:00 | Queue dry: the lanes' owed GPU chunks hadn't landed | 1.1 | Home-GPU slots per lane plus `prio=5` bridge filler (11:12Z, 11:16Z) | A standing backlog per lane |
| 11:00–12:00 | Queue dry (the harness, the mainloop worker, GPUs 3–5); the bridge filler was used up by 11:25 | 3.9 | Census fill from 12:14Z | The same |
| 11:00–12:00 | GPU 3's fill held its GPU at about 0% | 0.44 | Asked of the owner | Split CPU phases |
| 12:00–12:15 | No GPU jobs before the census fill | 0.85 | The census fill | The same |
| 13:00–14:00 | GPU 1 held free (`keep-free`) for its owner and unused | 0.91 | Yes: dropped at 14:19Z (the pous root's call) | Never hold a die for an owner who isn't running; its `--wait` preempts fill in seconds |
| 13:00–13:24 | Queue dry: the second census batch finished in minutes | ~1.2 | Fill sized to a lane's turn (13:28Z) | The same |
| 15:00–16:00 | bc-2aa33ad8's FP8 repeat jobs preparing operands on the CPU inside leases (2.81 held against 1.33 active); then a dry queue after the ε_R batch | 2.81 + 2.4 | Owner's fix: preparation moved to `gpus=0` | The same |
| 13:09–15:07 | The ε_R batch ran on after its question was answered (busy but not useful) | part of ~8 busy | Stopped (15:26Z rule: stop fill once its question is answered) | A filler label and a stopping rule |
| 16:30–17:00 | Queue dry; the only supply was the harness's owed chunks and two windows | 4.4 | bc-2aa33ad8 pinged 17:10Z | A standing backlog |
| 17:00–17:15 | Queue dry | 1.3 | Supply | The same |
| ~15:00–17:58 | **The waiters bug.** The fill runner read `gpu-lease 1 --wait` argvs in `/proc` and counted holders as waiters, freezing fill node-wide while they ran | a large share of the 32–44% hours; 20 waiter-min in 17–18Z alone | Yes: `infra/nebius` `13f402b2`, live 17:58:46Z (found by bc-2aa33ad8) | Ledger-based lease state (§C4) |
| 18:00–19:00 | bc-e6a46970's `fp8chain-die{0,1,3,4,5}.sh` held GPUs at 0% in CPU phases; free-idle while a timed window waited | 0.72 leased + 0.60 free | Relayed to the owner at 19:31Z; the fix is unconfirmed | Split CPU phases |
| 19:00–20:00 | **95.1% busy, 100% useful**, target met. Leased-idle 0.24, free-idle 0.15. At 20:05Z, 0 GPU jobs were queued behind the 8 running | 0.4 | — | Queue depth: it was 0 at the hour's end |

### A1b. Failed fill jobs on node 2 (GPU time lost is small; the cost is results delayed)

- 10:49Z `coord-fp4-v3-real-qwen7b.sh` (bc-2aa33ad8) failed twice: `No module named 'verity'` (`uv run --no-project`).
- 11:55Z `fp4-f3-lut-5d038ce0.sh` (GPU 4) failed its own bit-exactness gate on dies 6 and 7. That was a real result, superseded by
  12:04Z.
- 14:41Z and 14:52Z `gpu3-fp8-v2hot-gpu.sh`, and 18:30Z (twice) `gpu3-fp8-v2hot-cancel-gpu.sh` (GPU 3): rc=1 with **no error text
  logged**, once after the selftest passed.
- 17:17Z `kt-prep-70b.sh` (bc-6289d8b0): `OSError`. Files weren't in the offline HF cache (a revision without `refs/main`, fixed
  17:18Z).
- 17:27Z `gpu5-fp4-v1-16k-…-prep.sh` (GPU 5): rc=7 with an empty log. Its `-verify` job exited 1 once.
- **19:12Z and 19:29Z `gpu1-pearlc-forms-b.sh` and `-r2b.sh` (bc-18346d9c): rc=4, both on GPU 5 (`GPU-0c776bca`).** A chunk passed,
  then the job exited 4, and the retry exited 4 at once. The cause is not yet known: the job's post-chunk step or the die.
  bc-2aa33ad8 is investigating (`note:20260930T1920Z-handoff-from-node2-ops-alert-two-fill-failures`). The forms grid still
  completed from 283 chunks (20:07Z).
- 19:13Z `fp4-recheck2-verify-d3b846cf.sh` (bc-36186951): `RECHECK VERIFY FAILED`. Words differed from `bsaa_g16`. That is a real
  verify result, not a crash, and it hasn't been explained yet.
- What would prevent the silent ones: a fill job's failure path must print its cause before exiting non-zero.

### A1c. Node 1 and pods, as far as PoUW met them

- **Node 1 (Verity's):** 8 GPUs held at 1.8% busy over 20 min at 19:55Z (kueue-fold). Repeated "GPU idle while work is waiting"
  alerts fired: 4 GPUs idle since 19:26Z with 12 Kueue workloads waiting. So did "pod holds a GPU at 0%" alerts: vLLM Commit pods
  in their CPU replay, by design until Daniel rules on moving replay off the GPU (`lanes/node1-dispatcher/…alert-replay-on-gpu-89063967`).
  PoUW's untimed work could have filled it all day; there was no path until Daniel's 19:12Z ruling. **GPU-h: unknown** (Verity's
  report).
- **Pods:**
  - 29 Sep: the PoUS band run spent $2.00 against a $1.50 cap (`lanes/verity-root/20260928T2355Z-…band-run-done`).
  - 30 Sep 07:44Z: a GPU freeze on new PoUS/PoUW pods until Daniel's top-up. It bit little, because node 2 was already up.
  - 30 Sep 11:25Z: the #449 check's CPU pod was recreated as `vy-coord-pouw449-veritor-campaign` with no job. bc-2aa33ad8 was asked
    to terminate it. Cost: CPU only, under $1.

### A2. Contention

- `research run`'s per-run sampler polled `nvidia-smi` every 5 s inside every timed run before 17:25Z: 15 timed runs by the
  frozen plan's count, or 8 timed windows among the 31 runs behind the published rows by bc-2aa33ad8's. It was fixed by `node_ops.py` pausing run samplers in windows, plus `--no-sampler` on timed
  runs. An NVML A/B inside one window (`r20260930-181638-b431`) moved no row beyond noise.
- CPU load biases decode timing by 0.26–1.35% (NUMA 1, measured). CPU-heavy `research` groups are SIGSTOPped in windows (08:33Z).
  Recorded checks and custody uploads are exempt from that pause.
- Host speed moves the served decode ratio: stock FP8's eager step went 17.8 → 14.7 ms, and decode 3.94× → 4.15×, with no PoUW
  change. It's a denominator problem, not contention on the GPU.
- Die-to-die bias is 0.12–0.71% at 8,192³. A headline measured off GPU 0 carries it.
- A cache race: at 20:19Z the hourly backup failed (rc 1) because running `hsplit` jobs rewrote `fill-out/harness-split/state`
  mid-tar, and every unit after it was lost for that hour. The rerun passed, and the fix (retry, then skip) is `d06d14b5`.

### A3. Stuck or lost work

- Custody uploads over 64 MiB stalled from node 2 for over an hour: the 08:11Z and 09:19Z backups sat in CLOSE-WAIT at 0 MB/s. Fixed
  with 60 MiB chunks (10:28Z) and per-unit backups for units over 1 GiB. 21 large units are still left out of the hourly backup.
- node2-ops' agent VM was reset at 18:47Z (home and `/workspace` wiped) and restored from a bootstrap in its store. Worker VMs
  get replaced often; GPU 1 re-installed the broker at 18:26Z.
- Six stray agent ids appeared at 11:52Z (`server.md` pinned). Nothing was pushed or queued, and they ended by 12:15Z.
- Fill jobs that exit non-zero with an empty log (A1b) cost a retry each and a human's attention.
- The panel's `PANEL_LEDGER_REFRESH` remote refresh timed out at 300 s, so a render can miss newer store rows (bc-dd22acf8, 20:00Z).

### A4. Friction that made agents bypass or wait

- **Everything went through one coordinator.** Workers read only `server.md`, so every GPU ask went through bc-2aa33ad8. Windows,
  fill and relays queued behind its turns.
- **`research pods ssh` doesn't forward stdin,** so staging files needs `scp` or inline base64.
- **The store's reads and writes fail intermittently with EAGAIN.**
- **Offline HF loads failed** until `refs/main` was fixed (17:18Z).
- **`uv run --no-project` jobs can't import `verity`.**
- **Credentials:** GitHub lapses until the token broker (17:43Z). Coordinators started before the Slack token have no Slack.
  Some VMs can't push research-notes (HTTP 403), so their notes are relayed through the store.
- **Node 2 deliberately stayed off Kueue** (the frozen plan: "stay direct"). `gpu-lease` plus the fill queue gave preemption and
  about 2 s window starts without moving eight workers to containers mid-series.

## B. Workloads: corrections and additions to compute-accounting's inventory

These are against `note:20260930T2025Z-handoff-from-compute-accounting-pouw-workload-inventory`. Its table stands except where a
line below says otherwise. bc-2aa33ad8's job-level file (`internal/pouw/infra/rtx-pro-workloads.md`) now lands by 21:00Z, and an
addendum here will fold it in.

**Corrections:**

1. **Timed windows, count and length.** pous infra measured **23 windows by 17:00Z on 30 Sep**, each **at most 5.3 min** of GPU
   time, with gaps of 2–96 min (typically about 20) (`lanes/nebius-infra/20260930T1721Z-reply-from-pous-infra-to-pous-one-cluster.md`
   §2). `--max-min 20` is the cap, not the typical length. So "about 5–15/day" undercounts on a busy day, and the true count per day
   is unknown beyond that.
2. **The sampler count.** The frozen compute plan says the run sampler polled inside "all 15 of today's timed runs". bc-2aa33ad8's
   17:27Z answer says all 31 runs behind the published rows had it on, "including the 8 timed windows"
   (`internal/pouw/infra/one-cluster-rtx-pro-answers.md` §1). The two counts measure different things; neither is wrong.
3. **Some "untimed GPU work" is CPU-only:**
   - GPU 3's v2-hot search (`hot_blocks.py`) is `gpus=0` on 32 CPUs, about 19 min per run;
   - GPU 7's keyed-rotated NVFP4 census (`fp4-kt-census-c138ca9d.sh`) is `gpus=0 max_min=25 cpus=8 prio=10`;
   - GPU 4's FP4 recheck **verify** is `gpus=0 cpus=16`, about 9 min. Its capture half (`fp4-recheck2-d3b846cf.sh`) is the GPU job.
4. **Kernel-fill chunk length.** The GPU chunk rule is **≤ 8 min** (`max_min` ≤ 25–30 overall), not 3–25 min. The "about 20–40
   chunks/hour" figure has no source I can find, so treat it as unknown.
5. **Window verifies aren't fill.** The CPU verify of a timed window runs as `research run … -- bash verify.sh <run> 48`: 48
   processes, about 35 min, one per window. That is more than the fill CPU set (96–127, 32 CPUs) holds. Which CPUs it lands on is
   unknown. Smaller verifies (8–32 CPUs) do go through the fill queue.
6. **The 70B jobs.**
   - The current FP4 coverage job is **version 4**, not version 3 (`internal/pouw/rtx-pro/fp4-coverage-70b/job.md`, 19:35Z). Its
     GPU half is `gpus=1 max_min=12 cpus=16 prio=10 mem_gb=192`, and its CPU half is `gpus=0 max_min=12 cpus=16 prio=0 mem_gb=64`.
     It counts the rows #556's `volunteer` gives up.
   - "70–90 GB GPU memory each, about 1–2 h × a few" for the keyed-transform evals has no source I can find. Mark it unknown until
     bc-6289d8b0 or bc-2aa33ad8 says.
7. **The v2-hot fill jobs** (`gpu3-fp8-v2hot-*.sh`, the GPU halves) failed four times with no error text (§A1b). So "restartable"
   holds for the protocol, but those jobs haven't shown it.
8. **The sign-off in D3 is still owed.** `internal/pouw/infra/one-cluster-cutover-signoff.md`'s "Sign-off" section is "(empty)",
   and nothing in `lanes/cluster-build/` mentions the freeze list (checked 20:10Z).
9. **The A section's queue-dry total:** about 15 GPU-h, not 12. Add 15:07–16:00Z (2.4 GPU-h, after the ε_R batch) and
   13:00–13:24Z (about 1.2).

**Rows to add:**

10. **The assessor's leases.** bc-d7d4b0d1 takes GPU 6 or 7 (sometimes 2) through that index's `gpu-lease` lock for minutes. That
    is outside the fill queue: untimed, owner-driven.
11. **Approved-weights chunkers.** bc-8412d697's `aw-*` jobs are 5-minute CPU chunks at `max_min=8 prio=5`, plus 70B GPU runs
    (3.4 GPU-h in 10:00–11:00Z). Before the 10:51Z fix, four of them held all 4 CPU slots.
12. **GPU 0's capture fill.** `fp8cap2-die<d>.sh` and `fp8chain-die<d>.sh` are 16 jobs, 2 per die, pinned with `on=`, with CPU
    halves as `gpus=0` jobs. They are the leased-idle source in 18:00–19:00Z.
13. **The harness split (`hsplit-*`).** These run through `gpu-lease`, rank kernels (so node 2 only), and rewrite
    `fill-out/harness-split/state` while running. That rewrite raced the 20:05Z backup (§A2).
14. **Backups** (infra's, but they touch PoUW's data): hourly `research run`s of `/workspace/pouw`, about 17.7 GB and 395 units. 21
    large units are left out, and `gpu3-fp8/out` (517 GB) is never backed up. **Custody uploads are exempt from the window pause**,
    which is a quiet-window gap.
15. **Node-1 overflow** is a new class. Its terms are ≤ 20 GB GPU memory, SIGTERM with 5 s grace, exit 99 while work remains, and
    inputs staged over `vy-cluster` (`note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`). bc-2aa33ad8 owes the
    job list.
16. **Data sizes** on `/workspace` at 17:04Z (pous infra §5):
    - `hf` 163 GB (Qwen2.5-7B, Llama-3.1-70B, Llama-3.1-8B-Instruct, Llama-3.2-1B, WikiText-2);
    - `cache` 28 GB;
    - `research/runs` 89 GB (preserve until custody is verified);
    - `research/src` 28 GB;
    - `pouw/gpu3-fp8` 517 GB (regenerable, never moved);
    - `pouw/fill-out` 61 GB;
    - `pouw/approved-weights` 5 GB.
17. **Still unknown** (ask bc-2aa33ad8): per-job GPU memory, output size per batch, the week's window plan and count per day, and
    which ranking jobs could tolerate node 1.
