---
cursor:
  subagentId: "bc-efe47341-6cdf-5f91-a26b-d3946ca153b5"
---

# Node 2 operations (pous infra, bc-efe47341)

Status of vy-nebius-2's operations, for the pous root and the RTX PRO coordinator (bc-2aa33ad8). The hourly numbers and the rules are in [compute plan](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/compute-plan.md). The live page is on the node: `cat /workspace/pouw/infra/status.md`, refreshed every minute.

broker: source=broker 2026-09-30T17:41Z

## 18:57Z: node 2 handed to node2-ops (bc-c0738ef6)

- **Who runs node 2 now:** infra's node2-ops lane runs node 2's operations. This lane (bc-efe47341) has stopped, has no timers, and takes no further action on node 2.
- **The hand-back:** research-notes `lanes/node2-ops/20260930T1856Z-handoff-from-pous-infra-hand-back.md`. It lists the uncommitted and held files, the open promises and the partial hour: 77% for 18:00–18:55Z.
- **The lane's scripts:** `/workspace/pouw/infra/lane/` on node 2.
- **Where the hourly numbers go from now:** `/workspace/pouw/infra/utilization-report.json` on the node and `lanes/node2-ops/ops.md`.

## 18:19Z: the NVML A/B inside one timed window moved no timed row beyond noise

- **The run:** `r20260930-181638-b431`, custody preserved. It ran under `gpu-lease 8 --wait --timed` on GPU 0, with 4 blocks with no nvidia-smi loop against 4 with the sampler's 5 s loop, on the harness headline baselines.
- **Prefill 8,192³:** B against A was +0.02% (graph) and +0.04% (burst), inside the 0.13–0.15% spread between A blocks.
- **Decode m = 32:** B against A was −0.19% and −0.57%, inside the 1.0–1.6% spread; that's noise.
- **So the sampler's polling moved no published row beyond run-to-run noise.** Details: `note:20260930T1819Z-handoff-from-pous-infra-to-pouw-nvml-ab-result`.

## 17:58Z: the fill runner no longer freezes fill for leases that hold their GPUs

- **The bug** (found and patched live by bc-2aa33ad8 at 17:56Z): `waiters()` counted every `gpu-lease N --wait` argv, and a lease that holds its GPUs keeps that argv. So any untimed one-GPU `--wait` lease froze fill node-wide while it ran. It's likely a large part of today's 32–44% hours.
- **The fix, live since 17:58:46Z:** waiters are read from `gpu-lease`'s locked wait files, with no process scan.
  - It is committed at `infra/nebius` `13f402b2` with a regression test that pairs a lease holder with a real waiter. The runner's source of record is now `tools/research/src/research/pods/nebius/fill_runner.py`.
  - The runner restarted cleanly after GPU 2's window, and at once had 0 of 8 GPUs free.
  - The coordinator's restart watcher was stopped, because the runner has no restart loop. `restart_fill_after_window.sh` restarts it safely.
- **Effect:** the first full hour after the fix is 18:00–19:00Z, reported at the 19:03Z tick.

## 17:40Z: `gpu-lease` reports each lease's held and busy time at release (report-only)

- **What each holder now sees:** a stderr line per GPU at the end of every new lease, for example `gpu-lease: GPU 3 (GPU-9f1f172d) held 14m02s, busy 3m10s of 12m00s sampled (26%)`. Under 50% busy of at least 5 sampled minutes, it adds `; prepare on the CPU outside the lease`.
- **Where the records go:** `gpu-lease/usage/v1` records are written to the run's `gpu-lease-usage.jsonl` (published with the run) and to `/workspace/research/lease-usage.jsonl` on the node.
- **What it doesn't change:** busy comes from the node's sampler, never NVML. Nothing is refused or stopped on it, and each lease's exit status is its command's.
- **Where it lives:** `infra/nebius` `1ebbd156`, deployed at 17:40Z (sha256 `d03c8d15…`). Phase 1a of the one-cluster design; `note:20260930T1742Z-reply-from-pous-infra-gpu-lease-usage-shipped`.

## 17:25Z: `research run`'s nvidia-smi sampler is now paused during timed windows

- **The finding** (the one-cluster design, `docs/infra/one-cluster.md`): `research run` wraps every workload in its telemetry runner, which starts a sampler (`python3 -m research.telemetry sample`). The sampler queries nvidia-smi every 5 s (`--gpu-every 5.0`) for the whole life of the run.
- **Timed runs so far all had it on:** 15 of 15 runs today with a whole-node lease, from `r20260930-062850-de8e` to `-162438-25e9`, logged 19–272 nvidia-smi samples each inside their window. Every other live run's sampler kept polling too; 8 were running at 17:24Z, collector runs and backups among them.
- **Now (live 17:25Z, `node_ops.py`):**
  - while a timed window holds the GPUs, the window-quiet step pauses every `research.telemetry sample` process, the timed run's own included, whatever its CPU use;
  - it resumes them when the window ends, and each run's `resources.jsonl` records the gap;
  - nothing else changed on node 2, and the Verity pool code stays undeployed.
- **Timed-run owners:** add `--no-sampler` to `research run` for timed windows, so the sampler never starts. The harness's own per-rep clock and throttle reads are the measurement and stay.
- **Not measured:** whether the 5 s polls moved any timed row; the pause removes the question from now on.

## 15:30Z: the pous root's rulings on ε_R padding and GPU 3's flags (15:27Z)

- **No more ε_R seeds.** The batch settled the question (flat in k, stable across seeds), and more would only pad the utilisation figure. bc-2aa33ad8 is asked for real GPU supply, and to stop its FP8 repeat jobs holding GPUs during CPU preparation.
- **GPU 3's exactness flags (`/workspace/pouw/gpu3-fp8/out`) are never backed up.** They stay on disk until the v2-hot full-unit run is rated. After that, GPU 3 may delete them, since the replay regenerates them. The hourly backup already leaves them out as large units, and the 7 Oct final backup now skips them by name.
- **Disk:** it's raised again only past 60%. `node_ops.py`'s disk alert now fires at 60% (was 80%), so the alert relay reports it without anyone watching.
  - At 15:29Z the disk was at 18% (884 GB). The v2-hot run writes 8.6 GB per unit: four 2.1 GB bitsets, rows and columns for the hot and +0 chains. It was 60 of 64 units done, so it tops out near 920 GB, about 19%.

## 15:16Z: node 2 now stops at 2026-10-07T14:55Z; the `TERMINATED` line in `lease.log` is harmless

- **The new stop** (Daniel, 7:54 AM PT; `note:20260930T1502Z-handoff-from-nebius-infra-steward-to-pous-infra-hard-stop-oct-7`), checked read-only on node 2:
  - `/etc/research/deadline` reads `1791385200 2026-10-07T15:00:00Z daniel-2026-09-30T1454Z`.
  - The lease (`/home/research/.research/lease`) reads `2026-10-07T14:55:00Z … (clamped-to-deadline)`.
  - `vy-lease.service` and `vy-deadline.timer` are active.
  - That leaves 167.7 h and about 1,340 GPU-h from 15:14Z.
- **Replanned:**
  - The status page reads the stop from the lease and deadline files (the earlier of the lease expiry and deadline − 5 min) instead of a constant, so any further move shows up by itself.
  - The utilisation plot says 14:55Z Oct 7.
  - The final backups move to 7 Oct 09:00Z and 13:30Z.
  - The infra lane's hourly tick and alert relay are renewed to run until the stop.
  - The compute plan is updated.
  - `server.md` is bc-2aa33ad8's, so it has been asked to replan it.
- **The stray `lease.log` lines are harmless:**
  - They are `2026-10-03T05:32:24Z lease pid 7360: lease expired … terminating …` and `… TERMINATED computeinstance-… (nebius compute instance stop)`.
  - `lease.sh` only appends to `lease.log`. It decides from the lease file, the deadline file and the clock (`LEASE_NOW` is its test seam for the clock), so a log line changes nothing.
  - The VM is up, and the lease loop armed at 06:55:02Z reads the new cap.
- **Where the lines come from:** the node's bring-up, not a later test run. The log in order:
  - 05:30:26Z armed (pid 6368);
  - 05:30:30Z extended by launch;
  - 05:32:06Z a `renewal-test` clamped to the deadline (pid 7185);
  - the stray pair from the next process, pid 7360, stamped exactly Sep 30 05:32:24Z + 3 days. That's the expiry path exercised with the clock set 3 days ahead.
  - The VM then booted at 05:35:32Z, and the post-boot loop armed at 05:36:18Z (pid 3255).
  - It was all before node 2 was handed to pous at 05:40Z. The reboot 3 minutes after "TERMINATED" fits a real stop and restart during bring-up. The Nebius owner's instance events would confirm it.
  - The #504 isolation (tests writing to the real `~/.research`) is still right for check runs, but no line in this log dates from one.

## 14:20Z: GPU 1's hold dropped; fill may use every GPU (the pous root's 14:19Z decision)

- **For GPU 1's owner (bc-18346d9c):** GPU 1 is no longer held free. Your gate passed at 12:42Z. Fill now runs on GPU 1 preemptibly, and there are two ways to take it back:
  - `gpu-lease 1 --wait` preempts a fill lease within about 30 s (SIGTERM, then SIGKILL after 30 s);
  - a timed row leased with `--timed` pauses all fill for its window.
- **Why:** held free and unused, GPU 1 idled 0.91 of its 1.00 GPU-h in 13:00–14:00Z, 11% of the node, and cost the hour its target: 72% overall against 81% on the other seven.
- **What changed:** `/workspace/pouw/fill/keep-free` was removed at 14:19Z. The infra lane's queued and running ε_R jobs dropped their `on=0,2-7` pin. At 14:20Z GPU 1 was on fill, and 0 of 8 GPUs were free.
- **To hold a GPU again:** `echo "<index> # reason" > /workspace/pouw/fill/keep-free`. Use it only for a quiet die (a timing gate), and remove it when the gate ends.

## 13:55Z: `aw-70b-rotb-nvfp4-d9fd73f7` raised to `prio=10` (the pous root's 13:53Z ask)

- **The change:** bc-8412d697's 70B block-rotation NVFP4 job sat at `prio=5` behind 13 `prio=10` jobs, stopped at recovery step 183 of 250. Its header now says `prio=10`, keeping its queue time. It started at 13:55:08Z, and it needs about two 7-minute chunks. Its research run collects the result.
- **Timed windows:** a timed window stops it, like all GPU fill, and it resumes afterwards. The runner detects a window from a lease tagged `gpu-lease --timed` (or `GPU_LEASE_TIMED=1`) or a whole-node lease by one holder. A timed MVP run must be tagged that way for fill to stay out of it.

## 13:28Z: fill topped up to about a lane's turn (the pous root's 13:23Z ask)

The last hour was 77%, with three GPUs free and no GPU chunk queued. The infra lane queued 17 preemptible GPU jobs, about 5.2 GPU-h, which is about an hour on seven cards.
- **The jobs:** ε_R and the zero fraction for GPU 7's census families (`fp4_merge_gpu.py` at `ce5f8f18`, bc-dbc19788's code):
  - k = 32,768 at seeds 2–9 (about 12 GPU-min each);
  - k = 65,536 at seeds 1–3 (about 35 each);
  - k = 16,384 with 1,024 rows at seeds 7–12 (about 18 each).
  - Outputs are in `fill-out/fp4-merge-rate/seedN-kK-rR/`.
- **Rules:** `prio=10`, owners take turns, so any lane with nothing running starts first. `on=0,2-7`, and `keep-free` holds GPU 1 for its owner.
- **At 13:28Z:** GPUs 0 and 2–7 were on this fill, GPU 1 was free, and 12 GPU jobs were queued.
- **Earlier results for comparison:** k = 32,768 at seeds 0 and 1 is done. k = 65,536 at seed 0 is 11 of 30 units in.
- **The approved-weights lane (bc-8412d697): nothing left for infra to run on a GPU.**
  - Its folding recovery finished at 13:09Z. Its 70B block-rotation side product and recovery run as its own jobs.
  - Item 4's k = 16,384 cells (`aw-advdebit-{a,b,c}`) are CPU-only: `aw_advdebit.py` has no device option. They wait in the CPU queue.
- **The assessor's int8-Strassen replay: not ready.** `internal/pouw/red-team/fp4-int8-route.md` says the end-to-end rewrite replay against the MXF4 chain isn't written; `fp4_int8_depth.py` is CPU numpy. The assessor's base-split end-to-end replay (`assessor-basesplit-e2e.sh`) finished at 12:44Z.

## 13:00Z: the software power cap on node 2 (GPU 2's report, the pous root's 12:55Z check)

**Verdict:** there's no limit to restore. Every GPU is at its 600 W default, the same on all eight. The SW power cap flag is set on most prefill items at 298–443 W, well below that limit. When it's set, SM clocks sit 1–4 steps (7–30 MHz, 0.4–1.4%) below the 2,100 MHz lock. Arm and baseline share the same clocks, so ratios hold. Nothing was changed. A power-limit change would be bc-96a2e856's, and 600 W is already the maximum.

1. **Configured limits** (`nvidia-smi -q -d POWER` and `--query-gpu`, 12:56Z, outside a timed window): the current, requested and enforced limits are 600 W on every GPU, which is the default and the maximum; the minimum is 300 W. No GPU sits below its default.
2. **The SW power cap in timed prefill windows:** yes. The evidence is each run's per-item throttle record (`bench.json`, `items_with_bad_throttle`, with 40 timed items per kernel):
   - GPU 0's timed runs, including the whole-node windows at 06:28, 07:46 and 08:53Z (`r20260930-062850-de8e`, `-074616-9ec9`, `-085331-f280`): 65–76% of prefill items flagged.
   - One-GPU prefill runs up to 10:54Z (GPU 1's and GPU 2's): 0–3% flagged.
   - One-GPU prefill runs since 11:58Z (`r20260930-115810-a582`, `-122529-fb8b`, `-124211-a304`): 82–98% flagged. The change coincides with harness rule (a) at 10:33Z, a warm-up to steady clocks and equal device time per item, so items now run long enough at load to trip it.
   - Decode items (m = 32): 0 flagged in every run.
   - The driver's counters give SW-power-capping time since the 05:35Z boot of 726 s (GPU 2) to 1,681 s (GPU 4), so every die trips it, not one.
3. **Does the 2,100 MHz lock hold?** Within 1.4%. Per-rep SM clocks in flagged runs are 2,070–2,100 MHz: the median is 2,092 in GPU 0's windows and 2,085 in the recent one-GPU runs, and the minimum is 2,070. Arm and baseline medians differ by 0–7 MHz, and no run carries the `clock_gap` tag. This matches the 09:49Z holds: sustained FP8 ran at 2,077–2,092 with reason 0x4.
4. **Below the 600 W default?** No GPU. The draw when flagged, 298–443 W, is 50–74% of the limit, so the board limit isn't what binds.

**Rows that may be affected:** every prefill row (8,192³ and larger).
- Absolute times are read at 2,070–2,092 MHz, up to about 1.4% slower than a true 2,100 MHz.
- Ratios hold wherever arm and baseline alternate on one die with matching clocks, which is every run checked here.
- The most-flagged are the one-GPU runs since 11:58Z listed above: GPU 1 (bc-18346d9c) and GPU 2 (bc-7442ca43).
- **Open for the harness (bc-0de2d624):** if `panel.py` or the harness drops items flagged `bad_throttle`, 82–98% of the prefill items in those runs would be dropped. Please say how flagged items are treated.

## 12:14Z: census fill on GPUs 2–7 (the pous root's 12:09Z ask)

The hour to 12:02Z ran at 44%, with five GPUs idle while the slot-owner lanes were mid-turn. The infra lane queued 11 preemptible GPU census jobs from the lanes' existing code, so idle cards don't wait on a lane:
- Owner is bc-efe47341, `prio=10`, chunks of 8 minutes or less (exit 99), restartable from per-unit checkpoints.
- Every job is restricted to GPUs 2–7, keeping GPU 0 and GPU 1 free (GPU 1 for its `-h1` gate). Timed windows stop them, and they resume after.
- New in the fill runner (12:12Z): `on=` takes a set of GPUs (`on=2-7`), not only one index.

| Jobs | Census | Code (owner) | GPUs | Output on node 2 |
|---|---|---|---|---|
| `infra-f1-die{2..7}` | FP4-tile check F1: every sm_120a multiplier priced per nonzero product against dense NVFP4, all 10 families on each die, for a die-to-die `f1_rates.py compare` (pass 2 ran on die 7 only) | `f1_rates.py` at `258cb1c1` on the pass-2 library `8b0c72db` (GPU 4, bc-36186951) | pinned to 2, 3, 4, 5, 6, 7 | `fill-out/fp4-f1/dies-258cb1c1/gpuN/` |
| `infra-fp4-merge-seed{1,2,3}` | merge rate ε_R and the zero fraction per census family at fresh seeds and 1,024 rows (the seed-0, 256-row run is `art:a4268def`) | `fp4_merge_gpu.py` at `ce5f8f18` (GPU 7, bc-dbc19788) | any of 2–7 | `fill-out/fp4-merge-rate/seedN-r1024/` |
| `infra-aw-census-new-models` | the approved-weights census on the two cached models never censused, Llama-3.1-8B-Instruct and Llama-3.2-1B, at the original rotation seed 20260930 | `aw_census.py` at `94afd036` (bc-8412d697) | any of 2–7 | `fill-out/aw-census/new-models-s20260930/` |
| `infra-aw-census-key2` | the same census of Llama-3.1-70B and Qwen2.5-7B under a fresh rotation key (seed 20261001), to test whether the rotation's result depends on the key | `aw_census.py` at `94afd036` (bc-8412d697) | any of 2–7 | `fill-out/aw-census/key-s20261001/` |

- **GPU 1 kept free** (12:18Z): the runner starts no fill job on a GPU listed in `/workspace/pouw/fill/keep-free`, which holds `1` for GPU 1's `-h1` gate. Delete the file to release it. A fill chunk already running there finishes and doesn't restart.
- **Added 12:20Z:** merge-rate seeds 4–6, and `infra-aw-census-new-models-key2`, the two new models under the fresh key, which completes the models-by-keys grid. At 12:20Z, 7 GPU jobs were queued, and every card except GPU 1 was busy.
- **First results (fill outputs, not recorded runs):**
  - **F1, dies 2–6:** all 10 families passed their gates on every die. Across 97 forms, no rate differs between dies by more than 0.17% (`ffma_f32`), and the median spread is 0.001%. NVFP4 runs at 2,045.2 products/SM/clock on every die. So F1's prices hold die to die. Die 7 waits for its GPU.
  - **Approved-weights census, Llama-3.1-8B-Instruct (224 linears) and Llama-3.2-1B (112):** done in 48 s. The planted relation leaves 31.2% of its linear skippable as registered, and 0.00–0.05% (8B) or 0.00–0.20% (1B) after the rotation, the same pattern as 7B and 70B.
  - **ε_R at seeds 1–3, 1,024 rows:** running. The first NVFP4 grid-aligned units give ε_R ≤ 0.0003 and zero codes 7.9%.
- **FP8 merge rate ε₈:** not queued. Its script (`pearlc_merge_rate.py`) is CPU-only, and its base run is done. The GPU extension is GPU 3's to build.
- **F2 and F3:** not queued by the infra lane. F3 is GPU 4's own: its `5d038ce0` build failed its bit-exactness gate at 11:55Z, and `47eecb5c` (`fp4-f3-lut-47eecb5c`, `-g2c4`) finished at rc 0 by 12:04Z. F2's kernel is GPU 4's to write.
- **Code owners:** these runs use your code at the commits named. Results go to the paths above. The infra lane will post die-to-die and seed-to-seed comparisons here when they finish.

## 11:12Z: GPU slots for the lanes that owe node-2 chunks

At 11:11Z, 5 of 8 GPUs were idle, with 0 GPU jobs queued. Every lane that owes a GPU chunk has a home GPU. The full terms are in `note:20260930T1112Z-handoff-from-pous-infra-gpu-slots-owed-chunks`: chunks of 8 minutes or less, exit 99, `prio=10`, one queued at all times, and `on=` only if the die matters.

| Home GPU | Owner | Chunk |
|---|---|---|
| 0 | GPU 5, bc-71c6ab78 | the Pearl-C4 replay on real activations |
| 3 | GPU 3, bc-0f3f8a2f | the exact-region replay (it held its GPU at 0–13% from 11:03Z: move its CPU part into a `gpus=0` job), ε₈'s GPU side, the hot-chain census |
| 4 | GPU 4, bc-36186951 | F3 (LUT-GEMM), then F2 (TF32 Strassen) |
| 5 | Harness, bc-0de2d624 | FP8's cuBLASLt 13.1 space, then CUTLASS raster, swizzle and Stream-K |
| 6 | Mainloop, bc-fb55a759 | the configuration sweep, one configuration per chunk |
| 7 | bc-a8466279 (offered) | the `down_proj` coverage measurements |
| 1, 2, 4 | bc-8412d697 | the 70B loss runs (running) |
| any free | bc-b7cd617f (approved by the pous root, 11:20Z) | the FP4 scale-flatness attack, if asked: `prio=10` chunks of 8 minutes or less on idle GPUs |

bc-8412d697's five held CPU jobs were released at 11:09:19Z through its own trigger (`approved-weights/held/release`), because the CPU ordering fix has been live since 10:51Z.

## 10:53Z: the GPU queue is dry; the fill runner's start order is fixed

- **Utilisation:** 80% busy over the rolling hour to 10:37Z, which meets the target. The queue then ran out of GPU jobs: at 10:53Z 4 of 8 GPUs were free, with 0 GPU and 6 CPU jobs queued.
- **Supply:** the next GPU-heavy supply is GPU 0's capture fill and GPU 3's aligned-exact-regions census, both still being built. bc-2aa33ad8 was asked at 10:53Z (`note:20260930T1053Z-handoff-from-pous-infra-to-pouw-gpu-queue-dry-runner-fixed`).
- **Fill runner (live 10:51Z):** jobs start by `prio`, then with owners taking turns, then by time queued; a requeued job queues afresh. `max_min` no longer counts time paused for a timed window. This answers GPU 3's 10:18Z note: bc-8412d697's `aw-*` chunkers had held all 4 CPU slots since 09:44Z. The runner was restarted and adopted its 7 running jobs.
- **A failed job:** bc-2aa33ad8's `coord-fp4-v3-real-qwen7b.sh` failed twice with `No module named 'verity'` (`uv run --no-project`). They were sent a one-line fix; the job is in `fill/failed/`.
- **Backups:** the 10:27Z chunked hourly backup and six large-unit runs were preserved at 10:34Z. `gpu7-fp4/out` (1.46 GB) is still changing (414 files in 10 minutes), so its own backup waits.

## 10:07Z: the assessor's superseded CPU run `r20260930-094824-df8a`

- **Already stopped; nothing to kill.** Its runner recorded it as failed at 09:55:27Z: SIGTERM, exit 143, classifier class `UNKNOWN_SIGNAL`. Its custody is preserved.
- **No process of it remains on node 2:**
  - no `rowseed_grind_sm120.py` or multiprocessing worker (it ran `--procs 48`);
  - nothing whose environment carries its run id;
  - nothing working in its source tree (`5f1cb93e`).
- **The CPU-busy processes at 10:05Z are fill jobs** under the fill runner: the approved-weights `aw_debit`, `aw_advdebit` and `aw_gpu` runs, and a harness hold.
- **Recorded as cancelled:** the label `outcome CANCELLED` (by pous-infra) corrects the classifier's `UNKNOWN_SIGNAL`, because the assessor ended it deliberately.
- **Not in a timed window's path:** no window was running or waiting.

## 10:00Z: #449's exp test at `61d0298d`

- **At `61d0298d`, both pass on node 2** (run `r20260930-095512-4a39`, CPU only, CPUs 128–159, no timed window):
  - the two-file repro (`tests/commit/test_native_jit_load.py`, then the transcendentals test), 10/10;
  - `tests/commit/test_native_jit_isolation.py`, 1/1.
  - They also pass with a cold extension cache and unpinned.
- **The failing test's exact id** (suite `integrations_vllm`, relative to `integrations/vllm`) is `tests/program/test_ref_prims.py::test_transcendentals_vs_torch_and_float64[F32ExpRn_v1-f32_exp_rn_bits-exp]`. bc-9914c188's assumption is right. It's from the FAILED line of check `r20260930-081604-5569`.
- **The leak is intermittent:** the pre-fix tree `6a1a051f` failed twice (the check's worker gw7, and a manual run at about 09:19Z), then passed 5 of 5 at 09:55–10:00Z. A pass on node 2 doesn't prove the fix; running the state-changing tests in fresh interpreters makes the leak impossible by construction.
- **Node 1 overflow** is noted in the compute plan, for later.

## 09:46Z

- **08:45–09:45Z: 80% GPU-busy, reaching the 80% target** (6.42 of 7.98 GPU-h: timed windows 0.20, other kernels 6.22; leased-idle 0.47, free-idle 1.09; CPU 8%).
  - By 20-minute thirds: 77%, 85%, 79%.
  - It came from GPU-heavy fill: my harness autotunes, per-die holds and hash benches (3.65 GPU-h), the assessor's GEMMs and the approved-weights jobs. The CPU-bound probes stayed withdrawn.
  - The fill runner's one-GPU reserve caps busy at about 87.5% outside timed windows.
- **The next hour is at risk:** the GPU queue is down to 2 jobs at 09:47Z (`aw-census-94afd036` plus my last two 180 s holds). My GPU 6 and GPU 2 candidates are used up. The remaining GPU-heavy candidates are "to build" by their owners, so I pinged bc-2aa33ad8 at 09:49Z.
- **The FP8 merge-rate spec** has appeared (`fill-candidate-fp8-merge-rate.md`). Its base is CPU-only and bc-2aa33ad8 queued it at 09:01Z; its GPU extension is GPU 3's.
- **The 09:30Z chunk rule** (at most 8-minute chunks): my last holds are 180 s per family, about 7 minutes.
- **Power cap under sustained FP8:**
  - 300 s holds on GPUs 2 and 3: FP8 median 2,085 MHz, minimum 2,077, throttle 0x4 (SW power cap);
  - NVFP4: 2,085–2,092 MHz, no throttle.
  - A `locked-2100` label means 2,077–2,092 MHz under sustained FP8. bc-2aa33ad8 and the Nebius owner are told; this is for information, not asking for a change.

## 08:49Z: GPU-heavy fill queued

- **Assessor's generic-core GEMM and Strassen:** already queued by the assessor (bc-d7d4b0d1). `rt-gemm-ffma`, `-lowp-ffma`, `-dp4a` and `-packed` are done; `rt-gemm-strassen` runs in chunks; more `assessor-generic-gemm-*` jobs (5 queued) are running now.
- **Approved-weights GPU checks:** only `aw_gpu.py` (the loss/verification-cost sweep, done) exists in its tree (`fc88d086`). The census, relation-attack and registration checks have no entry point yet, so they stay with bc-8412d697, beside the rotation study it's about to queue.
- **FP8 merge-rate spec:** not in `fill-candidates.md` yet; there's only a CPU companion for FP4. It'll be queued when it appears.
- **Queued by me:** GPU 2's hash bench, pinned to each of the 8 dies (`prio=10`), plus the 8 per-die sustained holds from 08:42Z.
- **CPU-bound probes:** they stay withdrawn.
- **08:48Z:** 7 of 8 GPUs at 56–100% utilisation and 400–450 W. GPU 6 is the reserve.
- **Early observation from the holds:** under sustained FP8 and NVFP4 load, GPUs 0–4 ran at 2,070–2,077 MHz. That's below the 2,085–2,092 MHz of shorter loads, which is what the `locked-2100` label rests on. The hold outputs (`/workspace/pouw/fill-out/harness/hold-600s/gpu*/out/`) will say whether it's power-cap throttling; I'll report it when they finish.
- **The 08:45–09:45Z line** is posted here when the hour closes (a timer fires at about 09:47Z).

## 08:45Z update

- **Utilisation: not yet ≥ 80%.**
  - 08:18–08:40Z: 45% (1.3 of 2.9 GPU-h: timed 0.7, kernels 0.6; leased-idle 0.8, free-idle 0.8).
  - 08:30–08:43Z: 65%, with timed windows running.
  - The largest leased-idle share was then the infra lane's own 12 fresh-seed FP4 probe jobs, CPU-bound like the coordinator's. I withdrew them at 08:44Z to `/workspace/pouw/fill/withdrawn/`; they return only when no GPU-heavy job is queued.
  - The queue at 08:44Z held 10 GPU jobs (8 are the pinned per-die holds) and 6 CPU jobs.
  - Both lines are on node 2's status page (by-hour record) and in the lessons log.
- **Timed-window SIGSTOP:** on since 08:33Z. By 08:43Z it had made 4 pauses, each resumed after its window. A lease marks a window with `gpu-lease 8 --wait --timed -- CMD` (or `GPU_LEASE_TIMED=1`), which records `timed=1`; a lease of all 8 GPUs by one holder counts even untagged. bc-2aa33ad8 was told at 08:42Z.
- **Budget, 08:44Z:** no `vy-pous*` pods, so nothing to terminate. `vy-coord-pouw449` is still up ($0.56/h since 07:57:20Z, about $0.44 so far; busy with #449's check at 08:29Z). The account: $121.61 balance, $1.72/h.

## 08:40Z

**Utilisation, 07:18–08:18Z:** 34% GPU-busy against the 80% target.
- Busy: 2.8 of 8.0 GPU-h (timed windows 0.9, other kernels 1.8).
- Leased but idle: 3.8 GPU-h, 3.2 of it bc-2aa33ad8's FP4 probe fill (a GPU held while verifying on the CPU).
- Free and idle: 1.5 GPU-h.
- Last full hour (07:00–08:00Z): 44%.

**Fill queue, deepened at 08:34Z:** 33 GPU jobs and 14 CPU jobs.
- 19 full-quality baseline autotunes at the non-headline shapes, GPU-heavy, `prio=10`: `--lt-candidates 32 --finalists 4 --reps 40`, every family.
- 14 fresh-seed FP4 rechecks (seeds 20261005 and 20261006, 7 instructions), from bc-2aa33ad8's template, owned by me and done for GPU 4 (bc-36186951).
- 08:42Z: GPU 6's 600 s sustained hold on each of the 8 dies (pinned, about 2.7 GPU-h), to check every die holds the locked 2,100 MHz.
  The full-quality autotunes finished in 30–150 s each.
- GPU-heavy work is still the constraint. The candidates marked "to write" (the assessor's generic-core and Strassen GEMMs, GPU 6's FP4 rebuild, the approved-weights census at GPU scale) need their owners, or an extra agent.

**Timed windows keep the node quiet (live 08:33Z).**
- Measured reason: CPU load on NUMA node 1 slowed GPU 0's decode baselines by 0.26–1.35% (`r20260930-075259-37cc`).
- **How it works:**
  - While a timed window holds GPUs, `node_ops.py` SIGSTOPs the `research` user's CPU-heavy process groups: at least one core busy, or a build, Lean or cargo process.
  - It resumes them when the window ends.
  - Left running: the window's own process tree, research runners, fill jobs (the fill runner pauses its own CPU jobs) and anything under GNU `timeout`.
  - Every pause and resume is in `/workspace/pouw/infra/logs/quiet.jsonl`, and the status page lists what's paused.
- **Tagging a window:** `gpu-lease 8 --wait --timed -- CMD`, or `GPU_LEASE_TIMED=1`. It's `infra/nebius` `b4541ee1`, live on node 2 since 08:41Z (sha256 `f0af4e6f`); bc-2aa33ad8 was told at 08:42Z. A lease of all 8 GPUs by one holder counts as a window without the tag.

**Checks:** node 2's recorded checks pass preflight (`r20260930-075739-85ee`).
- A `~research/.bashrc` hook gives check runs only the pinned toolchain (uv 0.12.20, elan and lake, cargo), `UV_PYTHON=3.14.7` and CPUs 128–191.
- The node's default uv stays 0.12.21.
- Checked branches should merge `origin/main` and `origin/infra/nebius` (`eb2553d6`: the host-leak test fixes) before recording.

**Build-optimization's CPU request:** declined on measurement (note of 07:59Z). Their 40–60-minute Build attempts can't be paused, and they would bias our decode timings.

**Backups:** hourly, through `research run` custody.
- The 08:11Z backup (`r20260930-081105-b32f`) had grown to 17.4 GB. From 09:03Z, backups skip environments and source copies, and hard-link unchanged files into the previous backup.
- Final backups are set for 1 Oct 22:00Z and 2 Oct 03:30Z.

**Alerts:** none since the 06:59Z test OOM.

## Budget sweep (08:29Z)

This VM has `RUNPOD_API_KEY`.

| Pod | State | $/h | Since | Spend so far | Idle? |
|---|---|---|---|---|---|
| `vy-pous*` | none exist | – | – | – | – |
| `vy-coord-pouw449-veritor-campaign` (16 vCPU, 32 GB, CPU only) | RUNNING | 0.56 | 07:57:20Z | about $0.30 (0.53 h) | no: its Python workers were at ~95% CPU running #449's check (tree `6a1a051f`); not ours, left alone |
| `vy-coord-t7-veritor-campaign` | RUNNING | 0.99 | – | – | not checked (Verity's) |
| `vy-control-verity` | RUNNING | 0.03 | – | – | not checked (Verity's) |

- Nothing was terminated: there are no `vy-pous*` pods, idle or not.
- The account: $122.02 balance, $1.72/h current spend, spend limit $80.
