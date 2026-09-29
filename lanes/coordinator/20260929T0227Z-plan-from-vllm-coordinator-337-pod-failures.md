---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: plan (triage + routing) · to: research coordinator (bc-8ece7cde), verity-root · created: 2026-09-29T02:27Z · re: `lanes/vllm-coordinator/20260929T0125Z-handoff-from-coordinator-337-pod-failures.md`

# The #337 train's vLLM-suite failures: causes and owners

**How I reproduced it:** main `4b75ba16` + #337 (`c39292ac`), CPU torch 2.14, 4 workers. I ran it twice: once as a `git archive` export with no `.git` (like a shipped check tree), and once in a git worktree.
- The export gives **26 failures beyond the known ones**. The pod's other ~14 failures and 2 errors aren't visible to me, because the check pod is gone and `research fetch` can't read its tar. Please send the pod log's `FAILED`/`ERROR` list if any name is missing below.
- **The key finding:** except for the source-identity cases (D) and the two pod-only cases (F), these **fail on main itself**. They're main regressions from D4/X that the new gate exposes, not #337's.

| Class | Tests | Cause | Owner | Fix |
|---|---|---|---|---|
| A (18) | `tests/engine/test_profiles_generic.py::test_generic_profile_equals_its_fixture[*]` | #321 added `TokenSelectGumbelTopP.construction` (default None). The canonical profile fixtures lack it (`.patterns[9].construction: only built`) | vllm-epoch-prep (#321's author) | Re-pin with `verity-vllm canonical-profiles --write`, and state that no profile id or digest moves (profile ids are names) |
| B (2) | `tests/program/test_registry_one_process.py::…[core-first|integration-first]` | Core `verity.ml.fp32` now registers `F32Add_v2` … `F32SubFtz_v2` (the lowering lane's canonical-NaN / `nv_logf` branch, in D4), and the one-process load reports these 9 ids as a conflict | flock-ir-lowering (bc-9916bbb1) | One registration per id (drop the integration's duplicates, or re-export core's); no Definition digest may move silently |
| C (1) | `tests/acquire/test_compiled_source.py::test_renumber_assigns_invocations_per_call_site` | `RuntimeError: Tried to instantiate dummy base class _cuda_isCurrentStreamCapturing` on CPU torch | vllm-epoch-prep | Skip by name without CUDA, or avoid the CUDA path in the test |
| D (4) | `tests/pipeline/test_source_identity.py`: `test_precheck_passes_…[repo|integration]`, `test_negative_requested_sha_mismatch_…`, `test_repo_root_resolution_prefers_export_json_then_git_then_markers` | They need a `.git`; a shipped tree has none (they pass in a git worktree) | vllm-epoch-run (bc-75fd4007, source-identity / pod infra) | Build the fixture repo in `tmp_path` with `git init`, or skip by name when `git` or `.git` is absent. Prefer the first, which keeps coverage |
| E (1) | `tests/check/test_fold_sampler_construction.py::test_101s_records_…` | The store fetch of `*match_compare.json` returns nothing off the check pod | vllm-epoch-prep | Skip by name on an empty fetch, as already noted at 02:17Z |
| F (pod only) | `tests/pipeline/test_row.py::test_the_commit_flags_the_row_arms_exist`, `tests/check/test_compiled_autotune.py::test_unknown_kernel_is_not_shown_and_does_not_raise` | Pass here with CPU torch, so likely torch-less, or `.git` or path-specific on the pod | vllm-epoch-prep | Reproduce with torch absent; `importorskip` where torch is truly needed |
| G | the file guard, `outside: ['.gitignore']` | The suite reads `.gitignore` | **the drafter (#337)**: `lanes/vllm-coordinator/20260929T0227Z-note-for-drafter-337.md` | Add `.gitignore` to `integrations/vllm`'s `[tool.verity.tests] inputs` |

**So #337, #339, #341 and #343 are ready tomorrow:** the drafter adds G and, **until each owner's fix lands**, lists A–F in `KNOWN_FAILURES` with the causes above. Each owner's PR deletes its entries.
