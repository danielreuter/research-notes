---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T08:48Z
---

# #483's new head after TVF: `3cc9355c`, for re-grant

- **The merge:** main `cc0f4688` (TVF), merged into #483 by merge, is `3cc9355c`. It merged **without conflicts**:
  - TVF's `registry/targets.py` changes (the attention lane's FA2 binding, which carries #465) sit beside `gemm_bias_spec`;
  - #486 and #481 aren't in main yet, so their union resolution is still ahead of whichever lands second;
  - no other unmerged PR is merged in.
- **Tests on `3cc9355c`:** run `r20260930-084533-99ba`, vy-nebius-1 check slot a, CUDA hidden. All pass:
  - `test_gemm_bias_f32_epilogue`, `test_gemm_bias`, `test_gemm_targets`, `test_gemm_target_correspondence`, `test_kernel_self_check`, `test_target_family`;
  - `tests/lint` (P1–P12), `test_imports_resolve`, `test_no_by_name_rules`, `test_no_dead_modules`.
