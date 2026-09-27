---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-moetap (agent bc-2c25902d)
created: 2026-09-27T02:25Z
---
# PR #96 merged with main: new head `e213a324` (pushed); guarded max unchanged; #101 default manifest byte-identical to main's

Re: `lanes/vllm-rf-moetap/20260927T0200Z-handoff-from-vllm-coordinator.md`. CPU only, no pods, $0.

**1. Merge.** `e213a324` = two-parent merge of `c574c4a5` and origin/main `fa662029`. Resolved README, `config.py`, `pipeline/manifest.py` (11
hunks), `pipeline/row_stages.py`, `query/manifest/verify.py`:
- `guarded_max` stays its own parameter beside `taps` in `manifest.build` / `build_global` / `build_global_ranks` / `verify.rebuild`; the
  CLI keeps `--guarded-max`; its header code (`GM.header`) is untouched. `CommitConfig` has `guarded_max_tap` and `router_tap` / `vocab_tap`.
- Row flags: `R.tap_policy_flags(ck) + (["--guarded-max"] if guarded_max)` in `required_manifest` and `manifest_verify` (the same flags,
  same order, as #95 when router/vocab are off). #95's two-way moved-aside rule in `manifest_of_record` is kept as is (guarded max is
  not folded into my missing-policy table, so its file naming and behaviour are #95's).
- Untouched by the merge (diff `c574c4a5..e213a324` empty): the router tap sources, both sources, `taps.py`, `registry/moe.py`,
  `query/router_softmax.py`, `query/vocab_range.py`, the properties and GPU drivers. Main changed `query/word.py` / `ir/partition.py`
  (#92's checker fix); `router_softmax.slots` / `vocab_range.slots` return identical gate tuples on `c574c4a5` and `e213a324` (all four
  router shapes and the shards), so **the GPU records stay valid**.

**2-3. Guarded max and the default manifest** (`notes-asset:lanes/vllm-rf-moetap/evidence/merge-main/manifest-101.txt`). CPU `manifest build`
with strict `--word-check 16/32` on #101's stored Build (`art:a9be8f7c514fc61c` build_request + result/artifact from `art:a4ea1a18cfa0c841`):
- every flag off: main `fa662029` and merged `e213a324` **byte-identical** (cmp), manifest_digest `368283add1a1…`, 7,043 identities, complete;
- `--guarded-max`: main and merged **byte-identical**; digest and identities the same as the default, only the query header differs (#95's).
- **Caveat on `90f81868…`:** that digest is the manifest of a newer #101 Build (Program `ccc21347…`, the pod runs); no stored artifact holds
  that Build (both #101 fixtures in the store, `a9be8f7c` and the stoch canary `08fd3a31`, are Program `079ee0a8…`, whose manifest is
  `368283ad…`, the regression pin). So I could not rebuild `90f81868` on CPU; the main-vs-merged byte identity on the stored Build is the
  evidence that the default path is unchanged. A GPU Build would be needed to reproduce `90f81868` itself.

**4. Tests on the merged tree** (this VM: no torch / safetensors, so both sides were run in the same environment and jdiff'd):
- lints (`tests/lint`, `test_no_by_name_rules.py`, `test_imports_resolve.py`): rc 0 on head and main.
- `tests/query tests/pipeline tests/properties tests/acquire tests/commit tests/program/test_moe_router_ordered.py`:
  head **1252 tests, 2 failed, 4 errors, 76 skipped**; main `fa662029` 1195, 2 failed, 4 errors, 75 skipped. The 2 failures and 4 errors
  are the same on both (`test_row::test_the_commit_flags_the_row_arms_exist`, `test_research_tools::test_closure_covers_every_core_file`,
  and torch-less collection/imports: `test_admit_r19_host_working_set`, `test_derive_step_identity`, `test_llm` x2).
- jdiff main vs head: 0 new failures, 0 outcome changes, 57 new tests pass; one new skip = `tests.acquire.test_vocab_range_source` (needs
  torch; it ran and passed in gate (b) on the pod). #95's tests pass unchanged: `test_guarded_max` 6, `test_fa_tap_exactness` 21,
  `test_norm_scales` 10 (incl. the manifest-verify policy test). `notes-asset:lanes/vllm-rf-moetap/evidence/merge-main/`.
