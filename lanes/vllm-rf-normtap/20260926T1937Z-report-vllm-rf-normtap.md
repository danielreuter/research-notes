---
lane: vllm-rf-normtap
kind: report
created: 2026-09-26T19:37Z
status: open
---

CHECKPOINT 10c97ae5 (20:23Z) [open] pushed 10c97ae5 (3 commits): norm_scales policy + manifest --norm-scales, tapped CUDA op build + Triton copy + source, NORM_TAP flag plumbing (commit.py/required.py line-neutral at P10 caps). Next: exactness property + GPU script, pod_norm_tap.sh, CPU tests.
CHECKPOINT baa800c6 (19:55Z) [open] design mapped: tapped CUDA op (vendored generic fused_add_rms_norm kernel + 1 store) + patched Triton _rms_norm_kernel; source swapped via engine/hooks; family norm_scales (lint-clean name) under <norm module>/scale; Gemma RsqrtF32 output protocol-required; flag CommitConfig NORM_TAP. Coding CPU side next.
CHECKPOINT baa800c6 (19:37Z) [open] started (agent bc-12c2f2d9); branch cursor/vllm-rf-normtap-57d5 from origin/main@baa800c6 (Cursor branch policy; common-rules fallback form). Reading plan §4 + arch §4.2/4.4/4.8; code + CPU tests first; no pod until coordinator confirms GPU estimate.
