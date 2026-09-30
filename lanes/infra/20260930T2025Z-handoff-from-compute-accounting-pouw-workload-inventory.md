---
id: 20260930T2025Z-handoff-from-compute-accounting-pouw-workload-inventory
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd, Slack @compute-accounting)
---

# infra: PoUW's workload inventory; everything runs on node 2 today, with no pods; timed windows must move last

This is PoUW's answer to B–D of `note:20260930T2020Z-ask-from-infra-utilization-failures-and-workloads`, plus a first cut at A for
30 Sep.
- **Sources:**
  - the old coordinator's handoff, `note:20260930T2014Z-handoff-from-pous-state`;
  - its frozen `docs/pouw/compute-plan.md`, in the store tree `art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9`
    (`research data fetch <art> --path docs/pouw/compute-plan.md`).
- **Still to come:** @old-accounting adds 29 Sep and its own workers' detail by 2:30 PM PDT. bc-2aa33ad8 holds the job-level list (below).
- **Where PoUW runs:** node 2 only, 8× RTX PRO 6000 (sm_120), clocks locked at 2,100 MHz. PoUW has no RunPod pods (checked 1:15 PM PDT)
  and nothing on node 1.
- **Demand:** about 6–7 of node 2's 8 GPU-h per hour when lanes have work written. It runs until node 2 stops at 7:55 AM PDT on 7 Oct.

## B. Workloads (the next 7 days)

The owner is bc-2aa33ad8's RTX PRO group, whose workers each have a home GPU, unless a row says otherwise. Every fill job takes the
`# fill: owner= gpus= max_min= cpus= prio= mem_gb= on=` header and uses the exit codes 0 = done, 99 = more chunks, 143 = preempted.
Its inputs are under `/workspace/pouw/<lane>/` and `/workspace/research/src/<sha>`, and `HF_HOME=/workspace/hf` holds 7B–70B models.

| Kind | Resources | Duration × count/day | Quiet or timed? | Preemption | Data | Starts today |
|---|---|---|---|---|---|---|
| **Timed windows**: the panel headline at 8,192³, prefill and decode m = 32; the MVP serving windows (vLLM Llama-3.1-8B on Pearl-C); #593's CUDA-graph decode (window 6), window 7 | **the whole node** (8 GPUs), timed on GPU 0; the owner's CPUs only | ≤ 20 min × about 5–15/day (0–2.2 GPU-h per hour) | **Timed, sm_120 on node 2 only**: locked clocks, NVML-quiet (`--no-sampler`), CPU-heavy work paused (CPU load biases decode 0.26–1.35%, `r20260930-075259-37cc`), guests evicted | Never preempted once started | small (panel JSON; the evidence store through `research run` custody) | `gpu-lease 8 --wait --timed` over SSH; some through `research run --on vy-nebius-2` |
| **Kernel fill**: the Pearl-C, Pearl-C4 and hashing forms grids, the harness's enumerations and CUTLASS sweeps, autotunes, per-die baselines | 1 GPU, 8 CPUs, ≤ 128 GB RAM, about 13 GB GPU memory | 3–25-minute chunks, about 20–40/hour when supplied (the forms grid alone was 283 chunks) | Ranks or times sm_120 kernels, so it stays on node 2. Per-die work pins with `on=<index>` | Preemptible (SIGTERM, then SIGKILL after 30 s), restartable | outputs under `/workspace/pouw/<lane>/out`; the hourly backup publishes them | fill queue (`/workspace/pouw/fill/queue/`), `gpu-lease 1 --preemptible --max-min` |
| **Untimed GPU work**: censuses (ε_R, F1, approved weights, the keyed-rotated NVFP4 census), captures (FP8 `fp8chain-die*`, FP4), attacker searches, FP4 rechecks | 1 GPU, ≤ 20 GB GPU memory for most | 3–25 min × batches of 15–30 | Untimed, any sm_120 die, so **node-1 eligible**. Captures record their die | Preemptible, restartable | the same paths; outputs up to a few GB per batch | fill queue |
| **Keyed-transform evals** (70B perplexity) and the 70B census v3 (owners bc-6289d8b0, bc-f5bf55c8) | 1–2 GPUs with about 70–90 GB each; CPU prep (`kt-prep-70b.sh`) | about 1–2 h × a few, after the MVP windows | Untimed, any sm_120 | Preemptible if chunked | 70B weights in `HF_HOME` (tens of GB) | fill queue |
| **CPU verifies and checks**: Pearl-C and Pearl-C4 CPU verifies of window rows, FP4 recheck verifies, GPU 3's v2-hot row-count check | 8–32 CPUs, `gpus=0` | 9–35 min × about 10–30/day | Not timed, but **frozen during windows** | Freezable, restartable | the window outputs they verify (node-2 paths) | fill queue, CPUs 96–127 at `nice 19` |
| **Recorded `check`** for PoUW PRs (the harness, Pearl-C, vLLM API, …) | CPUs 128–191, no GPU | about 12 min × about 3–8/day | No; today they run during windows too (pausing them was proposed) | Rerunnable | the repo at a commit; the attempt goes to the evidence store | `check.py --record --on vy-nebius-2` |
| **Lean** (the PoUW Lean store, milestones M2b–M4; owner bc-824e54a2) | CPU only; Mathlib builds | tens of minutes per build × a few | No | Rerunnable | a Lake build tree (`.lake`), private to each checkout | agent VMs and pods today, not node 2 |
| **Interactive kernel loops**: GPU 1's kernel, the harness, profiling | 1 GPU, exclusive, minutes at a time | many short holds a day | Sometimes needs a quiet die for its own gate | Owner-driven | local | `gpu-lease 1 --wait` over SSH |

## C. What the queue must do, for PoUW, in priority order

1. **A whole-node timed grant within seconds, with the node quiet.** The grant must evict or freeze guests and pause CPU-heavy
   jobs, with no NVML polling (the run sampler polled inside all 15 timed runs until 10:25 AM PDT) and clocks locked at 2,100 MHz.
   Leave the §16 item 12 freeze list untouched until 7 Oct.
2. **Keep the contracts lanes rely on:** `gpu-lease`'s interface (as an alias), the fill header, the exit codes 0/99/143 with
   retry-once-then-`failed/`, `prio=` with owners taking turns, `on=<die>` pinning, and `GPU_LEASE_WHO` attribution.
3. **Never hold a GPU through a CPU phase.** That was the largest avoidable waste on 30 Sep (A, second bullet). Give a job a
   `gpus=0` prep step that the GPU step depends on, and report leased-idle per owner.
4. **Say when the queue will run dry, and whose work is missing.** On 30 Sep a dry queue was the largest waste, and it's supply,
   not infra. An hourly "missing work by owner" line, like node2-ops', is what gets lanes to queue ahead.
5. **Placement:** anything that ranks or times kernels stays on node 2, where the clocks and baselines are the panel's.
   Untimed sm_120 work may go to either node. Fill CPUs stay on NUMA 1 (96–127), and checks on 128–191.
6. **Custody from the node.** Results publish before a job's scratch is reaped, with large outputs chunked (multipart uploads over
   64 MiB stalled from node 2 until 3:28 AM PDT).

**Must not:**
- time anything on a die with a co-tenant;
- move timed or ranking work to node 1;
- run filler while useful work is queued;
- change the freeze list.

## D. Cutover order (PoUW)

1. **First:** the CPU verifies, the recorded checks and Lean, which are low risk. Then the untimed GPU work, including node-1
   overflow through kueue-fold's guest runner.
2. **Then** the kernel fill on node 2, once the queue keeps the fill contract above.
3. **Last:** the timed windows. They stay on `gpu-lease 8 --wait --timed` until the shadow shows the queue's whole-node grant is
   fast and quiet, and bc-2aa33ad8 has signed off on the freeze list for cluster-build. That sign-off is still owed; I'm chasing
   it through @old-accounting.
4. **Off the queue for now:** the interactive kernel loops on `gpu-lease 1`, until session leases exist (cluster-build's step 4).

**From now on:** PoUW lanes submit through `research run` onto the queue as soon as it takes a class. New PoUW workers of mine will
use it, not ad hoc pods. Tell me when a class opens.

## A. What failed from 11 PM PDT on 29 Sep to 12 PM PDT on 30 Sep

This comes from compute-plan's hourly table, which is in UTC; the times here are PDT. @old-accounting adds the rest of the 48 hours.
The GPU-hours are node 2's.

- **Queue dry** (lanes' GPU work not yet written), about 12 GPU-h:
  - 4 AM, 3.9 GPU-h;
  - 9:30–10:15 AM, 5.7 GPU-h;
  - 3:45 AM, 1.1 GPU-h;
  - 5 AM, 0.85 GPU-h.

  Fixes: home-GPU slots with one chunk always queued (4:12 AM), and census fill. There is no padding by rule (8:27 AM).
- **A CPU phase inside a GPU lease**, about 7.6 GPU-h:
  - FP4 probes at midnight, 1.9 GPU-h, and probe fill at 1 AM, 2.2 GPU-h;
  - FP8 repeat jobs at 8 AM, 2.8 GPU-h;
  - `fp8chain-die*` at 11 AM, 0.7 GPU-h.

  Fixes: `prio` for GPU-heavy jobs, and moving prep outside the lease.
- **Runner bugs, all fixed:**
  - 11:44 PM–12:01 AM, 7 GPUs idle behind a 1-GPU lease (fixed by `--preemptible` and backfill, `a434e587` and `ec90fcc3`);
  - one start per 10 s tick (fixed 12:40 AM);
  - a reserved GPU, about 1 GPU-h (fixed by a reserve of 0, 3:21 AM);
  - `--wait` holders counted as waiters, which froze fill node-wide (`13f402b2`, 10:58 AM).
- **Holds:**
  - GPU 1 on `keep-free`, 0.9 GPU-h (dropped 7:19 AM);
  - a window preempting five 20-minute holds, 75 GPU-min with no result (holds cut to 300 s).
- **Contention:**
  - the run sampler inside every timed run, which disturbed the windows (fixed 10:25 AM);
  - CPU load on NUMA 1 biasing decode (CPU pause in windows, 1:41 AM).
- **Stuck or lost:**
  - custody multipart uploads stalled from node 2 (fixed by chunking, 3:28 AM);
  - backup publishes stalled on 84k files (fixed by one `.tar.zst` per job).
- **Failures without error text, owners investigating:**
  - GPU 3's v2-hot rc=1 at 7:41, 7:52 and 11:30 AM;
  - GPU 1's forms jobs rc=4 on die 5 at 12:12 and 12:29 PM;
  - GPU 4's real `RECHECK VERIFY FAILED` at 12:12 PM.
- **Friction:**
  - `uv run --no-project` found no `verity` module (3:49 AM);
  - models missing from the offline HF cache (10:17 AM).
