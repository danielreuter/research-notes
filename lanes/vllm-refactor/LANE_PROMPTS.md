---
id: vllm-refactor/lane-prompts
lane: vllm-refactor
kind: reference
created: 2026-09-24T19:20Z
---
# vllm-refactor lanes: the launch prompts, verbatim

These are the exact prompts the six Phase 0/1 lanes were launched with, at 17:27-17:43Z, as generalPurpose subagents with model inherit. To relaunch a lane, put the restart preamble in front of its prompt.

**Restart preamble:**

~~~text
RESTART: the previous agent for this lane stopped mid-task. Before doing anything else: read
~/.research/notes/lanes/vllm-rf-<lane>/STATE.md, run `git status` and `git log --oneline -5` in your worktree, and check
whether any pod or command you started is still running. Then continue from where you left off. Keep following
LANE_BRIEF.md, and update STATE.md at least every 20 minutes. The test baseline is in
~/.research/notes/lanes/vllm-rf-a1/baseline.md: gate (b) is not green at the base (65 failures and errors, listed by
cause there), so judge your gate (b) as no failure, error or skip reason outside that list.
~~~

If the old agent might still be alive but stuck, relaunch on a new branch so the two can't collide. For example, lane a23b branches from `origin/lane/vllm-rf-a23` into worktree `rf-a23b` and notes dir `vllm-rf-a23b`. Say so in the prompt.

## a1: baseline and guardrail lints
~~~text
You are lane a1 of the vLLM integration refactor. First read /Users/danielreuter/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md completely and follow it (worktree, pods, gates, state notes, finish). Then read SYNTHESIS.md sections 4, 5 and 6 in the same directory.

Scope:
1. Baseline first, because the other lanes compare against it. Provision vyv-rf-a1 (the cheapest pod that can run the integration's CPU test suite with the pinned environment; a small GPU pod is fine if CPU pods are unavailable). Put main at 72884c8a on it, run gate (a) and (b) from the brief, and write ~/.research/notes/lanes/vllm-rf-a1/baseline.md with: the commit; an environment recipe (exact commands that reproduce the environment on a fresh pod, since the other lanes will copy it); pass/skip/fail/xfail/error counts overall and per test file; any failing tests with a one-line cause; and skip reasons grouped. Aim to have it written within about 60 minutes of starting, and update your STATE.md when it is.
2. Guardrails (SYNTHESIS section 6, lane A1; rules in section 4). Add integrations/vllm/tests/lint/ ratchet tests for P1, P3, P4, P6, P7, P8, P10, P11 and P12, plus layering checks for P2, P5 and P9, in the style of tests/check/test_quarantine_lint.py. Prefer small AST-based tests with no new dependencies over adding import-linter. Each rule has a committed allowlist of today's violations. A new violation fails, and an allowlist entry that no longer matches also fails, with a message telling the author to delete it. For P9, use an interim layer order for today's packages that is consistent with the target order (section 4 P9 and the mapping in 5.2), and put today's wrong-direction edges and import cycles in the allowlist. Where a rule refers to packages that don't exist yet (pipeline/, properties/, collectives/, engine/), encode only what is checkable today and say in the test docstring which part applies once the package exists. Skip the [project.scripts] entry; the CLI lane adds it. The lints must run in seconds on CPU and must not import torch or vllm.

Acceptance: lints green at your head; each rule's allowlist size listed in READY.md (the ratchet's starting point); gates (a) and (b) green.
~~~

## a23: dead code, data and paths
~~~text
You are lane a23 of the vLLM integration refactor. First read /Users/danielreuter/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md completely and follow it (worktree, pods, gates, state notes, finish). Then read SYNTHESIS.md sections 2, 5 and 6 in the same directory, and the DEAD and Map 3/Map 4 sections of survey-harness-ops-tests-data.md.

Scope (SYNTHESIS section 6, lanes A2 and A3):
1. Dead code out. Delete the section 5.4 'Dead now' list and move the 'Moved to tests' list into integrations/vllm/tests/ next to the tests that use them. By owner decision, also delete the CMT-1 committer (commit/reference_engine/, commit/reference_engine_adapter.py and the cmt_ref_* paths in harness/commit_delta.py) and commit/engine_rs/. Before deleting anything, re-verify at 72884c8a that it has no importer or caller: absolute and relative imports, importlib or string module paths, python -m in ops/*.sh and tests, and the research tool declarations in harness/research_tools.py. Skip and note anything that turns out to be live. Tests that only test deleted code go with it; tests of code or files that no longer exist are deleted or fixed. tools/ (the finished relayout tooling) and the test that enforces it are deleted.
2. Data and paths. Library-read data becomes package data loaded with importlib.resources (section 5.2, 'data directories' row: data/hf_configs, docs/data/ref-prims, fixtures/W11* and anything else the library reads). manifests/ and workloads/ stay where they are as run definitions, but are located through one helper instead of Path(__file__).parents[N]. Remove the 8 sys.path.insert calls, the 16 parents[N] uses, machine paths as library defaults (/workspace, /vault, laptop paths), and the library read of tests/ (harness/commit_delta.py:1793). pyproject.toml ships the package data. Data nothing reads is listed in READY.md, not moved or deleted.

Acceptance: gates (a) and (b) green with no new skips; counts of library lines deleted and moved to tests; a grep showing no sys.path.insert, parents[N] or machine-path defaults left in verity_vllm/ (or each remaining one justified in READY.md); and, if a changed path is only exercised by GPU stages, one small Build on the cheapest GPU pod showing it resolves.
~~~

## f1: opened-value replay (D1)
~~~text
You are lane f1 of the vLLM integration refactor (defect D1, opened-value replay). First read /Users/danielreuter/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md completely and follow it (worktree, pods, gates, state notes, finish). Then read, in the same directory: SYNTHESIS.md section 2 (D1) and section 4 (P2); 20260924T1625Z-coordinator-checks-on-check-commit-survey.md; and the evaluation and replay map in survey-check-commit.md.

Problem: the Commit value check, `OC.oracle_compare(..., OC.committed_reader(com), ...)` at harness/commit_delta.py:2339 (per rank at tp/worker.py:1192 and tp/partial_source.py:59-65), compares the oracle's recomputation with the collector's in-process retained buffers (check/oracle_compare.py:914-953), not with opened values. Openings are verified against the run root in a separate step (harness/commit_delta.py:2022-2033 and 734-742), but nothing ties the two together: the compared bytes are never shown to be the committed ones.

Fix (owner decision: inside the Commit process for now): the verdict-bearing value check consumes opened, verified values only. Work out which positions the oracle compare reads and which positions are opened. Then either open and verify every position the compare reads, or restrict the verdict-bearing compare to opened positions and keep any wider in-memory compare only as a labelled diagnostic that can never make the verdict PASS. Choose based on cost (measure opening cost on a real row) and give the reasoning in READY.md. Values opened by replay after release (openings_after_release) count as opened only if verified against the root. Do the same for the per-rank TP path.

Negative test: mutate the retained buffer after the commit (before openings and compare) and show the value check FAILs. Add it as a test wherever the existing Commit tests run (on CPU if a CPU double exists, otherwise as a pod-marked test), plus one real pod run.

Acceptance: gates (a) and (b). On GPU pods, re-run one dense, one MoE and one TP2 regression Commit row (the cheapest rows in tests/regression/fixtures.toml that exercise each) through the research Tools, with verdicts unchanged and the opened-value compare in the record. The negative test FAILs as intended. Report commit time before and after.
~~~

## f24: identity stamps and verdict integrity (D5, D6, D7, D10, D11, D13)
~~~text
You are lane f24 of the vLLM integration refactor (defects D5, D6, D7, D10, D11 and D13). First read /Users/danielreuter/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md completely and follow it (worktree, pods, gates, state notes, finish). Then read, in the same directory: SYNTHESIS.md section 2 for those defects and section 4 (P1, P4, P12), and the coordinator notes 20260924T1640Z-coordinator-checks-on-harness-survey.md and 20260924T1625Z-coordinator-checks-on-check-commit-survey.md.

Scope:
- D5: one code identity over the import closure (the integration plus Verity core), used by the hot worker (harness/hot_commit.py:51-52 CODE_ROOTS: 4 of its 6 roots don't exist and core is not hashed) and by the TP commit's key (tp/commit.py). Reuse the closure definition harness/research_tools.py:44-49 already has instead of inventing another. Test: editing a core file in a temp tree changes the key.
- D6: construction_version (harness/derive_step.py:52-80) resolves its 13 sources against packages/verity/src, so every file hashes as missing. Resolve them against the integration package, fail loudly on a missing file, and test that editing a listed file changes the value.
- D7: derive_step.py:371 records model_pin.dtype from vm.PIN (bf16) even for FP8 rows. Record the dtype the engine actually ran with.
- D10: check/global_match_fast.py:482-520 rebinds verity.ir.codec._spec_id, verity.ir.refs.runs and several Prog, compare and dag functions at runtime, and it is the default path. Remove the monkeypatching: either pass the memoised functions explicitly inside the integration, or, if memoisation belongs in core, make a small behavior-preserving change in packages/verity (no API change, no digest change) and say so in READY.md. GM-01 results must be byte-identical and runtime within about 10% (the fresh #23 GM-01 took 452 s).
- D11: input_provenance/weights_of_record.py:676-677 `_eq` accepts a 16-character prefix as equal for program digests. Require full digests. If records of record carry truncated digests, find out and report before changing behavior.
- D13: check/commit_verdict.py (for example :107, :152 and :353-354) decides by matching message text from other modules. Replace this with structured reason codes carried by the producing checks. The verdict JSON of regression rows must be unchanged.

Acceptance: gates (a) and (b). Build T0 rows unchanged except the construction_version stamp (expected to change) and the dtype field on FP8 rows. Match and verdict outputs of regression rows unchanged. The new identity tests pass. Use CPU pods only, unless a check needs a GPU.
~~~

## f3: undeclared inputs (D3, D4, D14, D15)
~~~text
You are lane f3 of the vLLM integration refactor (defects D3, D4, D14 and D15: results that depend on undeclared inputs). First read /Users/danielreuter/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md completely and follow it (worktree, pods, gates, state notes, finish). Then read, in the same directory: SYNTHESIS.md section 2 for those defects and section 4 (P7), and 20260924T1645Z-coordinator-checks-on-observe-survey.md.

Scope:
- D3: the committed leaf layout is chosen by VERITY_LAYOUT (acquire/native_collect.py:721) for executed leaves and by VERITY_LEAF_LAYOUT (commit/padding_steps.py:405) for padding leaves. Make the layout one declared parameter, threaded from the Commit's configuration (a CLI flag or config field recorded in the artifact), read once where the process starts, with inconsistent values refused. The environment variable may remain as the CLI's source for now, read in exactly one place. Roots must be unchanged for runs where the two variables agreed.
- D4: acquire/plan.py:371-377 swallows the ImportError from native_collect (which imports torch at module level) and uses empty GATHER_FLUSH_LEAVES and PRE_FLUSH_LEAVES, so a torch-less CPU gate and the GPU stage evaluate different tables. Move those tables into a torch-free module that both import, delete the fallback, and add a test that the plan and its digest are identical with torch importable and with torch stubbed out.
- D14: challenge seeds that default to 0 (check/compiled_kernel_check.py:206, check/relations.py:1143, and any others you find) become required arguments or are derived from the commitment. List every challenge derivation you touched.
- D15: environment variables change what a Definition computes. For example, MufuTanh_v1's table can come from an environment variable with no hash check (program/registry/prims.py:630-653). Load such tables from package data with a pinned digest and refuse a mismatch. List every Definition whose semantics can depend on the environment, and fix each.

Acceptance: gates (a) and (b); the torch-stub plan test; for D3, one GPU Commit row re-run with roots equal to its regression record; no Program or manifest digest changes. If a D15 fix would change a digest because the old environment path was actually in use, stop and report instead.
~~~

## f56: collectives guard and FA-tap exactness (D16, D17)
~~~text
You are lane f56 of the vLLM integration refactor (defects D16 and D17: collectives guard and FlashAttention-tap exactness). First read /Users/danielreuter/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md completely and follow it (worktree, pods, gates, state notes, finish). Then read, in the same directory: SYNTHESIS.md section 2 for D16 and D17 and section 4 (P5, P8), and the collectives and TP maps in survey-observe-acquire-tp.md and survey-program-query-corr.md.

Scope:
- D16a: the two collective patches disagree on MoE coverage (tp/partial_source.py:23-31 vs tp/worker.py:546-560; SharedFusedMoE). Make one class list that both use, living in the quarantine or a profile (P8), and check which list the regression TP rows actually exercised.
- D16b: the quarantine AllReduce reduction order (program/registry/quarantine/collective/allreduce.py:66-70) contradicts b1_tp2.py:128-134 and is wrong for world >= 3. Fix it to match NCCL's actual order as recorded in the repo's evidence, or, if no evidence exists for world >= 3, make it refuse world >= 3.
- D16c: owner decision: refuse world > 2 with a clear error until collectives land. correspondence/emit.py (:30, :318-325) records collective: null for world > 2. Make it, and any other silent world-2 assumption you find on the Build or Commit path, raise instead. Check what TP4 work exists (for example commit 40f40a21 and the tp-n lane) and list in READY.md what the refusal disables.
- D17: acquire/hidden_source.py:234 and :387 cite evidence that the patched FlashAttention kernels are bit-identical to vLLM's, but the cited files aren't in the repo. Implement FA-tap exactness as a property check with a record: on a seeded workload, the tapped FA2 kernel (on L40S) and FA3 kernel (on H100) produce outputs bit-identical to vLLM's stock kernels. Put it next to where property checks live today (beside check/noninterference.py) and make the record's digest citable. Don't build the future properties/ package.

Acceptance: gates (a) and (b); on a 2-GPU pod, one TP2 regression row (a shared-expert MoE row if one exists) with its verdict unchanged; the world > 2 refusal tested; FA-tap exactness records produced on L40S and H100 and preserved through research; any existing evidence the fixes contradict listed in READY.md.
~~~
