---
cursor:
  subagentId: "bc-1a23b70c-8ce6-52de-9b80-c005acb94607"
---

# Moving faster on Pearl-C kernels: what to adopt, borrow and build

30 Sep 2026, 16:20Z; [the pilot's result](#the-pilots-result) added at 18:37Z. For Daniel. An evaluation of [TIRx-harness](https://github.com/mlc-ai/TIRx-harness), [z.ai's GLM infra-agent post](https://z.ai/blog/glm-built-its-inference-infrastructure) and the tools around them, against how the sm_120 lanes actually iterate today. It is aligned with the [vLLM integration API](vllm-integration-api.md) (bc-f4e8ae34, 16:00Z). No GPU was used. The wider survey, with every source, is in `internal/pouw/kernel-tooling-landscape.md`.

## Verdict

**Adopt no external kernel platform. Borrow a handful of ideas, and build three small things on tools we already have.**

What makes our kernels hard is what these tools don't do:
- bit-exact arithmetic on sm_120's `mma.sync`;
- a verifier that must accept the timed run's own transcript;
- an objective in two dimensions: the slowdown, subject to γ ≤ 1% at both FP32 prices. γ itself depends on the kernel's measured instruction prices, such as 8.72 against 32.06 W1 per cast code.

TIRx-harness fails on each of these:
- **No sm_120 target.** Its repository has no `sm_120` string; its kernels target sm_100a, sm_103a, sm_107a and sm_110a.
- **Its simulator isn't bit-exact.** NumSim models FP8 `mma.sync` as a chain of binary32 FMAs. That disagrees with our captured sm_120 E4M3 step on 37% of k32 steps with Gaussian operands, and on 58% with full-range codes (the CPU check below).
- **Its correctness checks are tolerances,** not bits.
- **Adopting it means rewriting every kernel** in TIRx-lite.

It was also released yesterday.

**Our evaluation contract is already stricter than any public harness.** That includes TIRx, KernelBench v0.1, robust-kbench and NVIDIA's SOL-ExecBench. What slows us down is elsewhere:
1. **The contract lives in several places,** only partly in code. It is spread over #491's harness, #540's own gates and pipeline, and six or so lane benches, plus rules in `add-a-row.md`, `brief.md` and `server.md`.
2. **"What's been tried and why" is prose.** It fills about 580 KB of lane status files and 123 KB of panel descriptions. None of the panel's 218 rows names a parent attempt, and negative screening results rarely get a row at all.
3. **The one-GPU inner loop runs outside the contract.** It happens in lane benches and node 2's fill queue, whose outputs reach the evidence store only when someone preserves them.
4. **Operational lessons are learned again in every lane.**

All four can be fixed with code we mostly have. The fixes also let agents search on their own later, which is what makes TIRx and z.ai fast.

## Top recommendations

1. **The harness writes the attempt ledger, keyed by the vLLM API's `KernelVariant` id.**
   - Every run at every tier emits one record per (variant, shape) into the evidence store. The record holds the parent variant, the harness and gate versions, the metrics, the per-group time split, γ at both prices, and the verifier's lines.
   - The agent adds two one-liners: the hypothesis before the run, and the outcome with its reason after.
   - `panel.py` renders from the store, and hand appends to `attempts.jsonl` retire.
   - It builds on #240's approach registry rather than beside it.
2. **One evaluation ladder: the vLLM API's three tiers, with tier 2 split in two.** Tier 2a is a one-GPU screen: gates, poisoned verification, a diagnostic interleaved time, optional ncu and compute-sanitizer, and knob sweeps. Tier 2b is today's timed whole-node panel row. The lane benches become harness arms, so every screen is gated and recorded. This is z.ai's "dense feedback": local, cheap, and objective.
3. **The harness and serving share one kernel contract.** The harness times a variant through the same `KernelPackage`, `Schedule` and `lanes.py` the served executor runs. What was timed is then what serves, by construction, and "timed another commitment" can't recur. That incident voided GPU 1's 2.42× and FP4's attempt 5. Three additions and one move to the API's types follow in [Fit with the vLLM integration API](#fit-with-the-vllm-integration-api).
4. **Generate a "what's been tried" technique catalog from the ledger.** Each technique lists its attempts, its measured delta against the parent, the conditions, whether it was kept, and the evidence. A facts page records the sm_120 and toolchain gotchas, one line each with a citation. An agent backfills both from the lane notes. This is z.ai's "optimization skeletons" and TIRx's kernel catalog, but generated from evidence rather than written by hand.
5. **After 1–4, run agents on narrow optimization tasks, TIRx-style.**
   - A task is an immutable contract: a line, its shapes, a locked scorer, and a frontier of approach families. Agents iterate at tier 2a without the coordinator. Tier 2b windows go only to frontier members.
   - Before this starts, harden the harness against searching agents in three ways:
     - verify a call drawn from inside the timed sequence;
     - flag excessive speedups for the assessor;
     - test the evaluator against adversarial arms.

**Adopt now, as is:**
- **compute-sanitizer:** racecheck, synccheck and initcheck, as optional tier-2a gates.
- **CUTLASS 4.8 and cuBLASLt,** already pinned, remain the baselines. nvMatmulHeuristics (it has an `RTX_PRO_6000` target) can narrow CUTLASS's configuration search.
- **#240's approach registry:** land it.

**Ignore:**
- as platforms: TIRx-harness, ThunderKittens, TileLang and Helion;
- for exact kernels: Triton and Gluon;
- as trackers: MLflow, W&B, Aim and DVC.

The reasons are in [The tools, one by one](#the-tools-one-by-one).

## First step

**Make the harness write its own row.** Everything later hangs off it. It needs neither the vLLM refactor nor a GPU to build.

- **What.**
  - #491's `verify.py` already prints `panel.py append`'s arguments. It now publishes a `kernel-attempt/v1` record per (arm, shape) instead.
  - The arm's build record gains a `lineage` block: the variant id, the parent variant, the approach, the mechanism tags and the hypothesis.
  - The agent records the outcome with `bench.py --outcome` or `research data label`.
  - `panel.py` reads store records beside the old `attempts.jsonl`, so nothing is lost.
- **Where.** `benchmarks/pouw/harness/{arm.py, verify.py}`; a `kernel` vocabulary group in `tools/research/src/research/store/vocab.py`; `panel.py`'s reader. That is about 300–500 lines with CPU tests, and no GPU change.
- **Pilot.** One lane for a day, either the NVFP4 mainloop worker (bc-fb55a759) or GPU 1's `-h3` arm. Measure four things:
  - the share of its runs that get a record;
  - the minutes from a run's end to its panel row;
  - how often prose descriptions repeat what the record already says;
  - whether the coordinator can answer "was X tried?" from one query.
- **Owners.** The harness worker (bc-0de2d624) writes the code. The panel coordinator (bc-2aa33ad8) owns the renderer.
- **Exit.** Hand appends stop once 90% of tier-2 runs record themselves.

The prerequisites are for the research coordinator: land #491, the harness itself (18.7k lines, still unmerged), and #240. Today every run tree is assembled by hand from several branches ("this branch + `benchmarks/pouw/harness` at `f5e584af` + `research` from an `origin/main` worktree"). That assembly is itself a recurring cost.

## The pilot's result

GPU 2 (bc-7442ca43) ran the pilot as one timed run, `r20260930-174917-2585`, re-measuring attempts 67 (v1-h1) and 68 (v2-h1).
- `verify.py --tier 2b` accepted both arms at both headline shapes and rejected all four no-write controls.
- It wrote four `kernel-attempt/v1` records, all for variant `pearl-c-sm120/05d7b3d5c609`.
- They are the panel's first verified measured Pearl-C sm120 rows, all locked-2100. v1-h1 runs at 1.8043× for prefill and 3.4645× for decode; v2-h1 at 1.7665× and 3.3518×.

Sources: `workers/2-hashing.md` at 18:12Z, and `server.md` at 18:28Z.

**The three numbers:**

| Measure | Pilot |
|---|---|
| Runs that recorded themselves | 1 of 1 wrote its records; 0 of 1 published them itself (the gap below) |
| Minutes from a run's end to its panel row | 10.1 (18:01:34Z to 18:11:40Z), 5.5 of them a cold store-index refresh; publishing, labelling and rendering took 38 s |
| Rows that needed a hand append to `attempts.jsonl` | none |

The index was cold because GPU 2's VM had restarted and lost `~/.research`. The plan's other two measures, prose that repeats the record and answering "was X tried?" in one query, need more than one run. Until the records accumulate, the [tried-techniques catalogue](tried-techniques.md) answers that question from the lane notes.

**The publish gap, and its fix.**
- **The gap.** On the pod, `verify.py --publish --push` printed `no remote configured`. `research run --on` stages the store's custody key for the runner only, never in the workload's environment (`research/remote.py`, `store/custody.py`). So GPU 2 published from its own VM with `ledger.py publish`.
- **The fix is [#590](https://github.com/danielreuter/verity/pull/590) `bd5b284f`, and it touches no credentials.** It is GPU 2's own recommendation: the runner already publishes each Attempt's typed outputs with the key it holds.
  - verify.py now also declares every record in the run's `outputs.json` (`research/outputs/v0.1`), as a payload-less typed output named `kernel-attempt/<arm>/<shape>`.
  - The runner publishes those records when it publishes the Attempt at the run's end.
- **What stays with the lane.** A test runs the runner's `typed_outputs` on verify's `outputs.json`, and it yields the same art ids that `ledger.py publish` puts. A later `ledger.py publish RUN --by LANE`, from any machine with the store, is then a no-op for the records. It only asserts the outcome labels, which are judgments and stay the lane's.
- No infra-charter ask is needed.

**Index warm-up.** `research data refresh` fetches only the manifests, attempts and labels a catalog lacks (store README §7.2). The 5.5 minutes is a one-time cost for a machine with no catalog, not a per-run cost. A refresh can't be narrowed to one kind today, because the remote lists manifests by id and each one's kind is inside it. The pilot didn't time a warm refresh. So:
- **Render the panel on a machine that keeps its catalog between runs,** not on an agent VM that may restart.
- **An agent on a fresh VM refreshes once at the start of its turn,** off the critical path, rather than after its run ends.

**Resolved: attempts 67 and 68 ran the packed cast, so their records' `cast-8.72` is right.**
- **The binary.** GPU 1 confirmed it at 18:40Z (`workers/1-pearl-c-sm120.md`). In `e0902b4a0`, the `form_a` and `form_b` steps launch `form_s5`, which casts with two `cvt.rn.satfinite.e4m3x2.f32` per four codes and stores a row's eight codes with one 64-bit store at the 160-byte `FORM_ROW`.
- **The other cast.** The one-code cast, `form_s5_scalar`, runs only as the check's alternate.
- **The measurement.** The cast code is byte-identical to the kernel measured at 2.87 units per code or less (`r20260930-120753-303f`, `r20260930-124211-a304`).
- **The panel.** Its FP8 lines moved to the packed basis at 18:47Z (`server.md`).

What each attempt is cited at:
- **v1-h1 (attempt 67):** 0.519% forming credited and 0.967% chain-only at 8,192³ (0.51908% and 0.96704% from `price_twins.json`).
- **v2-h1 (attempt 68):** D.
  - The assessor's charged floor is at least 0.946% packed (3:24 PM PDT), because the record's figure charges nothing for the chain's open first atoms.
  - Compute-accounting ruled at 3:25 PM PDT that no uncharged v2 figure is cited, so the record keeps its priced γ but isn't cited.

## What this changes for your four asks

| Ask | Today | After |
|---|---|---|
| What's been tried | 16 lane status files (≈580 KB), panel prose; screening runs mostly unrowed | `research data select --kind kernel-attempt/v1 --label mechanism=…`; a generated `TECHNIQUES.md` with deltas |
| Why a decision was made | coordinator rulings in `server.md` (203 KB), row descriptions | an outcome and reason label on each attempt; #240's approach status and reason; a `pin` label, citing its ruling, on the variant that serves |
| How evaluation is managed | gates in the harness, in #540's `run.py`, and in rules; rows voided by hand when a rule changes | one gate code path, versioned; a row's validity is derived from its gate version, not voided by hand (40 of 108 measured rows predate the verifier rule) |
| Extensibility | a bench per lane, a branch per scheme | a new scheme or format is a new `KernelVariant` under the same `Schedule`, gate and ledger |

## How we iterate today

**What's strong. Keep all of it.**
- A measured row needs the reference verifier's acceptance of that run's own transcript.
- Outputs are poisoned (0xA5) before the dumped call, and a no-write negative control must be rejected.
- A SASS gate refuses `.FTZ` and FP32 `MUFU` outside ptxas's pinned IEEE sequences, and refuses any toolkit or flag that isn't pinned.
- Baselines are timed on the same die, interleaved rep by rep, in items of equal device time, with the SM clock recorded per rep.
- Decode is timed as a dependent chain, with the derive gated against a numpy twin.
- γ is published at the larger of the two FP32 prices, from Lean pins.

No public harness does most of this. KernelBench v0.1's and SOL-ExecBench's hardening lists are a subset of it.

**Where time goes.** Every item below is an incident from the last 12 hours.
- **The contract wasn't one code path.**
  - GPU 1's measured 2.42× and 2.35×, and FP4's attempt 5 (3.16×), timed a commitment of A that the verifier doesn't check. They were voided.
  - All 40 of the 108 measured rows that carry no verifier record were logged before the 08:35Z verifier rule, and were tagged by hand. The 11:50Z stale-output rule then voided GPU 1's early rows too.
  - Today there are two SASS gates (the harness's 1,396 lines, and `pearl_c_sm120/sass_gate.py`'s 89) and two `verify.py`s. The vLLM API's review counts three paths that install PoUW on vLLM's linears.
- **No lineage.**
  - None of the 218 panel rows names a parent. Commits appear only inside prose `source` fields (150 rows).
  - The mainloop lane's roughly 20 gated variants became two estimated rows (attempts 34 and 35): `x2r`, the tail, the 128 × 64, 64 × 64 and 128 × 32 tiles, LATE, fold and WIDE. Each has a commit, a run and a keep-or-drop decision, written only in `fp8-mainloop.md` and `nvfp4-mainloop.md`.
- **A shared file as a database.** Agents append to `attempts.jsonl` on the shared store. At 08:25Z an 89-row conflict copy split off, and one lane notes that an EAGAIN mid-append must not be retried.
- **Lessons learned twice.**
  - GPU 5 passed `--timeout` on four runs after GPU 0 had written that lesson down.
  - GPU 1 and GPU 2 both hit `fake_cuda.c`'s 65-name limit.
  - `c47a` never ran, because `research run` has no `--detach`.
  - A SIGTERM lost a run's results before the harness caught it.
  - A parallel edit made a job's header disagree with what it ran.
- **Screening outside the store.** Node 2's fill queue writes to `/workspace/pouw/fill-out/…`. Its results reach the store only when someone runs `research data put` (for example the FP4 sweep, `art:f3f2aefd…`).

None of this is a kernel-language problem. Kernel authoring itself is moving fast: the FP8 mainloop reached cuBLASLt parity for v2 in about two hours, and the NVFP4 mainloop reached 94.4% of peak.

## The tools, one by one

| Tool | Verdict | Why, against our constraints |
|---|---|---|
| **TIRx-harness** (MLC) | **Borrow ideas; ignore the platform** | No sm_120; NumSim's MMA isn't bit-exact; tolerance correctness; needs a TIRx-lite rewrite. Its harness ideas are good (below) |
| **z.ai GLM infra agent** | **Borrow the method** | Dense feedback, a shape map, optimization skeletons, humans owning objectives and semantics review. It's a practice, not a tool |
| CUTLASS 4.8 C++ | **Keep** (baselines, schedules) | Full sm_120 support, including block-scaled. GPU 1's mainloop already copies its warp-specialized sm_120 schedule |
| CuTe DSL (Python) | **Borrow; trial it only for plain baselines** | Has sm_120 warp MMA atoms (`MmaMXF4NVF4Op`, `MmaMXF8Op`) and fast JIT; Colfax's NVFP4 tutorial runs on the RTX PRO 6000. Our hand-written headers already beat CUTLASS (NVFP4 by 8.5%), so it would buy build latency only. Keep PTX for the chain |
| Triton, Gluon | **Ignore for exact kernels** | The compiler picks the lowering. On sm_120, `dot_scaled` silently falls back to dequantize plus FP16 MMA when K isn't packed (#9684). libdevice FTZ reflect is on by default. z.ai's own bug was `tl.dot` defaulting to TF32. Fine for glue a later exact check decides, as the MVP's screen kernel does |
| TileLang | Ignore | NVFP4 on sm_120 since July; plain `f8f6f4` is "future"; the compiler owns scheduling |
| ThunderKittens 2.0 | Ignore | sm_120 only through a synchronous pseudo-WGMMA shim. FP4 and MXFP8 go only through tcgen05 |
| Helion | Ignore | Autotuned Triton. Borrow its idea of hashing (source, shape, flags, hardware) into the run id |
| flashinfer-bench | **Borrow the schema** | Definition, Workload, Solution and Trace, plus `apply`, which routes by definition name and fails closed. The vLLM API's `KernelVariant` and `select` already follow this. Its correctness is tolerance-only, and it links by name, not digest |
| KernelBench v0.1, robust-kbench, SOL-ExecBench | **Borrow the hardening list** | We already have input cloning, poisoning, controls, same-stream timing, locked clocks and L2 flushes. Missing: an excessive-speedup flag, adversarial tests of the evaluator, and randomizing which call is verified |
| AlphaEvolve, OpenEvolve, ShinkaEvolve, AsmEvo | **Borrow the lineage fields; the loop later, narrowly** | `parent_id`, the code diff, islands for diversity, and AsmEvo's rule that the gate, not the agent, writes the lineage |
| NVIDIA: cuBLASLt, nvMatmulHeuristics, CAKE | Use for baselines; **watch CAKE** | CAKE (arXiv 2608.12629) is the one agentic kernel system that targets sm_120a with bitwise checks. It has no public code yet |
| MLflow, W&B, Aim, DVC | Ignore | A second source of truth, secrets and a UI. Our store already content-addresses attempts, conditions and labels. Borrow W&B's used-by and logged-by edges only if lineage needs them |

### TIRx-harness in detail

**What it is.** Four parts:
- **TIRx-lite,** a traced Python DSL in which each call becomes one PTX instruction.
- **CPU analyses:** NumSim (numerical simulation), Synccheck (every interleaving of barrier protocols), Racecheck (vector clocks, including proxy fences), and SASS dumps.
- **A knowledge base:** skills, a 60-kernel zoo, a perf checklist, and the PTX manual.
- **KCoral,** a remote benchmark server that gives each experiment an exclusive GPU and a fresh process.

An optimization run renders an immutable task YAML into the agent's prompt. It locks the benchmark entry point ("any modification invalidates the whole run"), bans the baseline's own source from the agent's view, and keeps a git-committed frontier. `frontier/index.json` lists each member's approach family, distinguishing mechanism, timings, and why it's worth keeping. Results: 1.33–6.84× family geomeans on Blackwell attention kernels (KDA, MSA, MLA, VSA), with web access off.

**Why not adopt it.**
- **Hardware.** No sm_120 target: every example says `arch="sm_100a"`, and NumSim rejects WGMMA "by the SM100 NumSim target".
- **Numerics.** NumSim runs `raw_mma_sync_f32_f8` through `fma_f32_abt_increasing_k`, an increasing-K binary32 FMA chain (`engine-rs/fp-env/src/lib.rs`). The hardware adds 32 products and the accumulator in one 26-bit truncating group.
  - The check (`internal/pouw/numsim-vs-sm120.py`) runs NumSim's rule and verity's `BLACKWELL_SM120_E4M3_M16N8K32` (6.4M elements, 0 mismatches) on random steps: 11,547 of 20,000 differ with full-range codes, and 1,866 of 5,000 with Gaussian operands.
  - The docs admit NumSim "is not a numerical oracle". For us the oracle is `verity.ml.tc`, which we already have.
- **Correctness model.** Tolerance-based: `rtol=0.01, atol=0.1` for 99% of elements in the GEMM task. Its gates stop no-op, stale-output and fast-math tricks, but not a wrong accumulation order.
- **Cost.** Moving #540's kernels, the mainloop headers and GPU 2's hashing module into TIRx-lite would redo all of them. Its Synccheck and Racecheck only read TIRx IR.

**What to borrow.**
- The task contract as one immutable file rendered into the prompt.
- The locked scorer.
- The frontier of distinct approach families, "not a leaderboard of near-identical variants".
- Committing each frontier change with its measured speedup and family.
- "Preserve concrete artifacts, not agent-written summaries, which overfit the case just debugged."
- KCoral's isolation: one exclusive GPU and a fresh process per measurement. Our `gpu-lease` and `research run` already give us this.
- Its book's lesson: "turn each escape into a regular input". Its KDA rewrite passed tests that never reached the −126 exponent boundary.

**Revisit TIRx** if it adds an sm_120 target. Its checkers would then be worth having. NumSim could even take `verity.ml.tc`'s captured models as its MMA semantics, a contribution upstream would likely welcome.

### z.ai's GLM infra agent in detail

**What happened.** A GLM-5.3 "Infra Agent" took GLM-5.3-Flash from its first run on over 100,000 Chinese-made accelerators to production in under two weeks, with about 3× end-to-end throughput. The post's thesis is that **agents move fast when feedback is dense**:
- **local:** tied to a kernel, a shape, a code path or a launch parameter;
- **cheap and timely:** a kernel test or a microbenchmark instead of a full deployment;
- **objective:** a reference implementation and comparable metrics.

Three mechanisms make this concrete:
- **A map from each serving configuration to the kernel tasks it implies.** Their parallelism configs became per-kernel checks. For us, the served `SiteMap`'s (n, k) and TP shards should be tier 2's shape set, not only 8,192³ and m = 32.
- **Layered validation.** A local check eliminates a change early, and end-to-end confirms it. That is our ladder.
- **"Optimization skeletons":** techniques distilled from existing kernels, each with its applicability conditions, the transformation, its resource constraints and its validation evidence. Validated changes flow back into them. KLineage (arXiv 2605.28213) formalizes the same idea. For us, this is the technique catalog, generated from the ledger.

Engineers keep three jobs: setting objectives and constraints, building the feedback environment, and reviewing changes that touch numerics, concurrency and production risk. That matches our split: statement parameters through the coordinator, and the assessor for anything that touches numerics.

### The anti-reward-hacking lessons

When agents search, they find the evaluator's gaps; the searches don't have to be malicious. There are three well-documented cases:
- Sakana's AI CUDA Engineer reused a reference's output memory; after the fix its mean speedup fell from 3.13× to 1.49×.
- METR removed 17 solutions that used unsynchronized streams.
- SOL-ExecBench flagged 14.5% of agent submissions as reward hacking.

We already block most of these classes. Three gaps matter once agents search on their own:
- **The verified call can be told apart.** The harness poisons buffers just before the dumped call. An arm could, in principle, do the full work only on a call whose outputs start at 0xA5. The fix: keep every timed call's transcript in a ring, and have the verifier draw which call to check after timing. Its cost needs measuring with the harness owner.
- **No excessive-speedup flag.** A row whose hash-free slowdown is under 1.00×, or that jumps more than a set fraction past its parent, should go to the assessor automatically.
- **No adversarial tests of the harness itself.** KernelBench runs `test_eval_adversarial.py` against its evaluator. The harness should likewise run a stale-output arm, a stream-escaping arm and a dump-detecting arm, each of which must fail. It already has one known-bad variant.

A side note: an evolutionary loop whose fitness is "passes the verifier at lower W1 cost" is an automated γ attack. The cheaper-computation lanes (GPUs 3 and 7) could use one later.

## What to build

### A. The attempt ledger

Numbers go in the record and judgments go in labels, as the store's rules require. Measurements are refused as labels.

~~~text
record  kind kernel-attempt/v1
  meta  variant          pearl-c-sm120/3f0a91c2d4e5       (the vLLM API's KernelVariant.id: sources' digest)
        parent           pearl-c-sm120/9b1e07aa41c0 | null
        scheme           pearl-c-sm120-v2-hot-h3          (SchemeId.name)
        schedule         deferred                          (Schedule.name)
        tier             2a | 2b | 3
        shape            m32-n8192-k8192
        harness, gates   <commit>, <gate version>          (validity is derived from these, never hand-voided)
        metrics          slowdown, hash_free, per-group ms (a_tree, forming, gemm, cleanup, tile_hash, screen),
                         baseline id and ms, sm_clock medians (arm, base), ncu headline counters when run
        gamma            {at_8.00, at_8.376, prices_ref}   (looked up from the variant's priced path and Lean pins)
        verify           {commit, accept, negative_control, transcript}
  refs  run: r2026…, gate_record: art:…
labels  approach   pouw/<slug>          (#240's registry)
        mechanism  [pipeline:tma-ws, unroll:2, release:fence-proxy, epilogue:wide-stores]   (namespaced; new tags warn)
        hypothesis one line, before the run
        outcome    screened | frontier | kept | dropped | voided | superseded
        reason     one line, required unless screened
        pin        on a variant: serves scheme S, ref = the ruling's note
~~~

- **What the harness fills in:** everything in `meta`, and `approach` and `mechanism` from the variant's declaration.
- **What the agent writes:** `hypothesis`, `outcome` and `reason`, two lines instead of today's median of 415 characters of prose.
- **What gets rendered from it:** `panel.py` renders the plots and the page, and the steward renders `TECHNIQUES.md` beside #240's `APPROACHES.md`.
- **What it retires:** hand appends to `attempts.jsonl`, and the conflict-copy class of failure with them.

### B. The evaluation ladder

| Tier (vLLM API numbering) | Runs on | Establishes | Recorded |
|---|---|---|---|
| 1 conformance | CPU | the build, the SASS gate, the twin against `verity.ml.tc` on small tiles, and the executor's step order on `RecordingDev` | yes, when it fails too |
| **2a screen** (new) | one leased GPU, a shared node, fill-preemptible | the device gates at the served shapes; a poisoned transcript verified and a control rejected; a diagnostic time interleaved with the baseline; the per-group split; optional ncu and compute-sanitizer; knob sweeps. It emits the `GateRecord` | always |
| 2b timed | the whole node, locked-2100 | today's panel row | always; the only tier plotted |
| 3 served | vLLM on the card | the arms, the time split and the verify job, keyed by variant | always |

- **Lane benches become tier-2a arms of the harness,** so their numbers share its gates and ledger: `mainloop_bench`, `nvf4_bench`, `run.py check`, `decode_chain.py` and `prefill_fused.py`.
- **Knob sweeps run inside tier 2a:** tile, stages, the register split, LATE, WIDE and unroll, the kind of enumeration the mainloop lane did by hand. The winning choice is part of the variant's sources, as the API requires.
- **Fill-queue jobs run through `research run`,** so tier 2a never bypasses the store.

### C. One kernel contract for the bench and for serving

The vLLM API already defines the contract: `KernelVariant`, `KernelModule` (`Dev`, `Pipeline`, `VARIANT`, `STEP_IO`), `Schedule` and `GROUPS`, `GateRecord`, and `select` by pin. Three things need doing:
- **The harness adopts it.** An arm becomes a thin adapter around a `KernelPackage` and a `Schedule`, timed through the same `lanes.py`. The harness's `before`, `gemm` and `after` phases map onto `GROUPS`.
- **The harness's gate emits the `GateRecord`** that `register` requires.
- **The panel row names the variant id** that `PassCommitment.kernel` carries.

### D. The technique catalog and the facts page

**First version: [tried techniques](tried-techniques.md)** (30 Sep, 19:20Z). It holds 326 techniques: 170 kept, 81 dropped, 44 open and 31 superseded. It was backfilled from the panel's attempts, `server.md`, the workers' status files (the FP8, FP4, hashing, harness and MVP lanes and the probes) and the kernel-ledger lineage (the pilot's four records). Later versions are generated from the `kernel-attempt/v1` records' mechanism tags. The page's inputs and its generator are in `internal/pouw/tried-techniques/`.

**First version: [sm_120 gotchas](sm120-gotchas.md)** (30 Sep, 19:40Z). It holds 251 facts, one line each with its source: research-notes `kb/sm120-kernels.md`'s 55 lines (4 corrected, 37 given evidence) and 196 more, backfilled from the lanes' status files, `server.md` and the lane notes. It replaces the kb list and is edited in place until `fact` records exist.

- **Techniques are generated from the ledger.** For every mechanism tag, the catalog lists each attempt that has a parent at the same tier and conditions, with its delta against the parent, its outcome and its evidence.
- **Facts are `fact` records:** one line and a citation each. Examples:
  - ptxas 12.9 lowers `cp.async.bulk.shared::cluster` to a CALL and then drops `setmaxnreg` (use `.shared::cta`);
  - there is no packed FADD on sm_120;
  - cuBLASLt 12.9 finds no algorithm for rowwise FP8 or 128-blockwise FP8 on sm_120;
  - multicast TMA compiles but ptxas warns it runs slowly;
  - the conflict-free `STS.64` and `STS.128` row strides.
- **The backfill is one agent's pass over the lane files,** using #240's `--at` timestamps: the Checkpoints and Lessons sections of `workers/*.md`, `fp8-mainloop.md` and `nvfp4-mainloop.md`. Expect about 100 attempts and 40 facts.
- **Lanes read it before starting a technique.** The catalog replaces "read the lane notes" at a lane's first checkpoint.

### E. Agent optimization runs, after A–D

- **The task file** follows TIRx's shape. It names:
  - the line and version, the `SchemeId`, the shapes (from the served site map), the baseline family and a tier-2a GPU-minute budget;
  - the scoring rule: the tier-2b slowdown, subject to every gate and γ ≤ 1% at both prices;
  - what's banned: any change to statement parameters, and any edit to the harness.
- **The frontier** is the ledger's `frontier` outcomes, at most a few families.
- **Tier 2b** is booked only for a new frontier member.
- **Where to start:**
  - the NVFP4 plain mainloop's last 0.7% (the tail and the tile scheduler);
  - the FP8 v1 register squeeze;
  - decode's hashing placement.

  Each has a clear scorer and cheap tier-2a runs.
- **An OpenEvolve-style loop** only for knob-level search, and only once tier 2a is automatic.

## Fit with the vLLM integration API

**Where we agree.**
- **Identity:** content-addressed variants, selected by pin and never "fastest at serving time". Tier 3 never compiles or autotunes.
- **Evaluation:** the three tiers, the gate as the only way into serving, and `Schedule` as data that the benches and the executor share. Its note that "kernel-iteration tools produce variants and time them in their own microbenchmarks" fits the harness as that tool.

**Four gaps and conflicts, with the fix I'd suggest:**
1. **Two things are called `Arm`.** The harness's `arm.py` `Arm` is a prover under test: its build, gates, timed call, work and verifier. The API's `Arm` is a bench mode at the serving level. Keep the API's name, and rename the harness's to `BenchArm`, or make it constructible only from a `KernelPackage`.
2. **`GateRecord` lacks what γ and the SASS rule need.** Add three fields:
   - `sass`: the verdict and the pinned toolkit and flags;
   - `prices`: the priced path the variant implements, for example the packed cast with 64-bit stores at a 160-byte stride, or `lut256` for the block scale. The published γ ("0.779% as the port stands" against 0.519% at 8.72) depends on it;
   - `gates`: the gate code version, so a row's validity can be derived.
3. **The data half of `kernels.py` belongs in `verity_pouw.serving`.** `KernelVariant`, `ShapeRule`, `StepIO` and `GateRecord` are stdlib data, but the API puts them in `verity_vllm/linear/impl/kernels.py`. The bench harness (stdlib, numpy, ctypes, no torch) and the ledger would then import the vLLM integration to name a variant. Only the loader needs ctypes. This follows the API's own rule that "the contract goes in the protocol package".
4. **Phase vocabularies differ.** The harness's `Call.phases` are `before`, `gemm` and `after`; the API's `GROUPS` are `a_tree`, `forming`, `gemm`, `cleanup`, `tile_hash` and `screen`. Use `GROUPS` everywhere, so every ledger row's time split names the same groups the executor schedules.

The API also leaves open a home for serving kernels. The ledger doesn't care: it keys on digests, not paths.

## Process check

This was assessed with the process-design skill.
- **The failures are incidents,** listed in [How we iterate today](#how-we-iterate-today).
- **The mechanism is code and labels,** not prose rules or human gates:
  - it adds no step to the common path, because rows are emitted automatically;
  - it asks for two one-line fields in place of a paragraph;
  - it adds no approval;
  - it removes a serialization point: the shared `attempts.jsonl`.
- **Owners:** the harness worker for the ledger emission and tier 2a, and the panel coordinator for the renderer.
- **The pilot** is one lane for a day.
- **The exit:** hand appends stop at 90% auto-coverage, and a dropped mechanism tag retires if nobody queries it in a week.
- **Words in `AGENTS.md`:** none. The lane brief's rule 11 shrinks to "the harness records your row; add hypothesis and outcome".

## Decisions for Daniel, each with a default

1. **Direction:** no external kernel platform; build the ledger, the ladder and the catalog on `research` and the harness. **Default: yes.**
2. **The panel's source of truth moves from `attempts.jsonl` to the evidence store** once the pilot meets its exit. **Default: yes.**
3. **The data types of `kernels.py` move to `verity_pouw.serving`,** the third fix above, to be settled with bc-f4e8ae34. **Default: yes, in its skeleton PR.**

## Sources

- TIRx-harness at `ccd7a04` (cloned, read): `docs/`, `evolution/{tasks,prompts,benchmark}`, `numsim/engine-rs/{SUPPORTED_OPS.md, src/runtime/matrix_ops.rs, fp-env/src/lib.rs}`; [blog](https://blog.mlc.ai/2026/09/29/tirx-harness-an-open-compiler-harness-for-agentic-gpu-programming); [book](https://mlc.ai/agentic-gpu-programming-for-mlsys/).
- [z.ai: How GLM built its own inference infrastructure](https://z.ai/blog/glm-built-its-inference-infrastructure).
- The CPU check: `internal/pouw/numsim-vs-sm120.py`.
- The survey of CUTLASS/CuTe DSL, Triton/Gluon, TileLang, ThunderKittens, Helion, flashinfer-bench, KernelBench, robust-kbench, SOL-ExecBench, AlphaEvolve, OpenEvolve, ShinkaEvolve, AsmEvo, KLineage, CAKE, nvMatmulHeuristics and the trackers, each with its links: `internal/pouw/kernel-tooling-landscape.md`.
- In the repo: [#491](https://github.com/danielreuter/verity/pull/491) (the harness), [#540](https://github.com/danielreuter/verity/pull/540), [#240](https://github.com/danielreuter/verity/pull/240), [#555](https://github.com/danielreuter/verity/pull/555), [#564](https://github.com/danielreuter/verity/pull/564); `tools/research/src/research/store/README.md`.
- In the store: the [panel](panel.md) and `internal/pouw/panel/attempts.jsonl` (218 rows, read 15:40Z); `internal/pouw/rtx-pro/{brief.md, server.md, workers/*.md}`; [research-notes structure](../research-notes-structure.md); [vLLM integration API](vllm-integration-api.md).
