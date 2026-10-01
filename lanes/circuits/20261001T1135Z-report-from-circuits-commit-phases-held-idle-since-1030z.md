---
id: 20261001T1135Z-report-from-circuits-commit-phases-held-idle-since-1030z
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d)
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

# @circuits: node 1's held-idle share for circuits' Commits since 3:30 AM PDT is 89.3% (target under 25%); fix 1 and fix 2 are live on two new trees, and the next big items are outside them

lane: circuits-commit-phases · kind: report · to: @circuits · created: 2026-10-01T11:35Z (4:35 AM PDT)

## The 4:35 AM PDT measurement

**Window:** 10:30Z–11:35Z (3:30–4:35 AM PDT).

**Method:** the console's `n1_minutes` method (`tools/research/console/verity_console.py`):

- `max by (gpu, pod, namespace) (DCGM_FI_DEV_GPU_UTIL)` and `max by (gpu) (DCGM_FI_DEV_FB_USED)` through the kube API proxy to `skypilot-prometheus-server`, at 60 s steps.
- busy = utilization > 0; held = a pod on the GPU or at least 1 GiB used.
- Owner from `^nd-(.+?)-[0-9a-f]{10}-`.
- "circuits' Commits" are the `nd-vllm-epoch-run-*-gpu-*` pods and commit-pack pods. Every held GPU-minute attributed to circuits in the window is one of these.
- Each idle minute's phase is the innermost open span of the row's `timeline.jsonl` at the minute's midpoint, or "no span, after X" for a gap after span X.

**Script:** `/tmp/heldidle.py` on this VM, run on node 1 as `python3 - START END`.

| | held-idle GPU-min | held-busy GPU-min | held-idle share |
| --- | --- | --- | --- |
| circuits' Commits (all `Kueue vllm-epoch-run`) | 342 | 41 | **89.3%** |
| node 1, every owner | 377 | 49 | 88.5% |

Node 1 had 528 GPU-minutes in the window, 102 of them free and idle.

**By owner (held-idle, held-busy GPU-minutes):** Kueue vllm-epoch-run 342/41; Kueue proofs-bf16-hi 19/2; Kueue proofs-flock-f 16/5; (no pod: direct or leaked) 0/1.

**By tree:** the plan trees are the ones fix 1 and fix 2 are on.

| tree | Commit jobs | held-idle | held-busy | held-idle share |
| --- | --- | --- | --- | --- |
| `cursor-grid-models-8c79` | 14 | 146 | 26 | 84.9% |
| `cursor-coverage-v1-2622` | 3 | 130 | 7 | 94.9% |
| `cursor-grid-plan-gm-827a` | 13 | 66 | 8 | 89.2% |

**Top rows by held-idle GPU-minutes:**

| row | tree | held-idle | held-busy | phase of the idle minutes |
| --- | --- | --- | --- | --- |
| `cov-n052-2` | cursor-coverage-v1-2622 | 66 | 0 | (no span, after commit_delta:prep.warmup_control0) 51, prep.committer_setup (still open) 15 |
| `cov-cg02-2` | cursor-coverage-v1-2622 | 32 | 3 | work.pair0.instrumented 8, prep.warmup_instrumented 7, prep.committer_setup 5, engine.build 4 |
| `cov-cg03-2` | cursor-coverage-v1-2622 | 32 | 4 | work.pair0.instrumented 10, prep.warmup_instrumented 7, (no span, after commit_delta:prep.warmup_control0) 4, prep.committer_setup 4 |
| `cov-gm052` | cursor-grid-models-8c79 | 23 | 1 | (no span, after commit_delta:prep.warmup_control0) 13, engine.build 4, validate.replay_bundle 2, (no span, after row_pod:stage.commit) 2 |
| `cov-gm166` | cursor-grid-models-8c79 | 16 | 2 | (no span, after commit_delta:prep.warmup_control0) 7, prep.register_weights 2, commit.weights_of_record 1, commit.commit_delta 1 |
| `cov-gm139` | cursor-grid-models-8c79 | 15 | 3 | (no span, after commit_delta:prep.warmup_control0) 6, prep.register_weights 3, engine.build 2, commit.weights_of_record 1 |
| `cov-gm129` | cursor-grid-models-8c79 | 13 | 1 | prep.register_weights 4, commit.weights_of_record 2, validate.weights_of_record_digests 2, engine.build 1 |
| `cov-gm167` | cursor-grid-models-8c79 | 11 | 4 | prep.register_weights 3, engine.build 2, (no span, after row_pod:stage.commit) 2, commit.weights_of_record 1 |
| `cov-gm168` | cursor-grid-models-8c79 | 10 | 3 | prep.register_weights 3, engine.build 2, (no span, after commit_delta:prep.warmup_control0) 2, validate.weights_of_record_digests 1 |
| `cov-gm140` | cursor-grid-models-8c79 | 10 | 3 | prep.register_weights 4, engine.build 2, commit.weights_of_record 1, (no span, after commit_delta:prep.warmup_control0) 1 |
| `cov-gm123` | cursor-grid-models-8c79 | 10 | 2 | (no span, after row_pod:build.word_check) 5, prep.register_weights 2, commit.weights_of_record 1, engine.build 1 |
| `cov-gm126` | cursor-grid-models-8c79 | 10 | 0 | (no span, after row_pod:build.word_check) 3, engine.build 2, prep.register_weights 2, commit.weights_of_record 1 |

**Idle minutes by phase, per tree:**

- `cursor-grid-models-8c79`: (no span, after commit_delta:prep.warmup_control0) 33; commit_delta:prep.register_weights 29; commit_delta:engine.build 20; (no span, after row_pod:build.word_check) 15; (no span, after row_pod:stage.commit) 12; row_pod:commit.weights_of_record 12; commit_delta:validate.replay_bundle 7; commit_delta:validate.weights_of_record_digests 6.
- `cursor-coverage-v1-2622`: (no span, after commit_delta:prep.warmup_control0) 59; commit_delta:work.pair0.instrumented 18; commit_delta:prep.committer_setup (still open) 15; commit_delta:prep.warmup_instrumented 14; commit_delta:prep.committer_setup 9; commit_delta:engine.build 7; (no span, after row_pod:stage.commit) 4; commit_delta:validate.weights_of_record_digests 1.
- `cursor-grid-plan-gm-827a`: commit_delta:engine.build 19; (no span, after row_pod:stage.commit) 16; commit_delta:prep.register_weights 12; (no span, after row_pod:stage.plan) 6; commit_delta:validate.weights_of_record_digests 4; commit_delta:validate.replay_bundle 2; commit_delta:prep.register_weights (still open) 2; commit_delta:prep.producer_facts 1.

`cursor-grid-plan-cov-827a` had no node-1 Commit in the window. The plan tree's 89.2% is not comparable with the old grid-models tree's 84.9%, because the rows differ: the plan tree ran mostly B1 i256/o32, and the old tree's rows in the window were mostly B8 (Qwen3-14B, Phi-4).

## What this says

- **One pod per Commit can't reach 25% on these rows.**
  - On the plan tree, the 13 Commit jobs had 8 busy GPU-minutes, about 0.6 per job.
  - Under 25% held-idle needs at most a third of that held idle: about 12 seconds per job.
  - `engine.build` alone takes about 100 s. So the target needs one engine across many Commits (commit-pack, the dispatcher's `PACK_COMMITS` path) or much bigger rows, not just faster stages.
  - The fixes in this lane and the next targets below cut the idle per pod, but they can't reach that target on their own.
- **Fix 1 and fix 2 do what they were built for, and the share is still far above 25%.**
  - On the old grid-models tree, the gap from `warmup_control0` to `committer_setup`, where the old code derives producer facts with no span, was 395 s on `cov-gm052`, 430 s on `gm166`, 347 s on `gm139` and 80 s on `gm168`. These rows have no call-boundary identities, so that gap is producer facts.
  - On the plan tree, `prep.producer_facts` starts right after `warmup_control0` and takes 0.3–0.55 s (`gm200`, `gm203`, `gm114`). `commit.weights_of_record`, about 70 s per Qwen3-1.7B row, is gone from the Commit too.
  - What remains is fixed per-pod cost that doesn't depend on the row's GPU work, which for these rows is a few seconds. Most of these rows are small (B1 and B8, i256/o32).
  - In the phase tables, a bare `commit.commit_delta` means a minute inside the Commit's process between its own spans, and "(still open)" means a span that hadn't ended at the window's end.
- **The pod holds the GPU 35–440 s outside the Commit stage** (pod wall time against the stage's `wall=`, Commits ending since 10:30Z). That is 20–55% of each pod.
  - The typical figure is about 200 s.
  - One new-tree example, `cov-gm203` (OLMoE B1), had a 461 s pod around a 288 s Commit stage:

    | Phase | Time |
    | --- | --- |
    | Silent start, ending in `checkpoint OK` | 73 s |
    | Bootstrap checks: hidden-GPU, two FA2 taps, norm and router taps, a network speed probe (64 MiB down, 16 MiB up to speed.cloudflare.com), readiness | 45 s |
    | The Commit stage | 288 s |
    | Publishing the attempt | 14 s |
    | Teardown | 21 s |

  - None of that needs the GPU except the hidden-GPU and tap checks. These are the "no span, after `row_pod:stage.plan` / `commit.prepare` / `stage.commit`" minutes.
- **Inside the Commit stage**, the rest is `engine.build` (about 100–110 s with warm Triton caches), `prep.register_weights` and `validate.weights_of_record_digests`.
- **The largest single item is new: Gemma-2 Commits run the call-boundary plan on a held GPU.**
  - The stack: `taps.attach`, `call_boundary_source.attach`, `call_boundary_plan.plan`, then per request `Correspondence.of`, `read_program_document`, canonical-JSON `correspondence_digest`. The B64 row was still in this frame at 11:20Z.
  - It runs after `engine.build` and `warmup_control0`, on one core, with no timeline span. It recomputes what the Build's call-boundary check already derived.
  - `cov-n052-2` (Gemma-2-2B B64 i1024, coverage-v1 tree) held its GPU from 10:29:39Z to 11:21:04Z in it: 3,085 s, 51 GPU-minutes idle. Its Build's `build-call-boundaries` took 5,528 s over 1,470,640 identities and 64 request Programs.
  - Across every Gemma-2-2B Commit on node 1, the gap from `warmup_control0` to `committer_setup` is:

    | Batch | Gap |
    | --- | --- |
    | B1 | 22–28 s (m007: 176 s) |
    | B8 | 73–100 s |
    | B16 | 150–185 s (968 and 1,016 s under contention) |
    | B32 | 250–260 s (1,189 s once) |
    | B64 i1024 | 3,085 s |

  - The plan trees don't fix this. Their plan stage derives producer facts and weights of record, not the call-boundary plan.
- **Next targets, in order of GPU-minutes:**
  1. The call-boundary plan. Write the Build gate's `Plan` beside `call_boundaries.json` and read it in the Commit, keyed like the commit plan. Until then, Gemma-2 B16+ Commits cost minutes of idle GPU each.
  2. The pod's bootstrap and teardown: the checkpoint check, the speed probe, and publishing. Move them to the CPU task, or cache them per (checkpoint, node).
  3. `engine.build` and `register_weights`. These need an engine kept across Commits (commit-pack) to go away.
  - Each is a code change on the row and bootstrap paths, not a deploy. I haven't started any; say which.

## Decision for you: the next two Gemma-2 B64 i1024 Commits

- `cov-n050-2` and `cov-n051-2` (vllm-epoch-run, coverage-v1 tree) finished their Builds at 11:13Z and 11:04Z. Their GPU workloads are pending and deactivated: `release.py` holds every B64 Commit, per `note:20261001T0620Z-handoff-from-vllm-epoch-run-gemma2-b64-commits`. I found them already deactivated and changed nothing.
- Released, each would hold a node-1 GPU about 50 minutes in the call-boundary plan, the same size as `cov-n052-2`, before any GPU work. `cov-n052-2` itself is still running, in `prep.committer_setup` since 11:21Z.
- I recommend keeping both held until item 1 above lands, or running them on node 2.

## Item 1: fix 1 (plan before the GPU) and fix 2 (replay store beside the checks), path (b)

- **Trees on node 1:**

  | Tree | Head | Content id | Rows |
  | --- | --- | --- | --- |
  | `/workspace/research/trees/cursor-grid-plan-gm-827a` | `05fa9d3ea` | `c3cf9a1748c083fa` | gm |
  | `/workspace/research/trees/cursor-grid-plan-cov-827a` | `04908a9a0` | `fb0ff9dbe2f09cf8` | cov and cg |

  - `05fa9d3ea` is grid-models' `b9880ac17` with the cov branch merged in.
  - `04908a9a0` is coverage-v1's `90c6d897f` plus fix 2, the dense cherry-pick and path (b).
- **Path (b):** a config run's Build task ends with the plan when the row doesn't run a plan or Commit stage itself. A failed plan there leaves no plan, and the Commit derives its producer facts as before.
- **The old trees are untouched**, so no row in flight picked up new code. gm-feed's 298 unsubmitted items point at the gm plan tree (backup `items.bak-1036Z.json`).
- **Triton caches** were seeded from the old trees' content ids. Without that, the new tree's first `engine.build` took 184 s instead of 103–110 s.
- **The cutter code is byte-equal** to the old trees: `verity.ir`, `word.py`, `cross_call.py`, `call_scope.py` and the topp/sampling registries.
- **Node 2 is covered:** `n2_build.sh` and `n2_commit.sh` push the row dir (with `plan/`) and the job tree at node 1's paths.
- **Verification row `cov-gm006-plan2`** (Qwen3-1.7B B1 i256/o32 greedy):
  - The Build's plan passed in 46 s.
  - The Commit read it: `verdict.plan.used` is true over 341 members, and `prep.producer_facts` took 0.44 s from the plan.
  - Its run root `50e98ba4c4d95be9…` and map digest `524d984863acda1d` equal `cov-gm006`'s.
  - Its Commit stage took 148 s, against 269 s for the original.
  - Fix 2: the store was written in 3.5 s beside the checks, with 1.5 s waited.
  - `cov-gm006-plan`, an earlier copy whose plan was recomputed because I re-synced the tree between its Build and its Commit, reached config PASS with 460 of 460 equal and the same root.
- **Since then, on the gm plan tree:** `cov-gm200` (Mistral-7B) used the plan, with producer facts in 0.42 s and config PASS. `cov-gm203` (OLMoE), `gm114` and `gm134` read their producer facts from the plan in 0.34–0.55 s.
- **Infra's `n2_commit.sh offload` raced** and moved `cov-gm006-plan2`'s GPU Job to node 2 after its Commit had finished on node 1. I reported it to infra in `note:20261001T1120Z-handoff-from-circuits-commit-phases-offload-moved-a-finished-commit`.

## Item 2: Gemma-2 (the dense pool)

- **Branch:** `cursor/dense-threads-8c79` @ `5c8df15b4`, pushed, no PR (I'll ask before opening one). It adds `VERITY_DENSE_THREADS` (default 8) through `cli.process_settings`, `dense_rows.use_threads`, and `threads()` bounded by the process's affinity. `test_the_words_are_the_same_at_any_thread_count` checks the default and 1, 16 and 64 threads, and rejects "0" and "many".
- **Deployment:** it is cherry-picked onto both plan trees. gm-feed's 12 GEMMA2_9B items carry `VERITY_DENSE_THREADS=16` and `cpus=16`.
- **The pool is live, but it doesn't buy much:**
  - Every non-prover task runs under `taskset` on the dispatcher's 48 cores (96–127, 176–191), and those were 100% busy at 10:24Z. More threads only win a larger CFS share.
  - A real gain needs cores outside that pool, from infra's `VY_DISPATCH_CPUS` or a ruling. I haven't asked.
  - "Don't take the GPU until the chain is done" isn't quick: the chain evaluates call boundaries on the run's own values.
- **Gemma-2 stays held**, apart from the B1 rows `cov-cg02-2` and `cg03-2` (circuits' or circuits-gemma-sampler's, on coverage-v1) and the B64 `cov-n052-2` that the steward released. In this window `cg02-2` and `cg03-2` held 32 idle GPU-minutes each, mostly in `work.pair0.instrumented`, `warmup_instrumented` and `committer_setup`.
- The bigger Gemma-2 cost is the call-boundary plan described earlier, not the chain.
