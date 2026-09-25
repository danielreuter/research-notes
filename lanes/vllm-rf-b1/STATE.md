---
id: vllm-rf-b1/state
lane: vllm-rf-b1
kind: state
updated: 2026-09-25T10:50Z
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
- 7cde62a5 difftest `evaluate_spec` = core `verity.evaluation.evaluate` (drops the hand-built one-call Program and the observe.fold `_replayer` import). Unverified on pod yet for unregistered `DT.spec(...)`.

## Plan
1. done (derived_rows move).
2. done (a6613e94).
3. twins -> core kernels (kernel "twin"); core `self_check` replaces twins.self_check/check_instances/gate_words and the Twin protocol. Test: every registered (kernel, Definition) pair self-checks.
4. `check/replay/challenge.py`: today's seed forms (root, challenge, prover) + generator constructors; RNG_OWNERS; drivers (replay tiers, stoch_recompute, compiled_kernel_check, vu_query, difftest) use it. No seed derivation changes.
5. Split sampled_replay.py into sample / open / evaluate / compare / c2 driver / linkage; delete it; repoint importers (import lines only in other lanes' files).
6. Pods: gate (b) head vs base, gate (a) T0+T1 on cpu3m 512 GB, GPU #101, #67 PAIRS=1, #70 if rank path changes.

## Running
- pod `vyv-rf-b1-cpu` (RunPod cei1t48zvrcnzu, cpu3g 32 vCPU / 128 GB cgroup, $1.28/h, created 08:47Z). Trees: /workspace/base (10996616), /workspace/head (a6ba1e5b). Logs /workspace/b1/logs.
  - base gate (b) done 10:18Z: 52 failed, 3645 passed, 287 skipped, 6 xfailed, 11 errors (base-xdist.xml).
  - head gate (b) at a6ba1e5b (intermediate), `-n 12 --dist loadfile`, started 10:24Z (head-a6ba-xdist).

## Next
- read head-a6ba-xdist vs base; ship 7cde62a5 to /workspace/head; touched tests; final head gate (b); gate (a) on a cpu3m 512 GB pod; GPU rows.

## Open questions
- difftest lives in properties/admission.py (b2v's `properties/`): will keep hunks to the rng call + evaluate call + import lines.

## Found, not fixed
- replay row evaluators differ from their Definitions on edge words (twins document the Definition's behaviour): TokenSelect_v1 with a NaN logits[0] (Definition -> 0; row kernel -> argmax of the rest); BiasAdd_v1 NaN result word (Definition 0x7FC0; row kernel 0x7FFF); Gemm_v1 / MoeExpertGemm(W)_v1 / padded MoE blocks evaluate lanes with a non-finite operand or accumulator with the vectorised twin instead of declining. Not reachable on finite committed words; kept as is (no per-VU result may move), the batch kernel declines them.
- Not routed through the challenge module (other lanes' files or P10-capped outside scope): engine/rank_worker.py:1220 root seed (b4), check/commit_verdict.py seed recompute (b2v), commit/binding.challenge_identities (c1), correspondence/capture_identities.run default_rng(seed) (module at its P10 cap). relations draw_sample/ensure_adjacent_pair have no caller in the integration.
