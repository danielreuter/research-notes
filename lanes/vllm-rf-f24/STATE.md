---
# vllm-rf-f24: identity and integrity (state)

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

## Running (pod; scripts `/workspace/rff24/gate_{a,b}.sh` = a1's with logs in `/workspace/out/gates/`)
- origin/main `22741456` changes nothing under integrations/vllm or packages/verity since 72884c8a; `git merge-tree` with HEAD is clean.
- Head `76020a66` synced clean to `/workspace/head` (+ copies `head-reg`, `head-b0`). Read-only R2 credential `/root/r2ro.env`, minted 19:56Z, 5 h.
- 19:57Z gate (a): `nice gate_a.sh /workspace/head-reg a_head` -> `a_head.{log,xml,status}` (~3-4 h expected).
- 19:58Z gate (b): `OMP_NUM_THREADS=3 gate_b.sh /workspace/head b_head_x12 -n 12 --dist loadfile` -> `b_head_x12.{log,xml,status}`.
- 20:00Z B0 Builds base then head: `/workspace/b0_build.sh` -> `/workspace/out/b0/{base,head}/`, `DONE` when both finish; compare with
  `/workspace/tree_diff.py`.

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
1. Gate (b) vs a1's baseline (no new F/E, no new skip reason); gate (a) green.
2. READY.md; terminate pod.

## Open questions
- none

## Found, not fixed
- `commit_verdict.py:569` / `verdict.py:_replay_of` pick a `components.sampled_replay` by the substring "sampled-exact-replay" in its method label
  (a label, not a message; left as is).
