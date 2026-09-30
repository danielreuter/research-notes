---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run (bc-75fd4007) · kind: GO · from: vllm-coordinator · created: 2026-09-30T05:22Z · spec: `docs/overnight-objectives.md` workstream 2

# GO: config sweep v0 (coverage), breadth before depth

**Grants pushed to the queue's remote (05:19Z):** #466 `5d9a6b99`, #467 `7b8eb2e1`, #470 `d5efed8e`, #465 `f740c1d5`, #476 `e213ccc3`. **#439 is not granted:** it conflicts with main, so rebase it and send me the new head.

## Money and machines
- **RunPod line `vyv-cov-`**, $150, until 2026-10-01T14:00Z, 12 h max per pod. I requested it from RC at 05:21Z (`lanes/coordinator/20260930T0521Z-ACTION-...-coverage.md`). **Launch nothing until the guard shows the line.** Pods are `vyv-cov-<gpu>-<n>` on SECURE on-demand in uk-south2, L40S / A100 / H100.
- **vy-nebius-1** (8× RTX PRO 6000). `research run --on vy-nebius-1` with `CUDA_VISIBLE_DEVICES=0,1,2,3` (the `circuits` share) until Kueue lands.
  - **CPU stages** (Build, replay) for any target may run there; it's the RAM-bound home (1.7 TiB).
  - **A Commit runs on the arch it targets.** Only sm_120 Commits go there, and only after #465 and #476 are on main.
  - `research run --on vy-nebius-1` needs #478, which is CONFLICTING right now; RC's train carries it.
- **Balance tripwire:** if the RunPod balance falls below $25, stop new launches and tell me. Never request a top-up.

## What a cell is
`row run --config-run 1 --replay-k 460`, with bounded staging and `--program-cache`.
- **Gate:** circuit built, commitment made, and **460/460 random proof units** replayed bit-exact on CPU.
- **A cell that fails the gate is a finding,** not a stop. Record its first differing unit and name its cause (Definition, capture, platform, or tooling) as far as you can see it.
- **Unsupported cells** (refused by the registry or target, e.g. TP4 over the heads, top-k where there's no Definition, FP8 on a target without its step) are recorded from the refusal message **without launching a pod**.

## The grid, breadth first
Cover each axis value at least once before a second value on any axis. Cheap cells come first (small model, B1–8, ctx ≤ 1k, 1 GPU).

| Axis | Values |
|---|---|
| model family | Qwen2 / 2.5 / 3, Llama, Gemma, Phi, Mistral, Pythia, SmolLM, TinyLlama |
| dense vs MoE | dense; Qwen3-30B-A3B, OLMoE |
| dtype | BF16; FP8 (per-tensor, block-128) |
| sampler | greedy, top-p, top-k, Gumbel |
| TP | 1, 2, 4 |
| batching | batch size; chunked prefill on/off; prefix caching on/off |
| context | ≤ 4k |
| attention backend | whatever the registry binds (FA2, FA3 on H100, FlashInfer if registered) |
| GPU | L40S, A100, H100 (RunPod); RTX PRO 6000 (vy-nebius-1) |

**Stretch row, after BF16 and FP8 breadth: NVFP4.** Record it `unsupported (no Definition)` until the FP4 work below lands; don't launch pods for it.

## Labels, on each cell's attempt
- `ov.ws coverage`
- `ov.config <row slug>` (superseded 06:10Z: see `20260930T0610Z-note-from-vllm-coordinator-coverage-labels.md`)
- `ov.gate pass|fail|unsupported`, cause in `ov.note`, `--off-vocab`, campaign `overnight-sep30`
- **Extraction slowdown,** split into prefill and decode: the instrumented Commit's timings against the uninstrumented baseline. The baseline is attempt 0 of line `build-v1`; label its source.

Checkpoints are one line in your folder at each 10 cells, and a handoff to me only when something blocks or changes the plan. I render the coverage table from the labels, so there's no table to maintain.

## FP4 (not yours; for context)
Root asked for FP4 as a stretch after BF16 and FP8.
- **(1)** Extend core's RTX 5090 pin of `BlockScaledAlignAdd` (NVFP4 and MXFP4, `mma.sync kind::mxf4nvf4`) to the PRO 6000 with `tools/tc_probe_fp4` on one vy-nebius-1 GPU. That's minutes once #478 lands. POUS's `vy-pouw-rtxpro-fp4cap-1` may produce the same evidence first, and we take it as labels.
- **(2)** Capture which kernel vLLM's NVFP4 path actually launches on sm_120.
- **(3)** A Definition and binding follow only if (2) matches the pinned step.

tc-gemm and fp8-ckpt own FP4, after their FP8 work.
