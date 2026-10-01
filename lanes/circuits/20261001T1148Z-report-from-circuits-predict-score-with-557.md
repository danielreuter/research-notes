---
id: 20261001T1148Z-report-from-circuits-predict-score-with-557
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-predict
---

# circuits-predict -> @circuits (4:50 AM PDT): with #557, the predictor is exact for 4139 of 4151 units (99.71%), and all 700 coverage-v1 drift units match

**For the overnight goal (at least 95% of units exact):** 99.71% on main plus #557's head. The landed confirmation is pending.

**#557 had not landed by 4:45 AM PDT.** It is still open, granted at `2fdd11053`, so this is the score on main plus #557's head, not
on landed main. Since my merge, main has moved six trains (T640R, T588R, T656, T1, T654 and T525, now `d88650921`). They change 25
files of the predictor's two packages, mostly the Boolean lowering. I checked on my VM (art:ced5f6b31acd):
- **PR head + current main:** all 432 sampled keys (349 non-Qwen, 83 Qwen2.5) have f6697c66e's digests.
- **Plus #557's head:** all 247 Qwen2.5 keys have the preview's digests.

So landed main should give the same 4139, unless #557 changes before it lands.

The landed re-score is ready on my VM: once #557 lands, resume me and I run `/tmp/predict_scratch/p557/land.sh --submit`. It builds
the tree (the PR head plus landed main, or main alone if the predictor has landed), prints its predictor code version and its
predictor-code diff from this preview, and then queues every Qwen2.5 row fresh, with the non-Qwen sample beside it. That takes about 15 minutes at full speed, and took 80 at last night's load. If #557 lands
in the 5:00–5:30 slot, Kueue is already holding (5:10) and node 1 is offline 5:40–5:55, so the re-score runs after 5:55.

## The score

- **Code.** The predictor at `cursor/vllm-predictor-8c79` `33a4ea8e2` with #557's head `2fdd11053` merged in (tree `abfbbc9cc`, predictor
  code version `0fdd00ac8afa0ad9`).
- **Fresh on that code** (r20261001-092331-b782):
  - every Qwen2.5 row in full (steps, requests, workloads): 706 compared, 700 exact;
  - every other row's steps and its requests of LP+T ≤ 64: 1073 prediction keys, each with the same digest as on `f6697c66e`.
- **Reused.** The remaining 2130 compared units are reused from art:344ba958f0e8 (`f6697c66e`); that code predicts them identically,
  as the sample shows. `summary.compared_by_code` counts both sources.
- **The result.** art:2fc889888864 (`score.json`, `score.md`, `table.md`, the composed cache): **4139 of 4151 units exact (99.71%)**,
  across 326 rows of 15 models. 278 of the 282 rows with a compared unit have every compared unit exact.

| model | rows | rows all exact | units compared | exact | differ: coverage-v1 trees | differ: other trees | not run / over budget | no trace |
|---|---|---|---|---|---|---|---|---|
| gemma2-2b | 35 | 33 | 615 | 615 | 0 | 0 | 4 | 4 |
| gemma2-2b TP2 | 3 | 1 | 6 | 6 | 0 | 0 | 0 | 22 |
| llama32-1b | 35 | 32 | 518 | 518 | 0 | 0 | 1 | 8 |
| llama32-1b TP2 | 6 | 4 | 52 | 52 | 0 | 0 | 0 | 22 |
| mistral-7b | 15 | 14 | 132 | 132 | 0 | 0 | 0 | 2 |
| mistral-7b TP2 | 5 | 3 | 32 | 32 | 0 | 0 | 0 | 22 |
| olmoe-1b-7b | 18 | 17 | 198 | 198 | 0 | 0 | 0 | 2 |
| olmoe-1b-7b TP2 | 4 | 2 | 26 | 26 | 0 | 0 | 0 | 22 |
| phi3-mini | 18 | 17 | 229 | 229 | 0 | 0 | 0 | 2 |
| phi3-mini TP2 | 5 | 3 | 32 | 32 | 0 | 0 | 0 | 22 |
| pythia-160m | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 33 |
| qwen25-05b | 19 | 16 | 329 | 323 | 0 | 6 | 0 | 2 |
| qwen25-15b | 12 | 11 | 228 | 228 | 0 | 0 | 0 | 10 |
| qwen25-15b TP2 | 3 | 3 | 32 | 32 | 0 | 0 | 0 | 0 |
| qwen25-7b | 8 | 8 | 85 | 85 | 0 | 0 | 0 | 0 |
| qwen25-7b TP2 | 3 | 3 | 32 | 32 | 0 | 0 | 0 | 0 |
| qwen3-30b-a3b | 16 | 16 | 115 | 115 | 0 | 0 | 0 | 1 |
| qwen3-30b-a3b TP2 | 3 | 1 | 6 | 6 | 0 | 0 | 0 | 22 |
| qwen3-4b | 15 | 14 | 172 | 172 | 0 | 0 | 0 | 2 |
| qwen3-4b TP2 | 5 | 3 | 32 | 32 | 0 | 0 | 0 | 22 |
| qwen3-4b-fp8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| smollm2-135m | 32 | 30 | 406 | 403 | 0 | 3 | 2 | 4 |
| smollm2-360m | 21 | 20 | 365 | 365 | 0 | 0 | 1 | 2 |
| tinyllama-11b | 28 | 25 | 483 | 480 | 0 | 3 | 2 | 4 |
| tinyllama-11b TP2 | 6 | 2 | 26 | 26 | 0 | 0 | 0 | 30 |
| **all** | **326** | **278** | **4151** | **4139** | **0** | **12** | **10** | **264** |

**The 12 that differ** were all traced on older code, three units (step, request, workload) per row:

- `cov-k03-7-124-ce1b86e4-head` (Qwen2.5-0.5B), traced on main before #557. The trace has `Gemm_v2` then `BiasAdd_v1` for the biased
  q/k/v linear; the prediction has `GemmBias_v2` with `GemmBiasCoordinate_v2`. These were 3 of the 3442 exact units before #557.
- `cov-k03-6-79`, `cov-k01-9-77` and `cov-k04-6-80` (Qwen2.5-0.5B, SmolLM2-135M and TinyLlama): old trees with `AttentionHead_v2` and
  `Attention_v2` where current code has `_v5`. These differ the same way without #557.

## The large-memory job: no unit settled

- **The Llama-3.2-1B request** went first (LP4096/T511, `b96e1dcc5d2eb7ed:request:None:None:4096:511`, 74 GB estimate). It ran as a
  fill-class, preemptible CPU job of 112 GiB, one at a time.
  - r20261001-090949-6279: I sized its timeout from full-speed rates (1440 s), so I stopped it by its process group after 16 minutes.
  - r20261001-093109-b25d: it got 0.14–0.26 of a core and could not finish within its 2610 s timeout, so I stopped it after 19 minutes.
  - r20261001-095111-6466: it timed out at 5320 s (`STAGE_TIMEOUT`, 4:20 AM). Its memory peaked at 102.9 GiB, 1.42× the estimate,
    with no OOM, and it got about 20% of a core from 3:00 to 4:15.
- **Not run.** The driver stops once a unit fails to settle, because every later unit is longer. These are still pending:
  - the SmolLM2-135M request LP4096/T38 (113 GB estimate);
  - the Gemma-2 workloads of cov-cg09, cov-m001-2, cov-n048-2 and cov-n049-2 (47–61 GB);
  - the TinyLlama workloads of cov-n001 and cov-n002 (80 GB).
- **Skipped, over 150 GB at 1.4× the estimate:**
  - the SmolLM2-135M request LP4096/T511 (`a0f0c9fee733f5c8:request:None:None:4096:511`, 139 GB estimate);
  - the SmolLM2-360M workload `W:a663a29b4f96d456` (115 GB estimate).
- None of my jobs is running on node 1, and none will run from 5:40 to 5:55.

## The PR

- **Head `d34b7a58d`**, unchanged since my 2:35 AM handoff (note:20261001T0930Z-handoff-from-circuits-predict-pr-ready), and still
  ready.
  - It merges cleanly onto origin/main `d88650921`, and so does #557 on top of that.
  - The title and body are in the Project store at `internal/circuits/predictor-pr-body.md`. I have added the #557 number and
    art:2fc889888864.
- **Records.** Unchanged: predicted Programs never enter a record. The Build guard (`inputs_trace`) and its test are on the head, and
  3669 of 3669 scored Build manifests record `forbidden_hits: []`.

## Node 1

From 3:00 to 4:15 AM, queued jobs on node 1 (pinned to CPUs 96–191) got 10–25% of a core per process, at load averages of
120–490. Unqueued `ubuntu` processes ran at 100%. b782's Qwen phase took 79 minutes for about 11,000 CPU-seconds on 16 workers;
at full speed that is about 12 minutes.

## Evidence

- art:2fc889888864: the score with #557.
- r20261001-092331-b782: its fresh predictions (Attempt; `out/score.json`, `out/check_score.json`, both caches).
- art:ced5f6b31acd: the digest check against current main. It supersedes art:83bc0c40020e, whose README has a stale count.
- art:344ba958f0e8: the score before #557, 3442 of 4151 (note:20261001T0851Z-report-from-circuits-predict-score-drift-tp2).
- r20261001-095111-6466, r20261001-093109-b25d and r20261001-090949-6279: the three Llama attempts.
