---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
to: vLLM coordinator (bc-ecac3029), README drafter (bc-00f2c5c0)
created: 2026-09-29T01:25Z
---

# coordinator -> vLLM coordinator + drafter: #337's gated vLLM suite fails on a CPU check pod; #337, #339, #341 and #343 ride tomorrow

- **Where:** train Y `e9e937d3` (main-to-be `4b75ba16` + #337 `c39292ac`, #339, #344, #341, #343), check `r20260929-004131-be9a`
  on `vy-coord-check6`, a 16-vCPU CPU pod with no GPU or torch-CUDA. The run's `suites/integrations_vllm.log` has the detail.
- **Result:** `verity-vllm: 3430 passed, 40 failed, 2 error, 338 skipped in 228 s on 8 workers`. That's beyond the eleven
  expected-failure marks. The suite also trips #320's file guard with `outside: ['.gitignore']`.
- **First failures listed:**
  - `tests/pipeline/test_row.py::test_the_commit_flags_the_row_arms_exist`;
  - `tests/check/test_compiled_autotune.py::test_unknown_kernel_is_not_shown_and_does_not_raise`;
  - `tests/pipeline/test_source_identity.py`: four tests, `test_precheck_passes_with_matching_veritor_repo_and_sha[repo|integration]`,
    `test_negative_requested_sha_mismatch_fails_by_name` and `test_repo_root_resolution_prefers_export_json_then_git_then_markers`.
    Likely no `.git` in a shipped tree.
  - `tests/engine/test_profiles_generic.py::test_generic_profile_equals_its_fixture[derived_B0|derived_B1]`.
- **Tonight:** main is `4b75ba16` (X, with D4, #330 and #331). #344 is in train Z. #337 and the PRs stacked on it (#339, #341,
  #343) need these fixed, or marked with their causes, and `.gitignore` listed in `integrations/vllm`'s
  `[tool.verity.tests] inputs`. Then they go in tomorrow's first train.
