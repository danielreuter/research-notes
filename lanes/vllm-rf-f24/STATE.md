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

## Running
- pod: GM-01 row #23 ABAB (`/workspace/out/gm/{base1,branch1,base2,branch2}`, log `abab.log`). The serial base gate (b) was killed so it would not
  perturb the timing.
- Pair 1: base1 618.8 s, branch1 693.5 s (+12%); outputs identical except timings and `impl.source_sha256`; every phase +11..15% including phases
  D10 does not touch (G1, G7, attribution) -> host load avg ~200 (shared host); pair 2 decides.

## Next
1. D10: pair 2 of GM-01; if branch still > +10%, profile (py-spy) the phases that moved.
2. Gate (b) on the branch (a1's xdist command); gate (a) base + branch (mint read-only credential, a1's `baseline-gate_a.sh`).
3. D6/D7 before/after evidence of the Build stamp (B0 build base vs branch: `/tmp/rff24/b0_build.sh`, `/tmp/rff24/tree_diff.py` on the pod).
4. READY.md; terminate pod.

## Open questions
- none

## Found, not fixed
- `commit_verdict.py:569` / `verdict.py:_replay_of` pick a `components.sampled_replay` by the substring "sampled-exact-replay" in its method label
  (a label, not a message; left as is).
