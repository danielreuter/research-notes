---
# vllm-rf-f24: identity and integrity (state)

> **Coordinator, 00:32Z: main moved again, to `4bd6c54c` (a23b merged). Rebase onto it when your runs finish.** There's one conflict, in `tests/lint/allowlists/p10_size.json`: take either side, then set each count to what `tests/lint` prints on your pod. See `../vllm-refactor/20260925T0032Z-main-moved-a23b.md`.
>
> **Coordinator, 22:13Z: main moved to `1d9c3198` (a1's lints merged).** When your gate (a) finishes, rebase onto `origin/main` (it's clean with your head) and push with `--force-with-lease`. Run `tests/lint` on your pod, fix the allowlists it prints (your D10 work likely makes P1 `core-patch` / P9 `runtime-patch` entries stale), and record both heads plus the green lint run in READY.md. Steps: `../vllm-refactor/20260924T2213Z-main-moved-rebase.md`.

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D5, D6, D7, D10, D11, D13), §4 (P1, P4, P12); coordinator notes 16:25Z and 16:40Z.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f24`, branch `lane/vllm-rf-f24` from `72884c8a`.
- **Launcher:** `~/.research/bin/research`. ssh wrapper `/tmp/rff24/ssh.sh` (recreate with `research pods ssh 0zb24mk1w6nb4o --print`).
- **Pod:** `vyv-rf-f24-veritor-campaign` = RunPod `0zb24mk1w6nb4o` (cpu3g, 16 vCPU / 64 GB, 80 GB). Trees: `/workspace/base` (72884c8a),
  `/workspace/branch` (base + every file changed on the branch, synced by tar of `git diff --name-only 72884c8a` + untracked). venv `/workspace/venv312`
  (+ pytest-xdist 3.8.0, as lane a1's baseline). GM-01 inputs of row #23: `/workspace/gm23/{build,matchrec}`.
- **Gate (b) baseline:** lane a1's `~/.research/notes/lanes/vllm-rf-a1/baseline.md` (xdist, 54 failed + 11 errors + 297 skipped at 72884c8a, listed).
  Gate (a) baseline there is still pending -> measure base and branch here.

## Done (commits on lane/vllm-rf-f24)
- `c9777273` D5: `research_tools.CLOSURE` + `packages/verity/src/verity/*.py` and `commitments/**`; `research_tools.code_identity(root)`;
  `hot_commit.code_identity` and `tp/commit.tree_of_record` use it. Tests: `tests/harness/test_hot_commit.py`, `tests/harness/test_research_tools.py`,
  `tests/tp/test_commit_tree_of_record.py`.
- `13acf676` D6 + D7: `construction_version` resolves sources against the integration root, raises on a missing one (`root=` for the test);
  `model_pin.dtype` = `engine_dtype(cfg.model_config)` (quantization, else model dtype). Test `tests/harness/test_derive_step_identity.py`.
- `0cdd61e2` D10: `batch_decomp.Ops` passed explicitly (record: `Ops.record()`, fast: `global_match_fast.ops()` with `FastProg` /
  `_ProjectionFast`); `COMPACT_ARGS` global -> `compact=` parameter. No core change. Affected tests passed on the pod (86 s).
- `2a07cd20` D11: `weights_of_record` refuses non-64-hex program digests by name, set equality instead of 16-char prefixes (`check`,
  `stamp_of_record_set`). Scan of every regression record: all program digests are full 64-hex, so no verdict of record moves.
- `76020a66` D13: new `check/replay_codes.py` (why classes, seed forms, legacy decoding). `sampled_replay.population` stamps
  `population.not_evaluable_codes`; `sampled_replay(seed_form=)` -> `sample.seed_form`; `commit_delta` passes the form (minimal hunk in f1/f3's file);
  `commit_verdict` reads codes (decodes the texts only for records without them). `verdict.py`'s three "Match account leg(s) missing" text tests now
  read `executed_prefix_of_record.facts_of_record[rid].account_missing / linked` of the faulted requests (the replay's own why never carries that text).
- All five pushed to `origin/lane/vllm-rf-f24`; tree clean.

## D10 GM-01 evidence (row #23, pod, done 19:54Z)
- ABAB wall / CPU(user+sys): base1 618.8 / 2409.3, branch1 693.5 / 2728.7, base2 664.0 / 2641.6, branch2 692.2 / 2642.8 s. Pair 2: CPU +0.05%,
  wall +4.2%; mean wall +8.0%. Per-phase main-process CPU in pair 2 within +-2.5% (load_fold 1.004, x09 1.025, g3-5 0.986, alternate 0.990).
  Same-code noise: base1 vs base2 load_fold CPU 157.9 vs 185.2 s (host load avg ~200).
- Outputs, both pairs: `global_match_global_program.json` byte-identical; `match_decomp.json` differs in 2 timing fields only; `global_match.json` in
  timings, `impl.source_sha256` (checker code identity) and `x09.pipeline.decomp_out` (the run's own output path) only. Verdicts PASS/PASS.
  Files: pod `/workspace/out/gm/{base1,branch1,base2,branch2}/`, `diff_global_match_2.json`, `diff_match_decomp_2.json`.
- `/workspace/branch` == head source (diff -rq: only sync metadata, macOS `._*` files, gitignored numerics build dir).

## Resume 22:22Z
- The lane agent restarted from an 18:0xZ context; this note is the state of record. Pod at 22:22Z: `a_final` (pid 14128, since 20:50Z)
  and `a_rerun_t0` (pid 19020, since 21:54Z) still running; `after_final` chain waits for `a_final`. Worktree clean at `be366f80`.
- Plan: wait for the gates, fill READY.md; rebase onto `origin/main` (coordinator 22:13Z), lints on the pod, allowlists, push; terminate the pod.
- 22:24Z rebased locally onto `origin/main` `1d9c3198`: clean, head `2dfc3d33` (not pushed yet). Two new lint violations of this branch, fixed in
  the worktree (uncommitted): P9 forbidden-import `research.store` (`research_tools.code_identity` now hashes with hashlib/json) and P11
  class-name `FastProg` (renamed `MemoProg`, code + `tests/check/test_global_match.py`). Pod tree `/workspace/head3` (`research pods sync`,
  ~7 min per sync: the pod has no rsync). Next: lints there, allowlists, commit, D5/D10 tests at the new head, push `--force-with-lease`.
- 22:42Z `a_final` 76/158.
- 22:24Z rebased locally onto `origin/main` `1d9c3198`: clean, head `2dfc3d33` (not pushed yet). Two new lint violations of this branch, fixed in
  the worktree (uncommitted): P9 forbidden-import `research.store` (`research_tools.code_identity` now hashes with hashlib/json) and P11
  class-name `FastProg` (renamed `MemoProg`, code + `tests/check/test_global_match.py`). Pod tree `/workspace/head3` (`research pods sync`,
  ~7 min per sync: the pod has no rsync). Next: lints there, allowlists, commit, D5/D10 tests at the new head, push `--force-with-lease`.
- 22:42Z `a_final` 76/158.
- 22:57Z `a_rerun_t0` exit 0 (22:52Z). Lints at head3 (`/workspace/out/lint/lint1.log`): 12 failed. Stale/moved entries (P1 core-patch x4,
  P1 core-private install->_spec_id_memo and Prog.__init__->Prog._node_functions, P4 verdict-import sampled_replay->replay_codes, P7 environ
  install->ops, P7 commit_verdict broad-except x2, P7 tp/commit cwd, P11 tp/commit M-nnnn, P12 hot_commit/tp/commit root-lists) plus
  NEW ones to fix in code: P9 cycle replay_codes<->sampled_replay (legacy decode's lazy NOT_YET import), P7 seed-default `seed_form`,
  P12 root-list in research_tools.code_identity (owner is harness/source_identity.py), P10 growth in 10 caps (my D10/D11/D13 hunks).
  Plan: NOT_YET -> replay_codes (sampled_replay re-exports); seed_form stamped by commit_delta on `sr["sample"]` (no defaulted param);
  code_identity -> source_identity; verdict.py's account-missing helpers -> commit_verdict (beside _query_population_scope); trims.
  P4 `why.startswith` in replay_codes.not_evaluable_codes = the legacy decode that was commit_verdict._no_evaluator_gaps'
  `k.startswith(_NO_EVALUATOR_PREFIX)` in base (unflagged: variable name) -> allowlist entry, stated in READY.md for the coordinator.

## Resume 23:40Z (after a context reset; this block is current)
- Lint fixes committed locally as `a2e2843e` on the rebased branch (`2dfc3d33` + fixes; not pushed yet). Pod tree `/workspace/head4`
  (head3 + tar of every file changed since 2dfc3d33; md5 of all 1328 files under integrations/vllm + packages/verity == laptop).
  `tests/lint` at head4: 41/41 pass (`/workspace/out/lint/lint3.log`).
- Code moves for the lints: `code_identity` -> `harness/source_identity.py` (P12 owner); `NOT_YET` -> `check/replay_codes.py` (P9);
  `sampled_replay(seed_form=)` dropped, `commit_delta` stamps `sr["sample"]["seed_form"]` (P7); D10's `Ops` -> new
  `check/program_ops.py`, `batch_decomp.record_ops()` (P10, no cycle); verdict's account-missing helpers -> `commit_verdict` (P10);
  D11 `FULL_DIGEST_RE` constant + inline checks (P10); `FastProg` -> `MemoProg` (P11). Allowlists: moved/deleted entries, 8 P10 caps
  lowered, one new P4 `reason-prefix` entry (replay_codes.not_evaluable_codes, the legacy decode) -> say so in READY.md.
- 23:36Z gate (b) at a2e2843e: `b_head4_x12` (`OMP_NUM_THREADS=3 gate_b.sh /workspace/head4 b_head4_x12 -n 12 --dist loadfile`).
- 23:44Z pushed `a2e2843e` (`--force-with-lease` against be366f80). NOT rebasing onto origin/main 58e4c1aa: its 11 commits since
  1d9c3198 touch only backends/ and benchmarks/ (disjoint from this branch), and the coordinator has not said main moved.
- 23:43Z D13 verdict A/B at head4 (`verdict_ab.py` -> `/workspace/out/d13/verdict_head4`): byte-identical to base for all 10 records.
- 23:47Z `a_head4` = gate (a) subset at the FINAL head, keyless (`/workspace/rff24/head4_gate.sh`): T0 minus manifest_digest on every
  row, T1 on #4/#11/#23 (deselect T1-replay_partition-r11), decisions. Supersedes `after_final`/`a_rerun_t1` (killed at 23:45Z; its
  key sweep matched its own pattern text, a false positive; head4_gate.sh's sweep needs a 20+ char secret-shaped value, self-tested).
  Why the subset suffices: the commits after be366f80 reach, among regression checks, only verdict (A/B'd), decomp_hashes
  (program_compare) and replay_partition (sampled_replay); manifest_digest's rebuild (query.cli) imports only batch_decomp.derived_shape.
- 23:56Z `a_head4` DONE: 53 passed, 57 skipped, 81 deselected, exit 0 (546 s). T1 on #4/#11/#23 all skip here (not applicable, or
  match/program.json / descriptor.json.gz not in the fixtures), exactly as at be366f80: the T1 part of the keyless rerun is moot.
- 00:13Z gate (b) at a2e2843e DONE: 55 failed, 11 errors, 296 skipped, 3592 passed, 6 xfailed (3960; 2240 s). jdiff vs a1 head run:
  only `ops/test_row_pod_cancel_forwarding::test_sigint_is_forwarded_the_same_way` failed->passed (also failed at be366f80); 16 new
  pass; 1 replaced. vs be366f80: +41 lint tests pass, same sigint flip. One reworded skip reason (test_ship_roots) is main's e0c7bfe9.
- 00:14:46Z GM-01 #23 at head4 running (`/workspace/out/gm/head4_1`); `a_final` on row #74 (118/~156 at 00:14Z).
- 00:24Z GM-01 at head4 DONE: rc 0, 569.5 s wall / 2186.2 s CPU, 13.34 GiB. Global program byte-identical to base1 and branch2;
  match_decomp 2 timing fields; global_match.json timing + impl.source_sha256 + x09.pipeline.decomp_out. PASS.
- 00:27Z READY.md rewritten for a2e2843e (only `a_final` PENDING); head4 evidence pulled into `evidence/` (gate_a, gate_b, gm/head4_1,
  d13, lint).
- Next: when `a_final` exits (`/workspace/out/gates/a_final.status`): counts + jdiff of skip reasons vs a_head4 into READY.md, copy
  a_final xml/log to evidence, status final, terminate the pod (`research pods terminate vyv-rf-f24-veritor-campaign`).

## Running (pod; scripts `/workspace/rff24/gate_{a,b}.sh` = a1's with logs in `/workspace/out/gates/`)
- origin/main `22741456` changes nothing under integrations/vllm or packages/verity since 72884c8a; `git merge-tree` with HEAD is clean.
- Head `be366f80` (= `76020a66` + the by-name allowlist fix) synced clean to `/workspace/head2` (+ copy `head2-reg`).
- 20:41-20:47Z prefetch (`/workspace/rff24/prefetch.sh`): all 26 fixture artifacts into the pod store, 0 failures; `/root/r2ro.env`
  deleted 20:47:22Z. The keyed T0 run at `76020a66` was killed (`a_head_76020a66_killed.*`).
- 20:50Z gate (a), T0,T1, no key in env or on disk: `nice gate_a.sh /workspace/head2-reg a_final --deselect
  tests/regression/test_regression.py::test_reproduces[T1-replay_partition-r11] --deselect ...[T1-replay_partition-r39]`
  -> `a_final.{log,xml,status}` (the two B=1 replay_partition checks need 120-250 GB each: big pod below).
- 20:51Z gate (b) at `be366f80`: `OMP_NUM_THREADS=3 gate_b.sh /workspace/head2 b_final_x12 -n 12 --dist loadfile`.
- Big pod `vyv-rf-f24-big` (cpu3m x64, 512 GB; 20:49-21:45Z, terminated): its own 3 h key minted 20:55:40Z, fetched #11/#39 +
  top-level, deleted 20:56:53Z. A first start ran two runner instances by accident (both #11 runs passed; logs in its `gates/dup/`,
  not evidence); clean run 21:14:28Z (flock), at be366f80, no key: T1 replay_partition #11 PASS (843 s, peak RSS 67 GB), #39 PASS
  (1364 s, 109 GB). Evidence `evidence/big/`.

## Key left on the main pod (found 21:5xZ)
- `/workspace/r2ro.env` (the early 12 h read-only key, written 17:43Z, before the credential route) was still on the main pod while
  `a_final` ran. Deleted 21:52:03Z. The store reads credentials only from env vars (store.pod.toml `*_env`); no `~/.aws`; the pytest
  process had 0 `AWS_*` vars. A sweep found no other key file (outside the data dirs). Not revocable (`--via local` JWT); expires ~05:43Z.
- Keyless rerun of what ran while it was on disk: `a_rerun_t0` (21:54:17Z, `-k "(T0 and (r4 or r11 or r23)) or (manifest_digest and
  r39)"`, parallel to `a_final`); after `a_final`: `a_rerun_t1` (`-k "T1 and (r4 or r11 or r23)"`, deselect T1-replay_partition-r11).
- READY.md drafted (status draft); fill gate (a) counts when `a_final` and both reruns are done.
- Slip (22:0xZ): one empty `python3 - <<EOF` fallback ran on the laptop while summarising the Build A/B diffs (no input, no repo
  import); switched to jq. Laptop rule: no python, ever.

## D13 verdict A/B (main pod, 21:50Z; `evidence/d13/`)
- `verdict.from_record(row).dumps()` (the T0 verdict check's reconstruction; it calls the D13-changed `_replay_seed_of_record`,
  `_complete_replay_population_gap`, `_partial_replay_named_gap`) over the 10 regression records with a Commit verdict: base == head
  byte for byte, 0 errors. `commit_summary` only lifts the recorded `commit/verdict.json`, so this A/B is the direct evidence.
- GPU pod `vyv-rf-f24-gpu` (RTX 4090) ran the Build A/B 21:03-21:47Z and is terminated. Evidence: `evidence/build_ab/`.

## Build A/B (RTX 4090, one venv: vllm 0.28.1rc1.dev472+gd9105ea80, torch 2.13.0+cu129, triton 3.7.1 = the records' versions)
- `rebuild_ab.sh`: `rebuild_digest_gate` from the recorded result.json of rows #73 (Qwen3-4B BF16: step, request_LP10_T8) and #74
  (Qwen3-4B-FP8: step, request_LP73_T1), base tree then head tree; `tree_diff.py` base vs head.
- Base == head: program_digest and correspondence_digest of all 4 wrappers; `descriptor.json.gz`, `instances.json.gz`,
  `derive-report.json` byte-identical. Differ: `construction_version` (+ `artifact.identity`, its hash), `model_pin.dtype` on #74 only
  (bfloat16 -> fp8), inputs trace (tree path; base opens the 14 sources at nonexistent `packages/verity/src/verity/verity_vllm/...`;
  vLLM's first-run model-info cache fell on base), timings.
- Both trees rebuild program digests different from the records' (records built pre-relayout, 25 binding rules; base has 27): pre-existing.

## Gate (b) at `be366f80` (`b_final_x12`): 56 F / 11 E / 296 s / 3550 p / 6 xf (3919) vs a1 base 54 / 11 / 297 / 3536 / 6 (3904)
- Outcome changes: the gc-freeze pair passed -> failed (on this pod base == head: both fail alone and after test_execution_label, at
  both trees); weakref skip -> pass. +16 new tests pass; `test_code_identity_hashes_code_not_tests_or_caches` replaced in D5. No new
  skip reason. vs a1's head run: no outcome change.

## Gate (b) at `76020a66` (`b_head_x12`, 58 F / 11 E) vs a1's head run
- 2 new failures, both the by-name ratchet (`test_no_by_name_rules`: the moved population-gap rule, the retired CODE_SKIP_SUFFIX entry);
  fixed in `be366f80`, 3/3 pass. The gc-freeze pair fails in a1's head run as well; one allocator-dependent weakref test passed there and
  skipped here (a1's documented noise).

## D6 / D7 evidence (pod, 20:10Z; local copies `/tmp/rff24/evidence/{d6,d7}`)
- A B0 Build cannot run on this CPU pod at base or head: vLLM's CUDA wheel makes no DeviceConfig without a GPU
  (`create_engine_config` -> "Device string must not be empty"; `/workspace/out/b0/base/build.log`). So the evidence is direct:
- D6 (`/workspace/rff24/cv_evidence.py`): base `construction_version(VLLM_BINDING_RULES)` hashes 14/14 sources as missing
  (sources_sha256 4a9cdf5b..., a constant of the file names); head hashes 14/14 by content, 0 missing (b941f904...). All 180 recorded Builds
  in the regression records carry ad140226... with 14/14 missing (pre-relayout names `verity_capture/experimental/cb_a/...`).
- D7 (`/workspace/rff24/fp8_dtype.py`, each recorded Build's own target + pin, `EngineArgs.create_model_config()`): 9 BF16 rows
  engine_dtype "bfloat16" == recorded; the FP8 row (Qwen3-4B-Instruct-2507-FP8) "fp8" (quantization fp8, model dtype bf16) vs recorded "bfloat16".
- Consumers: `construction_version` -> `ArtifactIdentity.identity` (echoed into summaries only; `check_reuse(..., construction_version_now)`
  has test callers only); `construction_manifest.json` readers use `structural_inputs` / `sampling` only; `model_pin.dtype` is read by no one
  (`rebuild_digest_gate` passes model / revision / max_model_len / tp / target). No digest, root or verdict moves.

## Next
1. Gate (a) `a_final` (main pod) to finish; then READY.md (drafted) with its counts; terminate the main pod.

## Open questions
- none

## Found, not fixed
- `commit_verdict.py:569` / `verdict.py:_replay_of` pick a `components.sampled_replay` by the substring "sampled-exact-replay" in its method label
  (a label, not a message; left as is).
