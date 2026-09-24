---
lane: vllm-57-fix
repo: verity (~/projects/verity), worktree ~/projects/verity-wt/57-fix
branch: lane/vllm-57-fix (off origin/lane/vllm-cleanup-2 = 38122d1f), pushed to origin + pod remote sw57
pod: vyv-sw-57 (ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 12152 root@202.181.159.235), checkout /workspace/verity
---
# vllm-57-fix: running state

Task: #57 v2 Commit local_replay fix (432 promoted model/out identities_without_rows + form (B) None; snapshot-steps gap);
#67 follow-on if same cause. Spec: pod /workspace/lane/BRIEF.md; facts /workspace/lane/sweep-status-0205Z.md.
Schedule: 20260924T0545Z-from-coordinator-schedule.md (57-cause 07:00Z, 57-fix 09:00Z, 57-pass 10:00Z, 57-ready 10:30Z, 67-pod 10:30Z, 67-pass 12:30Z).

## Checkpoints
- CHECKPOINT 57-cause MET 05:56Z -- offline repro on the pod (logs /workspace/lane/logs/repro_{pop,oracle}_base.log; script evidence/pod-scripts/repro57.py)

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
- #57 Commit-only rerun: `research run --on vyv-sw-57 --tool vllm.commit --source . (8b606f16)` with build=art:f1baace0…, match=art:a225cf5f…
  (launched 06:07Z from the laptop; run id pending in the launch output).
- offline repro, fixed oracle: pod `repro57.py oracle-fixed`, log /workspace/lane/logs/repro_oracle_fixed.log (derived 318 producers, 0 conflicts).

## Next
- #57 rerun -> verdict; preserve (data push + preserved --mode recorded + labels); ready note; #67 judgment (MoE experts output, 20,928 identities_without_rows).
