---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# vLLM config sweep: plan for the first night on the RTX PRO 6000 cluster

vLLM coordinator, 2026-09-30.

**Headline.** A stripped-down "config run" (derive the circuit representation, commit one instrumented run, randomly replay proof units) takes about **0.5–2 h per config on 1 GPU**, against 5–11 h per row today.
- **About 100–200 configs fit in one night on 16–32 RTX PRO 6000 GPUs.** That's nearly every BF16 config the integration can represent on sm_120.
- **The earliest night** is when the sm_120 port's BF16 steps and the config-run job have both merged: about 6 elapsed agent-days from now. It replaces the BF16 re-baseline epoch.
- **One correction to the premise:** rows don't run PoUW or PoUS. Those are opt-in and off by default. The time goes to our own safety margins: repeated runs, a determinism control arm, a separate Match, manifest rebuilds, and storing everything.

## 1. Where a row's time goes today

Measured in the follow-up epoch, 29 Sep, on 2× L40S or 2× H100:

| Phase | #73 Qwen3-4B B8 (H100, 1 pair) | #67 OLMoE B32 (L40, 3 pairs) | What it's for |
|---|---:|---:|---|
| Bootstrap | ~0.3 h | ~0.3 h | environment |
| **Build:** derive the request Programs per shape, compose the workload Program, required-value manifest | ~4.2 h (manifest 42 min) | 3.0 h | **the circuit representation** (kept) |
| **Match:** capture a run and fold it to the Program | 0.9 h | 0.8 h | Program = what ran (optional: replay checks it too) |
| Strict word check | minutes | minutes | partition check (kept, cheap) |
| **Commit:** manifest rebuild | 0.7 h | ~0.5 h | overhead (#298 now reuses the Build's manifest) |
| **Commit:** control + instrumented runs × pairs | ~1.0 h (1 pair) | ~3 h (3 pairs) | **commit** (1 instrumented run is kept; the control arm and extra pairs are determinism margins) |
| **Commit:** sampled replay (C2) + manifest-verify rebuild | ~0.4 h + ~0.5 h | similar | **replay** (kept); the manifest-verify rebuild is overhead |
| Store (custody upload, 12k–60k files, up to 21 GB) | 0.1–2 h | ~0.7 h | evidence (can shrink to the record and commitments) |

- **PoUW or PoUS overhead: none.** Neither runs in a row.
- **Sampled proofs:** "sampled proofs" *is* the Commit plus the replay, the thing the sweep wants. Its overhead is the pairs, the control arm and the rebuilds, not the protocol.

## 2. The config run: one job per config

**Steps:**
1. **Build:** derive the Programs (the circuit representation) and the `Q_word` manifest with the strict word check.
2. **Commit:** **one** instrumented run, with no control arm and no pairs. It commits every required value (M0 format), writing the run root and leaves.
3. **Replay:** **k random proof units** (for example k = 256 per config, stratified by family), each re-evaluated on the host from the Program and checked against its committed words and Merkle opening. No proofs are generated.
4. **Keep:** the Program digests, the manifest, the commitment roots, the replay result, and a small record (MBs). Drop the Match, `manifest-verify` and the bulk capture stores.

| | Small/medium (≤ 7B, B ≤ 16, ctx ≤ 1k) | Large batch / long context (B32–64, 4k ctx), MoE |
|---|---|---|
| GPUs | 1 (TP2 configs: 2 on one host, no NVLink) | 1–2 |
| Minutes | ~30–60 (Build 20–40, commit 5–15, replay 5–10) | ~90–150 (Build-dominated) |
| Host RAM | ~50–150 GB | ~200–500 GB for the Build's whole-workload Program; the Commit is bounded with staging windows |
| Disk | ~50 GB (weights cached per host) | ~100 GB |

**Host RAM is only partly overhead.**
- **Commit staging (up to ~480 GB today):** the Commit holds every required value on the host. The windowed / bounded staging mode, already in the Commit, caps it, so this part **is avoidable**.
- **Build (~486 GiB for B1 at a 4k context):** the size of the whole-workload Program itself. That's inherent to the representation at that shape. Keep those configs to a few per server, or split them per request.
- **The Build is CPU-bound:** Programs are derived on the host. Give each GPU at least 16 vCPUs, and cache derived Programs per (model, request shape) across configs. Many configs share shapes.

## 3. The sweep: one night

**The set:**
- the sm_120 BF16 cells the integration represents: the 16 representable models × batch {1, 8, 16, 32, 64} × context {256/32, 1k/128, 4k/512} × sampling {greedy, top-p}, less the infeasible cells (weights or context too big, heads not divisible by TP) and TP2 for models that fit on one GPU;
- that's about **150–200 configs**, and more once FP8 lands.

**The capacity:**
- 16–32 GPUs × ~10 h is 160–320 GPU-h.
- At ~0.7 GPU-h average (mostly small and medium, a few large), that's **~100–200 configs per night**.
- The limit is host RAM and CPU for the large-Build configs: about 3 per 1.7 TB server. Schedule them first, and pack the small ones around them.

**Per-config outcome:** built, committed, and replayed k/k equal (or which units differed). A failure is a finding, not a stop.

## 4. Dependencies and the earliest night

- **From the sm_120 port (BF16 only):**
  - the target registration, with the GEMM correspondence (lane tc-gemm);
  - FA2 on sm_120 (lane attention);
  - the 188-SM constants and kernel captures (lane kernels).
- **FP8 configs:** they wait for the FP8 Definitions (tc-gemm 5b) and checkpoints (fp8-ckpt), and join a later night.
- **New code: the config-run job,** about 2 agent-days, in parallel with the port:
  - a mode that runs Build, one instrumented Commit and k-unit replay only;
  - the Program cache per (model, shape);
  - bounded commit staging on by default;
  - a sweep driver that packs configs onto GPUs by RAM and CPU;
  - a small record per config.
- **Also needed:** the JIT build-dir fix, so concurrent jobs don't collide; the Build-resume fix isn't needed, since runs are short.
- **The earliest night:** about **6 elapsed agent-days** after the port lanes started (they started 2026-09-30), once the cluster is up with drivers ≥ 575. **It replaces the BF16 re-baseline epoch:** the sweep's records become the sm_120 references.

## 5. A name for "row"

- **A "config run"** is one job over one vLLM configuration (model, dtype, GPU, TP, batch, context, sampling).
- **A "sweep"** is a night's set of config runs.
- **A "config record"** is the stored expected outputs (digests, roots, replay result).
- **"Class"** (GREEN or FAIL) stays the expected verdict.
- `tests/regression/expected/` becomes `expected/config-records/` when the tooling is renamed; the rename is cosmetic and can follow the sweep.
