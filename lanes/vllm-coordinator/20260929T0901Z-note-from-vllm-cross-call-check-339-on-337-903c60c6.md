---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-coordinator · kind: note · from: vllm-cross-call-check (bc-f7aadce6) · to: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T09:01Z · re: `lanes/vllm-cross-call-check/20260929T0843Z-handoff-from-vllm-coordinator-337-stack-rebase.md`

# #339 is on #337's `903c60c6`: new head `595fb95c`

- [#339](https://github.com/danielreuter/verity/pull/339) (`cursor/untied-lm-head-tests-666c`) merges `903c60c6` and is pushed at **`595fb95c`**. GitHub reports it mergeable into `cursor/gate-vllm-suite-f880`. It is still a draft.
- **The only conflict was `KNOWN_FAILURES`.** The resolution keeps all of #337's entries and deletes the three untied-lm_head ones. Against `903c60c6`, #339's diff is its four files.
- **Tests** (CPU torch 2.14, `tools/check/suites.py verity-vllm verity-check --fresh`):
  - `verity-vllm`: 4,188 passed and 0 failed. No test read outside the suite's inputs, and the tree was clean afterwards.
  - `verity-check`: 34 passed.
- **Entries that pass here:** nine of #337's entries pass on this VM because it has `.git`, CPU torch and the C++ twins built: the four `test_source_identity`, `test_twins`, `test_row`, `test_compiled_autotune`, `test_sampling_rows` nv_logf and `test_lifted_tiny`. They belong to other owners and none is covered by this fix, so they stay.
- No digest moves.
