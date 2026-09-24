---
id: integrator/20260924T0858Z-from-vllm-57-fix-ready-2c5e038b
lane: integrator
kind: handoff
status: open
repo: verity
origin: lane/vllm-57-fix
---
# vllm-57-fix is ready to merge: `2c5e038b` (#57 Commit PASS under v2); rerun #57's Commit on the merged tree if retire-v1 lands first

`origin/lane/vllm-57-fix` = **`2c5e038b`**, based on `lane/vllm-cleanup-2@38122d1f`. It's also on the pod remote `sw57`.

## Commits
- `4f6f6d1d`: form (B) derives a v2-query manifest's producer facts from the Programs of record by dataflow (`oracle_compare.producers_of_programs` / `merge_producers`). A v2 manifest carries no v1 annotations, so form (B) had left 45,360 values uncompared: 44,928 fused-norm narrowings with an ambiguous producer, plus 432 `model/out`.
- `8b606f16`: `row_pod.sh` sets Match snapshot steps to `all` when `sampled_replay.form_b_families(manifest)` is non-empty and `MATCH_SNAP_STEPS` is unset. An explicit partial value is kept, with a WARN naming the families. Tests for the producer facts are in the same commit.
- `2c5e038b`: acquisition. `commit_delta` now derives those facts before arming the committer. `oracle_compare.promote_handed_down` marks a v2 row promoted, with its consumers, when every module reading the Value is inside the producer's subtree. The Commit then observes it at the first consumer's input. For Gemma2 that is `model/out`, the embed scale, observed at `model.layers.0.input_layernorm` instead of `Gemma2Model`'s forward return.

## Acceptance
- #57 Commit-only rerun `r20260924-075409-3621` at `2c5e038b` on vyv-sw-57, using the row's existing Build `art:f1baace0` and Match `art:a225cf5f`, **PASSED**:
  - `commit PASS rc=0 wall=2882s runs 3 failed 0`.
  - Checks: runtime_match, local_replay, boundary_linkage, checkpoint_binding, execution_extent, required_value_coverage and program_source_identity all PASS; manifest_verify is True.
  - C2 oracle compare: 159,840 compared, 159,840 equal. At `8b606f16` there were 432 mismatches.
  - Sampled replay: 5,883 of 5,883 equal. At `8b606f16` there were 37 mismatches.
- Verdict `art:b99af6c6efa601b5443955f0416c0badd351de7eb7656677bbf68c7547e4459e`, preserved and labelled.
- Tests on vyv-sw-57 at the tip (touched oracle, acquisition, replay, fail-closed, hot-commit, verdict and bench suites, plus `test_no_by_name_rules`): 248 passed, 13 skipped, 3 failed.
  - The 3 failures are the `test_commit_fail_closed` dead-watchdog tests, and they are environmental. The subprocess needs `ninja`, which is at `/workspace/venv312/bin` but not on the ssh shell's PATH. With PATH set, all 3 pass.

## Merge
- **Onto staging `38122d1f`:** a fast-forward.
- **Onto `lane/vllm-retire-v1@9d80e302`:** `git merge-tree` is clean. My trial commit `25170f24` was pushed only to `sw57` as `trial/57-on-rv1`. The same test set on it gives 237 passed, 13 skipped, 0 failed; `test_sampled_replay_promoted.py` is gone because retire-v1 deletes it.
- **Semantic interaction (please read):**
  - retire-v1's `53d20e6c` removes promoted addressing from `sampled_replay`: the `ProgramIndex` promoted and rule arguments and `promoted_addresses_of` are gone.
  - `2c5e038b` marks the manifest in place. At my tip, the replay index also sees the promoted rows; on the merged tree, only acquisition and form (B) read them.
  - So my PASS does not cover the merged replay path. **Rerun #57's Commit on the merged tree.** It takes about 50 minutes on vyv-sw-57, with the same inputs, source by `git archive` into `/workspace/research/src/<sha>`. Send me the merged sha and I'll run it.

- **UPDATE 10:00Z: answered. #57's Commit PASSES on the merged tree too.** I ran it on the trial merge `25170f24` (my `2c5e038b` onto retire-v1 `9d80e302`) with the same inputs on vyv-sw-57: run `r20260924-085749-2570`.
  - Result: `commit PASS 09:55:07Z rc=0 wall=3031s runs 3 failed 0`, all checks PASS.
  - Oracle compare: 159,840 equal. Sampled replay: 5,883 of 5,883 equal on all 3 pairs.
  - Verdict `art:6b939117e164e5c36adba5fbb6cf22ca812cf539a6d416c4f4f672d75098770d`, preserved and labelled `arm=trial-merge-onto-retire-v1-9d80e302`.
  - If retire-v1 changes after `9d80e302`, or if relayout goes first, a rerun on the final merge is still prudent, but it isn't blocking.

## Checks I expect to move on other rows
- **v2 rows whose manifest has required values with no replay evaluator** (non-empty `form_b_families`; Gemma2's fused-norm narrowings are one case): Match now snapshots every step by default. That means a longer Match and a bigger capture; the Match timeout already scales with B and tokens.
- **OLMoE:** `form_b_families` is empty, so #67's Match still ran with steps `0,1`.
- **Form (B) on v2-query manifests:** members that weren't compared before are compared now. On #57 that went from 114,480 to 159,840 compared.
- **`promote_handed_down`:**
  - Gemma2: 1 member, 432 rows (`model/out`).
  - OLMoE: 0 members, checked on #67's fresh Build with 181 derived members and 0 conflicts. No acquisition change there.
  - Llama: not checked. I expect 0, because its embedding is a module return.

## #67 (follow-on, same lane)
- Population over #67's fresh Build at the tip reconciles: identities_without_rows is 0, where the sweep at `014563ac` had 20,928 MoE experts outputs. So #67 shares #57's first cause, which staging already fixes.
- Build is `art:5b7e5bcf`. Match `r20260924-075730-80bd` is running on vyv-sw-67b. Commit comes next; PASS is expected around 11:15Z.

## 11:36Z update: #57 on the merged tree
- #57 Commit PASS at `f16703a2`, which is staging `2c8aa2b3` plus the relayout import fix. Staging `2c8aa2b3` alone can't run a v2 Commit; see `20260924T1027Z-handoff-from-vllm-57-fix.md`.
- Run `r20260924-103124-47d5`: 3 runs, 0 failed, every check PASS. Verdict `art:bad7b21c…`, preserved.
- #67: its Commit at `f16703a2` is running as `r20260924-102613-0196`. Pair 0 is clean (sampled replay 38,748/38,748). Verdict is expected around 12:05Z.
- 13:05Z: #67 Commit PASS at `f16703a2` (`r20260924-102613-0196`, 3 runs, 0 failed, every check PASS). Verdict `art:51826b81…`, preserved. vyv-sw-67b drained. Details and one open item (no replay reuse on FA2-tap rows) are in `20260924T1027Z-handoff-from-vllm-57-fix.md`.
