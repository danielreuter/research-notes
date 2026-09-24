---
lane: vllm-57-fix
repo: verity (~/projects/verity), worktree ~/projects/verity-wt/57-fix
branch: lane/vllm-57-fix (off origin/lane/vllm-cleanup-2 = 38122d1f), pushed to origin + pod remote sw57
pod: vyv-sw-57 (ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 12152 root@202.181.159.235), checkout /workspace/verity
---
# vllm-57-fix: running state

**07:58Z successor took over (predecessor died 06:51Z with Cursor).** BLOCKER (laptop-wide, handed to coordinator
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
  already fixed at staging 38122d1f. Promoted-member listing still running.

## Checkpoints
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

## Tip
- 8b606f16 (origin + sw57): 4f6f6d1d form (B) producer facts by dataflow; 8b606f16 row_pod.sh snapshot steps + tests.

## Done
- worktree + pod remote set up; pod checkout at 8b606f16.
- pod-side pilot worker loop is stopped (/workspace/lane/STOP_WORKER 05:40Z); its idle `agent worker` pid 37762 left alone.
- tests on the pod at 8b606f16: new commit/tests/test_oracle_compare_v2_producers.py + touched oracle_compare/commit_delta/sampled_replay
  tests + tests/test_no_by_name_rules.py all pass.
- original failing Commit 8cb4 evidence copied to /workspace/lane/evidence/commit_8cb4 (+ commit_8cb4.log) before the rerun.
- R2 credential: minted 06:07Z with the worktree's research (`PYTHONPATH=tools/research/src python -m research data mint-credential
  --ttl 6h --via local --env`, r2.env sourced in a subshell; the laptop venv's `research` binary is too old to have `data`), valid to ~12:07Z.

## Running
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

## Next
- #57 rerun -> verdict; preserve (data push + preserved --mode recorded + labels); ready note; #67 judgment (MoE experts output, 20,928 identities_without_rows).
