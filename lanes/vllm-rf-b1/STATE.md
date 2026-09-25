---
id: vllm-rf-b1/state
lane: vllm-rf-b1
kind: state
updated: 2026-09-25T11:45Z
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

## Running
- `vyv-rf-b1-cpu` (cei1t48zvrcnzu, cpu3g 32 vCPU / 128 GB, $1.28/h, since 08:47Z): base gate (b) done 10:18Z (52 F, 3645 P, 287 S, 6 xf, 11 E; base-xdist.xml, nohup run). **Final head gate (b) at 8c0bec08: `r20260925-112532-d480`** (`gate_b.sh /workspace/head gate_b-head-8c0bec08 -n 12 --dist loadfile`, OMP 3; tree verified == git 8c0bec08 by blob hash, test-written ref-prims restored).
- `vyv-rf-b1-g1` (nz7au6e51web6w, 1x L40S, driver 580.159.03, 125 GB cgroup, $1.09/h?, since 11:03Z): `r20260925-113151-99a2` = `/workspace/b1/tools/g1.sh`: bootstrap LLAMA32_1B (OK 11:37Z), #101 build,match,commit PAIRS=1 at head 8c0bec08 then at base 10996616, rowcmp vs record (program ccc21347, manifest 90f81868, run root 7adcef49).
- `vyv-rf-b1-big` (61mmy8g18xcj0z, cpu3m 64 vCPU / 512 GB, since 11:24Z): head sync running; then bootstrap, laptop key -> prefetch -> key deleted, gate (a) head split 4-way + base replay_partition (same-pod replay wall time).
- #67 (needs >= 180 GB RAM: Match 130 GB, Commit ~190-200 GB) and #70 (2x L40S): no RunPod capacity with CUDA 12.9/13.0 since 11:00Z; laptop retry loop every 60 s until ~12:04Z (/tmp/b1/retry_pods.log).

## Next
- gate (b) jdiff head vs base; #101 compare; gate (a) merged xml vs a23b base; #70 (covers MoE + TP2 rank path; OLMoE) if a 2x L40S appears, #67 PAIRS=1 if a >= 180 GB L40S appears; READY.md.

## Open questions
- GPU capacity: no 2x L40S or >= 180 GB 1x L40S with CUDA >= 12.9 on RunPod since 11:00Z. #70 is OLMoE, so it covers the MoE family and the TP2 rank path together; if it never comes up, the MoE/TP replay evidence is gate (a)'s T1 replay_partition on #67/#68/#73/#74 (CPU, recorded words).
- difftest lives in properties/admission.py (b2v's `properties/`): hunks are the rng call, the evaluate call and import lines.
- difftest lives in properties/admission.py (b2v's `properties/`): will keep hunks to the rng call + evaluate call + import lines.

## Found, not fixed
- replay row evaluators differ from their Definitions on edge words (twins document the Definition's behaviour): TokenSelect_v1 with a NaN logits[0] (Definition -> 0; row kernel -> argmax of the rest); BiasAdd_v1 NaN result word (Definition 0x7FC0; row kernel 0x7FFF); Gemm_v1 / MoeExpertGemm(W)_v1 / padded MoE blocks evaluate lanes with a non-finite operand or accumulator with the vectorised twin instead of declining. Not reachable on finite committed words; kept as is (no per-VU result may move), the batch kernel declines them.
- Not routed through the challenge module (other lanes' files or P10-capped outside scope): engine/rank_worker.py:1220 root seed (b4), check/commit_verdict.py seed recompute (b2v), commit/binding.challenge_identities (c1), correspondence/capture_identities.run default_rng(seed) (module at its P10 cap). relations draw_sample/ensure_adjacent_pair have no caller in the integration.
