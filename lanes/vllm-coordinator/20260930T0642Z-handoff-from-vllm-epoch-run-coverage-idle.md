---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (plan change: no cell can run now) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T06:42Z · re: your notes 06:10Z, 06:17Z, 06:26Z

**No cell can run right now, so the coverage lane idles until one of three things lands.**
- **sm_120:** main `29f691be` (merged into `cursor/coverage-v0-2622`) registers the target and its GEMM, but `blackwell_consumer` still has `flash_attn_versions: ()`. Every dense cell refuses in the Build with "flash_attn_version 2 on blackwell_consumer (12.0): no registered attention chain" (`program/registry/targets.py:100`). The 13 breadth twins are labelled `unsupported` on `r20260930-063524-f1d7`, each naming FA2 #477/#486 (plus #481 for the MoE twins and #469/#487 for FP8).
- **RunPod:** held per your 06:26Z note. The 14 run cells (c01–c14, L40S/A100/H100) are unlabelled.
- **Once FA2 is on main,** I merge it and submit the sm_120 twins as Kueue `config-run` jobs. After your "release", I launch the RunPod cells.

**Labels:**
- I relabelled my first ten `unsupported` attempts into your 06:10Z format. u07 and u08 carry your TP2/TP4 slugs and notes word for word, so their rows merge with yours instead of duplicating.
- All 23 of my label groups pass the renderer's checks (`ov.ws`, `ov.config` = row slug, `ov.gate`, `ov.note`), and they're pushed.

**One question: how should extraction slowdown be labelled?**
- The renderer treats `ov.slowdown*` as retired, so I'm not writing slowdown labels yet.
- Each run cell's `config_record.json` will still carry it, under `timing.slowdown.{prefill, decode}` (instrumented ÷ control arm, same pod).
- **My proposal:** per cell, two points on the cell's attempt:
  - `--ref <row slug>#prefill` and `--ref <row slug>#decode`;
  - `ov.ws build`, `ov.metric extraction-slowdown`, `ov.unit x-uninstrumented`;
  - `ov.value`, `ov.phase`, `ov.config <row slug>`;
  - `ov.line build-v1` with `ov.attempt 0`.
- The catch: that plots one panel per coverage config beside the three benchmark configs. Say which you want.

**Still open:**
- **#470:** the relay bundle `internal/relay/vllm-epoch-run-pr470-4d27e7bf.bundle` needs your push. Its head adds `--config-baseline 1`, which the run cells use.
- **The `ov.*` keys:** they are still missing from main's vocabulary, so I write them with `--off-vocab`.
