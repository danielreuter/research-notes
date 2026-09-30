---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

# Making the vLLM Build cheap: measured breakdown and plan

Build-optimization lane, 2026-09-30. The method and the raw numbers are in
[build-optimization-measurements.md](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/build-optimization-measurements.md).

**Headline.**
- **Two things make the Build expensive.**
  - **Serial derives:** each request shape is derived one after another. That's 55–78% of every B ≥ 8 Build. The row already has a
    parallel option (`--build-jobs`), but the epoch ran every Build 1-wide, and so would the config run.
  - **Terms that grow with context squared:** each attention Call lists every earlier key and value row, and the word check cuts one
    attention head per key length. At 4k/512 that's ~90% of the derive's time and memory, and ~94% of the manifest.
- **Four changes cut most of it**, about 8–10 agent-days in total, with Program digests identical:
  1. parallel derives by default;
  2. a persistent word-check cache;
  3. key and value references shared as prefixes;
  4. dropping redundant work.
- **Predicted effect:**
  - #67 (OLMoE B32 1k/128): **3.9 h → ~30 min**;
  - #74 (Qwen3-4B-FP8 B8): **5.3 h → ~1.5 h**, of which the call-boundaries gate becomes the largest part;
  - #11 (Llama-3.2-1B B1 4k/512): **> 5.3 h at 124.5 GB → ~25 min at ~12 GB**.
- **A correction:** the "486 GiB" is the admission planner's uncalibrated *estimate* for #39. The largest *measured* Build peak is
  #11's derive at **124.5 GB**. By the fit below, #39's is about 220 GB.
- **671B–1T models:** they need a fifth change, deriving each distinct layer once and instantiating it (8–12 agent-days). Without it,
  one 1k/128 request of a 61-layer MoE is about 5M Calls: roughly 2 CPU-h and 45 GB per request, per rank.

## 1. Where the time and memory go

**Per stage, from the epoch's stored Builds** (main `14f027c3`, before #443; derives ran serially; seconds):

| Row | Config | Build | Derives | Manifest | Composition | Call-boundaries gate |
|---|---|---:|---:|---:|---:|---:|
| #57 | Gemma-2-2B B8 1k/128 | 9,074 | 5,672 (62%) | 2,845 | 555 | 727 |
| #67 | OLMoE-1B-7B B32 1k/128 | 13,995 | 10,718 (77%) | 2,231 | 1,041 | 3 |
| #74 | Qwen3-4B-FP8 B8 1k/128, H100 | 18,943 | 14,736 (78%) | 2,887 | 1,315 | 1,689 |
| #75 | Qwen3-30B-A3B TP2 B2 | 12,666 | ~7,500 per rank (ranks in parallel) | 4,290 | 1,796 | 2 |
| #11 | Llama-3.2-1B B1 4k/512 | > 19,033 (killed) | 7,969 | > 9,465 (killed) | 1,567 | – |

**One derive.** A fit over all 89 stored request derives, with tokens = LP + T:
- **wall** ≈ 1.4 ms per Call + 20 µs × layers × tokens²;
- **peak RSS** ≈ 2.0 GB + 6.6 KB per Call + 0.35 KB × layers × tokens²;
- **Calls** ≈ tokens × layers × *k*, with *k* ≈ 10 (plain dense) to 54 (FP8, MoE); every token row is its own Call;
- **the quadratic term's share:** at 1k/128 it's ~20% of the time and 45–50% of the memory; at 4k/512 it's 88% of the time and
  94% of the memory.

It comes from attention. Each attention Call's key and value operands list one reference per earlier token, so a 4k/512 request
holds ~340M such references. The descriptor stores them compactly as aliases, but nothing else does:
- in memory, the rule rebuilds each operand from scratch at every position;
- the encoder builds a key tuple for every reference to find each alias, and the Program is encoded three times;
- `instances.json.gz` writes every reference out;
- composition decodes them all and re-encodes;
- the manifest reads them all back.

**Inside one derive** (profile, 2-layer SmolLM2 at 1024/127):

| Part | Share |
|---|---:|
| `torch.export`, run **twice** (vLLM's export, then the derive re-exports the same module) | 29% |
| rule translation | 12% |
| the Program encoded 3× for its digests | 13% |
| writing `instances.json.gz` (every operand's runs) | 16% |
| Program validation / liveness / correspondence | 7% / 6% / 4% |
| vLLM config and meta instantiation, per shape | 8% |

On the pods, the first export alone is 5–15% of a derive.

**The manifest** (on current `main`, with #443) is 94% the strict word check cutting `AttentionHead_v3{T}` once per key length T.
That is O(T²) and independent of layers and batch:

| Context (2 layers) | 256/31 | 512/63 | 1024/127 | 4096/511 |
|---|---:|---:|---:|---:|
| Manifest CPU (s) | 35 | 123 | 473 | ~9,500 (extrapolated; #11's was killed at 9,465) |

- #443 spreads this over cores, but every config recomputes it.
- The config run's separate strict word check (#470) computes it again.
- These specializations depend only on (T, head dim, block size), so they are the same across models and configs.

**Composition** costs 0.1 ms per Call plus the same quadratic term. Loading the component descriptors is 55–75% of it.

**Duplicated work:**
- **Across shapes:**
  - every shape re-instantiates vLLM and re-exports every layer and step;
  - on B > 1 rows, the envelope request (longest prompt × largest cap) is derived but is not a workload component. It's usually the
    single largest derive: #74's is 3,534 s against 2,727 s for its largest real request.
- **Across layers:** every layer is exported and translated anew at every step.
- **Across configs:** the attention head cuts are recomputed, then recomputed again by the config run.
- **Within a derive:** two exports and three encodes.

**How each part scales:**
- **Model size:** Calls grow with layers × *k*, and the quadratic term with layers.
- **Batch:** linear in the sum of the shapes, but serial today.
- **Context:**
  - the derive and composition grow as layers × tokens²;
  - the manifest grows as T²;
  - the Match's fold has the same quadratic term (the planner's 3.4 KB per step × context × layer).

## 2. The changes that cut the most

| # | Change | Build time | Memory | Agent-days | Representation |
|---|---|---|---|---:|---|
| 1 | **Derives run in parallel by default**, sized from a per-shape memory estimate, largest first | Derive phase ÷ 4–8 on B ≥ 8 (the critical path becomes the largest shape); local B8: 736 s → 311 s on 3 cores | concurrent derives capped at 80% of headroom | 0.5 (done: [#479](https://github.com/danielreuter/verity/pull/479)) | none: each derive is its own process (10/10 digests equal) |
| 2 | **Persistent word-check cache**: unit rules keyed by the Definition's digest, the query, the gate limits and the cut code's version, shared on the host (and seedable from the store) | **Measured:** the 1024/127 manifest took 463 s cold and **7.6 s warm**, and 512/63 took 3.0 s from the same cache (123 s without); at 4k about 9,500 s → under 5 min; the config run's second word check nearly free | ~20 MB of cache per 1k context | 1 (done: [#482](https://github.com/danielreuter/verity/pull/482)) | none: the manifests are byte-identical cold, warm and uncached |
| 3 | **Key and value references shared as prefixes**, end to end: the attention rule, codec encode and decode, liveness, `instances.json.gz`, composition, the manifest reader | 4k/512 derive ÷ 5–6 and composition ÷ 3–5; 1k/128 derive −20% | 4k/512 derive ÷ ~10 (124.5 GB → ~12 GB); 1k/128 −45% | 5–7 | descriptor bytes identical, so digests identical by construction; tested against stored Builds (#101, #57, #67, #11) |
| 3a | first step of 3, no format change: encode once and reuse, alias search on verified prefix hashes, stream `instances.json.gz` | long-context derive −25–35% | peak ÷ 2–3 | 1.5 | byte-identical outputs |
| 4 | **Drop redundant work**: skip the envelope Program on B > 1 rows (**needs the coordinator's OK**: its digest is in the verdict), one export per derive, lighter `derive-report.json` | derive CPU −20–35% on B > 1; shorter critical path | – | 1–1.5 | identical Programs; the envelope skip removes one recorded digest |
| 5 | **For 671B–1T:** derive each distinct decoder layer once per step kind, then instantiate it across layers, positions and TP ranks | per-Call cost 1.4 ms → ~0.05 ms (est.) | per-Call memory ÷ 10+ (est.) | 8–12 | needs an argued equivalence per architecture, backed by digest equality against the full derive on small models |

**Tested and set aside for now:**
- **Streaming the composition:** its measured time is 6–8% of the Build, and change 3 removes its quadratic part. Its peak on B ≥ 8
  wasn't recorded on the pods, so measure it on the next pod run before building a streaming writer. Parallel component loads are the
  cheap part (+0.5 day).
- **Moving hot loops out of Python:** most per-Call cost is Python object churn. But `verity.ir` is stdlib-only, so this means an
  accelerator package checked against the reference. It's worth it only after changes 3 and 5 have shrunk what's left to run.
- **The per-(model, shape) Program cache** (#470, the epoch-run lane): mixed lengths are seeded per row id, so configs share only the
  envelope and repeated runs. It helps re-runs, not the first run of a config.

**Predicted Build per config after changes 1–4** (16 vCPUs, #443 on main):

| Row | Today | After | Largest remaining part |
|---|---|---|---|
| #67 OLMoE B32 1k/128 | 3.9 h | ~30 min | composition (~14 min) |
| #74 Qwen3-4B-FP8 B8 1k/128 | 5.3 h | ~1.5 h | call-boundaries gate (28 min: the S1b plan's population, cacheable with the manifest) |
| #11 Llama-3.2-1B B1 4k/512 | > 5.3 h, 124.5 GB | ~25 min, ~12 GB | derive (~17 min) |

## 3. Order and coordination

- **Done, as draft PRs:**
  - **Change 1**, [#479](https://github.com/danielreuter/verity/pull/479): the top change by cut per effort, and what the
    config-sweep plan's "Build 20–40 min" assumed. It touches `row_records.py` and one line each of `row_stages.py` and `config.py`.
    None of those lines overlap #470 (`git merge-tree` is clean). The two complement each other: the cache fills derived dirs, and the
    parallel derives skip them.
  - **Change 2**, [#482](https://github.com/danielreuter/verity/pull/482), in `query/word.py`. The config run should set
    `VERITY_UNIT_RULE_CACHE` beside `PROGRAM_CACHE`, and a pod-wide default can follow once #470 lands.
- **Then 3a, then the rest of 3:** core `verity.ir` codec and liveness, the frontend's attention rule, `build.py`, `global_program.py`,
  and the manifest's reader, one PR per layer, each byte-identical on the stored Builds.
- **Change 4:** the envelope skip waits on the vLLM coordinator's answer (asked in its lane). The other two parts are independent.
- **Change 5** starts when the 671B–1T models are scheduled. It also needs TP > 2, which the IR doesn't model yet.
- **No pod spend** is needed for changes 1–3. The first pod-scale check of each should ride an already-approved config run.

## 4. Overnight, 30 Sep: the Build benchmark (workstream 1 of `docs/overnight-objectives.md`)

**The benchmark:**
- **Machine:** `vy-nebius-1`. Each attempt is pinned to 32 CPUs from the steward's map:
  - 128–159 is this lane's;
  - 96–127 is lent until build-v2-kv starts.

  Independent attempts run side by side, one per range. Other lanes share the machine, so results carry `ov.noisy=true`; the quiet hour
  re-measures the best attempt.
- **Isolation:** each run has a private `TMPDIR`. See "One manifest pool per host" below.
- **Configs:** `llama32-1b` (small dense), `mistral-7b` (mid dense) and `olmoe-1b-7b` (MoE), all BF16 with the L40S target declared in the
  workload. Each has two workloads, both B8:
  - prefill: I512 O2, one decode step per request;
  - decode: I32 O128.
- **Added 11:25Z, a build-v2 target:** `llama32-1b-1k`, Llama-3.2-1B at B8 I1024 O128. The sweep's Build of this shape took 28 minutes
  and peaked at 17 GiB, against about 4 minutes at batch 1:
  - derives, serially, were 80% of it, and the longest single derive is the envelope request at LP1024 T127 (596 s);
  - composition was 16%;
  - the manifest was 4%.

  Its baseline and attempt 7 run after the quiet hour.
- **What an attempt runs:** each row's real Build stage (`verity-vllm row run --stages build`) on a precompiled tree.
- **Metrics per row:** throughput = the workload Program's gates / Build wall; peak RSS of the Build's process tree; bytes per gate; Build
  wall and CPU.
- **Gate:** `ov.gate=pass` only when the Build completed and every Program, workload and manifest digest equals the baseline's.
- **Tooling:** copies are in `internal/build-benchmark/` of the Project store. Each measurement is labelled once, as it lands, on its run
  with `--ref config/phase/metric`.
- **The warm rule cache:** attempts 3–7 read one unit-rule cache, pre-warmed once from the baseline's Programs (run
  `r20260930-073754-20bf`, 2,609 rules). The pre-warm reproduced all six manifest digests. Attempt 2 starts from an empty cache.

**Attempts on line `build-v1`** (each adds to the previous; digests must be identical):

| # | Change | PR |
|---|---|---|
| 0 | baseline: `main` b82f1dd2, serial derives | – |
| 1 | derives in parallel by default (auto, memory plan) | [#479](https://github.com/danielreuter/verity/pull/479) |
| 2 | unit-rule cache, cold | [#482](https://github.com/danielreuter/verity/pull/482) |
| 3 | unit-rule cache, warm (pre-warmed once, shared) | #482 |
| 4 | one `torch.export` and one digest encode per derive | [#489](https://github.com/danielreuter/verity/pull/489) |
| 5 | no FX stack traces; composition digests each component once | #489, [#497](https://github.com/danielreuter/verity/pull/497) |
| 6 | `instances.json.gz` streamed with the C JSON encoder | [#493](https://github.com/danielreuter/verity/pull/493) |
| 7 | composition runs beside the derives (`global-program --follow`) | #497 |

**Baseline (attempt 0)**, run `r20260930-053403-c8cb`:

| Row | Build | Throughput (gates/s) | Peak | Bytes per gate |
|---|---:|---:|---:|---:|
| Llama prefill | 585 s\* | 2.1×10^8 | 3.8 GiB | 0.033 |
| Llama decode | 1,297 s | 3.9×10^7 | 2.8 GiB | 0.060 |
| Mistral prefill | 848 s | 9.7×10^8 | 6.4 GiB | 0.008 |
| Mistral decode | 1,882 s | 1.4×10^8 | 4.3 GiB | 0.018 |
| OLMoE prefill | 1,161 s | 1.3×10^9 | 5.8 GiB | 0.004 |
| OLMoE decode | 2,583 s\* | 2.2×10^8 | 4.6 GiB | 0.009 |

\* Two rows are re-measured in `r20260930-081207-306c`. The labels' `ov.note` says so on each affected point:
- Llama prefill includes first-derive bytecode compilation; without it the row took 552 s. The runner now precompiles.
- OLMoE decode's manifest step took 331 s, against 15–40 s on the other rows, waiting on the host-wide lock below.

**One manifest pool per host.** `manifest build-global` builds its components in a process pool under an exclusive `flock` on
`$TMPDIR/verity-manifest-build-components.lock` (`manifest._pool_lock`). The lock stops two pools from budgeting the same memory
headroom twice. On a shared host, though, every concurrent Build's manifest step queues behind whichever holds it: other rows, other
lanes' test suites, or a pre-warm. Two runs were hit:
- attempt 1's first row waited about 330 s, against a 23 s manifest step;
- the baseline's OLMoE decode waited about 290 s.

The benchmark now gives each run a private `TMPDIR`. For the sweep, which packs several Builds onto one host, the lock serializes every
row's component phase. A shared memory reservation, where each pool takes only its estimated peak, would remove the queue and keep the
bound.

**Commit on the RTX PRO 6000 (queued):**
- **What runs:** one Kueue job per benchmark config and workload, each on 1 GPU, using `config-run-row` with `CONFIG_RUN=1`:
  - the Build;
  - one instrumented Commit, with no control arm;
  - the 460-unit replay.
- **Tree:** `cursor/commit-bench-rtxpro-6942`, which is the sm_120 pre-merge `598c2a53` plus `infra/nebius` plus the six workloads as
  rtxpro6000 rows. Their seed is the row id, so their prompt lengths differ from the L40S rows'.
- **Per row:**
  - Commit time, the timeline's `stage.commit`;
  - throughput, the workload Program's gates per Commit second;
  - peak host RSS and peak GPU memory, from the run's own telemetry inside that window.
- **Labels:** `ov.phase commit` and `ov.gpu rtx-pro-6000`.
- **Two ways it failed first:**
  - on this tree a CPU-only Build task can't start vLLM (an empty device string), so the Build has to run in the GPU pod;
  - `config-run-row` needs the job paths (`PY`, `SWEEP_DIR`, …) passed as `--env`.

**Next (build-v2):** decode rows are bound by one derive, and `torch.export` is 60% of a T=127 derive, because every decode step of every layer
is traced. Deriving one decode step per layer and instantiating it across layers and positions is the change that removes that.
