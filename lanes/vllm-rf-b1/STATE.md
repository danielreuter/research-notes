---
id: vllm-rf-b1/state
lane: vllm-rf-b1
kind: state
updated: 2026-09-25T12:10Z
---
# b1 (evaluator kernels and replay): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT; updated 11:31Z)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-910bfdb6. Budget $45 of pod spend.
Worktree `~/projects/verity-wt/rf-b1`, branch `lane/vllm-rf-b1`.
a4 base: 10996616

## Done
- worktree created at 10996616.
- read: WAVE2_BRIEF, SYNTHESIS (smell 1, T1, P3, 5.1/5.2, B1, decisions), core verity.evaluation, check/replay/sampled_replay.py, program/kernels/twins.py, replay.py, f1/f3/a4 notes.
- bf3bdbec `derived_rows.py` moves `program/registry/` -> `program/kernels/` (git mv + import lines + allowlist paths). **c2: two import lines in your files changed** (`program/registry/ref_prims.py:850`, `program/registry/sampling_rows.py:34`), nothing else in `program/registry/`.

- a6613e94 (pushed) `program/kernels/rows.py` (the sampled-replay evaluator ladder as 22 per-family row kernels, registered with core `register_kernel` under kernel "rows", samplers + small check specialisations) and `program/kernels/kernel_registry.py` (instance form with decline reason, check targets, registered list: upstream candidates). `sampled_replay.evaluate` dispatches via `rows.ROWS`; `_Unresolved = Declined`. Gumbel kernel uses core `evaluate` (drops the check -> properties import, p05 entry deleted). Allowlists: p03/p05/by_name entries deleted, p08/p11 entries moved to rows.py, p10 SR 3099 -> 2614. Laptop lint scan 0 failing.
- fce215be rows.py imports `type_dtype`/`type_shape` from `verity.evaluation.batch`.
- c42923bc twins -> core kernels (kernel "twin"): Twin protocol, `twin_for`, `why_no_twin`, `TwinDeclined`, `self_check`, `gate_words` deleted; `twins.admit` runs core `self_check` per instance; `replay.twin_of` uses `kernel_registry.covers/instance`. Renamed tests: `test_twin_for_covers_every_logged_specialization` -> `test_twins_cover_every_logged_specialization`, `test_twin_for_declines_statics_outside_the_body` -> `test_twins_decline_statics_outside_the_body`.
- e86c93b3 `tests/program/test_kernel_self_check.py`: every registered (kernel, Definition) pair against core `self_check`.
- ee2a319f test fix (MoE router / padded memo live in rows). head-touched2 at e86c93b3: 2 failed (these), 239 passed.
- a6ba1e5b `check/replay/challenge.py`: every seed derivation of record + the only generator constructors; routed: SR.sample, SR.challenge_seed, replay tier_a/tier_chain, compiled_kernel_check, stoch_recompute reference rows, vu_query.production_sample, admission.produce (difftest), relations draw_sample/ensure_adjacent_pair, pipeline/commit.py main (3 one-line hunks + 1 import). RNG_OWNERS; 10 p03 entries deleted; P10 SR module 2614 -> 2611, commit.main 1914 -> 1913. Pinned-value tests in tests/check/test_challenge_seeds.py.
- 31a0be62 `check/sampled_replay.py` deleted: split into `check/replay/{index,opening,compare,evaluate,population,coverage,sample,linkage,driver}.py` (acyclic; driver `__all__` re-exports the caller interface so pipeline/commit.py and engine/rank_worker.py change one import line each). Allowlist entries moved in place (p03/p04/p07/p09/p10/p11/by_name); p10 SR module entry deleted (all new modules < 800).
- 7cde62a5 difftest `evaluate_spec` = core `verity.evaluation.evaluate` (drops the hand-built one-call Program and the observe.fold `_replayer` import). Verified on pod (head-touched3: test_sampled_replay_stoch, test_sampling_rows/operands, test_topp_splits_operand, test_gen_ln, properties/test_difftest pass, unregistered `DT.spec(...)` included).
- head gate (b) at a6ba1e5b vs base (same pod): 4 new failures -> fixed: hopper `gemm_dot_prim` (31a0be62), test_compiled_replay_seed_source (b7a70aa8), test_no_dead_modules (19ca2453: crosscheck + beyond_gemm lost their only production importer, the twins' gate-word self-check; moved to tests/program, 9 lint entries deleted), test_roundtrip::test_transient_storage_is_released (c1's lane saw it flip too; recheck at the final gate).
- b7a70aa8 compiled-check seed test reads `CH.kernel_check_seed(rc.run_root)` and pins its value. NOTE: `git mv` had staged the crosscheck/beyond_gemm renames, so they landed in this commit; their import lines are in 19ca2453 (b7a70aa8 alone does not import cleanly; no history rewrite).
- 19ca2453 crosscheck + beyond_gemm -> tests/program (import lines, p03/p06/p07/p08 entries deleted, dead_code_keep fa3_model reason). **c2: `program/registry/crosscheck.py` left your directory** (it has no production importer since the twins use core self_check).
- 8c0bec08 test_prescribed_input_linkage: the source-text assertion names `SR.arrivals_of_record` as commit.py writes it (split rewrite had changed it).
- head-touched3 at 19ca2453 (37 files + lints + regression, -n 12): 529 passed, 4 failed = 3 base failures (admit_r19 gc-freeze pair, test_sampling_rows nv_logf) + the linkage string (fixed in 8c0bec08).

## Plan
1. done (derived_rows move).
2. done (a6613e94).
3. twins -> core kernels (kernel "twin"); core `self_check` replaces twins.self_check/check_instances/gate_words and the Twin protocol. Test: every registered (kernel, Definition) pair self-checks.
4. `check/replay/challenge.py`: today's seed forms (root, challenge, prover) + generator constructors; RNG_OWNERS; drivers (replay tiers, stoch_recompute, compiled_kernel_check, vu_query, difftest) use it. No seed derivation changes.
5. Split sampled_replay.py into sample / open / evaluate / compare / c2 driver / linkage; delete it; repoint importers (import lines only in other lanes' files).
6. Pods: gate (b) head vs base, gate (a) T0+T1 on cpu3m 512 GB, GPU #101, #67 PAIRS=1, #70 if rank path changes.

## Results
- **GATE (b) at 8c0bec08 MEETS THE RULE** (`r20260925-112532-d480`, vyv-rf-b1-cpu, same pod as base): head 50 F / 3683 P / 286 S / 6 xf / 11 E vs base 52 / 3645 / 287 / 6 / 11; `baseline-jdiff.py` rc 0: new failures 0, new skips 0, new skip reasons 0; failures+errors 63 -> 61. Renamed 4 (seed-default param id now names `driver`; the 3 twins renames); 39 new tests all pass (31 self-check pairs: 22 rows + 9 twins). test_transient_storage_is_released passes (the a6ba flip did not recur). Lint gate tests inside it: 45/45 pass. Evidence: `head-gate_b-8c0bec08-xdist.{xml.gz,jdiff-base.txt}`, `base-gate_b-10996616-xdist.xml.gz`, `cpu-pod-logs.tgz` (logs/env/rss of every cpu-pod run).
- **#101 at head == base == record** (`r20260925-113151-99a2`, vyv-rf-b1-g1; head tree synced at 19ca2453, whose production code is 8c0bec08's): program ccc21347, manifest 90f81868, run root 7adcef49, commit PASS, every check the same; C2 oracle compare 6304 = 6304; sampled replay 1374 picked = evaluated = equal of 46558 VUs / 868 strata, seed 8853214064722388274, picks/strata/by_family digests equal; forked evaluators 84,118 reads both. Replay wall 79.3 s (base) -> 79.8 s (head), 32 workers; Commit 243 s (base, after the tree switch) / 191 s (head).
- cpu pod terminated 12:08Z, g1 terminated 12:02Z (runs fetched --all).

## Running
- `vyv-rf-b1-big` (61mmy8g18xcj0z, cpu3m 64 vCPU / 512 GB, $3.52/h, since 11:24Z): head 8c0bec08 + base synced, bootstrap OK 11:48Z; laptop-minted read-only key piped in 11:58Z. **Gate (a) `r20260925-115853-be37`** (`big_gate_a.sh`): prefetch done 12:07Z ok=26 fail=0 key_deleted=yes; head T0+T1 split 4-way running, then base replay_partition on the same pod for replay wall time.
- `vyv-rf-b1-g2` (l2w6439556ueod, 1x L40S, 188 GB, driver 580, $1.09/h): created 11:18:44Z by the first retry loop, which died before registering it; found and registered (guard 90) at 11:49Z, so ~30 min of it idle. **#67 `r20260925-120629-a48a`** (12:06Z) = `g2.sh`: bootstrap OLMOE, Build+Match once at head, row dir copied, Commit PAIRS=1 at head then at base (f1's shared-Match pattern), rowcmp vs record (program fdd998d4, v2 manifest 47990631, commit_pass True).
- #70 (2x L40S): still no capacity; the retry loop now tries tp2 only, until ~12:30Z.

## Next
- gate (a) merged xml vs a23b base (test by test) + replay_partition times head vs base; #67 stages vs record; #70 only if a 2x L40S appears; READY.md (draft /tmp/b1/READY.draft.md).

## Open questions
- **Ask (12:02Z): extend the pod deadline for `vyv-rf-b1-g2` only, to about 17:30Z.** #67 from scratch on one 1x L40S (f1's timings on the same pod shape): Build ~83 min, Match ~66 min, each PAIRS=1 Commit ~65-100 min (sampled replay dominates). Head Commit should end around 15:30-16:00Z, base around 17:00-17:30Z. Without an extension I stop at 15:30Z with whatever #67 reached (Build/Match vs record, maybe the head Commit), and the MoE replay evidence is gate (a)'s T1 replay_partition on #67/#68/#73/#74. About $6 on g2.
- **Ask (11:42Z):** RunPod has had no 2x L40S (any cloud, CUDA 12.8-13.0) since 11:00Z. If a lane's 2x L40S pod (b4-tp2, b2v-tp2, a5-tp2) is about to be terminated, could it be handed to b1 for #70 instead (about 2.5 h: bootstrap OLMOE, build, match, commit PAIRS=1 at head)? I'd use my own trees under /workspace/b1-* and never touch theirs.
- GPU capacity: no 2x L40S or >= 180 GB 1x L40S with CUDA >= 12.8 on RunPod since 11:00Z. #70 is OLMoE, so it covers the MoE family and the TP2 rank path together; if it never comes up, the MoE/TP replay evidence is gate (a)'s T1 replay_partition on #67/#68/#73/#74 (CPU, recorded words).
- difftest lives in properties/admission.py (b2v's `properties/`): hunks are the rng call, the evaluate call and import lines.
- difftest lives in properties/admission.py (b2v's `properties/`): will keep hunks to the rng call + evaluate call + import lines.

## Found, not fixed
- replay row evaluators differ from their Definitions on edge words (twins document the Definition's behaviour): TokenSelect_v1 with a NaN logits[0] (Definition -> 0; row kernel -> argmax of the rest); BiasAdd_v1 NaN result word (Definition 0x7FC0; row kernel 0x7FFF); Gemm_v1 / MoeExpertGemm(W)_v1 / padded MoE blocks evaluate lanes with a non-finite operand or accumulator with the vectorised twin instead of declining. Not reachable on finite committed words; kept as is (no per-VU result may move), the batch kernel declines them.
- Not routed through the challenge module (other lanes' files or P10-capped outside scope): engine/rank_worker.py:1220 root seed (b4), check/commit_verdict.py seed recompute (b2v), commit/binding.challenge_identities (c1), correspondence/capture_identities.run default_rng(seed) (module at its P10 cap). relations draw_sample/ensure_adjacent_pair have no caller in the integration.
