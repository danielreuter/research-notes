---
cursor:
  subagentId: "bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d"
---

# RTX PRO 6000 (sm_120) PoUW: worker brief

Coordinator: bc-2aa33ad8. The plan Daniel reads: `docs/pouw/rtx-pro-plan.md`. This file is the rulebook for the eight GPU workers. Only the coordinator edits it.

## Who owns what

| GPU | Stream | Worker | Agent | Status file |
|---|---|---|---|---|
| 0 | FP8 | FP8 capture | bc-e6a46970 | `workers/0-fp8-capture.md` |
| 1 | FP8 | Pearl-C on sm_120 (design, kernel, FP8 bench arm) | bc-18346d9c | `workers/1-pearl-c-sm120.md` |
| 2 | FP8 + shared | Hashing module (shared owner) and FP8 epilogue fusion | bc-7442ca43 | `workers/2-hashing.md` |
| 3 | FP8 | FP8 cheaper-computation search and realism | bc-0f3f8a2f | `workers/3-fp8-attacker.md` |
| 4 | FP4 | FP4 capture | bc-36186951 | `workers/4-fp4-capture.md` |
| 5 | FP4 | FP4 PoUW design, kernel, FP4 epilogue fusion, FP4 bench arm | bc-71c6ab78 | `workers/5-fp4-design.md` (and `fp4-design.md`) |
| 6 | FP4 + shared | Bench harness (shared owner) and card characterization | bc-0de2d624 | `workers/6-harness.md` |
| 7 | FP4 | FP4 cheaper-computation search and quality | bc-dbc19788 | `workers/7-fp4-attacker.md` |
| — | FP8 | Pearl-C's FP8 mainloop alone (a header adopted by GPU 1's kernel), from 07:45Z | bc-fb55a759 | `workers/fp8-mainloop.md` |

Paths are relative to `internal/pouw/rtx-pro/`. Each worker creates and owns its own status file (with the store's `cursor.subagentId` frontmatter) and edits no one else's.

**On node 2 (`vy-nebius-2`, ours from 05:40Z), GPUs are taken through `gpu-lease` and not by fixed index:** at most one per worker at a time (two for the assessor), each lease ≤ 30 minutes, and timed runs in `gpu-lease 8 --wait` windows (`server.md`, 06:00Z). The indices below are the plan's stream split, not locks. **Server GPUs from 05:05Z.** GPUs 6 and 7 go to the independent assessor (bc-d7d4b0d1, replacing bc-8b6cc7d8 from 05:35Z) while FP4 is in design. The harness worker (bc-0de2d624) runs on GPU 5 until the FP4 kernel is ready to gate, then GPU 5 returns to bc-71c6ab78. The FP4 cheaper-computation search (bc-dbc19788) takes GPU 4 once the FP4 recheck is done. Each handover is written in both workers' status files before the GPU changes hands. Tonight's pods: `server.md`, 05:05Z.

## Rules

1. **One GPU each, through `gpu-lease`.** On node 2, every GPU command runs as `gpu-lease 1 -- <cmd>`, which sets `CUDA_VISIBLE_DEVICES`. Record the UUID you got. Never use a GPU outside your lease, and never run anything GPU-wide (`nvidia-smi -r`, clock or power changes, killing other users' processes). **Any run whose numbers go on the panel takes its lease with `--timed`** (`gpu-lease N --wait --timed -- <cmd>`), and so do whole-node windows. Fill pauses only for a `--timed` lease or one holder of the whole node, so without the tag a preemptible fill job, the prio-10 approved-weights 70B job included, keeps running beside your timing (ops, 13:57Z).
2. **Gates before timing.** A shape and flag set is timed only after its gates pass on the device, in the same run. A failed gate writes no measurements. No shipped kernel may contain an FP32 `FADD`, `FFMA` or `FMUL` with `.FTZ`, so never build one with `-ftz=true` or `--use_fast_math`. The harness's SASS gate rejects such a kernel. The only exception is nvcc's correctly rounded `__fdiv_rn`, `__frcp_rn`, `__fsqrt_rn` and `__frsqrt_rn` sequences, matched as whole sequences and pinned bit-exact on subnormals.
3. **Clocks are locked node-wide** at 2,100 / 12,481 MHz by the Nebius owner. Don't change them. Label node-2 timings locked-2100, and record the clocks per rep.
4. **Honest arms only** in any end-to-end or bench run. The cheaper-computation search workers (GPUs 3 and 7) time the cheapest program that passes the verifier's checks, as a separate measurement and a check on γ.
5. **Baselines are the fastest plain path on the same card and shape,** timed in the same run on the same GPU, interleaved with the arm rep by rep in reps of similar duration (sustained load clocks about 1% lower than short bursts), with the SM clock recorded per rep, the same way: cuBLASLt autotuned over its top algorithms, and CUTLASS's sm_120 kernels. Record the algorithm chosen.
6. **Evidence** goes through `research run --on vy-nebius-2 --project verity --campaign pouw --source . -- gpu-lease 1 -- <cmd>` into the evidence store. Nothing generated goes into Git or the notes.
7. **Code** goes in ordinary draft PRs, one logical change per commit, merged only through the merge trains (the research coordinator's `research merge`). Follow the repo's `AGENTS.md`, and `~/.research/notes/kb/LANE-CONTRACT.md` where your VM has it. A new circuit needs `circuit-check`.
8. **Statement parameters don't change unilaterally:** the promotion period G, the domain's constants (α's formula, the noise floor, liveness, line norms), the cap ρ, the W1 prices Lean uses, and the credit formula. Propose a change in your status file's `Needs` section and in your return; the coordinator routes it to the cheap-binding and Lean lanes.
9. **Label every number:** Measured (a run id on this card), Public, Estimated, Derived, Proved, Conjectured. Flag every shortcut (a CPU stand-in, a stand-in model, an excluded cost).
10. **No spend** beyond the server and your row of the `vy-pouw-rtxpro-` pod table (`server.md`): no other pods or paid services without the coordinator.
11. **The panel.** Every GPU attempt is one appended row through `internal/pouw/panel/panel.py append` (prefill `m8192-n8192-k8192`, decode `m32-n8192-k8192`). Only γ ≤ 1% counts.
12. **A timed run emits the transcript the verifier checks, and runs the reference verifier on it in the same run.** No stand-in commitment, stand-in hash or stand-in format anywhere in a timed arm: the bytes the arm commits are the bytes the verifier recomputes. `panel.py` refuses a measured row without the verifier's commit, its accept line and the transcript it checked, which must name the run (`internal/pouw/panel/add-a-row.md`).
13. **The assessor's folder and ID are its own.** Only the assessor (bc-d7d4b0d1) writes in `internal/pouw/red-team/`, or queues fill or leases GPUs under its ID. Put code, jobs or proposals for it in your own folder, and tell the coordinator, who routes them through the pous root.
14. **Secrets.** Never print, `cat`, `echo` or `grep` a key file or a secret environment variable. Reach machines through the SSH config or agent only. List variable names with `compgen -e`, never `env`, and redact before logging anything. Nobody rotates or changes keys: that's Daniel's decision.
15. **A research-notes post to the research coordinator (RC) or the Verity root is named `-handoff-`,** never `-note-`: `lanes/<lane>/<YYYYMMDDTHHMMZ>-handoff-<slug>.md`. `research notes inbox` lists only `*handoff*`, `*asks*` and `*reply*` files, so a `-note-` to them goes unseen (the Verity root, 13:51Z).

## The server

Access isn't in yet. The root coordinator will relay it; the coordinator writes it to `server.md` (machine name for `research run`, how to connect, the GPU index → UUID table, which secret holds the key). No credential is ever written to the store. Until then, work CPU-side, and check `server.md` at each checkpoint.

## Toolchain (CPU side)

- nvcc 12.8 or later compiles sm_120 without a GPU: use NVIDIA's apt repo (`cuda-nvcc-12-9` or `cuda-toolkit-12-9`). The pip wheel `nvidia-cuda-nvcc-cu12` ships only `ptxas`, and there is no `nvidia-cuda-cuobjdump-cu12` wheel. On node 2, CUDA 13.0 is in `/usr/local/cuda`, and the harness's `jobs/env.sh` provides a runtime and cuBLASLt without a toolkit.
- Build `-gencode arch=compute_120a,code=sm_120a`. The block-scaled and `f8f6f4` instructions need the `a` target. Gate SASS offline with `cuobjdump -sass`: the intended OMMA, QMMA or HMMA count per kernel, and nothing lowered.
- The workspace: `uv sync --all-packages --extra torch-cpu`, then `uv run tools/check/suites.py` for the suites your change touches.

## Shared interfaces

- **Hashing module (GPU 2).** GPU 2 publishes the module's location, the device-function API and its CPU test vectors in `workers/2-hashing.md` as its first checkpoint. GPUs 1 and 5 code against that API; until it is published they keep #449's `hash_msg` and `hash_leaf`.
- **Bench harness (GPU 6).** GPU 6 publishes the arm interface (what an arm provides: its build, its gates, its timed call, its bytes hashed and its credited work per shape) in `workers/6-harness.md` as its first checkpoint. Arms are owned by their streams: FP8 by GPU 1, FP4 by GPU 5, the cheaper-computation searches' by GPUs 3 and 7.
- **Captured steps (GPUs 0 and 4).** Each capture lands as a `verity.ml.tc` model with a sampled fixture and an `instructions` entry, in a PR. The status file carries the Lean-shaped parameters: `Pipeline ⟨groups, adder width, exponent floor⟩` (for example Ada's E4M3 `⟨[16, 16], 14, −139⟩`), or, where no `Pipeline` fits, that fact plus the smallest extension that does. Until then, designs use a named stand-in model and say so.

## Status files and reporting

- Status file: a one-line checkpoint per milestone (time, what, run id or PR), a `Results` section with labelled numbers, and a `Needs` section for questions to the coordinator, the theory lanes or Daniel.
- Return to the coordinator when your CPU-side phase is done, or when you're blocked on the GPU or on a decision: a few lines, with links. The coordinator resumes you with server access. No routine progress messages.
- Questions for the theory (TT_OUT, γ) and Lean lanes go through the coordinator.

## Context

- Handoffs: `handoffs/capture.md`, `handoffs/pearl-c-kernel.md`, `handoffs/pouw-mvp.md`, `handoffs/ttout.md`.
- The Lean split, §8 (what is H100-only; keep new Lean parametric): `internal/pouw-fp8/pearl-c-lean-split.md`.
- Pearl-C: `docs/pouw/cheap-binding.md`, `docs/pouw/pearl-c-vllm-plan.md` (§12 bench, §13 the review's fixes). Hashing: `docs/pouw/hashing-accounting.md`.
- Earlier reviews: `internal/pouw/red-team-pearl-c-vllm.md` (F1–F8), `internal/red-team-bench-methodology.md` (W1–W12 for the PoUW bench).
- PRs: #449 (Pearl-C: scheme, verifier with F1, F2, F5–F8, H100 kernels, twin-gated bench; head `e8f86c8a`), #462 (vLLM half, paused; pinned `split_channels`), #453 (mixed accumulator chains), #435 (fused NCP kernel), #464 and #468 (hashing cut), #475 (PoUW-only bench).
- In the repo: `packages/verity/src/verity/ml/tc/` (models and instructions; sm_120 BF16 and FP4 pinned from the RTX 5090), `tools/tc_probe`, `tools/tc_probe_fp4`, `fixtures/tc/`.
