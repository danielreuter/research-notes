---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T13:50Z
---
# Verdicts: PR #63 APPROVE (as sent 13:30Z), PR #80 APPROVE with a follow-up that's now urgent

Merge both, in either order. On main `f41b62cf`, #63 + #80 merge cleanly together, and every ratchet lint runnable without
pytest passes on the combined tree (39/39).

## PR #63 (`898c32ef`, vllm-more-exports): APPROVE
Unchanged from `20260926T1330Z-handoff-from-vllm-coordinator.md`. The exporter learns FP8 block GEMM and MoE expert coordinates, and the
store keeps non-u16 weight rows. That fixes the silent drop of every FP8 GEMM and MoE unit. Each coordinate is verified against the
row's recorded word. Exporter-only.

## PR #80 (`30c7a28a`, vllm-vu-export): APPROVE
- **The bug:** `export_vus` started the draw's `max_seconds` (600 s) budget at `t0`, before the population build. On #67's 33 request
  Programs the build took over 18 min, so the export ran out of time before its first draw. That's exactly what left vllm-more-exports
  with no MoE sets.
- **The fix:** the draw's budget starts after the build (`t_draw`). The build has its own `max_population_seconds` (default 3600 s),
  checked between request Programs, and the Programs past it are named. The report gains a `timing` block. There'"'"'s a new test module
  `tests/pipeline/test_vu_store_budget.py` (in its own file, so it doesn'"'"'t conflict with #63'"'"'s tests). Exporter-only, no record effect.
- **Follow-up, now urgent (it'"'"'s PR #42'"'"'s, still open):** the export runs at `pipeline/commit.py:2513`, before `verdict.json` and
  `summary.json` are written (lines 2758/2853), and it's on by default in every row. With #80, it can now spend up to 3600 s + 600 s
  there, on every default-on Commit, before the verdict exists. That lengthens the window in which an OOM, a stage timeout or a
  preemption loses the record, and adds up to about 70 min per row.
  - Please have vllm-vu-export **move the export after the verdict and summary are written**. Until then, lower the default-on
    `max_population_seconds` (to about 900 s), or keep default-on only for rows whose population builds fast.
  - The lane rules (`vllm-cloud-common.md`) already set `VU_EXPORT=0` on memory-tight rows.
  - Tonight's #67 re-run by vllm-more-exports is an explicit export run, so it'"'"'s fine as is.
