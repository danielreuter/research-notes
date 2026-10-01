---
id: 20261001T0851Z-report-from-circuits-predict-score-drift-tp2
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-predict
---

# circuits-predict -> @circuits: predictor vs every traced Build, 3442 of 4151 units exact on main's code; all 709 differing units are tree drift, and the 700 coverage-v1 ones are 700 of 700 exact on their trees' code; TP2 now covers every traced family

**Branch** `cursor/vllm-predictor-8c79`, head `f6697c66e` (pushed). No PR opened; I'll ask first, since Circuits is at 7 open PRs.

**Evidence**
- art:344ba958f0e8: the final score (`score.json`, `score.md`, the merged cache, `first_divergences.txt`). It supersedes
  art:b853cdd8b211, which predates the last Gemma-2, TinyLlama and Qwen3-30B workloads and the last located divergences.
- art:aa54edf143d7: the drift re-score.
- art:94c14d2b4f26: label corpus v0.

## Your four asks (10:55 PM PDT)

1. **Pushed and checkpointed** after every step; the checkpoints are in `lanes/circuits-predict/`.
2. **Label corpus v0 = art:94c14d2b4f26** (preserved). It holds the 202 config records whose replay passed 460/460 on node 1:
   193 distinct rows, 190 TP1 and 12 TP2, across 13 models, including Gemma-2 cg01/cg08/cg12/cg13/cg14 and TP2
   p000/p004/p012/p016/p047. Each record has the workload Program digest (per rank at TP2), the request and step digests, the
   config, the verdict, the run roots, and the Build and Commit run ids.
3. **Drift, Gemma-2 and TP2.**
   - **Drift.** On main's code, every unit traced on a current tree that still differs is Qwen2.5 (0.5B, 1.5B and 7B, at TP1
     and TP2): 41 rows and 700 units (606 request, 47 step, 47 workload).
     - **Where they were traced.** Every one comes from one of six trees in the coverage-v1 lineage: `95aefc40`, `42f0cc44`,
       `41c52fef`, `41165cd4`, `cdd0564f` and `e8f9f515`. Those are commits `b3a7fde23`, `5bab849b1`, `cad0dff38`,
       `9d7189faf` and `7db8c4554` on `cursor/coverage-v1-2622`, and `79e7cce87` on `commit-tokens-on-coverage-v1-2ffa`.
     - **Why they differ.** All six trees carry `3dbcc9040`, which writes the biased q/k/v linear as `GemmBias_v2{K,N,DOT}`.
       Main (`4e2a7abcd`) still writes `Gemm_v2` then `BiasAdd_v1` on rtxpro6000. The predictor follows the tree it runs on
       (`gemm_bias_role` reads `registry.targets.gemm_bias_dot` where the tree has it).
     - **Re-scored on the trees' own code.** I ran the same predictor on coverage-v1 `5bab849b1` (a scratch commit
       `92849f82a`, shipped only to node 1, never pushed). Result: **700 of 700 units and 41 of 41 rows exact** across all six
       trees (r20261001-070751-89e2, art:aa54edf143d7).
     - **Main-tree traces.** Only one of the 37 drift configs has a trace off those trees: Qwen2.5-0.5B B1 256/32 on
       cov-k03-7, which is exact on main's code (3 of 3 units). The other 36 have no main-tree trace. Once `3dbcc9040` reaches
       main, its code predicts them as the drift run shows. Until then, settling them on main needs one main-tree Build per
       config.
     - **The other 9 differing units** are on 3 rows (cov-k01-9, cov-k04-6 and cov-k03-6) traced on old `ce1b86e4-head`
       trees, which have `Attention_v2` where current code has `_v5`. Newer traces of the same configs (cov-k01-10, cov-k04-7
       and cov-k03-7) are exact.
   - **Gemma-2** (soft-caps, normalizer, tied embeddings).
     - TP1 was already covered: cov-k06-5 is pinned, and all 615 traced Gemma-2 TP1 units are exact across 33 rows.
     - TP2 is now covered too (`25e6752b9`). cov-p058-2 has 6 of 6 units exact: step, request and workload on both ranks.
     - The normalizer scales the reduced embedding and the soft-cap acts on the gathered logits. Lifting the refusal was
       enough; no new construction was needed.
   - **TP2** (`889306669` and `f6697c66e`) now covers every family that has a TP2 trace: the dense families, Gemma-2, the fused
     MoE (Qwen3-30B-A3B) and OLMoE.
     - Under the fused MoE, each expert's width is sharded, the router and the experts stay whole, and the routed sum is
       all-reduced.
     - OLMoE's q/k norm over all heads all-gathers q and k, norms each row whole, then keeps this rank's slice.
     - **Every TP2 unit compared is exact**: 212 on main's code, and Qwen2.5's 64 on coverage-v1's code. That includes all 38
       Gemma-2 and MoE units (cov-p058-2, cov-p069, cov-p073-3 and cov-p081).
     - `tests/predict` pins the rank steps of Llama-3.2-1B, Gemma-2-2B, Qwen3-30B-A3B and OLMoE. All 43 tests pass.
     - Still refused at TP: stochastic sampling (no TP2 stochastic row was traced), world 4, and uneven head or vocabulary
       splits.
4. **This report** (2:05 AM PDT).

## Score: main's code (`f6697c66e`) over all 326 inventoried rows on node 1

**Headline numbers**
- 4151 units compared; 3442 are exact, and all of those are equivalent by digest.
- 709 differ: 700 are coverage-v1 drift and 9 are old-tree traces.
- 282 rows have a compared unit, and 238 of them are all exact. Every one of the other 44 rows is drift (41 coverage-v1 rows,
  3 old-tree rows).
- On the code each unit was traced on, 4142 of 4151 are exact. The 9 that aren't are the superseded old-tree traces.

**First divergences.** I located them for 301 of the 659 differing step and request units (r20261001-084105-ed67, plus the
TinyLlama shard r20261001-071553-eaf3). Only two causes occur:
- 296 units: the definitions differ. Predicted: `BiasAdd_v1` and `Gemm_v2`. Traced: `GemmBias_v2` and
  `GemmBiasCoordinate_v2`. All are on coverage-v1 trees.
- 5 units: the definitions differ. Predicted: `Attention_v5` and `AttentionHead_v5`. Traced: `Attention_v2` and
  `AttentionHead_v2`. All are on the old trees.

The 358 unlocated units sit on the same trees and are exact on those trees' code. Workloads aren't diverged separately (the 50
differing workloads are made of differing requests).

| model | rows | rows all exact | units compared | exact | differ: coverage-v1 drift | differ: old tree | not run / over budget | no trace |
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
| qwen25-05b | 19 | 1 | 329 | 3 | 323 | 3 | 0 | 2 |
| qwen25-15b | 12 | 0 | 228 | 0 | 228 | 0 | 0 | 10 |
| qwen25-15b TP2 | 3 | 0 | 32 | 0 | 32 | 0 | 0 | 0 |
| qwen25-7b | 8 | 0 | 85 | 0 | 85 | 0 | 0 | 0 |
| qwen25-7b TP2 | 3 | 0 | 32 | 0 | 32 | 0 | 0 | 0 |
| qwen3-30b-a3b | 16 | 16 | 115 | 115 | 0 | 0 | 0 | 1 |
| qwen3-30b-a3b TP2 | 3 | 1 | 6 | 6 | 0 | 0 | 0 | 22 |
| qwen3-4b | 15 | 14 | 172 | 172 | 0 | 0 | 0 | 2 |
| qwen3-4b TP2 | 5 | 3 | 32 | 32 | 0 | 0 | 0 | 22 |
| qwen3-4b-fp8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| smollm2-135m | 32 | 30 | 406 | 403 | 0 | 3 | 2 | 4 |
| smollm2-360m | 21 | 20 | 365 | 365 | 0 | 0 | 1 | 2 |
| tinyllama-11b | 28 | 25 | 483 | 480 | 0 | 3 | 2 | 4 |
| tinyllama-11b TP2 | 6 | 2 | 26 | 26 | 0 | 0 | 0 | 30 |
| **all** | **326** | **238** | **4151** | **3442** | **700** | **9** | **10** | **264** |

"Rows all exact" counts rows that have a compared unit, all of them exact. The 264 no-trace units come from Builds that left no
Program:
- 206 are TP2 rows on trees `941aa910` and `dac5abd8`, where vLLM's `ParallelConfig` validation rejects world size 2.
- 33 are Pythia-160M, whose rotary-embedding mutation the frontend refuses.
- 18 failed with "Device string must not be empty".
- the rest are Qwen3-4B-FP8 and others.

## What's left

- **10 units not predicted yet.** The Gemma-2 (r20261001-061329-0720), TinyLlama (r20261001-071553-eaf3) and
  locating (r20261001-084105-ed67) shards finished cleanly; every unit they predicted is exact or old-tree.
  - 4 Gemma-2 workloads (cov-cg09, cov-m001-2, cov-n048-2 and cov-n049-2): their rows reached the inventory after 0720
    started, so no shard was given them.
  - 2 TinyLlama B64 workloads (cov-n001 and cov-n002): estimated at about 80 GB, over eaf3's 74 GB cap.
  - 1 Llama-3.2-1B request (LP 4096 / T 511, about 74 GB estimated): never run, because eaf3's cap left it out.
  - 3 units over the 100 GB cap: two SmolLM2-135M LP 4096 requests (estimated 139 and 113 GB) and one SmolLM2-360M
    workload (115 GB).
  - One more node job settles all 10, given a larger cap and whatever memory node 1 can spare.
- **36 drift configs have no main-tree trace.** One main-tree Build each settles them on main, or `3dbcc9040` landing on main
  makes main's code predict them (exact per art:aa54edf143d7).
- **358 differing units have no located first divergence** (over the locating budget). They are on the same trees as the 301
  located ones and are exact on those trees' code. r20261001-061352-4f7e is still running and locating more of the
  Qwen2.5 ones.
- **The branch is not in a PR.** Opening one waits on your go-ahead.

## Incidents and friction

- At 11:39 PM PDT (06:39Z) the wave-3 shard r20261001-061345-57ab (SmolLM2, Llama-3.2 and TinyLlama TP1 workloads) got a
  SIGTERM 26 minutes in; nothing records a cause. Its requeue (r20261001-070823-a316) showed the scorer's ordering cost: every
  request is predicted before any workload, so one LP 4096 / T 511 request held up all 65 workloads. I stopped my own a316 by
  its process group and relaunched it with a 74 GB cap as r20261001-071553-eaf3.
- Friction for the scorer: interleave workloads with requests, or schedule all tasks by estimated cost.
- Scoring coverage-v1 traces needed main's `tools/cluster` and `tools/research` in the scratch tree. The coverage-v1 tree
  predates `research run --queue`.
- Friction for the scorer: a cache entry is keyed by φ, not by the predictor's code. When I merged the shard caches, the
  "unexpressible" entries the 06:13Z shards wrote before the Gemma-2 and MoE TP commits overrode the newer predictions for 30
  units, until I put the newest cache last. Adding the predictor's tree to the key, or rejecting entries from another tree
  under `--cached-only`, would make this impossible.
