---
lane: vllm-57-fix
repo: verity (~/projects/verity), worktree ~/projects/verity-wt/57-fix
branch: lane/vllm-57-fix (off origin/lane/vllm-cleanup-2 = 38122d1f), pushed to origin + pod remote sw57
pod: vyv-sw-57 (ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 12152 root@202.181.159.235), checkout /workspace/verity
---
# vllm-57-fix: running state

**07:58Z successor took over (predecessor died 06:51Z with Cursor).** (RESOLVED ~08:50Z, free disk 6.2 GB) BLOCKER (laptop-wide, handed to coordinator
`lanes/coordinator/20260924T0758Z-handoff-from-vllm-57-fix.md`): laptop free disk is at the guardian's 3.5 GB floor
(cursor_db 69.8 GB and growing). The guardian SIGKILLed my laptop `research run` launchers 3x (07:52Z, 07:57Z). Freed: data evict
0.23 GB, ~/Library/Caches/com.apple.python 0.16 GB, uv cache 0.40 GB; each launch then squeaked through. Every further
laptop launch (#67 Commit, preserve) needs >=3.5 GB free.

## Now (07:58Z)
- #57 Commit-only rerun at the tip 2c5e038b: run r20260924-075409-3621 on vyv-sw-57 (GPU 0), same inputs as 061950-2148
  (build art:f1baace0, match art:a225cf5f), source tree /workspace/research/src/2c5e038b… built on the pod by git archive. ETA ~09:00Z.
- #67 Build r20260924-063717-5860 PASS 07:42Z (build_wall 2012 s; manifest 406,432 identities, digest 4799063127e655ff); published
  from the pod: build art:5b7e5bcf7655c313dc4ca28a4891ffcdbfabaa3fb1fc41810795c5519ac052e0 (+evidence art:cb051bae, logs art:e76c34f2).
- #67 Match: run r20260924-075730-80bd on vyv-sw-67b (GPU 0), source 2c5e038b (shipped as a gzip'd git archive, 57 s),
  --input build=art:5b7e5bcf…, no extra env (8b606f16's row_pod picks all snapshot steps if form (B) needs them). ETA ~08:45Z.
- 2c5e038b pod tests (/workspace/lane/logs/tests_2c5e.log, run by the predecessor 06:51Z): all pass except 3
  test_commit_fail_closed dead-watchdog tests, which fail on "Ninja is required to load C++ extensions" in a subprocess
  (environment, not the fix: /workspace/venv312/bin/ninja exists but is not on the ssh shell's PATH). 08:06Z: rerun with
  PATH=/workspace/venv312/bin:$PATH + a private TORCH_EXTENSIONS_DIR: all 3 pass (logs/tests_2c5e_watchdog_path.log).
- #67 Match runs with snapshot steps 0,1: no row_pod form (B) line => form_b_families(OLMoE manifest) is empty (every required
  value has a replay evaluator), so 8b606f16's `all` does not apply. Manifest: 406,432 = instance_outputs 275,988,
  moe_block_stream 125,568, fa2_hidden_m1_stream 2,048, tokens 1,308+1,308, weights 212.
- #67 early check (vyv-sw-67b CPU, /workspace/lane/logs/repro67.log; script evidence/pod-scripts/repro67.py): population
  reconciliation over the fresh Build's Programs at 2c5e038b (the sweep's 20,928 identities_without_rows) + which members the
  promoted rule selects on OLMoE.

**#67 SCOPE CHANGE (06:30Z, for the coordinator):** a Commit-only rerun of #67 is impossible. Its row dir lived only on vyv-sw-67
(terminated 04:16Z), and the stored artifacts are account summaries: Build art:a0fb7ea8 (vllm-build/v1, 0.9 GB) skipped every
`instances.json.gz` (the Programs), Match art:f3430c8f (vllm-match-record/v1, 1.4 MB) skipped match/instances.jsonl + match/program.json;
no full row-dir tree exists for #67 (store select meta.row=olmoe-...b32...: 9 artifacts, all summaries). The Commit reads exactly those.
So the offline repro over #67's inputs is impossible too. Plan: run #67's full row (Build -> Match -> Commit, same flags, source
8b606f16) on vyv-sw-67b, one laptop `research run --on` per stage as the sweep did. Estimate from the sweep: Build ~26 min, Match
~45 min, Commit ~1h40m => ~3h after bootstrap (~10:00Z), ~$5-6 at $1.58/h. Proceeding unless told to stop.

Task: #57 v2 Commit local_replay fix (432 promoted model/out identities_without_rows + form (B) None; snapshot-steps gap);
#67 follow-on if same cause. Spec: pod /workspace/lane/BRIEF.md; facts /workspace/lane/sweep-status-0205Z.md.
Schedule: 20260924T0545Z-from-coordinator-schedule.md (57-cause 07:00Z, 57-fix 09:00Z, 57-pass 10:00Z, 57-ready 10:30Z, 67-pod 10:30Z, 67-pass 12:30Z).

- Merge check (08:10Z): staging lane/vllm-cleanup-2 is still 38122d1f (clean). Onto lane/vllm-retire-v1 9d80e302: merge-tree
  clean (tree eddd75bd; trial commit 25170f24, pushed ONLY to sw57 as trial/57-on-rv1, extracted at /workspace/lane/trial-rv1).
  Every symbol the fix calls exists there. SEMANTIC NOTE for the integrator: retire-v1 53d20e6c removes promoted addressing
  from sampled_replay (ProgramIndex promoted/rule, promoted_addresses_of gone) and deletes test_sampled_replay_promoted.py.
  2c5e038b's promote_handed_down marks the manifest in place, so at my tip the replay index also sees the promoted rows; on
  the merged tree only acquisition + form (B) read them. The #57 PASS at my tip therefore does not cover the merged replay
  path: #57's Commit should be rerun on the merged tree (int-57). Trial tests (same set as tests_2c5e minus the deleted
  test_sampled_replay_promoted.py, ninja on PATH): 237 passed, 13 skipped, 0 failed (logs/tests_trial_rv1.log).
- 08:14Z #57 rerun live signals (row commit.log): COMPOSITION OK; MANIFEST COVERAGE OK checked 163,168 missing 0;
  C2 ORACLE COMPARE OK compared 159,840 equal 159,840 mismatch 0 (was 432 mismatches at 8b606f16). Waiting on local_replay + verdict.
- 08:22Z #67 early check (repro67.log): population over the fresh Build's 32 Programs at 2c5e038b reconciles: vus 5,745,046,
  query_checks ok, accounted, vus_outside_query 0, identities_without_rows 0 (sweep: 20,928 MoE experts out at 014563ac),
  unreachable_by_alias 0, rows_disagree 0. => #67's population failure is #57's cause 1 (v1 addressing in the sweep's replay),
  already fixed at staging 38122d1f. Producer facts: 181 derived members, 0 conflicts; promote_handed_down selects 0 members
  on OLMoE => 2c5e038b changes nothing in #67's acquisition (no-behaviour-change evidence for a second model family).
- 08:27Z #57 at pair 1 (MANIFEST COVERAGE pair 1 OK 163,168). Laptop free disk back to 3.95 GB (someone freed space).
- 08:40Z #57 pairs 0+1 clean: "v2 manifest: 432 row(s) of 1 member(s) handed down ... marked promoted" (model/out -> first
  consumer model.layers.0.input_layernorm); SAMPLED REPLAY COMPLETE 5,883/5,883 equal (8b606f16 rerun: 37 Bf16MulScalarTensor
  mismatches); BOUNDARY LINKAGE 432/432; WEIGHTS PIN 316/316; OPENINGS 68/68. Pair 2 running, verdict ~08:45Z.

- 08:56Z #67 Match r20260924-075730-80bd PASS (`match PASS rc=0/0/0 wall=3482s verdict PASS global PASS tokens_equal True
  fold True`); match art:f95c7d6037484fd0f244b62d532b19f835b200e4a33f478c38b38426596d8ea5 (+result art:13ca9182, evidence art:a117d772).
- 08:57Z #67 Commit launched: run r20260924-085702-d2e3 on vyv-sw-67b GPU 0, source 2c5e038b, build art:5b7e5bcf + match
  art:f95c7d60. ETA ~10:40Z (sweep: ~1h40m).
- 09:00Z vyv-sw-57 idle -> #57 Commit on the retire-v1 trial merge 25170f24 (same inputs), to answer the merged-replay question
  before int-57: run r20260924-085749-2570 (GPU 0), launched from a throwaway /tmp worktree (removed), source tree
  /workspace/research/src/25170f24… on the pod. ETA ~09:50Z. It reuses #57's row dir (the PASS run's evidence is preserved:
  verdict art:b99af6c6, logs art:e364e35a, run dir outputs/). #67 Match artifacts preserved (rc 0).
- 09:22Z trial-merge #57: 432 rows marked promoted; C2 ORACLE COMPARE pair 0 OK 159,840/159,840 (replay pending).
  #67 Commit: producer facts 181 members, 0 conflicts, no handed-down rows; MANIFEST COVERAGE pair 0 OK 406,220 missing 0.
- 09:33Z trial-merge #57 pair 0: SAMPLED REPLAY COMPLETE 5,883/5,883, BOUNDARY LINKAGE 432/432 (the merged replay path holds).
  #67 pair 0 C2 ORACLE COMPARE partial (Match snapshot steps 0,1): compared 16,120 equal 16,120 mismatch 0; 262,484 values at
  unsnapshotted steps go to the sampled replay (form_b_families empty, so a partial C2 is not a gap; the sweep failed only population).
- 09:55Z trial-merge #57 (25170f24 = 2c5e038b onto retire-v1 9d80e302) r20260924-085749-2570: commit PASS rc=0 wall=3031s runs 3
  failed 0, every check PASS; replay 5,883/5,883 x3. verdict art:6b939117e164e5c36adba5fbb6cf22ca812cf539a6d416c4f4f672d75098770d
  (preserved rc 0, 6 labels incl. arm=trial-merge-onto-retire-v1-9d80e302). Appended to the integrator ready note. vyv-sw-57 idle.
- 10:00Z #67 Commit pair 0 in the sampled replay (32 workers, 38,748 VUs).
- 10:12Z #67 Commit at 2c5e038b (r20260924-085702-d2e3) pair 0 COMMIT FAIL: "C2 of record not established: sampled replay
  partial -- 2416 strata not evaluated", all MoeSum_v1{TOPK=8,H=2048} at model.layers.N.mlp.experts, why "evaluator produced no
  member 'out'" (36,332 evaluated, all equal; population ok; linkage 1308/1308; weights 212/212; C2 oracle 16,120 equal).
  That is exactly what retire-v1 6813fe06 fixes ("replay_vu compares a copied row's one output against its member (the MoeSum at
  TP1 was 'evaluator produced no member out' under v2)"). Evidence copied to vyv-sw-67b /workspace/lane/evidence/commit67_2c5e038b/.
  Terminated the run at 10:15Z (SIGTERM to pgid; rc 143; pairs 1-2 would fail the same way and hold the row dir).
- DECISION 10:16Z: staging lane/vllm-cleanup-2 had already merged this lane (b53686f0 = merge of 2c5e038b), the relayout
  (738e63f5) and retire-v1 (6813fe06 included); tip 2c8aa2b3. Fast-forwarded lane/vllm-57-fix to 2c8aa2b3 (no new commit),
  pushed origin + sw57. #67 now runs at the integrated tip; script path is now integrations/vllm/verity_vllm/ops/run_row_v2.sh.
- 10:19Z #67 Commit at 2c8aa2b3: run r20260924-101839-ef1b on vyv-sw-67b GPU 0 (source shipped by git archive, 2813 files),
  build art:5b7e5bcf + match art:f95c7d60. ETA ~12:00Z (pair 0 took ~75 min last time). 67-pass at risk only if it slips past ~12:15Z.
- vyv-sw-57: /workspace/verity now at 2c8aa2b3; one untracked leftover dir integrations/vllm/verity_vllm_numerics/ (relayout residue, left alone).
- 10:20Z #67 Commit at 2c8aa2b3 (r20260924-101839-ef1b) died in 29 s: commit_delta.py:1417 `ModuleNotFoundError: No module named
  'verity_capture'` (then the stage graded the killed run's leftover commit/runs.jsonl: "runs 1 failed 1"). STAGING IS BROKEN for
  every v2 Commit: the relayout's move map predates #57's fix and its import check runs module bodies only; the fix's function-local
  imports kept old paths (commit_delta 996-998 + 1417 verity_capture.commit; oracle_compare.producers_of_programs
  verity_vllm.query.correspondence -> correspondence.reader_for_query). Tree-wide ast scan (py3.12): only these + a data script
  (data/contract/ck-elem/argmax_rule/measure_archive.py:27 verity_vllm.capture, not on a Commit path, left alone).
- f16703a2 (origin + sw57): repoints the 5 imports + tests/test_imports_resolve.py (ast lint: every absolute first-party import in
  verity_vllm/ and tests/ resolves to a file, function-local included). Handoff to the integrator:
  lanes/integrator/20260924T1027Z-handoff-from-vllm-57-fix.md (take f16703a2 before the final harness).
- Stale #67 commit/ dir moved to vyv-sw-67b /workspace/lane/evidence/commit67_2c5e038b/commit_dir (so a crash can't grade it again).
- 10:26Z #67 Commit at f16703a2: run r20260924-102613-0196 on vyv-sw-67b GPU 0 (source f16703a2 shipped, 2814 files), build
  art:5b7e5bcf + match art:f95c7d60. ETA ~12:05Z.
- Tests at f16703a2 on vyv-sw-57, green 10:27Z: logs/tests_f16703a2.log 79 passed (imports lint, oracle v2 producers, oracle,
  promoted key, commit_delta cli, verdict, no_by_name, no_dead_modules) + tests_f16703a2_b.log 77 passed 4 skipped (promoted
  acquisition, form B perturbation, fail-closed, hot commit, sampled replay v2 addresses + query population). 0 F/E.
- 10:28Z #67 Commit r20260924-102613-0196 is past the import that killed 2c8aa2b3 (0 Tracebacks; engine warm-up running).
- 10:31Z integrator 0905Z asks for #57 Commit-only on the merged tip 2c8aa2b3 (same inputs). 2c8aa2b3 crashes on the stale imports, so
  run it at f16703a2 (= 2c8aa2b3 + import fix): r20260924-103124-47d5 on vyv-sw-57 GPU 0, build art:f1baace0 + match art:a225cf5f,
  source tree built on the pod by git archive. Trial-merge commit dir moved to /workspace/lane/evidence/commit57_trial_rv1_25170f24/
  (already preserved as art:6b939117). Past imports, warm-up at 10:32Z. ETA ~11:25Z (last wall 3031 s).
- 10:45Z #57@f16703a2 pair 0: BINDING coverage 171,388/171,388, COMPOSITION OK, MANIFEST COVERAGE OK 163,168 missing 0.
  #67@f16703a2 pair 0: source identity OK f16703a2 (all four trees), control tokens_eq True; attempt running. 0 errors on both.
- 10:58Z #57@f16703a2 pair 0: producer facts used (318 members, 0 conflicts), 432 model/out rows marked promoted, C2 ORACLE COMPARE OK
  159,840/159,840 (so the repointed oracle_compare import is live; dropped facts would show compared 114,480). Replay next.
  #67@f16703a2 pair 0: producer facts used (181, 0 conflicts), MANIFEST COVERAGE OK 406,220, C2 partial 16,120/16,120 equal --
  identical to the 2c5e038b run. The decider is pair 0's sampled replay (MoeSum strata, fixed by 6813fe06), expected ~11:40Z.

## Checkpoints
- CHECKPOINT 67-pass AT-RISK 10:28Z -- #67 Commit at 2c5e038b failed on MoeSum replay (fixed by retire-v1 6813fe06, now on staging);
  the rerun at staging 2c8aa2b3 crashed on stale relayout imports (fixed f16703a2). Rerun r20260924-102613-0196 launched 10:26Z;
  ~1h40m => PASS ETA ~12:05Z, preserve + drain by ~12:20Z. Slips past 12:30Z if pair 0 runs >90 min.
- CHECKPOINT 57-cause MET 05:56Z -- offline repro on the pod (logs /workspace/lane/logs/repro_{pop,oracle}_base.log; script evidence/pod-scripts/repro57.py)
- CHECKPOINT 57-pass AT-RISK 07:05Z -- the #57 rerun (r20260924-061950-2148) exposed a second v2 gap on the ACQUISITION side: form (B)
  now compares 159,840 (equal 159,408, incl. all 44,928 fused-norm narrowings) but MISMATCHES the 432 `model/out`. The Commit hooks
  Gemma2Model's forward RETURN (final hidden, committed tensor `model`, ordinal 1615 at the end of the step stream) for `model/out`,
  while the v2 Value is the embed scale (Bf16MulScalarTensor_v1) that model's body hands to model.layers.0. Cause: the v2 manifest has
  no `promoted`/`consumers`, so acquisition_plan (correspondence source v1_annotations) picks producer_output(model, out) and
  commit_delta's promoted_input_acquisition arms nothing. Fix in progress: derive promoted+consumers from the Programs before arming
  (a body Value whose readers are all inside the producer module's subtree is no return of it -> first consumer's input). Needs a
  second Commit rerun (~50 min + ~9 min producer facts); ETA PASS ~09:45Z if the fix lands by ~08:45Z.
- CHECKPOINT 57-fix MET 06:20Z -- 4f6f6d1d + 8b606f16 pushed (origin, sw57); touched tests + test_no_by_name_rules green on the pod; offline
  repro with the fix: form (B) compared 159,840 (base 114,480), not compared outside no-oracle families 0 (log repro_oracle_fixed.log).
- CHECKPOINT 57-ready MET 08:58Z -- lanes/integrator/20260924T0858Z-from-vllm-57-fix-ready-2c5e038b.md (tip 2c5e038b; ff onto
  staging 38122d1f; clean onto retire-v1 9d80e302 with trial tests 237/0; asks for a #57 Commit rerun on the merged tree because
  retire-v1 53d20e6c drops promoted addressing from replay). Verdict art:b99af6c6 preserved (rc 0) + 5 labels durable.
- CHECKPOINT 57-pass MET 08:49Z -- #57 Commit-only rerun r20260924-075409-3621 at 2c5e038b on vyv-sw-57: `commit PASS
  2026-09-24T08:48:50Z rc=0 wall=2882s runs 3 failed 0` runtime_match, local_replay, boundary_linkage, checkpoint_binding,
  execution_extent, required_value_coverage, program_source_identity PASS; manifest_verify True. C2 oracle 159,840/159,840 equal,
  sampled replay 5,883/5,883 equal (x3 pairs). verdict art:b99af6c6efa601b5443955f0416c0badd351de7eb7656677bbf68c7547e4459e,
  result art:8a8b7f9b, evidence art:73d5fa9b, logs art:e364e35a (published from the pod, "PRESERVED on the remote").
- CHECKPOINT 57-fix MET 08:06Z (re-met at the tip 2c5e038b, the acquisition-side fix) -- pushed origin + sw57; its touched tests
  green on the pod (tests_2c5e.log; the 3 dead-watchdog failures pass with ninja on PATH, tests_2c5e_watchdog_path.log).

## Root cause (#57 Commit 8cb4, from the offline reproduction at base 38122d1f)
Two independent failures; the first is already fixed on staging, the second is the fix of this lane.
1. `population_scope identities_without_rows x432 (model/out)`: the sweep's Commit ran source 014563ac, whose replay addressed Program rows
   by the v1 rule. At 38122d1f (v2 addressing in sampled_replay.ProgramIndex, rule `v2-query`, program_dir correspondence) the same
   Programs + manifest reconcile exactly: query_checks ok, identities_without_rows 0, vus_outside_query 0, rows_disagree 0, accounted, 163484/163484.
   No code change needed; the rerun at the tip confirms it.
2. `population_gaps ... form (B) result None`: form (B) (oracle_compare) left 45,360 instance_outputs not compared (reproduced exactly: compared 114,480):
   - 44,928 = "ambiguous producer: 2 instances of NarrowF32ToBf16_v1 per row" under every fused norm (input_layernorm, pre_feedforward_layernorm, model.norm; members 0/1);
   - 432 = `model/out` "no fold instance of this op at this step": the embed scale (Bf16MulScalarTensor_v1) is hinted `model.normalizer` by the fold, its v2 identity is `model/out`.
   Cause: the oracle selects a producer by the manifest row's v1 annotations (producer_operand / producer_ordinal; promoted + consumers).
   A `v2-query` manifest (v1_bridge.request_manifest) carries none of them, so the oracle can neither pick among the fused norm's two
   narrowings nor resolve the embed scale through its consumers.
Fix (committed): derive the same facts from the Programs of record by dataflow at Commit time (oracle_compare.program_producer_facts:
producing Call family, first-operand producer family, reading modules outside the producer's module) and merge them where the manifest
row declares none (merge_producers); the oracle resolves a member through the Value (consumer operand -> producer output, M-0721(1)'s
mechanism) when the fold has no instance of the producer family under the identity's path. Facts that disagree across Programs carry no selector.
Snapshot-steps gap: row_pod.sh sets Match snapshot steps = all when sampled_replay.form_b_families(manifest) is non-empty (required
instance_outputs with no replay evaluator) and MATCH_SNAP_STEPS is unset; an explicit partial value is kept with a WARN naming the families.

## Tip (10:30Z)
- f16703a2 (origin + sw57, worktree clean) = staging 2c8aa2b3 + relayout import fix. Lane commits: 4f6f6d1d form (B) producer facts
  by dataflow; 8b606f16 row_pod.sh snapshot steps; 2c5e038b observe handed-down v2 values at first consumer (all merged into staging
  as b53686f0); f16703a2 repoint 5 stale imports + tests/test_imports_resolve.py (NOT yet on staging; handoff 1027Z).

## Done
- worktree + pod remote set up; pod checkout at 8b606f16.
- pod-side pilot worker loop is stopped (/workspace/lane/STOP_WORKER 05:40Z); its idle `agent worker` pid 37762 left alone.
- tests on the pod at 8b606f16: new commit/tests/test_oracle_compare_v2_producers.py + touched oracle_compare/commit_delta/sampled_replay
  tests + tests/test_no_by_name_rules.py all pass.
- original failing Commit 8cb4 evidence copied to /workspace/lane/evidence/commit_8cb4 (+ commit_8cb4.log) before the rerun.
- R2 credential: minted 06:07Z with the worktree's research (`PYTHONPATH=tools/research/src python -m research data mint-credential
  --ttl 6h --via local --env`, r2.env sourced in a subshell; the laptop venv's `research` binary is too old to have `data`). Minted fresh
  per launch; the one inside r20260924-102613-0196 (10:26Z, 6h) outlives its ~12:05Z publish.

## Running (10:30Z)
- #67 Commit r20260924-102613-0196 on vyv-sw-67b GPU 0 at f16703a2 (build art:5b7e5bcf, match art:f95c7d60). ETA ~12:05Z.
  Row dir /workspace/cp/sweep-v2s/olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager (commit.log, stages.txt).
- vyv-sw-57: idle (checkout 2c8aa2b3; do not terminate).

## Next
- #67 verdict -> preserve (published from the pod; check `data preserved --mode recorded`, labels) -> CHECKPOINT 67-pass -> drain vyv-sw-67b.
- Final summary.

## History (pre-08:00Z, superseded)
- #57 Commit-only rerun: run r20260924-061950-2148 on vyv-sw-57 (runner pid 39395, workload pid 39406), GPU 0, source 8b606f16,
  build=art:f1baace0…, match=art:a225cf5f…, launched 06:19Z. Observe: pod /workspace/research/runs/r20260924-061950-2148/ or `research fetch`.
  (06:07Z attempt refused: shipping 168 MB from the laptop exceeded 600s at ~0.3 MB/s. Workaround: build /workspace/research/src/<sha>/ on
  the pod with `git archive <sha> | tar -x` from /workspace/verity; the launcher adopts it by per-file sha256 (legacy path). Local record
  r20260924-061901-c333 is an orphan stuck at phase=shipping; nothing ran for it.)

- vyv-sw-67b: pod w5aiv36vhliqbu, 2x L40S COMMUNITY, 251 GB, 56 vCPU, 300 GB disk, driver 550.144 (CUDA 12.4; the stack is cu129 --
  bootstrap's torch_cuda check decides; if it fails, replace the pod with a >=575 driver host), $1.58/h, ssh -p 1728 root@193.183.22.51
  (runpodctl key), machines.toml entry added. Source 8b606f16 shipped as a gzip'd git archive over ssh (55 s) then adopted by the launcher.
  Bootstrap run r20260924-062646-d1a9 (`pod_bootstrap.sh --gpu --cases OLMOE`): BOOTSTRAP-OK 06:35Z, readiness ok (torch 2.13+cu129
  runs on driver 550 via minor-version compat; hidden_gpu + FA2 taps built sm_89).
- #67 Build: run r20260924-063717-5860 on vyv-sw-67b (runner pid 2146), GPU 0, source 8b606f16, launched 06:37Z. Next: Match with
  --input build=<its vllm-build artifact>, then Commit with build+match (each a laptop `research run --on vyv-sw-67b`, same env as #57).
- #67 row args: OLMOE allenai/OLMoE-1B-7B-0924 6d84c48581ece794365f2b8e9cfb043c68ade9c5, row
  olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager, --retain host --build-jobs auto --sweep-dir /workspace/cp/sweep-v2s.
- (old next, done) #57 rerun -> verdict; preserve; ready note; #67 judgment.
