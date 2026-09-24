---
id: vllm-rf-f56/state
lane: vllm-rf-f56
kind: state
status: active
created: 2026-09-24T17:40Z
---
# vllm-rf-f56: collectives guard and FA-tap exactness (D16, D17) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D16, D17), §4 (P5, P8); survey maps `survey-observe-acquire-tp.md` §5.2, `survey-program-query-corr.md` Map 4.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f56`, branch `lane/vllm-rf-f56` from `72884c8a`.
- **Laptop helpers:** `/tmp/rff56/research.sh` (research launcher wrapper); recovered deleted xcheck sources `/tmp/rff56/fa{2,3}_tap_xcheck.py` (from `ca5d65e8^`).
- **Scope:**
  - D16a: one MoE collective class list used by `tp/partial_source.py` and `tp/worker.py`, living in quarantine or a profile; check which list the TP regression rows exercised.
  - D16b: quarantine `AllReduceSumBf16` order vs `b1_tp2.allreduce_order`; fix to NCCL's recorded order or refuse world >= 3.
  - D16c: refuse world > 2 on Build/Commit (emit `collective: null` etc.); list what the refusal disables (TP4 work, commit 40f40a21, tp-n lane).
  - D17: FA-tap exactness property check with a record (FA2 on L40S, FA3 on H100), beside `check/noninterference.py`, digest citable.
- **Acceptance:** gates (a), (b); 2-GPU pod TP2 regression row (shared-expert MoE if one exists) verdict unchanged; world > 2 refusal tested; FA-tap records on L40S + H100 preserved via research; contradicted evidence listed in READY.md.

## Findings so far
- D16b evidence for world 4 EXISTS: research artifact `art:53e58b1ce31bd9365f808dfde9746d9cec75df22cb74e7b1218b510d333aa599` (TP4 llama32-1b B8 match record, `match/tp2_match.json`): provenance pass, 1056/1056 all-reduces equal the descending chain order [3,2,1,0]; `alt_ascending_equal` 32 (embedding all-reduces only). Commit `b33386e0` moved b1_tp2 AllReduce v1 -> v2 for the same reason (precedent: body meaning changed -> identity bump).
- Quarantine family `AllReduceSumBf16` is used only by `tp/collective_link.py` (research tool, no Build/Commit caller) + tests; `registry_version()` hashes only `registry.prims`/`registry.b1` sources, so editing the quarantine changes no Program/derive digest.
- D17: cited `fa2_tap_xcheck.py` / `fa3_tap_xcheck.py` existed at `integrations/vllm/verity_capture/sweep/` and were deleted in `ca5d65e8` (cleanup 3/3). Hidden-source `evidence` strings go only into the free-text coverage declaration (no digest).
- D16a: no regression fixture row is shared-expert MoE (OLMoE #70, Qwen3-30B-A3B #75 are the TP2 rows; neither has shared experts).
- by-name lint (`tests/test_no_by_name_rules.py` + `tests/by_name_allowlist.json`) pins `MOE_SITE_CLASSES` / `MOE_COLLECTIVE_CLASSES` tables and their predicates: moving the list needs allowlist entry updates.

## Done
- 17:40Z worktree created.
- 18:47Z resumed after the 18:02Z Cursor restart: worktree clean at `72884c8a` (no commits yet), no `vyv-rf-f56` pod exists, nothing of this lane running. Gate (b) baseline now in `vllm-rf-a1/baseline.md` (65 failures+errors listed by cause; judge gate (b) as nothing outside that list).
- Laptop scratch from before the restart: `/tmp/rff56/{r70,r75,tp4match}` (match/commit records of rows #70, #75 and the TP4 match artifact).
- 19:06Z (uncommitted, worktree) D16b written. DECISION CHANGED from "quarantine v2": the quarantine family now refuses R > 2 (`_two_ranks`), its R = 2 body/ids unchanged; the linkage tool's only R > 2 use routes to `b1_tp2.all_reduce(R, N)` (= `AllReduce_v2`, body reads `allreduce_order`). Why: routing in place needs a v1->v2 bump (identity rule) = retiring `AllReduceSumBf16_v1` (owner: not decided) and duplicating `AllReduce_v2`; a naive route also reorders R = 2 gate operands. Tests: `tests/tp/test_tp_collective.py` (R=2 params, refusal test, R=3 test rewritten), `tests/tp/test_tp_world_n.py` (world-3 link id).
- 19:06Z (uncommitted) D16a written: `MOE_COLLECTIVE_CLASSES` / `MOE_COLLECTIVE_MODULES` live in `tp/collective_sites.py` (already the one module both observers share); `worker.py` imports them, `partial_source.py` imports them (`MOE_SITE_CLASSES` alias; `SITES` MoE rows from the module list, adds `shared_fused_moe`). By-name allowlist: 2 worker table entries moved to collective_sites.py (with decision), stale partial_source table entry deleted. No shared-expert MoE model builds (`observe/profiles/generic.py` `_UNMODELLED_MOE`), so the TP2 regression rows (#70 OLMoE, #75 Qwen3-30B-A3B: `mlp.experts` is MoERunner, no nesting) see no site change.

- 19:17Z (uncommitted) D16c written. Build: `correspondence/emit.py` `emit_correspondence` raises `NotImplementedError` for `rank[0] > 2` (test `tests/correspondence/test_runtime_correspondence.py::test_world_above_two_is_refused`). Commit: `tp/commit.py` `main` exits (`SystemExit "--tp N refused..."`) right after `--world` folds into `--tp`, before any engine/import work (test `tests/tp/test_tp_world_n.py::test_rank_commit_refuses_world_above_two_before_building_an_engine`, `apply_env` patched: `tp/capture.py` runs it at import and no other test imports tp.capture). Match at world > 2 (`tp/match.py`) deliberately NOT refused (research instrument, no Build/Commit artifact; b33386e0's evidence came from it).
  - What the refusal disables (for READY): `tp_stage.sh` / `run_row_v2.sh` rows with WORLD > 2 (the TP4 workload `1601bdd2` llama32-1b l40s tp4 b8 i256 o32 can no longer Build or Commit); `derive_step --tp N>2`; `tp.commit --tp/--world N>2`. `40f40a21` (TPPartialSource occurrence reset) is world-independent (also fixed frozen TP2 #70): only its TP4 re-measurement is lost. Offline world-N machinery stays tested (CollectiveBus world N, AllReduce_v2, cross_rank_check world 3, tp_links v2).
- 19:17Z D17 design (writing): `check/fa_tap_exactness.py` = the GPU half of the deleted xchecks (per case: tapped out/lse == installed kernel == same .so untapped; skipped 0; stream closed (no spill, nothing unwritten); fail-closed negatives). Launch args recorded at the op from vLLM's own `flash_attn_varlen_func` (robust to the FA3 37-arg drift); geometry from `hidden_source` (`fa2_swapped`, `fa2_kblock_n`, `fa3_tile`); record `fa_tap_exactness.json` with `digest` = sha256(canonical_json(record minus digest)) (`correspondence.runtime.canonical_json`, no new canonicalisation); `verify_record` torch-free. The CPU oracle half (tapped words == AttentionHead_v3 / FA3 oracle) is NOT restored: a23 `c1cf11ef` moves `check/fa2_attn_oracle.py` to `tests/acquire/`, so the package cannot import it -> Found, not fixed.

- 19:33Z COMMITTED + PUSHED `lane/vllm-rf-f56`: `dfd21f73` D16 (a, b, c), `9b07c19f` D17 (`check/fa_tap_exactness.py`, `tests/check/test_fa_tap_exactness.py`, census root `verity_vllm.check.fa_tap_exactness` in `tests/census_roots.txt` (else test_no_dead_modules fails), evidence text in `acquire/hidden_source.py`, comments in `ops/pod_fa{2,3}_tap.sh`). Deliberately NOT edited: `acquire/fa3_tap_src/build_fa3_ext.py:11` (every fa3_tap_src file is in the tap's source-set hash: an edit forces an FA3 rebuild on every pod) and `tests/acquire/test_fa2_tap_geometry.py:7` (cites the oracle half, not restored). Nothing run yet (laptop: py_compile only).

- 19:50Z #70 at the base (integrator note `20260924T0240Z-from-vllm-tp-v2-ready-4f3a1e7.md` + `vllm-tp-v2/20260924T1810Z-70-commit-fail-diagnosis.md`): Build PASS (manifest `ede1ad81`, 357,796), Match PASS collective-level (oracle 14,592/14,592 per rank), Commit `r20260924-021402-69d8` FAIL rc 12 with legs query_population False (25,408 per rank, build_global keeps one request's op_path_aliases), cross_rank_collectives False (AllGather2 161 sites / 1 covered), sampled_replay partial, fold_match_binding None; every compared value equal (replay 9,656/9,665 0 mismatches, weight pins 212/212, TP-12 154/154, linkage 434/434). Build `art:962a12b3…`, Match `art:7ecab74a…` preserved. Regression expected files: #70 and #75 class FAIL, only `program_digest` applies (gate (a) covers it). "Verdict unchanged" for #70 = the same FAIL legs and numbers.

## Running (pods created 19:45-19:48Z)
- CPU `vyv-rf-f56` = RunPod `3rl2gsbclq3nhs` (cpu3g x16, 80 GB): `research pods sync` of `9b07c19f` to `/workspace/base` in flight (laptop background shell).
- 2x L40S `vyv-rf-f56-l40s` = `lhe6h1dv0bw43c` (300 GB disk): not bootstrapped yet.
- 1x H100 SXM `vyv-rf-f56-h100` = `1ja36qvgnyy0g3` (150 GB disk): not bootstrapped yet.

## Next
1. CPU: a1 recipe venv, gates (a)/(b) at `9b07c19f`; check vLLM `flash_attn_varlen_func` keyword names + which models build `SharedFusedMoE` (site-packages source).
2. GPU pods: sync tree, `verity_vllm/ops/pod_bootstrap.sh` (builds FA2 tap; FA3 on the H100). Then `python -m verity_vllm.check.fa_tap_exactness --so <tap .so> --out DIR` on each (L40S FA2, H100 FA3) under `research run` so the record is preserved.
3. L40S: TP2 #70 at head (reuse Build/Match artifacts or rerun), compare to the base Commit legs above.

## Open questions
- none yet

## Found, not fixed
- SYNTHESIS D17's "require its record for FA-tap rows": wiring a record requirement into the verdict would change FA-tap regression verdicts (brief: not decided). Not done; the record is produced and citable only.
- The tapped-words-vs-oracle cross-check (the deleted xchecks' CPU half) has no in-package home once `fa2_attn_oracle` moves to tests (a23 `c1cf11ef`); `check/commit_verdict.py:330,441` still names "a bit-exact plane xcheck on record" that nothing produces.
